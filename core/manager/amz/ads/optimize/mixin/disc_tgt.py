import datetime
import pandas as pd
from decimal import Decimal
from core.models import AmzSkuAdsMetric


class DiscTgtSubManagerMixinTgtOpt:
    """
    Base class for bid optimization services.
    """

    def _bid_calcu_for_new_targ(self, key_or_tar):
        data_list = []
        all_new_targets = self.model.manager.filter(**{f'{key_or_tar}__isnull': True}).values('id','sku_disc_tgt__cost','sku_disc_tgt__sales','sku_disc_tgt__clicks','sku_disc_tgt__sku')
        df = pd.DataFrame(all_new_targets)
        df.rename(columns={'sku_disc_tgt__cost': 'cost', 'sku_disc_tgt__sales': 'sales', 'sku_disc_tgt__clicks': 'clicks', 'sku_disc_tgt__sku': 'sku'}, inplace=True)
        print(df)
        for _, row in df.iterrows():
            if row['sales'] > 0:
                current_date = datetime.datetime.now().date()
                _sku = row['sku']
                matrix_object = AmzSkuAdsMetric.objects.filter(amz_sku=_sku, opt_duration=99999,
                                                               date=current_date, ratio__gt=0)
                if matrix_object:
                    matrix_obj = matrix_object.first()
                    ratio = matrix_obj.ratio
                    acos = row['cost'] / row['sales']  # spend by sale
                    print(f"{row['cost']} / {row['sales']} = {acos}")  # spend by sale
                    print(ratio)
                    if acos == 0:
                        data_list.append({
                            'id': row['id'],
                            'bid': 2.0
                        })
                        continue
                    desired_ads = matrix_obj.amz_sku.desired_ads_percentage / 100
                    bid_multiplier = (desired_ads / ratio) / acos
                    auto_bid = bid_multiplier * (row['cost'] / row['clicks'])
                    data_list.append({
                        'id': row['id'],
                        'bid': min(auto_bid, 5)
                    })
                else:
                    print(f"No AmzSkuAdsMetric found for the sku {_sku}.")
                    # raise ValueError(f"No AmzSkuAdsMetric found for the sku {_sku}.")
            else:
                data_list.append({
                    'id': row['id'],
                    'bid': 2.0
                })
        df = pd.DataFrame(data_list)
        return df

    def _set_max_bid(self, tgt_type_field_name):

        current_date = datetime.datetime.now().date()
        optimize_periods = [7, 15, 180, 99999]
        data_list = []

        # Prefetch related SKU data
        live_targets = self.model.manager.filter(**{f'{tgt_type_field_name}__isnull': False}).select_related('amz_sku')

        # Bulk fetch optimization model objects and metrics
        optimize_model_objs = self.manager.filter(
            date=current_date, acos__gt=0, opt_duration__in=optimize_periods
        )
        metrics = AmzSkuAdsMetric.objects.filter(
            date=current_date, ratio__gt=0, opt_duration__in=optimize_periods
        ).values('amz_sku_id', 'opt_duration', 'ratio')

        # Convert queryset to list for in-memory operations
        optimize_model_list = list(optimize_model_objs)
        metrics_list = list(metrics)

        for tgt in live_targets:
            bid_values = []
            desired_ads = tgt.amz_sku.desired_ads_percentage/100

            for opt_period in optimize_periods:
                # Filter in-memory
                tgt_optimize_model_obj = next((obj for obj in optimize_model_list if obj.opt_duration == opt_period), None)
                matrix_obj = next((m for m in metrics_list if m['amz_sku_id'] == tgt.amz_sku_id and m['opt_duration'] == opt_period), None)

                if tgt_optimize_model_obj and matrix_obj:
                    ads_to_total_revenue_ratio = matrix_obj['ratio']
                    bid_multiplier = (desired_ads / ads_to_total_revenue_ratio) / tgt_optimize_model_obj.acos
                    auto_max_bid = bid_multiplier * (tgt_optimize_model_obj.spend / tgt_optimize_model_obj.clicks)
                    bid_values.append(min(auto_max_bid, 20))

            if bid_values:
                min_bid_value = min(bid_values)
                data_list.append({
                    "id": tgt.id,
                    "bid": max(min_bid_value,1.5)
                })

        df = pd.DataFrame(data_list)
        return df
    
    def _set_muted_on_unviable_and_optimize_bid(self, key_or_tar):
        data_list = []
        all_live_targets = self.model.manager.filter(
            **{f"{key_or_tar}__isnull": False}).values('id', 'amz_sku__sale_price',f'{key_or_tar}__id' , 'bid', 'muted_on', 'unviable_on', 'lifetime_spend', 'spend_since_mute')
        print(all_live_targets.count())

        for target in all_live_targets:
            l = {}
            current_date = datetime.datetime.now().date()
            sku_price = target['amz_sku__sale_price']
            live_bid = target['bid']

            # category divided target occur in target-report or not

            # search that target in SpKeyTgtOpt for opt_duration = lifetime and spend > 0 , sales = 0,  date = today
            target_lifetime = self.manager.filter(disc_tgt_id= target[f'{key_or_tar}__id'],
                opt_duration=99999, spend__gt=0, sales=0, date=current_date)
            twenty_percentage_sku = sku_price * Decimal('0.20')

            # this include targets which r in the tgt rpt check the shortest duration for bid updation or set muted_on or unviable_on
            if target_lifetime:
                tar_exst_in_rprt_for_short_period = self.manager.filter(disc_tgt_id= target['id'],
                                                                                  opt_duration=7, spend__gt=0, sales=0,
                                                                                  date=current_date).values('impressions').first()
                
                if tar_exst_in_rprt_for_short_period:
                    if tar_exst_in_rprt_for_short_period['impressions'] > 0:
                        _bid = min(Decimal('1.5'), live_bid * Decimal('0.8'))
                        l["id"] = target['id']
                        l["bid"] = _bid

                    elif tar_exst_in_rprt_for_short_period['impressions']== 0:

                        if (not target['muted_on']) and (not target['unviable_on']) and (target['lifetime_spend'] > twenty_percentage_sku):
                            l["id"] = target['id']
                            l["bid"] = 1.5  # minimum for SB
                            l["muted_on"] = current_date
                        elif target['muted_on'] and (not target['unviable_on']) and (target['spend_since_mute'] > twenty_percentage_sku):
                            l["unviable_on"] = current_date
                        else:
                            _bid = live_bid * Decimal('1.02')
                            l["id"] = target['id']
                            l["bid"] = _bid

                    else:
                        raise ValueError("Small check fails, Something went wrong")

            # this include targets which r not in the tgt rpt but present in our ecosystem
            # else:
            #     if (not target['muted_on']) and (not target['unviable_on']) and (target['lifetime_spend'] > twenty_percentage_sku):
            #         l["muted_on"] = current_date
            #         l["bid"] = 1.5  # minimum for SB
            #     elif target['muted_on'] and (not target['unviable_on']) and (target['spend_since_mute'] > twenty_percentage_sku):
            #         l["unviable_on"] = current_date
            #     else:
            #         _bid = live_bid * Decimal('1.02')
            #         l["bid"] = _bid
            #     l["id"] = target['id']
            # print(l)
            if l:
                data_list.append(l)
        df = pd.DataFrame(data_list)
        return df
    
    def _optimize_bid_with_no_spend(self, key_or_tar):
        """
        Filter -- No Spend, duration -- lifetime
        If the target has no impressions in the shortest opt duration, then increase the bid by the default bid increment (2%).
        Else, decrease the bid by 20%.
        """
        data_list = []
        # Generate the queryset based on the model
        current_date = datetime.datetime.now().date()
        all_live_targets = self.model.manager.filter(
            **{f'{key_or_tar}__isnull': False}).values('id', 'bid', f'{key_or_tar}__id')
        # Iterate over each live target
        for target in all_live_targets:
            live_bid = float(target['bid'])
            # print(f"{target.keyword.keyword_text if key_or_tar == 'keyword' else target.target.expression}, was bid={target.keyword.bid if key_or_tar == 'keyword' else target.target.bid}")

            # category divided target occur in target-report or not
            # search that target in SpKeyTgtOpt for opt_duration = lifetime and spend = 0

            target_lifetime = self.manager.filter(disc_tgt_id= target[f'{key_or_tar}__id'],
                opt_duration=99999, spend=0, date=current_date).values('disc_tgt_id').first()

            # if occur
            if target_lifetime:
                # category divided impressions occur and impressions not occur

                # if impressions occur in the shortest opt duration, (and target was present in target report), update the bid
                tar_exst_in_rprt = self.manager.filter(disc_tgt_id= target_lifetime['disc_tgt_id'],
                                                                opt_duration=7, spend=0, impressions__gt=0,
                                                                date=current_date)
                # As, there are impressions are greater than 0, so Decrease bid by 20%
                if tar_exst_in_rprt.exists():
                    # minimum bid for SB, can not be less than 1.5
                    _bid = max(1.5, live_bid * 0.8)
                    data_list.append({
                        "id": target['id'],
                        "bid": _bid
                    })
                    # print(
                    #     "As, there are impressions is greater than 0, so Decrease bid by 20%")
                    # print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

                # this will handle the case if impressions do not occur, (but target was present in the target report), update the bid
                # As, there are impressions= 0, so Increase bid by 2%
                else:
                    _bid = live_bid * 1.02
                    data_list.append({
                        "id": target['id'],
                        "bid": _bid
                    })
                    # print(
                    #     "PRESENT IN REPORT As, there are impressions= 0, so Increase bid by 2%")
                    # print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

            # if the target did not occur in the report
            # it didn't occur in the report because there are no impressions, means impressions = 0, so Increase bid by 2%
            # else:
            #     _bid = live_bid * 1.02
            #     data_list.append({
            #         "id": target['id'],
            #         "bid": _bid
            #     })
            #     print(
            #         "NOT PRESENT IN REPORT As, there are impressions= 0, so Increase bid by 2%")
            #     print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

        df = pd.DataFrame(data_list)
        return df
