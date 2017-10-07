from simulation.agent.driver import Driver


class DummyDriver(Driver):

    def decide_acceleration(self, ego, front, bumper_distance, v_delta):
        return 0
