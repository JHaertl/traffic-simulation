from vector2 import Vector2
from typing import List, Tuple


class SimulationObject(object):

    ID = 0  # type: int

    def __init__(self,
                 position: Vector2 = Vector2(0, 0),
                 orientation: float = 0.0,
                 color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                 mesh: List[Vector2] = None):
        if mesh is None:
            mesh = [Vector2(0.5, 0.5), Vector2(-0.5, 0.5), Vector2(-0.5, -0.5), Vector2(0.5, -0.5)]
        self.position = Vector2(position.x, position.y)  # type: Vector2
        self.orientation = orientation  # type: float
        self.color = color  # type: (int, int, int)
        self.mesh = mesh  # type: [Vector2]
        self.active = True  # type: bool
        self.id = SimulationObject.ID  # type: int
        SimulationObject.ID += 1

    def apply_world_transform(self, vector: Vector2) -> Vector2:
        """Transform a vector from the local coordinate system of this object to the world coordinate system"""
        result = vector.copy()
        result.rotate(self.orientation)
        result += self.position
        return result
