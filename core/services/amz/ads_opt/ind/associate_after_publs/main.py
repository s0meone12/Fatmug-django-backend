from core.models import SPDiscKeyCamp, SPDiscProCamp, SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyTgt, SBDiscKeyTgt, SPDiscProTgt, SBDiscProTgt
# from core.models import SpDiscFetchKeyCamp,SpDiscFetchProCamp,SPFetchKeyTgt,SPFetchProTgt
import pandas as pd
from django.db import transaction


class AmzAdsIndAssociateLiveToDisc:

    def __campaign_association(self):
        with transaction.atomic():
            SPDiscKeyCamp.manager.associater()
            SPDiscProCamp.manager.associater()
            SBDiscKeyCamp.manager.associater()
            SBDiscProCamp.manager.associater()
            # SpDiscFetchKeyCamp.manager.associater()
            # SpDiscFetchProCamp.manager.associater()

    def __target_association(self):
        with transaction.atomic():
            SPDiscKeyTgt.manager.associater()
            SPDiscProTgt.manager.associater()
            SBDiscKeyTgt.manager.associater()
            SBDiscProTgt.manager.associater()
            # SPFetchProTgt.manager.associater()
            # SPFetchKeyTgt.manager.associater()

    def __check(self):
        camp_model = [SPDiscKeyCamp, SPDiscProCamp,
                      SBDiscKeyCamp, SBDiscProCamp]
        for c in camp_model:
            disc_camp = c.objects.filter(campaign__isnull=True)
            if disc_camp:
                raise ValueError(
                    f"check fails, all campaigns ({c}) are not associated yet. Try after some time")

        target_model = [SPDiscProTgt, SBDiscProTgt]
        for t in target_model:
            disc_targ = t.objects.filter(target__isnull=True)
            if disc_targ:
                raise ValueError(
                    f"check fails, all targets ({t}) are not associated yet. Try after some time")

        keyword_model = [SPDiscKeyTgt, SBDiscKeyTgt]
        for k in keyword_model:
            disc_targ = k.objects.filter(keyword__isnull=True)
            if disc_targ:
                raise ValueError(
                    f"check fails, all keywords ({k}) are not associated yet. Try after some time")

    def _run(self):
        """
        This method will associate the published campaigns with the discovered campaigns.
        """
        self.__campaign_association()
        self.__target_association()
        self.__check()
