import abc
from enum import Enum, unique
from simulation.layout.world import World
from simulation.vector2 import Vector2
from simulation.io.camera2d import Camera2D
import simulation.config_reader as cr


class Renderer:
    __metaclass__ = abc.ABCMeta

    @unique
    class Mode(Enum):
        SURFACE = 0
        WIREFRAME = 1

    def __init__(self, camera: Camera2D):
        self.camera = camera  # type: Camera2D
        self.camera.viewport = Vector2(cr.CONFIG.getint('renderer', 'width'), cr.CONFIG.getint('renderer', 'height'))
        self.camera.zoom = cr.CONFIG.getfloat('renderer', 'zoom')  # type: float
        self.interactive = cr.CONFIG.getboolean('renderer', 'interactive')  # type: bool
        self.mode = Renderer.Mode.SURFACE  # type Enum
        self.background_brightness = 1.0  # type: int

    @abc.abstractmethod
    def render(self, world: World):
        return

    @abc.abstractmethod
    def update(self, delta_time: float):
        return
