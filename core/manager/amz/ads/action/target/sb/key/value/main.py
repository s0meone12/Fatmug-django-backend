from ........ import BaseManager


class SbKeyTargActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        from .target_action import SbKeyTargActionSubManagerSbKeyActionValue
        if not self._action:
            self._action = SbKeyTargActionSubManagerSbKeyActionValue(self)
        return self._action
