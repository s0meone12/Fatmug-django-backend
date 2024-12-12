from core.models import SPDiscKeyCamp, SPDiscProCamp, SBDiscKeyCamp, SBDiscProCamp, SpDiscFetchKeyCamp, SpDiscFetchProCamp
import re
from django.db import transaction


class RenameCampaignWithNewFormat():
    """
    This clas will update the old name with new name format
    """

    def _sb_camp_key(self):
        live_camps = SBDiscKeyCamp.objects.filter(
            campaign__isnull=False, campaign__amz_sku__isnull=False)
        for camp in live_camps:
            current_name = camp.campaign.name
            match = re.match(r'Vdo(\d)_(.*?)_Key', current_name)
            if match:
                group1 = match.group(1)
                group2 = match.group(2)
                updated_name = f'{group1}^Vdo_{group2}_Key'
                camp.name = updated_name
                camp.save()

    def _sb_camp_pro(self):
        live_camps = SBDiscProCamp.objects.filter(
            campaign__isnull=False, campaign__amz_sku__isnull=False)
        for camp in live_camps:
            current_name = camp.campaign.name
            match = re.match(r'Vdo(\d)_(.*?)_Pro', current_name)
            if match:
                group1 = match.group(1)
                group2 = match.group(2)
                updated_name = f'{group1}^{current_name[0:3]}_{group2}_{current_name.split("_")[-1]}'
                camp.name = updated_name
                camp.save()

    def _sp_camp_key(self):
        live_camps = SPDiscKeyCamp.objects.filter(
            campaign__isnull=False, campaign__amz_sku__isnull=False)
        for camp in live_camps:
            current_name = camp.campaign.name
            match = re.match(r'Opt(\d)_(.*?)_Key', current_name)
            if match:
                group1 = match.group(1)
                group2 = match.group(2)
                updated_name = f'{group1}^Opt_{group2}_{current_name.split("_")[-1]}'
                camp.name = updated_name
                camp.save()

    def _sp_camp_pro(self):
        live_camps = SPDiscProCamp.objects.filter(campaign__isnull=False)
        l = []
        for camp in live_camps:
            current_name = camp.campaign.name
            parts = current_name.split('_')
            middle_value = parts[1]+'_'+parts[2]

            if not any(char.isdigit() for char in parts[0]):
                updated_name = f"{1}^{parts[0]}_{middle_value}_{parts[3]}"
                l.append(middle_value)

            elif len(parts[0]) == 4:
                if middle_value in l:
                    i = str(int(parts[0][3]) + 1)
                    updated_name = f"{i}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                else:
                    updated_name = f"{parts[0][3]}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                    l.append(middle_value)
            else:
                print("something wrong")
                raise ValueError(f"irrelevent name {current_name}")

            camp.name = updated_name
            camp.save()

    def _sp_fetch_key_camp(self):
        live_camps = SpDiscFetchKeyCamp.objects.filter(
            campaign__isnull=False)
        l = []
        for camp in live_camps:
            current_name = camp.campaign.name
            parts = current_name.split('_')
            middle_value = parts[1]+'_'+parts[2]

            if not any(char.isdigit() for char in parts[0]):
                updated_name = f"{1}^{parts[0]}_{middle_value}_{parts[3]}"
                l.append(middle_value)

            elif len(parts[0]) == 4:
                if middle_value in l:
                    i = str(int(parts[0][3]) + 1)
                    updated_name = f"{i}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                else:
                    updated_name = f"{parts[0][3]}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                    l.append(middle_value)
            else:
                print("something wrong")
                raise ValueError(f"irrelevent name {current_name}")

            camp.name = updated_name
            camp.save()

    def _sp_fetch_pro_camp(self):
        live_camps = SpDiscFetchProCamp.objects.filter(campaign__isnull=False)
        l = []
        for camp in live_camps:
            current_name = camp.campaign.name
            parts = current_name.split('_')
            middle_value = parts[1]+'_'+parts[2]

            if not any(char.isdigit() for char in parts[0]):
                updated_name = f"{1}^{parts[0]}_{middle_value}_{parts[3]}"
                l.append(middle_value)

            elif len(parts[0]) == 4:
                if middle_value in l:
                    i = str(int(parts[0][3]) + 1)
                    updated_name = f"{i}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                else:
                    updated_name = f"{parts[0][3]}^{parts[0][0:3]}_{middle_value}_{parts[3]}"
                    l.append(middle_value)
            else:
                print("something wrong")
                raise ValueError(f"irrelevent name {current_name}")

            camp.name = updated_name
            camp.save()

    def rename_camp_in_disc_modl(self):
        with transaction.atomic():
            self._sb_camp_key()
            self._sb_camp_pro()
            self._sp_camp_key()
            self._sp_camp_pro()
            self._sp_fetch_key_camp()
            self._sp_fetch_pro_camp()
