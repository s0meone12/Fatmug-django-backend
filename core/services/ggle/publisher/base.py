from ..common import GoogleClient
from googleapiclient.http import MediaFileUpload
import os


class GoogleBasePublisher(GoogleClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_gd = self._client_gd()

    def upload_file_to_gdrive(self, file_path, folder_id=None):
        """
        Uploads a file to Google Drive or a Shared Drive.

        :param file_path: Path to the file to upload.
        :param folder_id: The ID of the folder on Google Drive or Shared Drive where the file will be uploaded.
        """
        # Name of the file on Google Drive after the upload.
        file_name = os.path.basename(file_path)

        # Define the MIME type of the file
        mime_type = 'application/octet-stream'  # Or use a specific MIME type if known

        # Create the media file upload object
        media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

        # Create the body of the request
        file_metadata = {
            'name': file_name,
            'mimeType': mime_type
        }

        # If a folder ID was provided, add it to the file's metadata
        if folder_id:
            file_metadata['parents'] = [folder_id]

        try:
            # Call the Google Drive API to upload the file
            file = self._client_gd.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            return file.get('id')
        except Exception as e:
            raise Exception(f"Error uploading file to Google Drive: {e}")

    def delete_file_from_gdrive(self, file_id):
        """
        Deletes a file from a Shared Drive in Google Drive.

        :param file_id: The ID of the file on the Shared Drive to be deleted.
        """
        try:
            # Call the Google Drive API to delete the file
            self._client_gd.files().delete(fileId=file_id, supportsAllDrives=True).execute()
            return f"File with id {file_id} was deleted successfully."
        except Exception as e:
            raise Exception(f"Error deleting file from Shared Drive: {e}")
