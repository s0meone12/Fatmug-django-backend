from rest_framework import status
from kn_api.ggle_api.ggle_operations import GgleModelOperation


class GoogleFetcher:

    def download_video(self, old_file_id):
        data = {"file_id": old_file_id}
        ggle_client = GgleModelOperation()
        response = ggle_client.download(data)
        if response["status"] == status.HTTP_200_OK:
            data = response["data"]
            return data
        raise Exception("Error while downloading video")
        # return None

    def delete_video(self, old_file_id):
        data = {"file_id": old_file_id}
        ggle_client = GgleModelOperation()
        response = ggle_client.delete(data)
        if response["status"] == status.HTTP_200_OK:
            return "delete succesfull"

    def list_files(self, folder_id, shared_drive_id):
        data = {"folder_id": folder_id, "shared_drive_id": shared_drive_id}
        ggle_client = GgleModelOperation()
        response = ggle_client.list_files(data)
        if response["status"] == status.HTTP_200_OK:
            return response["data"]

    def upload_video(self, file_path):
        with open(file_path, "rb") as file:
            files = {"file": file}
            ggle_client = GgleModelOperation()
            response = ggle_client.upload(
                files=files, params={"get_download_links": True}
            )
            if response["status"] == status.HTTP_200_OK:
                url = response["data"].get("data")
                return url
        return None
