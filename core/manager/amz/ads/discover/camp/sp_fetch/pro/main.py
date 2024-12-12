from ....... import BaseManager


class SpDiscFetchProCampManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__aso = None

    @property
    def aso(self):
        if not self.__aso:
            from .aso import AdsAssociatorSubManagerSpDiscFetchProCamp
            self.__aso = AdsAssociatorSubManagerSpDiscFetchProCamp(self)
        return self.__aso
