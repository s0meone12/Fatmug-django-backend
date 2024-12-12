from ..main import AmzSbDiscKeyCampManager


class AdsAssociatorSubManagerAmzSbDiscKeyCamp:
    def __init__(self, manager: AmzSbDiscKeyCampManager):
        self.manager = manager
        self.__ini = None

    @property
    def _ini(self):
        if self.__ini is None:
            from .initial import AdsInitialAssociatorSubManagerAmzSbDiscKeyCamp
            self.__ini = AdsInitialAssociatorSubManagerAmzSbDiscKeyCamp(self.manager)
        return self.__ini

    def run(self):
        """
        This method will map the fk discovered targets with the disc campaigns.
        """
