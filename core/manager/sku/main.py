from core.manager.base import BaseManager


class SkuManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__odoo_api = None

    @property
    def odoo(self):
        from .odoo_api import OdooApiSubManagerSku
        if self.__odoo_api is None:
            self.__odoo_api = OdooApiSubManagerSku(self)
        return self.__odoo_api
