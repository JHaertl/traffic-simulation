from random import Random
import numpy as np
import simulation.config_reader as cr
from simulation.io.camera2d import Camera2D
from simulation.io.data_io import DataIO
from simulation.io.renderer import Renderer
from simulation.vector2 import Vector2
from simulation.layout.world import World


class RandomSampleRenderer(Renderer):

    def __init__(self, camera: Camera2D):
        super(RandomSampleRenderer, self).__init__(camera)
        self.background_brightness = 0.0
        self.save_data = cr.CONFIG.getboolean('renderer', 'save_data')  # type: bool
        self.max_samples = cr.CONFIG.getint('renderer', 'max_samples')
        self.writer = DataIO(write=self.save_data)  # type: DataIO
        self.save_delay = cr.CONFIG.getfloat('renderer', 'save_delay')  # type: float
        self.timer = 0.0  # type:float
        self.render_image = np.full((self.camera.viewport.y, self.camera.viewport.x, 3),
                                    self.background_brightness, np.float32)  # type: np.ndarray
        self.step = 0  # type: int
        self.rng = Random()
        self.jitter = cr.CONFIG.getboolean('renderer', 'jitter')  # type: bool
        self.jitter_size = (20.0, 4.0, 5.0)  # type: (float, float ,float)
        self.locations = [self.camera.position, 0]

    def render(self, world: World) -> None:
        pass

    def update(self, delta_time: float) -> None:
        self.timer += delta_time
        if self.timer >= self.save_delay:
            self.save_image()
            self.timer = 0.0
            self.step += 1
            if not self.free_camera:
                self.move_camera()
        self.render_image.fill(self.background_brightness)

    def save_image(self) -> None:
        pass

    def move_camera(self) -> None:
        if self.step % self.writer.write_sample_size == 0:
            location = self.rng.randint(0, len(self.locations) - 1)
            self.camera.position = self.locations[location][0].copy()
            self.camera.orientation = self.locations[location][1]
            if self.jitter:
                r = self.rng.uniform(-self.jitter_size[2], self.jitter_size[2])
                f = self.rng.randint(0, 1)
                s = self.rng.uniform(-self.jitter_size[1], self.jitter_size[1])
                t = self.rng.uniform(-self.jitter_size[0], self.jitter_size[0])
                self.camera.position += Vector2(t, 1 + s)
                self.camera.orientation += r + f * 180.0
