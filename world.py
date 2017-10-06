from spawner import Spawner
from vector2 import Vector2
from typing import List, Tuple
from road import Road


class World:

    def __init__(self):
        self.roads = []  # type: List[Road]
        self.vehicles = []  # type: List[Vehicle]
        self.spawners = []  # type: List[Spawner]
        self.camera_locations = [(Vector2(0, 0), 0)]  # type: List[Tuple[Vector2, float]]

    def update(self, delta_time: float) -> None:
        for road in self.roads:
            road.reset_hashes()
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.update_idm()
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.update_vehicle(delta_time)
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.update_lane()
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.update_mobil()
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.update_events(delta_time)
        for spawner in self.spawners:
            spawner.update(delta_time)

    def add_road(self, road: Road) -> None:
        self.roads.append(road)

    def add_spawner(self, spawner: Spawner) -> None:
        self.spawners.append(spawner)

    def add_vehicle(self, vehicle) -> None:
        self.vehicles.append(vehicle)
        Spawner.add_vehicle(vehicle)
