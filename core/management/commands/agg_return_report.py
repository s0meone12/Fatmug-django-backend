from django.core.management.base import BaseCommand
from core.services.amz.sell.amz_return import AmzSaleReturnService
import sys


class Command(BaseCommand):
    help = "Aggregate Return Report"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            "start_from",
            type=int,
            help="Enter numbers of past days to fetch reports for.",
        )

    def handle(self, *args, **options):
        start_from = options["start_from"]
        print(f"Fetching data for past {start_from} days.")
        try:
            rs = AmzSaleReturnService()
            rs.aggregate_data(start_from=start_from)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Something Went Wrong: \n{e}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                "Successfully aggregated data."))
