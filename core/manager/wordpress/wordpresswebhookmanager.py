from django.db import models
from ...services.amz.sell.publisher.fulfillment_outbound import AmzSellFulfillmentPublisher
from kn_api.odoo_api.odoo_operations import OddoModelOperation
import datetime

class WordPressWebhookManager(models.Manager):
            
    def _process_hook(self, payload):  
        action = payload.get('action')
        payload = payload.get('data')
        if action == 'order.created':
            self.create(action=action, payload=payload)
        elif action == '':
            pass

class WordpressOrderManager(models.Manager):
    def _create_order(self, payload):
        try:
            order_id = payload["id"]
            self.create(order_id=order_id, order_data=payload)
            return True
        except Exception as e:
            print("Error creating order:", e)
            return False


class WordpressOrderShipmentManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mcf = AmzSellFulfillmentPublisher()
        
    def _full_fill_order(self, payload):
        from core.models.wordpress_webhook.wordpress_webhook_model import WordpressOrder 
        try:
            data = mcf_payload_generating(payload=payload)
            body = self._mcf._create_fulfillment_order(payload=data)
            order = WordpressOrder.manager.get(order_id=int(data["sellerFulfillmentOrderId"]))
            fulfillment_channel = "Amazon MCF"
            self.create(order=order, fulfillment_channel=fulfillment_channel, details=body)
            return True
        except Exception as e:
            print("Error creating order:", e)
            return False
        
def mcf_payload_generating(payload):
    sku_class = OddoModelOperation()
    fields = {"filters": [], "fields": ["sku_code"]}
    odoo_sku_response = sku_class.search_read_record(data=fields, model_name='kn.amz.sku')['data']
    
    six_digit_skus = ()
    for item in payload['line_items']:
        patterns = item.get("sku")
        six_digit_skus += (patterns,)
    
    full_sku_codes = [item['sku_code'] for item in odoo_sku_response['data'] if item['sku_code'].startswith(six_digit_skus)]
    
    items_list = []
    for item in payload["line_items"]:
        for sku in full_sku_codes:
            if sku.startswith(item["sku"]):
                item_id = item.get("id")
                quantity = item.get("quantity")
                perUnitDeclaredValue = {
                        "currencyCode": "INR",
                        "value": item.get("price")
                    }
                items_list.append({"sellerSku": sku, "sellerFulfillmentOrderItemId": item_id, "quantity": quantity, "perUnitDeclaredValue": perUnitDeclaredValue})
        
    payload_to_sent = {
            "sellerFulfillmentOrderId": payload["id"],
            "displayableOrderId": payload["id"],
            "displayableOrderDate": (datetime.datetime.now().strftime('%Y-%m-%d')),
            "displayableOrderComment": "Order",
            "shippingSpeedCategory": "Standard",
            "fulfillmentAction": "Ship",
            "destinationAddress": {
                "name": payload["shipping"]["first_name"] + " " + payload["shipping"]["last_name"],
                "addressLine1": payload["shipping"]["address_1"],
                "addressLine2": payload["shipping"]["address_2"],
                "city": payload["shipping"]["city"],
                "stateOrRegion": payload["shipping"]["state"],
                "countryCode": payload["shipping"]["country"],
                "postalCode": payload["shipping"]["postcode"],
                "phone": payload["shipping"]["phone"]
            },
            "notificationEmails": [
                payload["billing"]["email"]
            ],
            "items": items_list,
            "paymentInformation": [
                {
                "paymentTransactionId": "Paymenttransaction" + str(payload["id"]),
                "paymentMode": "Other",
                "paymentDate": datetime.datetime.now().isoformat()
                }
            ]
            }
    return payload_to_sent