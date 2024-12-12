import os
import platform
import re
import subprocess
import tempfile
import uuid

from core.services.ggle.fetcher.main import GoogleFetcher

from .odoo.fetcher import OdooFetcher


# Restrict resources that the celery process uses for this
class GoogleDriveVideoCompressor:

    def __init__(self):
        self.compress_to_folder_id = ""
        self.compress_from_folder_ids = []
        self.odoo_fetcher = OdooFetcher()
        self.ggle_fetcher = GoogleFetcher()
        self.path = ""

    def _fetch_video_urls_from_odoo(self):
        df = self.odoo_fetcher.read_uncompress_video_url()
        return df

    def _download_video(self, file_id):
        """
        Logic to download video from google drive with url
        """
        tempfile_dir = tempfile.gettempdir()+r'\video_compress'
        # Ensure the directory exists
        os.makedirs(tempfile_dir, exist_ok=True)
        print(f'FileId: {file_id}')
        data = self.ggle_fetcher.download_video(file_id)
        unique_filename = str(uuid.uuid4()) + "_.mp4"
        temp_file_path = os.path.join(tempfile_dir, unique_filename)
        # Write the video content to the temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(data)
        return temp_file_path

    def _compress_video(self, video_file_path):
        """
        Logic to compress video
        """
        print(f'Video file path: {video_file_path}')
        output_compressed_file_path = f"{video_file_path[:-5]+".mp4"}"
        print(f'Output compressed file path: {output_compressed_file_path}')
        codec = ["libx265", "libx264", "libvpx", "libaom-av1"][0]
        preset = ["ultrafast", "superfast", "veryfast", "faster",
                  "fast", "medium", "slow", "slower", "veryslow", "placebo"][5]
        crf = 35 # 0-51, 0 is lossless, 23 is default, 51 is worst
        compress_cmd = [
            # compression 73.10% less size (80514 -> 21660)
            # time 6X (131.356366)
            "ffmpeg",
            "-i",
            video_file_path,
            "-vcodec",
            codec,
            "-preset",
            preset,
            "-crf",
            str(crf),
            output_compressed_file_path,
        ]

        # Check the operating system
        if platform.system() == "Windows":
            ffmpeg_command = list()
            print("Windows")
            print(compress_cmd)
            ffmpeg_command.extend(compress_cmd)
        elif platform.system() == "Linux":
            ffmpeg_command = ["taskset","-c","0,1",]
            print("Linux")
            print(compress_cmd)
            ffmpeg_command.extend(compress_cmd)
        else:
            raise Exception("Unsupported operating system")

        # Execute the command
        subprocess.run(ffmpeg_command)
        return output_compressed_file_path

    def _upload_video(self, temp_video_path):
        """
        Logic to upload video to the new limited access (read-only to normal user) google drive folder
        """
        file_url = self.ggle_fetcher.upload_video(file_path=temp_video_path)
        return file_url

    def _delete_video_from_original_folder(self, file_id):
        """
        Logic to delete video from old folder
        """
        self.ggle_fetcher.delete_video(file_id)

    def _publish_video_links_to_odoo(
        self, model,data
    ):
        """
        Logic to publish video links to odoo one by one (write method from odoo fetcher)
        """
        return self.odoo_fetcher.write_model(
            model_name=model,
            data=data
        )

    def _kill_process(self):
        """
        Logic to kill the process if it is already running
        """
        pass

    def compress(self):
        """
        Logic to compress video
        """
        self._kill_process()
        df = self._fetch_video_urls_from_odoo()
        for _, row in df.iterrows():
            try:
                url = row["video_url"]
                _id = row["id"]
                field_url = row["field_name"]
                field_bool = row["is_compressed_field_name"]
                model = row["model_name"]

                match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
                old_file_id = match.group(1)
                download_video_path = self._download_video(old_file_id)
                compressed_video_path = self._compress_video(download_video_path)
                new_file_url = self._upload_video(compressed_video_path)
                data = {
                    "id":int(_id),
                    field_url:new_file_url,
                    field_bool:True
                }
                if self._publish_video_links_to_odoo(
                    model,data
                ):
                    print(f"Deleted video_id: {old_file_id}")
                    # uncomment when sure everything is right
                    # self._delete_video_from_original_folder(old_file_id)
                os.remove(download_video_path)
                os.remove(compressed_video_path)
                print('File compressed successfully')
                # remove break when sure everything is right
                break
            except Exception as e:
                raise Exception(
                    "Error while compressing video_id: %s" % row["id"] + str(e)
                )
