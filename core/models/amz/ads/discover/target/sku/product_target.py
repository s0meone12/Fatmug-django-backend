from .base import BaseAmzSkuDiscTgt
from core.manager import AmzSkuDiscProTgtManager


class AmzSkuDiscProTgt(BaseAmzSkuDiscTgt):
    manager = AmzSkuDiscProTgtManager()
