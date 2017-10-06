from vector2 import Vector2
from simulation_object import SimulationObject


class Camera2D(SimulationObject):

    def __init__(self, width: int = 512, height: int = 256, zoom: float = 2.0, target: SimulationObject = None):
        super(Camera2D, self).__init__()
        self.__viewport = Vector2(width, height)  # type: Vector2
        self.__offset = Vector2(self.__viewport.x/2, self.__viewport.y/2)  # type: Vector2
        self.__zoom = zoom  # type: float
        self.target = target  # type: SimulationObject
        self.distance_threshold = 0.05  # type: float

    def update(self, delta_time: float):
        """Follow the camera's target"""
        if self.target is not None:
            distance = self.target.position.distance(self.position)
            if distance > self.distance_threshold:
                self.position.x, self.position.y = self.target.position.x, self.target.position.y
            self.orientation = self.target.orientation - 90.0

    def apply_view_transform(self, vector: Vector2) -> Vector2:
        """Transform a vector from the world coordinate system to the camera coordinate system of this camera"""
        result = vector.copy()
        result -= self.position
        result.rotate(-self.orientation)
        result *= self.zoom
        result += self.__offset
        result.y = self.viewport.y - result.y
        return result

    def apply_inverse_view_transform(self, vector: Vector2) -> Vector2:
        """Transform a vector from the camera coordinate system of this camera to the world coordinate system"""
        result = vector.copy()
        result.y = self.viewport.y - result.y
        result -= self.__offset
        result /= self.zoom
        result.rotate(self.orientation)
        result += self.position
        return result

    def move(self, distance: Vector2) -> None:
        """Move the camera a given distance in the camera's perspective"""
        heading = Vector2(0, 1)
        heading.rotate(self.orientation)
        normal = heading.copy()
        normal.rotate(90)
        self.position += heading * distance.y + normal * distance.x

    @property
    def viewport(self):
        return self.__viewport

    @viewport.setter
    def viewport(self, viewport):
        self.__viewport = viewport
        self.__offset = Vector2(self.__viewport.x / 2, self.__viewport.y / 2)

    @property
    def zoom(self):
        return self.__zoom

    @zoom.setter
    def zoom(self, zoom):
        self.__zoom = zoom

