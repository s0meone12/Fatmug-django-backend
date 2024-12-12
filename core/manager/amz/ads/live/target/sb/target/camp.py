from .......base import CheckQSMeta
from core.models import AmzSbAdsCamp
from ...mixin import AdsCampSubManagerMixinAdsTarget


class AmzSbAdsCampSubManagerAmzSbAdsTarget(AdsCampSubManagerMixinAdsTarget, metaclass=CheckQSMeta):

    def __init__(self, manager):
        self.manager = manager
        self.model = AmzSbAdsCamp
