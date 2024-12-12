from ........base import CheckQSMeta
from core.models import AmzSdAdsCamp
from ....mixin import AdsCampSubManagerMixinAdsTarget


class AmzSdAdsCampSubManagerAmzSdAdsTarget(AdsCampSubManagerMixinAdsTarget, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSdAdsCamp