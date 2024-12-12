from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from core.models.wordpress_webhook.wordpress_webhook_model import WordPressWebhook

class WordpressWebhookView(ViewSet):
    permission_classes = [AllowAny]
    
    def wordpress_webhooks(self, request):
        data = request.data
        if data:
            ship_res = WordPressWebhook.manager._process_hook(payload=data)
            return Response({'message': 'data received successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
    