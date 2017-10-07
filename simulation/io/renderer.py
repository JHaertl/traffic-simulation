import abc

from simulation.layout.world import World


class Renderer:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    MODE_SURFACE = 0
    MODE_WIREFRAME = 1
    MODE_DEBUG = 2

    @abc.abstractmethod
    def render(self, world: World):
        return

    @abc.abstractmethod
    def update(self, delta_time: float):
        return
