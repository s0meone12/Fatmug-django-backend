from ..main import AmzSdDiscProCampManager


class AdsAssociatorSubManagerAmzSdDiscProCamp:
    def __init__(self, manager: AmzSdDiscProCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerAmzSbDiscProCamp
            self.__ini = AdsInitialAssociatorSubManagerAmzSbDiscProCamp(
                self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
