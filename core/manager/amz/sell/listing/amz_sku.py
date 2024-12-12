from core.apis.clients import SP_FETCHER
from core.manager.base import CheckQSMeta
from core.models.amz import AmzSku
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
import pandas as pd
from django.db import models
from django.db.models.functions import RowNumber
from .main import SkuPriceActionManager


class AmzSkuSubManagerSkuPriceAction(metaclass=CheckQSMeta):
    def __init__(self, manager: SkuPriceActionManager):
        self.manager = manager
        self.model = AmzSku
        self.__listing = SP_FETCHER.AMZ_SPAPI_IN.listing.sku

    def get_qs(self, qs=None):
        return self.manager.filter(status="draft", sku__in=qs).select_related("sku")

    def _generate_actions(self, qs=None):
        def __check_mrp():
            _df = df[df['mrp'] < df['discounted_price']]
            if not _df.empty:
                raise ValidationError(
                    "MRP is less than discounted price for %s" % _df['sku'].tolist())

        def __check_cost():
            _df = df[df['cost'] >= df['discounted_price']]
            if not _df.empty:
                raise ValidationError(
                    "Cost is greater than or equal to discounted price for %s" % _df['sku'].tolist())

        def __check_desired_profit():
            _df = df[df['desired_profit'] <= 0]
            if not _df.empty:
                raise ValidationError(
                    "Desired profit is less than or equal to 0 for %s" % _df['sku'].tolist())

        def add_our_price(row):
            our_price = row['discounted_price'] + 100
            if our_price < row['mrp']:
                return our_price
            return row['mrp']
        sale_start_at = timezone.now() - timedelta(days=2)
        sale_end_at = sale_start_at + timedelta(days=365)
        df = pd.DataFrame(qs.filter(product_type__isnull=False, to_publish_sale_price__isnull=False, to_publish_sale_price__gt=0).values('id', 'to_publish_sale_price',
                                                                                                                                         'product_type', 'mrp', 'desired_profit', 'sale_price', 'cost'))
        if df.empty:
            raise ValidationError(
                "No actions could be generated from the given queryset")
        df.rename(columns={
            'id': 'sku',
            'to_publish_sale_price': 'discounted_price',
            'sale_price': 'old_price',
        }, inplace=True)
        __check_mrp()
        __check_cost()
        __check_desired_profit()
        df['our_price'] = df.apply(add_our_price, axis=1)
        df['sale_start_at'] = sale_start_at
        df['sale_end_at'] = sale_end_at
        df['id'] = None
        df = df[['id', 'sale_start_at', 'sale_end_at', 'sku',
                 'old_price', 'our_price', 'discounted_price']]
        self.manager.exclude(status='accepted').delete()
        self.manager.dfdb.sync(df)

    def publish(self, qs):
        if not qs or not qs.exists():
            return
        self._generate_actions(qs=qs)
        qs = self.get_qs(qs=qs)
        l = []
        for i in qs:
            l.append({
                'name': i.sku.name,
                'product_type': i.sku.product_type,
                'our_price': i.our_price,
                'sale_start_at': i.sale_start_at,
                'sale_end_at': i.sale_end_at,
                'discounted_price': i.discounted_price,
            })
        df = pd.DataFrame(l)
        print('To Publish DF: ', df)
        df = self.__listing.publish_sku_price(df)
        _df = pd.DataFrame(self.manager.filter(
            sku__name__in=df['name'].tolist()).values('id', 'sku__name'))
        _df.rename(columns={'sku__name': 'name'}, inplace=True)
        df = pd.merge(df, _df, on='name', how='left')
        df = df[['id', 'status', 'submissionId', 'issues']]
        self.manager.dfdb.sync(df)

    def get_last_submission(self, qs=None):
        # Get the last submission for the given queryset of SKUs
        qs = self.manager.filter(sku__in=qs).annotate(
            row_number=models.Window(
                expression=RowNumber(), partition_by=[models.F('sku_id')], order_by=models.F('created_at').desc())
        ).filter(row_number=1)
        df = pd.DataFrame(qs.values(
            'sku__asin', 'status', 'discounted_price'))
        df.rename(columns={
            'sku__asin': 'asin',
            'discounted_price': 'sale_price',
        }, inplace=True)
        df['status'] = df['status'].apply(
            lambda x: True if x == 'accepted' else False)
        return df
