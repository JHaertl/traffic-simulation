import random
import sys
import logging


class Spawner:

    _vehicle_pool = []

    def __init__(self, road, lane=None, node=0, delay=0.0, seed=None):
        self.road = road
        self.lane = lane
        self.node = node
        self.delay = delay
        self.timer = 0.0
        self.seed = seed
        if seed is None:
            self.seed = random.randint(0, sys.maxsize)
        self.logger = logging.getLogger('simulation.spawner.Spawner')
        self.logger.info('Seed for spawner: ' + str(self.seed))
        self.rng = random.Random(self.seed)

    def update(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.delay:
            if self._spawn_vehicle():
                self.timer = 0.0

    @staticmethod
    def add_vehicle(vehicle):
        Spawner._vehicle_pool.append(vehicle)

    def _spawn_vehicle(self):
        if not Spawner._vehicle_pool:
            return False
        vehicle_index = self.rng.randint(0, len(Spawner._vehicle_pool) - 1)
        vehicle = Spawner._vehicle_pool[vehicle_index]
        lane_index = self.lane
        if lane_index is None:
            lane_index = self.rng.randint(0, len(self.road.lanes) - 1)
        lane = self.road.lanes[lane_index]
        if not self._check_spawn_area(vehicle, lane):
            return False
        start_pos = lane.center[self.node]
        target_pos = lane.center[self.node + 1]
        Spawner._reinit_vehicle(lane, vehicle, start_pos, target_pos)
        lane.add_vehicle(vehicle)
        Spawner._vehicle_pool.remove(vehicle)
        return True

    def _check_spawn_area(self, vehicle, lane):
        min_spawn_space = 20.0  # TODO: NOTE this should always be equal or higher than the maximum idm min_spacing
        vehicle.position = lane.center[self.node].copy()
        back_vehicle = lane.find_back_vehicle(vehicle.position)
        front_vehicle = lane.find_front_vehicle(vehicle.position)
        if front_vehicle is None and back_vehicle is None:
            return True
        if front_vehicle is not None:
            distance = lane.projected_bumper_distance(vehicle, front_vehicle)
            if distance < min_spawn_space:
                return False
        if back_vehicle is not None:
            distance = lane.projected_bumper_distance(back_vehicle, vehicle)
            if distance < min_spawn_space:
                return False
        return True

    @staticmethod
    def _reinit_vehicle(lane, vehicle, start, target):
        vehicle.active = True
        vehicle.position = start.copy()
        vehicle.target = target
        vehicle.velocity = 0
        vehicle.acceleration = 0
        vehicle.lane = lane
        vehicle.turn_signal = 0
