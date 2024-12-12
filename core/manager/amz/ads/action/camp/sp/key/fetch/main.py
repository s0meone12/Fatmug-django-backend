from ........ import BaseManager

    
class SpKeyFetchCampActionManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._disc_fetch_camp = None

    @property
    def disc_fetch_camp(self):
        from .disc_camp import SpKeyFetchCampSubManagerSpKeyFetchAction
        if not self._disc_fetch_camp :
            self._disc_fetch_camp = SpKeyFetchCampSubManagerSpKeyFetchAction(self)
        return self._disc_fetch_camp      
