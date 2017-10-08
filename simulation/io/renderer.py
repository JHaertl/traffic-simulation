import abc

from simulation.layout.world import World
from simulation.simulation_object import SimulationObject
from simulation.vector2 import Vector2
from simulation.io.camera2d import Camera2D
from typing import List
import numpy as np
import cv2


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

    @staticmethod
    def apply_transform(obj: SimulationObject, camera: Camera2D) -> np.ndarray:
        temp = []
        for vertex in obj.mesh:
            temp.append(camera.apply_view_transform(obj.apply_world_transform(vertex)))
        poly = Renderer.numpy_from_list(temp)
        return poly

    @staticmethod
    def numpy_from_list(poly: List[Vector2]) -> np.ndarray:
        points = []
        for node in poly:
            points.append([node.x, node.y])
        return np.array(points, np.int32)

    @staticmethod
    def draw_text(image, text, x, y):
        cv2.putText(image, text, (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA)