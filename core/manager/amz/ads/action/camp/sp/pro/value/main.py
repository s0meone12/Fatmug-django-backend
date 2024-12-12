from ........ import BaseManager


class SpProCampActionValueManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action = None

    @property
    def action(self):
        from .camp_action import SpProCampActionSubManagerSpProActionValue
        if not self._action:
            self._action = SpProCampActionSubManagerSpProActionValue(self)
        return self._action
