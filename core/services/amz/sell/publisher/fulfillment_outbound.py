from kn_api._kn_sp_api.fulfillment_outbound import FulfillmentOutbound
from kn_api._kn_sp_api.fulfillment_outbound import FulfillmentOutbound
from sp_api.base.marketplaces import Marketplaces



class AmzSellFulfillmentPublisher:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_fullfillment = FulfillmentOutbound(Marketplaces.IN)
    
    def _get_fulfillment_preview(self, payload):
        method = 'POST'
        payload = payload
        order_preview = self._client_fullfillment.get_fulfillment_preview(method=method, data=payload)
        return order_preview
        
    def _create_fulfillment_order(self, payload):
        method = 'POST'
        payload = payload
        order_response = self._client_fullfillment.create_fulfillment_order(method=method, data=payload)
        return order_response