from ........ import BaseManager


class SpKeyCampActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        from .camp_action import SpKeyCampActionSubManagerSpKeyActionValue
        if not self._action:
            self._action = SpKeyCampActionSubManagerSpKeyActionValue(self)
        return self._action
