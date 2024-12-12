from sp_api.base.marketplaces import Marketplaces


class AmzAdsPublisher:
    """
    Main Publisher for Sponsored Brands, Sponsored Display and Sponsored Products.
    """

    def __init__(self, marketplace: Marketplaces, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Initalizing AmzAdsApiPublisherr for {marketplace}")
        self._marketplace = marketplace
        self._sb = None
        self._sp = None
        self._sb_video_assets = None

    @property
    def sb(self):
        if not self._sb:
            from .sb import AmzAdsSbPublisher
            self._sb = AmzAdsSbPublisher(self._marketplace)
        return self._sb
    
    @property
    def sp(self):
        if not self._sp:
            from .sp import AmzAdsSpPublisher
            self._sp = AmzAdsSpPublisher(self._marketplace)
        return self._sp

    @property
    def sb_video_assets(self):
        if not self._sb_video_assets:
            from .sb_video_assets import VideoAssetIdGenerator
            self._sb_video_assets = VideoAssetIdGenerator(self._marketplace)
        return self._sb_video_assets