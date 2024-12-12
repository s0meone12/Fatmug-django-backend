from django.db import models
from core.manager.wordpress.wordpresswebhookmanager import WordPressWebhookManager, WordpressOrderManager, WordpressOrderShipmentManager

class WordPressWebhook(models.Model):
    action = models.CharField(max_length=255, blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    manager = WordPressWebhookManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        order_details = self.payload
        WordpressOrder.manager._create_order(payload=order_details)
    
    
class WordpressOrder(models.Model):
    STATE_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ]
    order_id = models.CharField(max_length=100, primary_key=True, default='')
    order_data = models.JSONField(blank=True, null=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='pending')
    manager = WordpressOrderManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        order_details = self.order_data
        WordpressOrderShipment.manager._full_fill_order(payload=order_details)
     
        
class WordpressOrderShipment(models.Model):
    order = models.ForeignKey(WordpressOrder, on_delete=models.CASCADE)
    fulfillment_channel = models.CharField(max_length=255)
    details =  models.TextField(blank=True, null=True)
    manager = WordpressOrderShipmentManager()


        
    