from simulation.agent.driver import Driver
from simulation.simulation_object import SimulationObject


class DummyDriver(Driver):

    def decide_acceleration(self, ego: SimulationObject, front: SimulationObject,
                            bumper_distance: float, v_delta: float):
        return 0
