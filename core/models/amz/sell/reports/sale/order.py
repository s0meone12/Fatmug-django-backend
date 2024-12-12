from django.db import models
from .....inheritance.base_model import BaseModel
from .....amz.sku.main import AmzSku
from core.manager.amz.sell.reports.sale.order.main import SaleOrderRptManager


class SaleOrderRpt(BaseModel):
    amazon_order_id_code = models.CharField(max_length=100, null=False, blank=False)
    purchase_date = models.DateTimeField(null=False, blank=False)
    order_status = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        choices=(
            ("cancelled", "Cancelled"),
            ("pending", "Pending"),
            ("shipping", "Shipping"),
            ("shipped", "Shipped"),
        ),
    )
    sku = models.ForeignKey(AmzSku, on_delete=models.RESTRICT, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    item_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    ship_city = models.CharField(max_length=100, null=True, blank=True)
    ship_state = models.CharField(max_length=100, null=True, blank=True)
    ship_postal_code = models.CharField(max_length=100, null=True, blank=True)
    manager = SaleOrderRptManager()

    class Meta:
        unique_together = ("amazon_order_id_code", "sku")
