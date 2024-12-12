from .ind import AmzInAdsOptimizor
from .usa import AmzUsAdsOptimizor


class AmzAdsOptimizor:
    def __init__(self):
        self.__in = AmzInAdsOptimizor()
        self.__us = AmzUsAdsOptimizor()

    def ind(self):
        self.__in.run()

    def usa(self):
        self.__us.run()

    def run(self):
        self.ind()