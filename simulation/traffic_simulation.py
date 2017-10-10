from datetime import datetime
import simulation.config_reader as cr
from simulation.io.camera2d import Camera2D
from simulation.io.input_controller import InputController
from simulation.io.simple_renderer import SimpleRenderer
from simulation.io.renderer import Renderer
from simulation.vector2 import Vector2
from simulation.layout.world import World


class TrafficSimulation:

    def __init__(self, world: World):
        self.time_step = cr.CONFIG.getfloat('simulation', 'time_step')
        if self.time_step == 0.0:
            self.time_step = None
        self.camera = Camera2D()  # type: Camera2D
        self.step = 0  # type: int
        self.renderer = SimpleRenderer(self.camera)  # type: Renderer
        self.input_controller = self.renderer  # type: InputController
        self.world = world  # type: World
        self.renderer.locations = self.world.camera_locations  # type: [Vector2]

    def simulate(self):
        delta_time = 0.0
        while not self.input_controller.quit:
            before = datetime.now()
            self.input_controller.handle_input()
            if not self.input_controller.pause:
                self.world.update(delta_time)
            self.renderer.update(delta_time)
            self.renderer.render(self.world)
            after = datetime.now()
            delta_time = self.time_step
            if self.time_step is None:
                delta_time = (after - before).total_seconds()
            self.step += 1
