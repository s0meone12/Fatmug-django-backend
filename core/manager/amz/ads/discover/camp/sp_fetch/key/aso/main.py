from ..main import SpDiscFetchKeyCampManager


class AdsAssociatorSubManagerSpDiscFetchKeyCamp:
    def __init__(self, manager: SpDiscFetchKeyCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerSpDiscFetchKeyCamp
            self.__ini = AdsInitialAssociatorSubManagerSpDiscFetchKeyCamp(
                self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
