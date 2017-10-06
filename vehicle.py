from simulation_object import SimulationObject
from vector2 import Vector2
from intelligent_driver import IntelligentDriver
from lane import Lane
import events
from typing import List, Tuple
import random
import sys
import logging


class Vehicle(SimulationObject):

    SEED = random.randint(0, sys.maxsize)
    RNG = random.Random(SEED)

    vehicle_logger = logging.getLogger('simulation.vehicle')
    vehicle_logger.info('Seed for vehicles: ' + str(SEED))

    TURN_SIGNAL_NONE = 0
    TURN_SIGNAL_LEFT = 1
    TURN_SIGNAL_RIGHT = 2

    def __init__(self,
                 position: Vector2 = Vector2(0, 0),
                 orientation: float = 90.0,
                 color: Tuple[float, float, float] = (0, 0, 0),
                 mesh: List[Vector2] = (Vector2(1.25, 2), Vector2(-1.25, 2),
                                        Vector2(-1.25, -2), Vector2(1.25, -2)),
                 velocity: float = 0.0,
                 max_velocity: float = 10.0,
                 acceleration: float = 0.0,
                 max_acceleration: float = 1.0):
        super(Vehicle, self).__init__(position, orientation, color, mesh)
        self.__velocity = velocity  # type: float
        self.max_velocity = max_velocity  # type: float
        self.__acceleration = acceleration  # type: float
        self.max_acceleration = max_acceleration  # type: float
        self.__target = None  # type: Vector2
        self.trajectory = []  # type: [Vector2]
        self.active = False
        self.length = self.mesh[0][1] - self.mesh[2][1]  # TODO: length and width specifically for rectangular vehicles!
        self.width = self.mesh[0][0] - self.mesh[1][0]
        self.driver = IntelligentDriver()
        self.turn_signal = Vehicle.TURN_SIGNAL_NONE
        self.events = []
        self.lane = None  # type: Lane
        self.change_permit = False
        self.respawn = True
        self.blocker = None
        self.logger = logging.getLogger('simulation.vehicle.Vehicle')

    def update_events(self, delta_time: float) -> None:
        for event in self.events:
            if event.triggered:
                continue
            event.update(delta_time)

    def update_idm(self):
        self.apply_idm()

    def update_vehicle(self, delta_time: float) -> None:
        self.velocity += delta_time * self.acceleration
        heading = Vector2(0, 1)
        heading.rotate(self.orientation)
        self.position += delta_time * self.velocity * heading
        direction = self.position - self.target
        direction.normalize()
        angle = Vector2(0, 1).distance_angular_signed(direction)
        # check if vehicle passed its target
        if abs(angle - self.orientation) < Lane.EPSILON:
            self.lane.fix_vehicle_position(self)

    def update_lane(self):
        first, second, closest_lane = self.lane.find_closest_segment(self.position)
        if closest_lane is not self.lane:
            self.lane.vehicles.remove(self)
            self.lane = closest_lane
            self.lane.add_vehicle(self)

    def update_mobil(self):
        if self.turn_signal != Vehicle.TURN_SIGNAL_NONE and not self.change_permit:
            return
        value = 0.0
        new_lane = None
        for lane in self.lane.neighboring_lanes:
            change_value = self.apply_mobil(lane)
            if value < change_value < float('infinity'):
                value = change_value
                new_lane = lane
        if value > 0:
            if self.change_permit:
                self.initiate_lane_change(new_lane)
                self.change_permit = False
            else:
                t = Vehicle.RNG.uniform(0.5, 1.5)
                self.turn_signal = Vehicle.TURN_SIGNAL_LEFT if new_lane == self.lane.left_neighbor else Vehicle.TURN_SIGNAL_RIGHT
                change_permit_event = events.ChangePermitEvent(vehicle=self, timer=t)
                self.events.append(change_permit_event)
        elif self.velocity >= self.max_velocity / 2.0:
            # if change is not viable anymore for a moving vehicle, abort change
            self.turn_signal = Vehicle.TURN_SIGNAL_NONE
            self.change_permit = False

    def apply_mobil(self, lane: Lane) -> float:
        """Decide if the given vehicle should change to the given lane.

        MOBIL model is used to decide.

        -------------------------
          back_c   ^    front_c     lane
        -----------|-------------
          back    ego    front
        -------------------------

        :param lane: lane in question
        :return: > 0 if the vehicle should change, <= 0 otherwise
        """
        ego = self
        back = self.lane.find_back_vehicle(ego.position)
        front = self.lane.find_front_vehicle(ego.position)
        back_c = lane.find_back_vehicle(ego.position)
        front_c = lane.find_front_vehicle(ego.position)

        dist_be = self.lane.projected_bumper_distance(back, ego)
        dist_ef = self.lane.projected_bumper_distance(ego, front)
        dist_bf = self.lane.projected_bumper_distance(back, front)
        dist_bce = lane.projected_bumper_distance(back_c, ego)
        dist_efc = lane.projected_bumper_distance(ego, front_c)
        dist_bcfc = lane.projected_bumper_distance(back_c, front_c)

        vel_be = self.lane.approaching_velocity(back, ego)
        vel_ef = self.lane.approaching_velocity(ego, front)
        vel_bf = self.lane.approaching_velocity(back, front)
        vel_bce = self.lane.approaching_velocity(back_c, ego)
        vel_efc = self.lane.approaching_velocity(ego, front_c)
        vel_bcfc = self.lane.approaching_velocity(back_c, front_c)

        acc_b = 0
        acc_b_change = 0
        acc_bc = 0
        acc_bc_change = 0

        acc_e = ego.driver.decide_acceleration(ego, front, dist_ef, vel_ef)
        acc_e_change = ego.driver.decide_acceleration(ego, front_c, dist_efc, vel_efc)
        if back is not None:
            acc_b = back.driver.decide_acceleration(back, ego, dist_be, vel_be)
            acc_b_change = back.driver.decide_acceleration(back, front, dist_bf, vel_bf)
        if back_c is not None:
            acc_bc = back_c.driver.decide_acceleration(back_c, front_c, dist_bcfc, vel_bcfc)
            acc_bc_change = back_c.driver.decide_acceleration(back_c, ego, dist_bce, vel_bce)

        b_safe = self.driver.b_safe
        p = ego.driver.politeness
        thresh = self.driver.thresh

        if self.change_permit:
            # bonus incentive to change lane when turn signal was activated
            b_safe *= 4.0
            p /= 5.0
            thresh = 0.0

        if acc_bc_change < -b_safe:
            return -float("infinity")

        personal_gain = acc_e_change - acc_e
        other_hinder = p * (acc_b + acc_bc - acc_b_change - acc_bc_change)
        thresholds = thresh + lane.lane_change_threshold
        return personal_gain - other_hinder - thresholds

    def apply_idm(self):
        """Let the driver of the given vehicle decide the new acceleration.

        Drivers do not necessarily have to implement IDM.
        """
        front_vehicle = self.lane.find_front_vehicle(self.position)
        bumper_distance = self.lane.projected_bumper_distance(self, front_vehicle)
        approach_vel = self.lane.approaching_velocity(self, front_vehicle)
        idm_acceleration = self.driver.decide_acceleration(self, front_vehicle, bumper_distance, approach_vel)
        if bumper_distance is not None and bumper_distance <= 0:
            self.logger.error('Negative bumper distance occured: %s%s - %s%s distance: %s',
                              self.id, self.position, front_vehicle.id, front_vehicle.position, bumper_distance)
            idm_acceleration = 0
        self.acceleration = idm_acceleration

    def initiate_lane_change(self, lane: Lane) -> None:
        self.change_permit = False
        target = lane.traverse(lane.projected_position(self.position), self.velocity * 0.5 + 10.0)  # TODO: magic number
        if target is None:
            self.turn_signal = Vehicle.TURN_SIGNAL_NONE
            return
        self.target = target
        block_lane_event = events.BlockLaneEvent(vehicle=self, target=self.target)
        self.events.append(block_lane_event)
        self.lane.vehicles.remove(self)
        self.lane = lane
        lane.add_vehicle(self)

    def calculate_trajectory(self, start, end):
        return [end]
        # TODO: needs fixing
        v = end - start
        direction = v.copy()
        direction.normalize()
        distance = v.length()
        angle = start.distance_angular_signed(end)
        angle_sign = angle / abs(angle)
        direction.rotate(angle_sign * -45)
        p0 = start
        p1 = start + direction * distance / 3.0
        direction.rotate(180)
        p2 = end + direction * distance / 3.0
        p3 = end
        return [Vehicle.bezier(0.0, p0, p1, p2, p3),
                Vehicle.bezier(0.2, p0, p1, p2, p3),
                Vehicle.bezier(0.4, p0, p1, p2, p3),
                Vehicle.bezier(0.6, p0, p1, p2, p3),
                Vehicle.bezier(0.8, p0, p1, p2, p3),
                Vehicle.bezier(1.0, p0, p1, p2, p3)]

    @staticmethod
    def bezier(t, p0, p1, p2, p3):
        return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, target):
        self.__target = target
        direction = target - self.position
        direction.normalize()
        angle = Vector2(0, 1).distance_angular_signed(direction)
        self.orientation = angle

    @property
    def velocity(self):
        return self.__velocity

    @velocity.setter
    def velocity(self, velocity):
        self.__velocity = velocity
        if self.__velocity > self.max_velocity:
            self.__velocity = self.max_velocity
        if self.__velocity < 0:
            self.__velocity = 0

    @property
    def acceleration(self):
        return self.__acceleration

    @acceleration.setter
    def acceleration(self, acceleration):
        self.__acceleration = acceleration
        if self.__acceleration > self.max_acceleration:
            self.__acceleration = self.max_acceleration
