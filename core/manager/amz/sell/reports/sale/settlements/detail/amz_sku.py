from core.manager.base import CheckQSMeta
from core.models.amz.sku import AmzSku
import pandas as pd
from django.db.models import Q, F, Avg, Sum, Min
from django.utils import timezone
from datetime import timedelta
from django.db.models import Window
from django.db.models.functions import RowNumber


class AmzSkuSubManagerAmzSettlementDetail(metaclass=CheckQSMeta):

    def __init__(self, manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.model = AmzSku
        # Default days to consider for the averaging the amount values in the settlement report
        self.days = 0
        # In case order not found in the default days then we will consider the last 100 orders
        self.order_count = 100

    def get_qs(self, qs=None):
        days = self.days
        order_count = self.order_count
        cutoff_date = timezone.now() - timedelta(days=days)
        base_query = self.manager.filter(
            sku__in=qs
        )
        # Create a base queryset that filters by the cutoff date
        within_days = Q(posted_datetime__gte=cutoff_date)
        order_codes = base_query.filter(transaction_type__name='Order', amount_description__name='Principal', amount_type__name='ItemPrice').annotate(
            rank=Window(
                expression=RowNumber(),
                partition_by=[F('sku')],
                order_by=F('posted_datetime').desc(),
            )
        ).filter(rank__lte=order_count).values_list('order_id', flat=True)
        within_count = Q(order_id__in=order_codes)
        qs = base_query.filter(within_days | within_count)
        return qs

    def principal_amount(self, qs=None):
        qs = self.get_qs(qs=qs)
        # Get the average principal amount for each SKU, when the transaction type is 'Order'
        df_order = pd.DataFrame(qs.filter(transaction_type__name='Order', amount_description__name='Principal', amount_type__name='ItemPrice').annotate(
            unit_amount=F('amount')/F('quantity_purchased')
        ).annotate(
            principal_amount=Window(
                expression=Avg('unit_amount'),
                partition_by=[F('sku')],
            )
        ).distinct('sku').values('sku', 'principal_amount'))
        # Get minimum principal amount for each SKU, when the transaction type is 'Refund'
        df_refund = pd.DataFrame(qs.filter(transaction_type__name='Refund', amount_description__name='Principal', amount_type__name='ItemPrice').annotate(
            principal_amount=Window(
                expression=Min('amount'),
                partition_by=[F('sku')],
            )
        ).distinct('sku').values('sku', 'principal_amount'))
        df_refund['principal_amount'] = -1 * df_refund['principal_amount']
        # Add value from refund to the order in case sku not present in order
        df = pd.concat([df_order, df_refund[~df_refund['sku'].isin(
            df_order['sku'])]], ignore_index=True)
        return df

    def qty_purchased(self, qs=None):
        qs = self.get_qs(qs=qs)
        return pd.DataFrame(qs.filter(transaction_type__name='Order', amount_description__name='Principal', amount_type__name='ItemPrice').values('sku').annotate(
            quantity=Window(
                expression=Sum('quantity_purchased'),
                partition_by=[F('sku')],
            )
        ).distinct('sku').values('sku', 'quantity')).sort_values('quantity', ascending=False)

    def qty_returned(self, qs=None):
        df_principal_amount = self.principal_amount(qs=qs)
        qs = self.get_qs(qs=qs)
        df_refund = pd.DataFrame(qs.filter(transaction_type__name='Refund', amount_description__name='Principal',
                                           amount_type__name='ItemPrice').values('sku', 'order_id', 'amount', 'quantity_purchased'))
        df_refund_qty = pd.merge(
            df_refund, df_principal_amount, on='sku', how='left')
        df_refund_qty['quantity_purchased'] = df_refund_qty['amount'] / \
            df_refund_qty['principal_amount']
        df_refund_qty.drop(
            columns=['amount', 'principal_amount', 'order_id'], inplace=True)
        df_refund_qty = df_refund_qty.groupby('sku').agg(
            quantity=('quantity_purchased', 'sum'))
        return df_refund_qty.sort_values('quantity', ascending=True)

    def net_qty_purchased(self, qs=None):
        df_qty_purchased = self.qty_purchased(qs=qs)
        df_qty_purchased.rename(
            columns={'quantity': 'quantity_purchased'}, inplace=True)
        df_qty_returned = self.qty_returned(qs=qs)
        df_qty_returned.rename(
            columns={'quantity': 'quantity_returned'}, inplace=True)
        df_merged = pd.merge(
            df_qty_purchased, df_qty_returned, on='sku', how='outer')
        df_merged.fillna(0, inplace=True)
        df_merged['quantity'] = df_merged['quantity_purchased'].astype(
            float) + df_merged['quantity_returned'].astype(float)
        df_merged.drop(
            columns=['quantity_purchased', 'quantity_returned'], inplace=True)
        return df_merged.sort_values('quantity', ascending=False)

    def avg_amounts(self, qs=None):
        df_net = self.net_qty_purchased(qs=qs)
        df_net = df_net[df_net['quantity'] > 0]
        skus = df_net['sku'].tolist()
        qs = self.get_qs(qs=qs)
        df = pd.DataFrame(qs.filter(sku__in=skus).annotate(
            avg_amount=Window(
                expression=Sum('amount'),
                partition_by=[F('sku'), F('amount_type'),
                              F('amount_description')],
            )
        ).distinct('sku', 'amount_type', 'amount_description').values('sku', 'amount_type', 'amount_description', 'avg_amount'))
        df_merged = pd.merge(df, df_net, on='sku', how='left')
        df_merged['avg_amount'] = df_merged['avg_amount'].astype(float) / \
            df_merged['quantity'].astype(float)
        df_merged.drop(columns=['quantity'], inplace=True)
        return df_merged.rename(columns={'avg_amount': 'amount'})

    def print_csv(self, qs=None):
        qs = self.get_qs(qs=qs)
        return pd.DataFrame(qs.values(
            'transaction_type__name',
            'order_id',
            'merchant_order_id',
            'adjustment_id',
            'shipment_id',
            'marketplace_name',
            'amount_type__name',
            'amount_description__name',
            'amount',
            'fulfillment_id',
            'fulfillment_id',
            'posted_datetime',
            'order_item_code',
            'merchant_order_item_id',
            'merchant_adjustment_item_id',
            'sku__name',
            'quantity_purchased',
            'promotion_id',
            'promotion_id',
        )).to_csv('test.csv', index=False)
