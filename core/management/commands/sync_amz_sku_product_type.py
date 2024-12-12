from django.core.management.base import BaseCommand
from core.services.amz.sell.data_agg.main import AmzSellDataAggregationService


class Command(BaseCommand):
    help = "Aggregate Amazon SKU Data (Product Type)"

    def handle(self, *args, **options):
        try:
            ins = AmzSellDataAggregationService()
            updated = ins.aggregate_amz_sku_product_type_data()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Something Went Wrong: \n{e}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully Sync Product Type For {updated or 0} SKU's."
                )
            )
