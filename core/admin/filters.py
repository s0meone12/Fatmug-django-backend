from django.contrib import admin


class AmzSkuSettlementAdmin(admin.ModelAdmin):
    list_filter = (
        "amount_type",
        "sku",
    )
    list_display = (
        "__str__",
        "amount_type",
        "amount_description",
        "avg_amount_value",
    )


class AmzSaleReturnSkuAdmin(admin.ModelAdmin):
    list_filter = ("sku",)
    list_display = (
        "__str__",
        "detailed_disposition",
        "total_return_percentage",
        "total_order_percentage",
    )


class SkuPriceActionAdmin(admin.ModelAdmin):
    list_filter = ("status", "sku")
    list_display = [
        "sku",
        "old_price",
        "our_price",
        "discounted_price",
        "status",
        "sale_start_at",
        "sale_end_at",
        "updated_at",
    ]
    readonly_fields = ["old_price", "our_price", "created_at", "updated_at"]
