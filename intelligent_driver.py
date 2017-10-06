import math
from driver import Driver


class IntelligentDriver(Driver):

    def __init__(self, min_spacing = 12.0, time_headway = 1.0, comf_break = 3.0, delta = 4,
                 politeness=0.5, b_safe=3.0, thresh=0.4):
        super(IntelligentDriver, self).__init__(politeness, b_safe, thresh)
        # IDM parameters (v_0 and a_max are implemented as vehicle parameters)
        self.min_spacing = min_spacing
        self.time_headway = time_headway
        self.comf_break = comf_break
        self.delta = delta

    def decide_acceleration(self, ego, front, bumper_distance, v_delta):
        if front is None:
            return ego.max_acceleration
        if bumper_distance <= 0:
            return -float('inf')

        s_star = self.min_spacing + ego.velocity * self.time_headway + (ego.velocity * v_delta / (2 * math.sqrt(ego.max_acceleration * self.comf_break)))
        acceleration = ego.max_acceleration * (1 - (ego.velocity / ego.max_velocity)**self.delta - (s_star / bumper_distance)**2)

        return acceleration
