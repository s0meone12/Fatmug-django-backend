# from django.conf import settings
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build


# class GoogleClient:

#     def __init__(self, *args, **kwargs):
#         pass

#     def _client_gd(self):
#         credentials = Credentials.from_service_account_info({
#             "client_email": settings.GOOGLE_CLIENT_EMAIL,
#             "private_key": settings.GOOGLE_PRIVATE_KEY,
#             "token_uri": settings.GOOGLE_TOKEN_URI,  # This remains constant
#         }, scopes=['https://www.googleapis.com/auth/drive'])

#         drive_service = build('drive', 'v3', credentials=credentials)
#         return drive_service
