from ........base import CheckQSMeta
from core.models import AmzSpAdsCamp
from ....mixin import AdsCampSubManagerMixinAdsTarget


class AmzSpAdsCampSubManagerAmzSpAdsKeyword(AdsCampSubManagerMixinAdsTarget, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSpAdsCamp
