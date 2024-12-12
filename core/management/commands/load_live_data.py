from django.core.management.base import BaseCommand
from core. models import Sku, AmzSku, AmzSbAdsCamp, AmzSdAdsCamp, AmzSpAdsCamp, AmzSbAdsTarget, AmzSdAdsTarget, AmzSpAdsTarget, AmzSpAdsNegativeTarget, AmzSpAdsNegativeKeyword, AmzSbAdsKeyword, AmzSpAdsKeyword
from core.services.amz.ads_opt.ind.discover.fill_live_data_in_disc_mdl import AddLiveDataInDiscModels
from core.services.amz.ads_opt.ind.discover.rename_camp import RenameCampaignWithNewFormat

class Command(BaseCommand):
    help = 'Load live models data in discovered models, before run discovery load live data in Discovered model, one time.'

    def handle(self, *args, **options):
        # print('Loading of live data into discovered models')
        # # sync Sku
        # Sku.manager.odoo.sync()
        # AmzSku.manager.odoo.sync()
        
        # # sync Campaigns
        # AmzSbAdsCamp.manager.api.sync()
        # AmzSdAdsCamp.manager.api.sync()
        # AmzSpAdsCamp.manager.api.sync()
        
        # # sync Targets
        # AmzSbAdsTarget.manager.api.sync()
        # AmzSdAdsTarget.manager.api.sync()
        # AmzSpAdsTarget.manager.api.sync()
        # AmzSpAdsNegativeTarget.manager.api.sync()

        # # sync Keywords
        # AmzSbAdsKeyword.manager.api.sync()
        # AmzSpAdsKeyword.manager.api.sync()
        # AmzSpAdsNegativeKeyword.manager.api.sync()
        
        # # add live model data in discovered models
        load= AddLiveDataInDiscModels()
        load.populate_disc_models_with_live_data()

        # # rename campaign with new format
        # ren=RenameCampaignWithNewFormat()
        # ren.rename_camp_in_disc_modl()