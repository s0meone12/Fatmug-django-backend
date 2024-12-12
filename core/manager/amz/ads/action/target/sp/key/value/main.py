from ........ import BaseManager

class SpKeyTargActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None
        
    @property
    def action(self):
        from .target_action import SpKeyTargActionSubManagerSpKeyActionValue
        if not self._action:
            self._action = SpKeyTargActionSubManagerSpKeyActionValue(self)
        return self._action
