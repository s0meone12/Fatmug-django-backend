from django.core.management.base import BaseCommand
from core.services.amz.sell.settlement import AmzSettlementService
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Aggregate Settlement Report"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            "createdSince",
            type=int,
            nargs="?",
            default=0,
            help="Enter numbers of past days to fetch reports for.",
        )
        parser.add_argument(
            "createdUntil",
            type=int,
            nargs="?",
            default=0,
            help="Enter numbers of past days to fetch reports until.",
        )

    def handle(self, *args, **options):
        createdSince = options["createdSince"] or None
        createdUntil = options["createdUntil"] or None
        if createdSince is not None:
            createdSince = datetime.now() - timedelta(days=createdSince)
        if createdUntil is not None:
            createdUntil = datetime.now() - timedelta(days=createdUntil)
        try:
            ss = AmzSettlementService()
            ss.aggregate_data(createdSince=createdSince, createdUntil=createdUntil)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Something Went Wrong: \n{e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Successfully aggregated data."))
