import abc

from simulation.agent import vehicle_types


class Event:
    __metaclass__ = abc.ABCMeta

    def __init__(self, timer=None, trigger=None):
        self.timer = timer
        self.trigger = trigger
        self.triggered = False

    def update(self, delta_time):
        if self.triggered:
            return
        if self.timer is not None:
            self.timer -= delta_time
            if self.timer <= 0.0:
                self.process()
                self.triggered = True
        if self.trigger is not None and self.trigger.triggered:
            self.process()
            self.triggered = True

    @abc.abstractmethod
    def process(self):
        pass


class TurnSignalEvent(Event):

    def __init__(self, vehicle, value, timer=None, trigger=None):
        super(TurnSignalEvent, self).__init__(timer=timer, trigger=trigger)
        self.vehicle = vehicle
        self.value = value

    def process(self):
        self.vehicle.turn_signal = self.value
        self.vehicle.events.remove(self)


class ChangePermitEvent(Event):

    def __init__(self, vehicle, timer=None, trigger=None):
        super(ChangePermitEvent, self).__init__(timer=timer, trigger=trigger)
        self.vehicle = vehicle

    def process(self):
        self.vehicle.change_permit = True
        self.vehicle.events.remove(self)


class BlockLaneEvent(Event):

    def __init__(self, vehicle, target):
        super(BlockLaneEvent, self).__init__(timer=None, trigger=None)
        self.vehicle = vehicle
        self.target = target
        self.blocker = vehicle_types.Volatile(vehicle)

    def update(self, delta_time):
        if self.triggered:
            return
        self.blocker.update_idm()
        self.blocker.update_vehicle(delta_time)
        if not self.blocker.active:  # blocker may have finished and removed from lane after update
            self.process()
            self.triggered = True
            return
        self.blocker.update_lane()
        if self.target != self.vehicle.target:
            self.process()
            self.triggered = True

    def process(self):
        self.vehicle.turn_signal = 0  # no access to Vehicle.TURN_SIGNAL_NONE
        self.blocker.vanish()
