from ..main import SpDiscFetchProCampManager


class AdsAssociatorSubManagerSpDiscFetchProCamp:
    def __init__(self, manager: SpDiscFetchProCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerSpDiscFetchProCamp
            self.__ini = AdsInitialAssociatorSubManagerSpDiscFetchProCamp(
                self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
