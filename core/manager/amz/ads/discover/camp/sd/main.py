from ...... import BaseManager


class AmzSdDiscProCampManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__aso = None
        self.__publisher = None

    @property
    def aso(self):
        if not self.__aso:
            from .aso import AdsAssociatorSubManagerAmzSdDiscProCamp
            self.__aso = AdsAssociatorSubManagerAmzSdDiscProCamp(self)
        return self.__aso

    @property
    def publisher(self):
        if not self.__publisher:
            from core.apis.clients import ADS_PUBLISHER
            self.__publisher = ADS_PUBLISHER.AMZ_ADS_PUBLISHER_IN.sb
        return self.__publisher
