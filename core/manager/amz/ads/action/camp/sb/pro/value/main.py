from ........ import BaseManager


class SbProCampActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        if not self._action:
            from .camp_action import SbProCampActionSubManagerSbProActionValue
            self._action = SbProCampActionSubManagerSbProActionValue(
                self)
        return self._action
