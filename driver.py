import abc


class Driver:
    __metaclass__ = abc.ABCMeta

    def __init__(self, politeness=0.5, b_safe=3.0, thresh=0.4):
        # MOBIL parameters
        self.politeness = politeness
        self.b_safe = b_safe
        self.thresh = thresh

    @abc.abstractmethod
    def decide_acceleration(self, ego, front, bumper_distance, v_delta):
        return
