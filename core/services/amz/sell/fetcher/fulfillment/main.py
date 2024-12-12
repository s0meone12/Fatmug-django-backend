from ..base import AmzSellBaseFetcher
from datetime import datetime
from kn_api._kn_sp_api.fulfillment_inbound import FulfillmentInbound
from sp_api.base import Marketplaces


class AmzSellFulfillmentFetcher(AmzSellBaseFetcher):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_fullfillment = FulfillmentInbound(Marketplaces.IN)

    def _create_shipment_plan(self, df_of_inbound_items=None, dict_of_facility_address=None):
        if dict_of_facility_address is None:
            dict_of_facility_address = {
                "Name": "Fatmug Designs",
                "AddressLine1": "H 61, SECTOR 4",
                "AddressLine2": "Bawana Industrial Area",
                "City": "New Delhi",
                "StateOrProvinceCode": "Delhi",
                "CountryCode": "IN",
                "PostalCode": "110039",
            }
        if df_of_inbound_items is None:
            list_of_inbound_items = [
                {
                    "SellerSKU": "700013SWHQ28A1",
                    "ASIN": "B07MF82BG4",
                    "Condition": "NewItem",
                    "Quantity": 1,
                }
            ]
        else:
            list_of_inbound_items = []
            for _, row in df_of_inbound_items.iterrows():
                sku = row['amz_sku']
                asin = row['asin']
                units = row['units']
                list_of_inbound_items.append(
                    {
                        "SellerSKU": sku,
                        "ASIN": asin,
                        "Condition": "NewItem",
                        "Quantity": units,
                    }
                )
        arg_data = {
            "ShipFromAddress": dict_of_facility_address,
            "LabelPrepPreference": "SELLER_LABEL",
            "InboundShipmentPlanRequestItems": list_of_inbound_items,
        }
        # payload = getattr(
        #     self._client_fullfillment.plans(data=arg_data), "payload"
        # )
        # shipment_id = payload["InboundShipmentPlans"][0]["ShipmentId"]
        data = self._client_fullfillment.plans(data=arg_data).json()
        inbound_shipment_plans = data.get("InboundShipmentPlans", [])
        shipment_id = inbound_shipment_plans[0].get("ShipmentId", None)
        return shipment_id

    def _create_shipment(self, df_of_inbound_items=None, fc=None, dict_of_facility_address=None):
        if dict_of_facility_address is None:
            dict_of_facility_address = {
                "Name": "Fatmug Designs",
                "AddressLine1": "H 61, SECTOR 4",
                "AddressLine2": "Bawana Industrial Area",
                "City": "New Delhi",
                "StateOrProvinceCode": "Delhi",
                "CountryCode": "IN",
                "PostalCode": "110039",
            }
        if fc is None:
            fc = 'DEL5'
        if df_of_inbound_items is None:
            list_of_inbound_items = [
                {
                    "SellerSKU": "700013SWHQ28A1",
                    "QuantityShipped": 1,
                }
            ]
        else:
            list_of_inbound_items = []
            for _, row in df_of_inbound_items.iterrows():
                sku = row['amz_sku']
                units = row['units']
                list_of_inbound_items.append(
                    {
                        "SellerSKU": sku,
                        "QuantityShipped": units,
                    }
                )
        shipment_id = self._create_shipment_plan(
            df_of_inbound_items, dict_of_facility_address)
        arg_data = {
            "InboundShipmentHeader": {
                "ShipmentName": fc + datetime.now().strftime('%d-%m-%Y-%H-%M-%S'),
                "ShipFromAddress": dict_of_facility_address,
                "DestinationFulfillmentCenterId": fc,
                "ShipmentStatus": "WORKING",
                "LabelPrepPreference": "SELLER_LABEL",
            },
            "InboundShipmentItems": list_of_inbound_items,
            "MarketplaceId": "A21TJRUUN4KGV",
        }
        res = (
            self._client_fullfillment
            .create_shipment(shipment_id, data=arg_data)
            .__dict__
        )
        errors = res.get('errors')
        if not(errors is None):
            raise Exception(errors)
        return res.get('payload')

    def _get_shipment_items(self, shipment_id):
        return self._client_fullfillment.shipment_items_by_shipment(shipment_id).json().get('ItemData')

    def _get_shipments_by_id(self, list_of_shipment_ids):
        return self._client_fullfillment.get_shipments(QueryType="SHIPMENT",ShipmentIdList=list_of_shipment_ids).json().get('ShipmentData')

    def _update_shipment(self, shipment_id, arg_data):
        self._client_fullfillment.update_shipment(shipment_id, data=arg_data)

    def get_shipment_info(self, list_of_shipment_ids):
        dict_of_ship_info = {}
        list_of_shipment_info = []
        for shipment_id in list_of_shipment_ids:
            list_of_shipment_info.extend(
                self._get_shipments_by_id(shipment_id))
        for shipment_info in list_of_shipment_info:
            shipment_id = shipment_info['ShipmentId']
            item_data = self._get_shipment_items(shipment_id)
            dict_of_ship_info[shipment_id] = {
                'shipment_info': shipment_info,
                'item_data': item_data,
            }
        return dict_of_ship_info

    def delete_shipments(self, list_of_shipment_ids):
        list_of_shipment_info = []
        for shipment_id in list_of_shipment_ids:
            list_of_shipment_info.extend(
                self._get_shipments_by_id(shipment_id))
        for shipment_info in list_of_shipment_info:
            list_of_item_dict = self._get_shipment_items(
                shipment_id)
            list_of_item_args = []
            for dict_of_item in list_of_item_dict:
                list_of_item_args.append(
                    {
                        'ShipmentId': dict_of_item['ShipmentId'],
                        'SellerSKU': dict_of_item['SellerSKU'],
                        'QuantityShipped': dict_of_item['QuantityShipped'],
                    }
                )
            arg_data = {
                'InboundShipmentHeader': {
                    'ShipmentName': shipment_info['ShipmentName'],
                    'ShipFromAddress': shipment_info['ShipFromAddress'],
                    'DestinationFulfillmentCenterId': shipment_info['DestinationFulfillmentCenterId'],
                    'ShipmentStatus': 'DELETED',
                    'LabelPrepPreference': 'SELLER_LABEL',
                },
                'InboundShipmentItems': list_of_item_args,
                'MarketplaceId': 'A21TJRUUN4KGV',
            }
            self._update_shipment(shipment_id, arg_data)
