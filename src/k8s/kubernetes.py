from abc import ABCMeta, abstractmethod


class Kubernetes(metaclass=ABCMeta):
    def __init__(self):
        self.configuration = ""

    @abstractmethod
    def apply(self):
        pass
