from .main import AdsOptSubManagerAmzSku
from core.models import SpDiscFetchKeyCamp, SpDiscFetchProCamp, SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyCamp, SPDiscProCamp


class AdsAssociationSubManagerAmzSku:
    def __init__(self, manager: AdsOptSubManagerAmzSku):
        self.manager = manager

    def _run(self):
        ms = [SpDiscFetchKeyCamp, SpDiscFetchProCamp, SBDiscKeyCamp, SBDiscProCamp, SPDiscKeyCamp, SPDiscProCamp]
        for m in ms:
            m.manager.aso._ini._run()
        
