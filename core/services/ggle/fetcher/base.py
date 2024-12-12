from ..fetcher import GoogleFetcher
import io


class GoogleBaseFetcher():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ggle_fetcher=GoogleFetcher()

    def _list_files_in_folder(self, folder_id, shared_drive_id=None):
        
        data = self.ggle_fetcher.list_files(folder_id, shared_drive_id)
        files = data['files']
        return files

    def download_file_from_gdrive(self, file_id):
        """
        Downloads a file from Google Drive using the file ID.
        """
        data = self.ggle_fetcher.download_video(file_id)
        file_data = io.BytesIO(data)
        return file_data