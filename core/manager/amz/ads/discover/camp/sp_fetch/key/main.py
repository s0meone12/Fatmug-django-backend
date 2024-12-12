from ....... import BaseManager


class SpDiscFetchKeyCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__aso = None

    @property
    def aso(self):
        if not self.__aso:
            from .aso import AdsAssociatorSubManagerSpDiscFetchKeyCamp
            self.__aso = AdsAssociatorSubManagerSpDiscFetchKeyCamp(self)
        return self.__aso
