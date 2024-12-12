from ..main import AmzSpDiscKeyCampManager


class AdsAssociatorSubManagerAmzSpDiscKeyCamp:
    def __init__(self, manager: AmzSpDiscKeyCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerAmzSpDiscKeyCamp
            self.__ini = AdsInitialAssociatorSubManagerAmzSpDiscKeyCamp(self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
