from vehicle import Vehicle
from vector2 import Vector2
from dummy_driver import DummyDriver
from intelligent_driver import IntelligentDriver


class Truck(Vehicle):

    def __init__(self):
        super(Truck, self).__init__(mesh=[Vector2(1.25, 6.0), Vector2(-1.25, 6.0),
                                          Vector2(-1.25, -6.0), Vector2(1.25, -6.0)],
                                    max_velocity=22,
                                    max_acceleration=2.0)
        self.driver = IntelligentDriver(min_spacing=14.0, time_headway=1.5, comf_break=2.5, politeness=0.5, b_safe=2.5)


class Minivan(Vehicle):

    def __init__(self):
        super(Minivan, self).__init__(mesh=[Vector2(1.0, 2.5), Vector2(-1.0, 2.5),
                                            Vector2(-1.0, -2.5), Vector2(1.0, -2.5)],
                                      max_velocity=30,
                                      max_acceleration=3.5)
        self.driver = IntelligentDriver(min_spacing=10.0, time_headway=1.0, comf_break=3.0, politeness=0.4, b_safe=3.0)


class Sportscar(Vehicle):

    def __init__(self):
        super(Sportscar, self).__init__(mesh=[Vector2(0.7, 2.0), Vector2(-0.7, 2.0),
                                              Vector2(-0.7, -2.0), Vector2(0.7, -2.0)],
                                        max_velocity=42,
                                        max_acceleration=6.0)
        self.driver = IntelligentDriver(min_spacing=6.0, time_headway=0.75, comf_break=4.0, politeness=0.3, b_safe=3.5)


class Obstacle(Vehicle):

    def __init__(self, position = Vector2(0, 0)):
        super(Obstacle, self).__init__(position,
                                       orientation=90,
                                       color=(0, 0, 0),
                                       mesh=[Vector2(0.5, 0.5), Vector2(-0.5, 0.5),
                                             Vector2(-0.5, -0.5), Vector2(0.5, -0.5)],
                                       velocity=0,
                                       max_velocity=0,
                                       acceleration=0,
                                       max_acceleration=0)
        self.driver = DummyDriver()

    def update_idm(self):
        pass

    def update_vehicle(self, delta_time):
        pass

    def update_lane(self):
        pass

    def update_mobil(self):
        pass


class Volatile(Vehicle):

    def __init__(self, vehicle: Vehicle):
        super(Volatile, self).__init__(position=vehicle.position,
                                       velocity=vehicle.velocity,
                                       max_velocity=vehicle.max_velocity,
                                       acceleration=vehicle.acceleration,
                                       max_acceleration=vehicle.max_acceleration,
                                       mesh=vehicle.mesh)
        self.vehicle = vehicle
        self.lane = vehicle.lane
        self.lane.add_vehicle(self)
        self.target = vehicle.target
        self.active = True
        self.respawn = False

    def update_vehicle(self, delta_time: float) -> None:
        if not self.active:
            return
        self.acceleration = min(self.acceleration, self.vehicle.acceleration)
        super(Volatile, self).update_vehicle(delta_time)

    def update_mobil(self) -> None:
        pass

    def vanish(self) -> None:
        self.active = False
        if self.lane is not None and self in self.lane.vehicles:
            self.lane.vehicles.remove(self)
        self.lane = None
