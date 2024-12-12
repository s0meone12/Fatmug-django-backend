from ........ import BaseManager


class SbProTargActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action=None

    @property
    def action(self):
        from .target_action import SbProTargActionSubManagerSbProActionValue
        if not self._action:
            self._action = SbProTargActionSubManagerSbProActionValue(self)
        return self._action
