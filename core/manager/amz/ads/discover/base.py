import pandas as pd
import datetime
from decimal import Decimal


class BaseDiscoveryManager():
    """
    Discovery happens from SP-ST Report and is added to SKU. SKUTargets the target gets distributed to SP, SB, SD campaigns.
    """

    def _update_spend_matrix(self, disc_tgt_model, related_tgt_field_name, tgt_rpt_model):
        # Fetch all targets at once
        targets_df = pd.DataFrame(list(disc_tgt_model.objects.filter(
            **{f'{related_tgt_field_name}__isnull': False}).values()))
        # Fetch all spend data at once
        spend_data_df = pd.DataFrame(list(tgt_rpt_model.objects.filter(
            **{f'{related_tgt_field_name}__isnull': False}).values()))

        # Initialize an empty list to store the results
        results = []
        # Iterate over the targets
        for _, target in targets_df.iterrows():
            # Filter the spend data for the current target
            target_spend_data = spend_data_df[spend_data_df[f'{related_tgt_field_name}_id'] == target[f'{related_tgt_field_name}_id']]

            # Calculate lifetime_spend and spend_since_mute
            lifetime_spend = target_spend_data['cost'].sum()
            spend_since_mute = target_spend_data[target_spend_data['date'] >=
                                                 target['muted_on']]['cost'].sum() if target['muted_on'] else 0

            results.append({
                'id': target['id'],
                'lifetime_spend': lifetime_spend,
                'spend_since_mute': spend_since_mute
            })
        df = pd.DataFrame(results)
        return df

    def _optimize_bid_with_no_spend(self, disc_model, tgt_opt_model, key_or_tar):
        """
        Filter -- No Spend, duration -- lifetime
        If the target has no impressions in the shortest opt duration, then increase the bid by the default bid increment (2%).
        Else, decrease the bid by 20%.
        """
        data_list = []
        # Generate the queryset based on the model
        all_live_targets = disc_model.objects.filter(
            **{f'{key_or_tar}__isnull': False})
        # Iterate over each live target
        for target in all_live_targets:
            live_bid = float(getattr(target, key_or_tar).bid)
            print(f"{target.keyword.keyword_text if key_or_tar == 'Keyword' else target.target.expression}, was bid={target.keyword.bid if key_or_tar == 'Keyword' else target.target.bid}")

            # category divided target occur in target-report or not
            # search that target in SpKeyTgtOpt for opt_duration = lifetime and spend = 0

            target_lifetime = tgt_opt_model.objects.filter(
                **{f"{key_or_tar.lower()}__id": getattr(target, f'{key_or_tar}.id')},
                opt_duration=99999, spend=0, date=datetime.datetime.now().date())

            # if occur
            if target_lifetime:
                # category divided impressions occur and impressions not occur

                # if impressions occur in the shortest opt duration, (and target was present in target report), update the bid
                tar_exst_in_rprt = tgt_opt_model.objects.filter(**{f"{key_or_tar.lower()}__id": target_lifetime.keyword_id if key_or_tar == 'Keyword' else target_lifetime.target_id},
                                                                opt_duration=7, spend=0, impressions__gt=0,
                                                                date=datetime.datetime.now().date())
                # As, there are impressions are greater than 0, so Decrease bid by 20%
                if tar_exst_in_rprt.exists():
                    # minimum bid for SB, can not be less than 1.5
                    _bid = max(1.5, live_bid * 0.8)
                    data_list.append({
                        "id": target.id,
                        "bid": _bid
                    })
                    print(
                        "As, there are impressions is greater than 0, so Decrease bid by 20%")
                    print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

                # this will handle the case if impressions do not occur, (but target was present in the target report), update the bid
                # As, there are impressions= 0, so Increase bid by 2%
                else:
                    _bid = live_bid * 1.02
                    data_list.append({
                        "id": target.id,
                        "bid": _bid
                    })
                    print(
                        "PRESENT IN REPORT As, there are impressions= 0, so Increase bid by 2%")
                    print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

            # if the target did not occur in the report
            # it didn't occur in the report because there are no impressions, means impressions = 0, so Increase bid by 2%
            else:
                _bid = live_bid * 1.02
                data_list.append({
                    "id": target.id,
                    "bid": _bid
                })
                print(
                    "NOT PRESENT IN REPORT As, there are impressions= 0, so Increase bid by 2%")
                print(f"{target.keyword.keyword_text if key_or_tar =='Keyword' else target.target.expression}, new bid={_bid}")

        df = pd.DataFrame(data_list)
        return df

    def _set_muted_on_unviable_and_optimize_bid(self, disc_model, trgt_rep_model, key_or_tar):
        data_list = []
        related_disc_tgt_type = "sku_disc_key" if key_or_tar == 'Keyword' else "sku_disc_pro"
        all_live_targets = disc_model.objects.filter(
            **{f"{key_or_tar.lower()}__isnull": False})

        for target in all_live_targets:
            l = {}
            l["id"] = target.id
            related_disc_tgt_type_field = getattr(
                target, related_disc_tgt_type)
            sku_price = related_disc_tgt_type_field.sku.sale_price
            live_bid = float(getattr(target, key_or_tar).bid)

            # category divided target occur in target-report or not

            # search that target in SpKeyTgtOpt for opt_duration = lifetime and spend > 0 , sales = 0,  date = today
            target_lifetime = trgt_rep_model.objects.filter(
                **{f"{key_or_tar.lower()}__id": getattr(target, key_or_tar.lower()).id},
                opt_duration=99999, spend__gt=0, sales=0, date=datetime.datetime.now().date())

            # this include targets which r in the tgt rpt check the shortest duration for bid updation or set muted_on or unviable_on
            if target_lifetime:
                tar_exst_in_rprt_for_short_period = trgt_rep_model.objects.filter(**{f"{key_or_tar.lower()}__id": getattr(target_lifetime, key_or_tar.lower()).id},
                                                                                  opt_duration=7, spend__gt=0, sales=0,
                                                                                  date=datetime.datetime.now().date())
                twenty_percentage_sku = sku_price * 0.20

                if tar_exst_in_rprt_for_short_period.impressions > 0:
                    _bid = min(1.5, live_bid * 0.8)
                    l["bid"] = _bid

                elif tar_exst_in_rprt_for_short_period.impressions == 0:

                    if (not target.muted_on) and (not target.unviable_on) and (target.lifetime_spend > twenty_percentage_sku):
                        l["bid"] = 1.5  # minimum for SB
                        l["muted_on"] = datetime.datetime.now().date()
                    elif target.muted_on and (not target.unviable_on) and (target.spend_since_mute > twenty_percentage_sku):
                        l["unviable_on"] = datetime.datetime.now().date()
                    else:
                        _bid = live_bid * 1.02
                        l["bid"] = _bid

                else:
                    raise ValueError("Small check fails, Something went wrong")

            # this include targets which r not in the tgt rpt but present in our ecosystem
            else:
                if (not target.muted_on) and (not target.unviable_on) and (target.lifetime_spend > twenty_percentage_sku):
                    l["muted_on"] = datetime.datetime.now().date()
                    l["bid"] = 1.5  # minimum for SB
                elif target.muted_on and (not target.unviable_on) and (target.spend_since_mute > twenty_percentage_sku):
                    l["unviable_on"] = datetime.datetime.now().date()
                else:
                    _bid = live_bid * 1.02
                    l["bid"] = _bid

            print(l)
            data_list.append(l)
        df = pd.DataFrame(data_list)
        return df

    def _set_max_bid(self, disc_tgt_model, tgt_optimize_model, tgt_type_field_name):
        from core.models.amz.ads.optimize.sku.metrics import AmzSkuAdsMetric
        data_list = []
        optimize_periods = [7, 15, 180, 99999]
        current_date = datetime.datetime.now().date()
        filter_tgt_field = getattr(disc_tgt_model, tgt_type_field_name)
        disc_targets = disc_tgt_model.objects.filter(
            **{f'{filter_tgt_field}__isnull': False})

        for disc_tgt in disc_targets:

            bid_values = []
            for optimize_period in optimize_periods:

                tgt_optimize_model_obj = tgt_optimize_model.objects.filter(
                    date=current_date,
                    opt_duration=optimize_period, acos__gt=0)

                if tgt_optimize_model_obj:

                    tgt_optimize_model_obj = tgt_optimize_model_obj.first()

                    tgt_type_field = getattr(disc_tgt, tgt_type_field_name)
                    amz_sku_obj = tgt_type_field.campaign.amz_sku

                    matrix_object = AmzSkuAdsMetric.objects.filter(
                        amz_sku=amz_sku_obj,
                        opt_duration=optimize_period,
                        date=current_date, ratio__gt=0)

                    if matrix_object:
                        matrix_obj = matrix_object.first()

                        ads_to_total_revenue_ratio = matrix_obj.ratio
                        desired_ads_percentage = matrix_obj.amz_sku.desired_ads_percentage
                        bid_multiplier = (
                            desired_ads_percentage / ads_to_total_revenue_ratio) / tgt_optimize_model_obj.acos
                        auto_max_bid = (
                            bid_multiplier * (tgt_optimize_model_obj.spend / tgt_optimize_model_obj.clicks))

                        bid_values.append(auto_max_bid)

            if bid_values:
                min_bid_value = min(bid_values)
                data_list.append({
                    "id": disc_tgt.id,
                    "bid": min([min_bid_value, 20])
                })
                # disc_tgt.bid = min([min_bid_value, 20])
                # disc_tgt.save()
            else:
                data_list.append({
                    "id": disc_tgt.id,
                    "bid": 2.0
                })

        df = pd.DataFrame(data_list)
        return df

    def bid_calculation(self, disc_model, key_or_tar):
        from core.models.amz.ads.optimize.sku.metrics import AmzSkuAdsMetric
        data_list = []
        all_new_targets = disc_model.objects.filter(
            **{f'{key_or_tar}__isnull': True})
        print(all_new_targets.count())
        sku_disc_key_or_pro = "sku_disc_key" if key_or_tar == 'keyword' else "sku_disc_pro"
        for tar in all_new_targets:
            if getattr(tar, f'{sku_disc_key_or_pro}').sales > 0:
                current_date = datetime.datetime.now().date()
                _sku = getattr(tar, f'{sku_disc_key_or_pro}').sku
                matrix_object = AmzSkuAdsMetric.objects.filter(amz_sku=_sku, opt_duration=99999,
                                                               date=current_date, ratio__gt=0)
                if matrix_object:
                    matrix_obj = matrix_object.first()
                    ratio = matrix_obj.ratio
                    acos = getattr(tar, f'{sku_disc_key_or_pro}').cost / getattr(
                        tar, f'{sku_disc_key_or_pro}').sales  # spend by sale
                    print(f"{getattr(tar, f'{sku_disc_key_or_pro}').cost} / {getattr(tar, f'{sku_disc_key_or_pro}').sales}")  # spend by sale
                    print(acos, ratio)
                    if acos == 0:
                        data_list.append({
                            'id': tar.id,
                            'bid': 2.0
                        })
                        continue
                    bid_multiplier = (
                        matrix_obj.amz_sku.desired_ads_percentage / ratio) / acos
                    auto_bid = bid_multiplier * \
                        (getattr(tar, f'{sku_disc_key_or_pro}').cost /
                         getattr(tar, f'{sku_disc_key_or_pro}').clicks)
                    tar.bid = Decimal(min(auto_bid, 5))
                    data_list.append({
                        'id': tar.id,
                        'bid': min(auto_bid, 5)
                    })
                else:
                    print(f"No AmzSkuAdsMetric found for the sku {_sku}.")
                    # raise ValueError(f"No AmzSkuAdsMetric found for the sku {_sku}.")
            else:
                data_list.append({
                    'id': tar.id,
                    'bid': 2.0
                })
        df = pd.DataFrame(data_list)
        return df
        disc_model.dfdb.sync(df)

        # optimized method
        # current_date = datetime.datetime.now().date()
        # current_date = current_date - datetime.timedelta(days=1)
        # all_new_targets = pd.DataFrame(list(disc_model.objects.filter(**{f'{key_or_tar}__isnull': True}).values('id', f'{sku_disc_key_or_pro}__sku_id',f'{sku_disc_key_or_pro}__cost', f'{sku_disc_key_or_pro}__sales', f'{sku_disc_key_or_pro}__clicks', 'bid', 'target_name')))
        # print(all_new_targets.shape[0])
        # sku_metrics = pd.DataFrame(list(AmzSkuAdsMetric.objects.filter(date=current_date, ratio__gt=0).values('amz_sku_id', 'ratio', 'amz_sku__desired_ads_percentage', 'date', 'opt_duration', 'revenue', 'ads_revenue')))
        # print(sku_metrics.shape[0])
        # merged_df = pd.merge(all_new_targets, sku_metrics, left_on=f'{sku_disc_key_or_pro}__sku_id', right_on='amz_sku_id', how='left')
        # print(merged_df.shape[0])
        # column_rename = {
        #     f'{sku_disc_key_or_pro}__sku_id': 'sku_id',
        #     f'{sku_disc_key_or_pro}__clicks': 'clicks',
        #     f'{sku_disc_key_or_pro}__cost': 'cost',
        #     f'{sku_disc_key_or_pro}__sales': 'sales',
        #     'amz_sku__desired_ads_percentage': 'desired_ads_percentage'
        #     }
        # merged_df = merged_df.rename(columns=column_rename)
        # # Check for NaN values in 'ratio' column
        # if merged_df['ratio'].isnull().any():
        #     raise Exception("There's a row in all_new_targets that doesn't have a matching row in sku_metrics")

        # def calculate_bid(row):
        #     if row['sales'] > 0 and pd.notnull(row['ratio']):
        #         acos = row['cost'] / row['sales']
        #         if acos == 0:
        #             return 2.0
        #         print(f"{row['desired_ads_percentage']} / {row['ratio']}) / {acos}")
        #         bid_multiplier = (row['desired_ads_percentage'] / row['ratio']) / acos
        #         auto_bid = bid_multiplier * (row['cost'] / row['clicks'])
        #         return min(auto_bid, 5)
        #     else:
        #         return 2.0
        # merged_df['bid'] = merged_df.apply(calculate_bid, axis=1)
        # df = merged_df[['id', 'bid']]
        # print(df)
        # df.to_csv('using_new_method.csv')
        # disc_model.dfdb.sync(df)
