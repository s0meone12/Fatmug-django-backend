from django.core.management.base import BaseCommand
from core.services.amz_ad_camp import AmzAdCampaignService

class Command(BaseCommand):
    help = 'Aggregate Amazon Ad Campaign data'

    def handle(self, *args, **options):
        print('Aggregating Pre API data...! ')
        ad_campaign_service = AmzAdCampaignService()
        ad_campaign_service.aggregate_data_pre_api()
