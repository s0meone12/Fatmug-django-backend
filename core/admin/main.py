from core.models import *
from core.models.wordpress_webhook.wordpress_webhook_model import WordPressWebhook, WordpressOrderShipment, WordpressOrder
from .filters import (
    AmzSaleReturnSkuAdmin,
    AmzSkuSettlementAdmin,
    SkuPriceActionAdmin,
)

from django.contrib import admin

# Odoo Data
admin.site.register(Sku)
admin.site.register(AmzSku)

# Live data
admin.site.register(AmzSpAdsCamp)  # SP live data
admin.site.register(AmzSpAdsKeyword)
admin.site.register(AmzSpAdsNegativeKeyword)
admin.site.register(AmzSpAdsTarget)
admin.site.register(AmzSpAdsNegativeTarget)

admin.site.register(AmzSbAdsCamp)  # SB live data
admin.site.register(AmzSbAdsKeyword)
admin.site.register(AmzSbAdsTarget)

admin.site.register(AmzSdAdsCamp)  # SD live data
admin.site.register(AmzSdAdsTarget)

# Report Data
admin.site.register(AmzAdsPerformanceRptUpdate)
admin.site.register(AmzAdsSpTgtRpt)
admin.site.register(AmzAdsSpStRpt)
admin.site.register(AmzAdsSdMtRpt)
admin.site.register(AmzAdsSbTgtRpt)
admin.site.register(AmzAdsSbStRpt)
admin.site.register(SaleOrderRpt)

# Discover Data
admin.site.register(AmzSkuDiscKey)
admin.site.register(AmzSkuDiscProTgt)
admin.site.register(SBDiscKeyCamp)
admin.site.register(SPDiscKeyCamp)
admin.site.register(SPDiscProCamp)
admin.site.register(SBDiscProCamp)
admin.site.register(SBDiscKeyTgt)
admin.site.register(SBDiscProTgt)
admin.site.register(SPDiscKeyTgt)
admin.site.register(SPDiscProTgt)
admin.site.register(SpDiscFetchKeyCamp)
admin.site.register(SpDiscFetchProCamp)
admin.site.register(SPFetchProTgt)
admin.site.register(SPFetchKeyTgt)

# Optimization Data
admin.site.register(SpKeyTgtOpt)
admin.site.register(SpProTgtOpt)
admin.site.register(SbKeyTgtOpt)
admin.site.register(SbProTgtOpt)
admin.site.register(AmzSkuAdsMetric)

# Action Data
admin.site.register(SbProCampaignAction)
admin.site.register(SbKeyCampaignAction)
admin.site.register(SpKeyCampaignAction)
admin.site.register(SpProCampaignAction)
admin.site.register(SbKeyCampaignActionValues)
admin.site.register(SpKeyCampaignActionValues)
admin.site.register(SbProCampaignActionValues)
admin.site.register(SpProCampaignActionValues)
admin.site.register(SpInitialFetchKeyCampaignAction)
admin.site.register(SpInitialFetchProCampaignAction)

admin.site.register(SbKeyTgtAction)
admin.site.register(SbProTgtAction)
admin.site.register(SpKeyTgtAction)
admin.site.register(SpProTgtAction)
admin.site.register(SbKeyTgtActionValues)
admin.site.register(SpKeyTgtActionValues)
admin.site.register(SbProTgtActionValues)
admin.site.register(SpProTgtActionValues)

# admin.site.register(WordPressWebhook)


class WordPressWebhookAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'payload', 'created_at']


admin.site.register(WordPressWebhook, WordPressWebhookAdmin)
admin.site.register(WordpressOrder)
admin.site.register(WordpressOrderShipment)
# Amz Reports
admin.site.register(AmzSettlementTransactionType)
admin.site.register(AmzSettlementAmountType)
admin.site.register(AmzSettlementAmountDescription)
admin.site.register(AmzSettlement)
admin.site.register(AmzSettlementDetail)
admin.site.register(AmzSkuSettlement, AmzSkuSettlementAdmin)
admin.site.register(AmzSaleReturnReason)
admin.site.register(AmzSaleReturnDetailedDisposition)
admin.site.register(AmzSaleReturn)
admin.site.register(AmzSkuSaleReturn, AmzSaleReturnSkuAdmin)
admin.site.register(SkuPriceAction, SkuPriceActionAdmin)
