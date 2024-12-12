"""
We will need to define optimization periods, and then run the optimization for each period. This configuration will be \
stored in the database.
Period : 7, 15, 180, lifetime

There are going to be 4 kinds of targets
1. Targets that are present in the Target Reports (Optimization Metrics available) --- aggregation
2. Targets that are not present in the Target Reports but have a live Target associated with them (+default bid increment)
3. Targets that are not present in the Target Reports and do not have a live Target associated with them, (suggested_bid)
4. Targets that have been declared unviable
"""
from django.db import transaction
from core.models import SpKeyTgtOpt,SpProTgtOpt,SbKeyTgtOpt,SbProTgtOpt,AmzSkuAdsMetric,SBDiscKeyTgt,SBDiscProTgt,SPDiscKeyTgt,SPDiscProTgt


class AmzAdsIndOptimize:

    def __init__(self):
        self.q1_sb_disc_key_tgt = 0
        self.q2_sb_disc_key_tgt = 0
        self.q3_sb_disc_key_tgt = 0
        self.q1_sb_disc_pro_tgt = 0
        self.q2_sb_disc_pro_tgt = 0
        self.q3_sb_disc_pro_tgt = 0
        self.q1_sp_disc_key_tgt = 0
        self.q2_sp_disc_key_tgt = 0
        self.q3_sp_disc_key_tgt = 0
        self.q1_sp_disc_pro_tgt = 0
        self.q2_sp_disc_pro_tgt = 0
        self.q3_sp_disc_pro_tgt = 0
    


    def __calculate_bid_for_targets_with_no_spend(self):
        """
        Filter -- No Spend, duration -- lifetime
        If the target has no impressions in the shortest opt duration, then increase the bid by the default bid increment (2%).
        Else, decrease the bid by 20%.
        """

        with transaction.atomic():
            self.q3_sb_disc_key_tgt = SbKeyTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()
            self.q3_sb_disc_pro_tgt = SbProTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()
            self.q3_sp_disc_key_tgt = SpKeyTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()
            self.q3_sp_disc_pro_tgt = SpProTgtOpt.manager.disc_tgt.optimize_bid_with_no_spend()

    def __calculate_bid_for_targets_with_spend_but_no_sales(self):
        """
        Filter -- Spend but no sales, duration -- lifetime
        unmuted, muted, unviable
        1. unmuted -- spend < 20% of SKU Price, Duration -- lifetime
        2. to_mute -- muted_on not set, spend > 20% of SKU Price, Duration -- lifetime, set to minimum bid (1or2 rupee)
        3. muted -- muted_on set, unviable_on not set, spend after mute < 20% of SKU Price
        4. to_unviable -- muted_on set, unviable_on not set and spend after mute > 20% of SKU Price
        5. unviable -- muted_on set, unviable_on set -- Exclude from optimization
        ----------------
        for all states impressions > 0 in shortest duration, decrease bid by 20%. else, increase bid by default bid increment (2%).
        ----------------
        """
        with transaction.atomic():
            self.q2_sb_disc_key_tgt = SbKeyTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()
            self.q2_sb_disc_pro_tgt = SbProTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()
            self.q2_sp_disc_key_tgt = SpKeyTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()
            self.q2_sp_disc_pro_tgt = SpProTgtOpt.manager.disc_tgt.set_muted_on_unviable_and_optimize_bid()

    def __calculate_bid_for_targets_with_sales(self):
        """
        Filter -- Has Acos, duration -- lifetime (sales>0, spend>0)
        This method will calculate the bid for all the targets that have sales, over any optimization period and \
        save the bid on the discover models.
        algo:
            if sales > 0 and clicks > 0 and spend > 0 and ads_sales > 0 and total_sales > 0:
                ads_to_total_revenue_ratio = ads_sales/total_sales
                bid_multiplier = (
                    desired_ads_percentage/ads_to_total_revenue_ratio)/acos
                auto_max_bid = (
                    bid_multiplier*(spend/clicks))
        """
        with transaction.atomic():
            self.q1_sb_disc_key_tgt = SbKeyTgtOpt.manager.disc_tgt.set_max_bid()
            self.q1_sb_disc_pro_tgt = SbProTgtOpt.manager.disc_tgt.set_max_bid()
            self.q1_sp_disc_key_tgt = SpKeyTgtOpt.manager.disc_tgt.set_max_bid()
            self.q1_sp_disc_pro_tgt = SpProTgtOpt.manager.disc_tgt.set_max_bid()

    def __check_all_targets_optimized(self):
        """
        This method will check whether all the targets have been optimized or not.
        """
        Q_sb_disc_key_tgt = SbKeyTgtOpt.manager.filter(disc_tgt__keyword__isnull=False).count()
        print(Q_sb_disc_key_tgt, "**", f"{self.q1_sb_disc_key_tgt} + {self.q2_sb_disc_key_tgt} + {self.q3_sb_disc_key_tgt} = ", f"{self.q1_sb_disc_key_tgt + self.q2_sb_disc_key_tgt + self.q3_sb_disc_key_tgt}")
        if Q_sb_disc_key_tgt ==(self.q1_sb_disc_key_tgt + self.q2_sb_disc_key_tgt + self.q3_sb_disc_key_tgt):
            print("All targets optimized")

        Q_sb_disc_pro_tgt = SbProTgtOpt.manager.filter(disc_tgt__target__isnull=False).count()
        print(Q_sb_disc_pro_tgt, "**", f"{self.q1_sb_disc_pro_tgt} + {self.q2_sb_disc_pro_tgt} + {self.q3_sb_disc_pro_tgt} = ", f"{self.q1_sb_disc_pro_tgt + self.q2_sb_disc_pro_tgt + self.q3_sb_disc_pro_tgt}")
        if Q_sb_disc_pro_tgt ==(self.q1_sb_disc_pro_tgt + self.q2_sb_disc_pro_tgt + self.q3_sb_disc_pro_tgt):
            print("All targets optimized")

        Q_sp_disc_key_tgt = SpKeyTgtOpt.manager.filter(disc_tgt__keyword__isnull=False).count()
        print(Q_sp_disc_key_tgt, "**", f"{self.q1_sp_disc_key_tgt} + {self.q2_sp_disc_key_tgt} + {self.q3_sp_disc_key_tgt} = ", f"{self.q1_sp_disc_key_tgt + self.q2_sp_disc_key_tgt + self.q3_sp_disc_key_tgt}")
        if Q_sp_disc_key_tgt ==(self.q1_sp_disc_key_tgt + self.q2_sp_disc_key_tgt + self.q3_sp_disc_key_tgt):
            print("All targets optimized")

        Q_sp_disc_pro_tgt = SpProTgtOpt.manager.filter(disc_tgt__target__isnull=False).count()
        print(Q_sp_disc_pro_tgt, "**", f"{self.q1_sp_disc_pro_tgt} + {self.q2_sp_disc_pro_tgt} + {self.q3_sp_disc_pro_tgt} = ", f"{self.q1_sp_disc_pro_tgt + self.q2_sp_disc_pro_tgt + self.q3_sp_disc_pro_tgt}")
        if Q_sp_disc_pro_tgt ==(self.q1_sp_disc_pro_tgt + self.q2_sp_disc_pro_tgt + self.q3_sp_disc_pro_tgt):
            print("All targets optimized")


    def _calculate_bid(self):
        """
        This method will calculate the bid for all the targets, over each optimization period along with the final bid (which will be the minimal bid of all the optimization periods) and save them in the database.
        """
        self.__calculate_bid_for_targets_with_sales()
        self.__calculate_bid_for_targets_with_spend_but_no_sales()
        self.__calculate_bid_for_targets_with_no_spend()
        self.__check_all_targets_optimized()

    def _aggregate_metrics(self):
        """
        This method will aggregate the metrics for all the targets, over each optimization period and save them in the database.
        """
        with transaction.atomic():
            SbKeyTgtOpt.manager.associated_report.sb_aggregated_data()
            SbProTgtOpt.manager.associated_report.sb_aggregated_data()
            SpKeyTgtOpt.manager.associated_report.sp_aggregated_data()
            SpProTgtOpt.manager.associated_report.sp_aggregated_data()

    def _update_ads_n_total_sales(self):
        """
        This method will update the ads to total orders for all the SKUs, over each optimization period and save them in the database.
        When adding the total sales field please ignore orders from the orders report that have more than 2 sku items in the order
        total_sales field added on the optimization models
        """
        AmzSkuAdsMetric.manager.amz_sku.update_ads_n_total_sales()

    def _update_discovered_targets_spend_matrix(self):
        """
        This method will update the spend matrix((lifetime spend and spend since mute) for all the discovered targets.
        """
        with transaction.atomic():
            SBDiscKeyTgt.manager.update_spend_matrix()
            SBDiscProTgt.manager.update_spend_matrix()
            SPDiscKeyTgt.manager.update_spend_matrix()
            SPDiscProTgt.manager.update_spend_matrix()

    def _calc_bid_for_new_disc_targets(self):
        """
        Filter -- Has Acos, duration -- lifetime (sales>0, spend>0)
        This method will calculate the bid for all the targets that have sales, over any optimization period and \
        save them on the optimization models.
        algo:
            if sales > 0 and clicks > 0 and spend > 0 and ads_sales > 0 and total_sales > 0:
                ads_to_total_revenue_ratio = ads_sales/total_sales
                bid_multiplier = (
                    desired_ads_percentage/ads_to_total_revenue_ratio)/acos
                auto_max_bid = (
                    bid_multiplier*(spend/clicks))
        """
        with transaction.atomic():
            SpKeyTgtOpt.manager.disc_tgt.bid_calcu_for_new_targ()
            SpProTgtOpt.manager.disc_tgt.bid_calcu_for_new_targ()
            SbKeyTgtOpt.manager.disc_tgt.bid_calcu_for_new_targ()
            SbProTgtOpt.manager.disc_tgt.bid_calcu_for_new_targ()

    def _run(self):

        # this will update the optimize models and store matrix which is required for optimization
        self._update_discovered_targets_spend_matrix()
        self._update_ads_n_total_sales()
        self._aggregate_metrics()

        # this will give a best bid to our new discovered targets
        # self._calc_bid_for_new_disc_targets()

        # this will optimize the current bid of our live targets
        # self._calculate_bid()

        # for future use
        # self.optimize_budget_for_live_camp()
