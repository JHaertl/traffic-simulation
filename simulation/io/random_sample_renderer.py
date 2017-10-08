from random import Random
from typing import List, Tuple

import cv2
import numpy as np

import simulation.config_reader as cr
from simulation.io.camera2d import Camera2D
from simulation.io.data_io import DataIO
from simulation.io.renderer import Renderer
from simulation.simulation_object import SimulationObject
from simulation.vector2 import Vector2
from simulation.layout.world import World


class RandomSampleRenderer(Renderer):

    def __init__(self, camera: Camera2D):
        super(RandomSampleRenderer, self).__init__()
        self.camera = camera  # type: Camera2D
        self.camera.viewport = Vector2(cr.CONFIG.getint('renderer', 'width'), cr.CONFIG.getint('renderer', 'height'))
        self.camera.zoom = cr.CONFIG.getfloat('renderer', 'zoom')  # type: float
        self.mode = Renderer.MODE_SURFACE  # type: int
        self.background_brightness = 0.0  # type: int
        self.render_image = np.full((self.camera.viewport.y, self.camera.viewport.x, 3),
                                    self.background_brightness, np.float32)  # type: np.ndarray
        self.save_data = cr.CONFIG.getboolean('renderer', 'save_data')  # type: bool
        self.max_samples = cr.CONFIG.getint('renderer', 'max_samples')
        self.writer = DataIO(write=self.save_data)  # type: DataIO
        self.save_delay = cr.CONFIG.getfloat('renderer', 'save_delay')  # type: float
        self.timer = 0.0  # type:float
        self.interactive = cr.CONFIG.getboolean('renderer', 'interactive')  # type: bool
        self.free_camera = cr.CONFIG.getboolean('renderer', 'free_camera')  # type: bool
        if self.interactive:
            cv2.namedWindow('Simulation')
            cv2.setMouseCallback('Simulation', self.mouse_callback)
        self.step = 0  # type: int
        self.rng = Random()
        self.jitter = cr.CONFIG.getboolean('renderer', 'jitter')  # type: bool
        self.jitter_size = (20.0, 4.0, 5.0)  # type: (float, float ,float)
        self.locations = [self.camera.position, 0]

    def render(self, world: World) -> None:
        pass

    def update(self, delta_time: float) -> None:
        if self.interactive:
            display = self.render_image
            camera_pos_string = '(%.2f, %.2f)' % (self.camera.position.x, self.camera.position.y)
            cv2.putText(display, camera_pos_string, (int(self.camera.viewport.x * 0.05), self.camera.viewport.y),
                        cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA)
            if self.pause:
                cv2.putText(display, 'P', (int(self.camera.viewport.x * 0.95), self.camera.viewport.y),
                            cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA)
            cv2.imshow('Simulation', display)
            cv2.waitKey(1)
        self.timer += delta_time
        if self.timer >= self.save_delay:
            self.save_image()
            self.timer = 0.0
            self.step += 1
            if not self.free_camera:
                self.move_camera()
        self.render_image.fill(self.background_brightness)

    def save_image(self) -> None:
        if not self.save_data:
            return
        image = np.concatenate((self.road_image, self.vehicle_image), axis=2)
        self.writer.add_data(image)
        if self.writer.counter >= self.max_samples:
            self.quit = True

    def move_camera(self) -> None:
        if self.step % self.writer.write_sample_size == 0:
            l = self.rng.randint(0, len(self.locations) - 1)
            self.camera.position = self.locations[l][0].copy()
            self.camera.orientation = self.locations[l][1]
            if self.jitter:
                r = self.rng.uniform(-self.jitter_size[2], self.jitter_size[2])
                f = self.rng.randint(0, 1)
                s = self.rng.uniform(-self.jitter_size[1], self.jitter_size[1])
                t = self.rng.uniform(-self.jitter_size[0], self.jitter_size[0])
                self.camera.position += Vector2(t, 1 + s)
                self.camera.orientation += r + f * 180.0

    def apply_transform(self, obj: SimulationObject) -> np.ndarray:
        temp = []
        for vertex in obj.mesh:
            temp.append(self.camera.apply_view_transform(obj.apply_world_transform(vertex)))
        poly = self.numpy_from_list(temp)
        return poly

    def numpy_from_list(self, poly: List[Vector2]) -> np.ndarray:
        points = []
        for node in poly:
            points.append([node.x, node.y])
        return np.array(points, np.int32)

    def tuple_from_vector(self, vector: Vector2) -> Tuple[int, int]:
        return int(vector.x), int(vector.y)
