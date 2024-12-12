from core.models.amz.ads import (
    SbKeyTgtAction,
    SpKeyTgtAction,
    SbProTgtAction,
    SpProTgtAction,
)
from core.models.amz.ads import (
    SpKeyTgtActionValues,
    SbKeyTgtActionValues,
    SbProTgtActionValues,
    SpProTgtActionValues,
)
from django.db import transaction


class AmzAdsTargetActionGenerator:

    def generate_action(self):
        """
        This method will store the action of updation of the live targets and save the actions and also store action values in the database.
        values can be updated are: bid
        """
        with transaction.atomic():
            # this update Target Action
            SbKeyTgtAction.manager.disc_target.target_update_action() 
            SpKeyTgtAction.manager.disc_target.target_update_action()
            SbProTgtAction.manager.disc_target.target_update_action()
            SpProTgtAction.manager.disc_target.target_update_action()
        
        with transaction.atomic():
            # this update Target Action Values
            SbKeyTgtActionValues.manager.action.target_update_action_values()
            SpKeyTgtActionValues.manager.action.target_update_action_values()
            SbProTgtActionValues.manager.action.target_update_action_values()
            SpProTgtActionValues.manager.action.target_update_action_values()
