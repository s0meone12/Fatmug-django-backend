from ..main import AmzSbDiscProCampManager


class AdsAssociatorSubManagerAmzSbDiscProCamp:
    def __init__(self, manager: AmzSbDiscProCampManager):
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
