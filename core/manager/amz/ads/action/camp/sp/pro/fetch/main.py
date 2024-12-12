from ........ import BaseManager


class SpProFetchCampActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disc_fetch_camp = None
         
    @property
    def disc_fetch_camp(self):
        from .disc_camp import SpProFetchCampSubManagerSpProFetchAction
        if not self._disc_fetch_camp:
            self._disc_fetch_camp = SpProFetchCampSubManagerSpProFetchAction(self)
        return self._disc_fetch_camp
  