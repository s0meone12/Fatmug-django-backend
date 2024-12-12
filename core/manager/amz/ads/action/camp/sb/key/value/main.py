from ........ import BaseManager
 

class SbKeyCampActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        if not self._action:
            from .camp_action import SbKeyCampActionSubManagerSbKeyActionValue
            self._action = SbKeyCampActionSubManagerSbKeyActionValue(
                self)
        return self._action
