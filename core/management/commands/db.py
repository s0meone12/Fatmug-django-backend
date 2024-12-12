from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import subprocess
import os
import datetime
from django.db import connections


class Command(BaseCommand):
    help = 'Backup PostgreSQL database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--operation', choices=['backup', 'restore', 'restore_from_server'], help='Operation to perform: backup or restore')
        parser.add_argument(
            '--backupfile', help='Path to the backup file (required for restore operation)')

    def handle(self, *args, **options):
        operation = options['operation']
        backup_file_name = options['backupfile']

        if operation == 'backup':
            self.backup_database()
            print("backup is running")
        elif operation == 'restore':
            print("restoring is running")
            self.restore_database(restore_file_name=backup_file_name)
        elif operation == 'restore_from_server':
            print("restoring from server is running")
            self.restore_from_server()

    def backup_database(self):
        # Get database settings from Django settings
        db_settings = settings.DATABASES['default']

        # Get current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')

        # Define backup file name
        backup_file = f"{db_settings['NAME']}_backup_{timestamp}.sql"

        # Define backup file path
        backup_folder = os.path.join(settings.BASE_DIR, 'backups')
        # Ensure the backup folder exists
        os.makedirs(backup_folder, exist_ok=True)
        backup_file_path = os.path.join(backup_folder, backup_file)

        # Prepare the command for dumping the database
        dump_cmd = [
            'pg_dump',
            '-U', db_settings['USER'],
            '-h', db_settings['HOST'],
            '-p', str(db_settings['PORT']),
            '-d', db_settings['NAME'],
            '-f', backup_file_path
        ]

        # Set up the environment with the database password
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']

        # Run the command
        subprocess.run(dump_cmd, shell=False, check=True, env=env)

        self.stdout.write(self.style.SUCCESS(
            f"Backup created successfully at {backup_file_path}"))

        # Manage old backups if necessary
        backups = [f for f in os.listdir(backup_folder) if os.path.isfile(
            os.path.join(backup_folder, f))]
        if len(backups) > 5:  # Keep only the latest 5 backups, adjust this number as needed
            oldest_backup = min(backups, key=lambda f: os.path.getctime(
                os.path.join(backup_folder, f)))
            os.remove(os.path.join(backup_folder, oldest_backup))
            self.stdout.write(self.style.SUCCESS(
                f'Oldest backup file {oldest_backup} deleted'))

    def __drop_and_recreate_database(self):
        db_settings = settings.DATABASES['default']
        dbname = db_settings['NAME']
        user = db_settings.get('USER', 'postgres')
        password = db_settings.get('PASSWORD')
        host = db_settings.get('HOST', 'localhost')
        port = db_settings.get('PORT', 5432)

        # Setup environment variables for subprocess
        env = os.environ.copy()
        env['PGPASSWORD'] = password

        # Close Django's connection to the database
        connections.close_all()

        try:
            # Terminate all connections to the database
            terminate_connections_cmd = (
                f'psql -h {host} -p {port} -U {user} -d postgres -c "SELECT pg_terminate_backend(pg_stat_activity.pid) '
                f'FROM pg_stat_activity WHERE pg_stat_activity.datname = \'{dbname}\' AND pid <> pg_backend_pid();"'
            )
            subprocess.run(terminate_connections_cmd,
                           shell=True, check=True, env=env)

            # Drop the database
            drop_db_cmd = f'psql -h {host} -p {port} -U {user} -d postgres -c "DROP DATABASE IF EXISTS \\"{dbname}\\";"'
            subprocess.run(drop_db_cmd, shell=True, check=True, env=env)

            # Create the database
            create_db_cmd = f'psql -h {host} -p {port} -U {user} -d postgres -c "CREATE DATABASE \\"{dbname}\\";"'
            subprocess.run(create_db_cmd, shell=True, check=True, env=env)

            self.stdout.write(self.style.SUCCESS(
                f'Successfully dropped and recreated database: {dbname}'))
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Error executing database operation: {e}')

    def restore_database(self, *args, **kwargs):
        backup_folder = os.path.join(settings.BASE_DIR, 'backups')
        restore_file_name = kwargs.get("restore_file_name")
        restore_file_path = None
        if restore_file_name:
            restore_file_path = os.path.join(backup_folder, restore_file_name)
            if not os.path.exists(restore_file_path):
                raise CommandError(
                    f'Restore file {restore_file_name} does not exist')

        if not restore_file_name and not len(os.listdir(backup_folder)):
            raise CommandError('No file exists for restoring')

        if not restore_file_name:
            files = [f for f in os.listdir(backup_folder) if os.path.isfile(
                os.path.join(backup_folder, f))]
            latest_restore_file_name = max(
                files, key=lambda f: os.path.getctime(os.path.join(backup_folder, f)))
            restore_file_path = os.path.join(
                backup_folder, latest_restore_file_name)

        self.__drop_and_recreate_database()
        db_settings = settings.DATABASES['default']

        restore_cmd = [
            'PGPASSWORD=' + db_settings['PASSWORD'],
            'psql',
            '-U', db_settings['USER'],
            '-h', db_settings['HOST'],
            '-p', str(db_settings['PORT']),
            '-d', db_settings['NAME'],
            '-f', restore_file_path
        ]

        subprocess.run(" ".join(restore_cmd), shell=True, check=True)

        self.stdout.write(self.style.SUCCESS(
            f"Restore successfully done for {restore_file_name}"))

    def __generate_backup_at_server(self):
        server_host = settings.SERVER_IP
        server_user = settings.SERVER_USERNAME
        core_container_name = 'core'
        ssh_key_path = '/root/.ssh/id_rsa'

        generate_backup_cmd = (
            f'ssh -i {ssh_key_path} -o StrictHostKeyChecking=no {server_user}@{server_host} '
            f'"docker exec {core_container_name} python manage.py db --operation backup"'
        )

        try:
            subprocess.run(generate_backup_cmd, shell=True, check=True)
            self.stdout.write(self.style.SUCCESS(
                'Backup generated successfully on the server'))
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Error generating backup on server: {e}')

    def __download_backup_from_server(self):
        def __get_latest_backup_file():
            backup_dir = settings.SERVER_DB_BACKUP_DIR
            get_latest_backup_cmd = (
                f'ssh -i {ssh_key_path} -o StrictHostKeyChecking=no {server_user}@{server_host} '
                f'"ls -t {backup_dir}/*.sql | head -n 1"'
            )

            try:
                result = subprocess.run(
                    get_latest_backup_cmd, shell=True, check=True, stdout=subprocess.PIPE)
                latest_backup_file = result.stdout.decode().strip()
                return latest_backup_file
            except subprocess.CalledProcessError as e:
                raise CommandError(
                    f'Error getting latest backup file from server: {e}')
        server_host = settings.SERVER_IP
        server_user = settings.SERVER_USERNAME
        ssh_key_path = '/root/.ssh/id_rsa'

        # Get the latest backup file on the server
        remote_backup_path = __get_latest_backup_file()
        if not remote_backup_path:
            raise CommandError("No backup file found on the server")

        local_backup_folder = os.path.join(settings.BASE_DIR, 'backups')

        local_backup_path = os.path.join(local_backup_folder, os.path.basename(
            remote_backup_path))  # Update this to the desired local path

        download_backup_cmd = (
            f'scp -i {ssh_key_path} -o StrictHostKeyChecking=no {server_user}@{server_host}:{remote_backup_path} {local_backup_path}'
        )

        try:
            subprocess.run(download_backup_cmd, shell=True, check=True)
            self.stdout.write(self.style.SUCCESS(
                f'Backup downloaded successfully from server to {local_backup_path}'))
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Error downloading backup from server: {e}')

    def _remove_all_local_backups(self):
        backup_folder = os.path.join(settings.BASE_DIR, 'backups')
        for backup_file in os.listdir(backup_folder):
            backup_file_path = os.path.join(backup_folder, backup_file)
            if os.path.isfile(backup_file_path):
                os.remove(backup_file_path)
                self.stdout.write(self.style.SUCCESS(
                    f'Deleted local backup file: {backup_file}'))

    def __remove_local_migration_files(self):
        local_migration_folder = os.path.join(settings.BASE_DIR, 'migrations')

        if os.path.exists(local_migration_folder):
            for migration_file in os.listdir(local_migration_folder):
                migration_file_path = os.path.join(
                    local_migration_folder, migration_file)
                if os.path.isfile(migration_file_path):
                    os.remove(migration_file_path)
                    self.stdout.write(self.style.SUCCESS(
                        f'Deleted local migration file: {migration_file}'))
                elif os.path.isdir(migration_file_path):
                    for root, dirs, files in os.walk(migration_file_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            self.stdout.write(self.style.SUCCESS(
                                f'Deleted local migration file: {file_path}'))
                    os.rmdir(migration_file_path)
                    self.stdout.write(self.style.SUCCESS(
                        f'Deleted local migration directory: {migration_file_path}'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Local migration folder does not exist: {local_migration_folder}'))

    def __download_migration_files_from_server(self):
        server_host = settings.SERVER_IP
        server_user = settings.SERVER_USERNAME
        ssh_key_path = '/root/.ssh/id_rsa'
        remote_migration_folder = settings.SERVER_MIGRATION_FOLDER
        local_migration_folder = os.path.join(settings.BASE_DIR, 'migrations')

        # Ensure the local migration folder exists
        os.makedirs(local_migration_folder, exist_ok=True)

        # Command to download migration files from the server
        download_migration_cmd = (
            f'scp -i {ssh_key_path} -o StrictHostKeyChecking=no -r {server_user}@{server_host}:{remote_migration_folder}/* {local_migration_folder}/'
        )

        try:
            subprocess.run(download_migration_cmd, shell=True, check=True)
            self.stdout.write(self.style.SUCCESS(
                f'Migration files downloaded successfully from server to {local_migration_folder}'))
        except subprocess.CalledProcessError as e:
            raise CommandError(
                f'Error downloading migration files from server: {e}')

    def restore_from_server(self):
        self.__generate_backup_at_server()
        self._remove_all_local_backups()
        self.__download_backup_from_server()
        self.__remove_local_migration_files()
        self.__download_migration_files_from_server()
        self.restore_database()
