from core.models import AmzSkuDiscKey, AmzSkuDiscProTgt, SBDiscKeyTgt, SBDiscProTgt, SPDiscKeyTgt, SPDiscProTgt, SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyCamp, SPDiscProCamp
from .main import AdsOptSubManagerAmzSku


class AdsDiscoverySubManagerAmzSku:
    def __init__(self, manager: AdsOptSubManagerAmzSku):
        self.manager = manager

    def _run(self):
        """
        Discovery happens from SP-ST Report and is added to SKU. SKUTargets the target gets distributed to SP, SB, SD campaigns.
        This method will discover new targets from report and save them in the database.
        """
        AmzSkuDiscKey.manager.amz_sku.discover()
        AmzSkuDiscProTgt.manager.amz_sku.discover()

        """
        This method is for make a new rows in DiscTgt model, which have AmzSkuDiscKey or AmzSkuDiscProTgt and associate them.
        """
        SBDiscKeyTgt.manager.amz_sku.discover()
        SBDiscProTgt.manager.amz_sku.discover()
        SPDiscKeyTgt.manager.amz_sku.discover()
        SPDiscProTgt.manager.amz_sku.discover()

        # """
        # This method will identify the need to create new campaigns and save them in the database.
        # """
        SBDiscKeyCamp.manager.amz_sku.discover()
        # SBDiscProCamp.manager.amz_sku.discover()
        # SPDiscKeyCamp.manager.amz_sku.discover()
        # SPDiscProCamp.manager.amz_sku.discover()

        # """
        # This method will map the fk discovered targets with the disc campaigns.
        # """
        # SBDiscKeyTgt.manager.fk_mapping_on_disc_trgt()
        # SBDiscProTgt.manager.fk_mapping_on_disc_trgt()
        # SPDiscKeyTgt.manager.fk_mapping_on_disc_trgt()
        # SPDiscProTgt.manager.fk_mapping_on_disc_trgt()
