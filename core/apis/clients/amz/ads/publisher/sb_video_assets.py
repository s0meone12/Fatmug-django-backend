from kn_api._kn_ad_api.sb.creative_assets import CreativeAssets
from sp_api.base import Marketplaces
from core.services.ggle.fetcher.base import GoogleBaseFetcher
import tempfile, os, time
from core.apis.clients.odoo.model import OdooModelClient


class VideoAssetIdGenerator:
    """
    This class will generate a unique video asset id for the video asset that is being uploaded to Amazon.
    """

    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        self.sb_video_asset = CreativeAssets(marketplace)
        self.ggle = GoogleBaseFetcher()

    def extract_file_id_from_gdrive_link(self, gdrive_link):
        # Split the URL on the '/' character
        parts = gdrive_link.split('/')

        # The file ID is the part after 'd'
        file_id_index = parts.index('d') + 1
        if file_id_index < len(parts):
            return parts[file_id_index]
        else:
            print("Invalid Google Drive link")
            return None

    def generate_video_asset_id(self, name, sku_id):
        """
        This method will generate a unique video asset id for the video asset that is being uploaded to Amazon.
        :param name: str: The name of the add.
        :param sku_id: str: The name of the id of sku of AmzSku model.
        :return: str: The unique video asset id.
        """
        # odoo give gdrive link of video by taking sku
        model_name = "kn.plm.creative.asset.iteration"
        fields = ['name','link','asset_id','state']
        self.odoo = OdooModelClient(model=model_name)
        res_df = self.odoo._read(fields=fields)
        df = res_df[res_df['state'] == 'approved']
        print(df)
        filtered_df = df[df['name'].str.startswith(sku_id)]
        if len(filtered_df) == 1:
            gdrive_link = filtered_df['link'].values[0]

        # gdrive_link = "https://drive.google.com/file/d/14f-6DyA0SS1Jau3grnUYVKrbtBJJu72b/view?usp=drive_link"
        file_id = self.extract_file_id_from_gdrive_link(gdrive_link)

        downloaded_io = self.ggle.download_file_from_gdrive(file_id)
        if downloaded_io is not None:
            # Save the downloaded file temp to disk and get the file path
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_file.write(downloaded_io.read())
                temp_file_path = temp_file.name
        else:
            print("Failed to download file")
            ValueError("Failed to download file")
            return

        # Create an asset upload URL and Upload your video asset
        # temp_file_path = 'C:\\Users\\HAMZA SIDDIQUI\\OneDrive\\Desktop\\ongoing work\\fatmug.mp4'
        params = {'__country__': 'IN'}
        with open(temp_file_path, 'rb') as file:
            files = {'file': file}
            res = self.sb_video_asset.create_asset(files, params)
            print(res)
        os.remove(temp_file_path)
        if res['status'] == 200:
            url = res['data']['url']
        else:
            return
        
        # now Register the asset 
        body = {
                "url": url,
                "name": name,
                "assetType": "VIDEO",
                "assetSubTypeList": ["BACKGROUND_VIDEO"],
                "associatedSubEntityList": [{"brandEntityId": "ENTITY2IK3PMA3W6DN"}],
                "skipAssetSubTypesDetection": True
                }
        response = self.sb_video_asset.register_asset(body=body, params=params)
        payload = response.payload
        asset_id = payload['assetId']

        condition = True
        while(condition):
            time.sleep(5)
            get_res = self.sb_video_asset.get_asset(assetId=asset_id, params=params)
            asset_id = get_res.payload['assetGlobal']['assetId']
            asset_status = get_res.payload['assetVersionList'][0]['assetStatus']
            if asset_status == 'ACTIVE':
                condition = False
        return asset_id
