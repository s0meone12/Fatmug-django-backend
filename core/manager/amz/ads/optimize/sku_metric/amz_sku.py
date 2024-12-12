from core.models import AmzSku, AmzAdsSpTgtRpt, AmzAdsSbTgtRpt, AmzAdsSbStRpt, SaleOrderRpt
from .....base import CheckQSMeta
import pandas as pd
import datetime
from django.db.models import Sum
from .main import AmzSkuMetricManager


class AmzSkuSubManagerSkuMetric(metaclass=CheckQSMeta):
    def __init__(self, manager: AmzSkuMetricManager):
        self.model = AmzSku
        self.manager = manager

    def update_ads_n_total_sales(self, qs=None):
        """
        This method will update the ads to total orders for all the SKUs, over each optimization period and save them in the database.
        When adding the total sales field please ignore orders from the orders report that have more than 2 sku items in the order
        total_sales field added on the optimization models
        """
        if qs is None:
            qs = AmzSku.objects.all()
        matrix_data = []
        optimize_periods = [7, 15, 180, 99999]
        for qs_i in qs:
            for optimize_period in optimize_periods:

                from_date = datetime.datetime.now().date(
                ) - datetime.timedelta(days=optimize_period)

                total_sales = SaleOrderRpt.objects.filter(sku=qs_i, purchase_date__gte=from_date).exclude(quantity__gt=2).aggregate(
                    total_sales=Sum('item_price')
                )['total_sales'] or 0

                total_sales = float(total_sales)

                sp_ads_sales = AmzAdsSpTgtRpt.objects.filter(campaign__amz_sku=qs_i, date__gte=from_date).aggregate(
                    sales=Sum('sales_14d'))['sales'] or 0
                sb_tgt_ads_sales = AmzAdsSbTgtRpt.objects.filter(campaign__amz_sku=qs_i, date__gte=from_date).aggregate(
                    sales=Sum('attributed_sales_14d'))['sales'] or 0
                sb_st_ads_sales = AmzAdsSbStRpt.objects.filter(campaign__amz_sku=qs_i, date__gte=from_date).aggregate(
                    sales=Sum('attributed_sales_14d'))['sales'] or 0

                ads_sales = sp_ads_sales + sb_tgt_ads_sales + sb_st_ads_sales

                data = {
                    "amz_sku_name": qs_i.name,
                    "opt_duration": optimize_period,
                    "revenue": total_sales,
                    "ads_revenue": ads_sales,
                    "ratio": round(ads_sales / total_sales, 3) if total_sales else 99999,
                }
                matrix_data.append(data)

        df = pd.DataFrame(matrix_data)
        df['amz_sku'] = df['amz_sku_name'].apply(lambda x: {"name": x})
        df.drop(columns=['amz_sku_name'], inplace=True)
        df['date'] = datetime.datetime.now().date()
        return self.manager.dfdb.sync(df)
