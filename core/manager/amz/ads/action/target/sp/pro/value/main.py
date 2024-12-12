from ........ import BaseManager


class SpProTargActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        from .target_action import SpProTargActionSubManagerSpProActionValue
        if not self._action:
            self._action = SpProTargActionSubManagerSpProActionValue(self)
        return self._action
        
