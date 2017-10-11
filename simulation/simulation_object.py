from typing import List, Tuple
from simulation.vector2 import Vector2


class SimulationObject(object):

    ID = 0  # type: int

    def __init__(self,
                 position: Vector2 = Vector2(0, 0),
                 orientation: float = 0.0,
                 color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 velocity: float = 0.0,
                 max_velocity: float = 0.0,
                 acceleration: float = 0.0,
                 max_acceleration: float = 0.0,
                 mesh: List[Vector2] = None):
        if mesh is None:
            mesh = [Vector2(0.5, 0.5), Vector2(-0.5, 0.5), Vector2(-0.5, -0.5), Vector2(0.5, -0.5)]
        self.position = Vector2(position.x, position.y)  # type: Vector2
        self.orientation = orientation  # type: float
        self.color = color  # type: Tuple[float, float, float]
        self.mesh = mesh  # type: List[Vector2]
        self.active = True  # type: bool
        self.__acceleration = acceleration  # type: float
        self.max_acceleration = max_acceleration  # type: float
        self.__velocity = velocity  # type: float
        self.max_velocity = max_velocity  # type: float
        self.id = SimulationObject.ID  # type: int
        SimulationObject.ID += 1

    def apply_world_transform(self, vector: Vector2) -> Vector2:
        """Transform a vector from the local coordinate system of this object to the world coordinate system"""
        result = vector.copy()
        result.rotate(self.orientation)
        result += self.position
        return result

    @property
    def velocity(self):
        return self.__velocity

    @velocity.setter
    def velocity(self, velocity):
        self.__velocity = min(self.max_velocity, max(0.0, velocity))

    @property
    def acceleration(self):
        return self.__acceleration

    @acceleration.setter
    def acceleration(self, acceleration):
        self.__acceleration = min(self.max_acceleration, acceleration)
