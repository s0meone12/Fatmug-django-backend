from ..main import AmzSpDiscProCampManager


class AdsAssociatorSubManagerAmzSpDiscProCamp:
    def __init__(self, manager: AmzSpDiscProCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerAmzSpDiscProCamp
            self.__ini = AdsInitialAssociatorSubManagerAmzSpDiscProCamp(
                self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
