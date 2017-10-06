from renderer import Renderer
from input_controller import InputController
from camera2d import Camera2D
from vector2 import Vector2
import numpy as np
import cv2
from data_io import DataIO
from random import Random
import config_reader
from world import World
from simulation_object import SimulationObject
from typing import List, Tuple


class OpenCVRenderer(Renderer, InputController):

    def __init__(self, camera: Camera2D):
        Renderer.__init__(self)
        InputController.__init__(self)
        self.camera = camera  # type: Camera2D
        self.camera.viewport = Vector2(config_reader.CONFIG.getint('renderer', 'width'), config_reader.CONFIG.getint('renderer', 'height'))
        self.camera.zoom = config_reader.CONFIG.getfloat('renderer', 'zoom')  # type: float
        self.mode = Renderer.MODE_SURFACE  # type: int
        self.background_brightness = 1.0  # type: int
        self.render_image = np.full((self.camera.viewport.y, self.camera.viewport.x, 3),
                                    self.background_brightness, np.float32)  # type: np.ndarray
        self.save_data = config_reader.CONFIG.getboolean('renderer', 'save_data')  # type: bool
        self.max_samples = config_reader.CONFIG.getint('renderer', 'max_samples')
        self.writer = DataIO(write=self.save_data)  # type: DataIO
        self.save_delay = config_reader.CONFIG.getfloat('renderer', 'save_delay')  # type: float
        self.timer = 0.0  # type:float
        self.interactive = config_reader.CONFIG.getboolean('renderer', 'interactive')  # type: bool
        self.free_camera = config_reader.CONFIG.getboolean('renderer', 'free_camera')  # type: bool
        if self.interactive:
            cv2.namedWindow('Simulation')
            cv2.setMouseCallback('Simulation', self.mouse_callback)
        self.step = 0  # type: int
        self.rng = Random()
        self.jitter = config_reader.CONFIG.getboolean('renderer', 'jitter')  # type: bool
        self.jitter_size = (20.0, 4.0, 5.0)  # type: (float, float ,float)
        self.locations = [self.camera.position, 0]
        self.mouse_drag = False
        self.ix, self.iy = -1, -1
        self.last_position = self.camera.position.copy()

    def render_surfaces(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = self.apply_transform(lane)
                cv2.fillPoly(self.render_image, pts=[poly], color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            poly = self.apply_transform(vehicle)
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            cv2.fillPoly(self.render_image, pts=[poly], color=color)

    def render_wireframes(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = self.apply_transform(lane)
                cv2.polylines(self.render_image, pts=[poly], isClosed=True, color=lane.color)
                for node in poly:
                    cv2.circle(self.render_image, center=(int(node[0]), int(node[1])), radius=3, color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            poly = self.apply_transform(vehicle)
            cv2.polylines(self.render_image, pts=[poly], isClosed=True, color=color)
            for node in poly:
                cv2.circle(self.render_image, center=(int(node[0]), int(node[1])), radius=3, color=color)

    def render(self, world: World) -> None:
        render_function = {
            Renderer.MODE_SURFACE: self.render_surfaces,
            Renderer.MODE_WIREFRAME: self.render_wireframes,
        }.get(self.mode, self.render_surfaces)
        render_function(world)

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

    def mouse_callback(self, event: int, x: int, y: int, flags: int, param: int) -> None:
        window_position = Vector2(x, y)
        world_position = self.camera.apply_inverse_view_transform(window_position)
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print('world(' + str(world_position.x) + ', ' + str(world_position.y) + ')')
        if event == cv2.EVENT_RBUTTONDOWN:
            self.mouse_drag = True
            self.ix, self.iy = x, y
            self.last_position = self.camera.position.copy()
        elif event == cv2.EVENT_RBUTTONUP:
            self.mouse_drag = False
        elif event == cv2.EVENT_MOUSEMOVE and self.mouse_drag:
            movement = Vector2(x, y) - Vector2(self.ix, self.iy)
            self.camera.position = self.last_position.copy()
            self.camera.position += Vector2(-movement.x, movement.y) / self.camera.zoom

    def handle_input(self) -> None:
        if not self.interactive:
            return
        k = cv2.waitKey(1)
        if k == 27 or k == 1048603:  # wait for ESC key to exit
            self.quit = True
            cv2.destroyAllWindows()
            return
        if k == 119 or k == 1048695:  # W
            self.camera.move(Vector2(0, 10.0) / self.camera.zoom)
        if k == 115 or k == 1048691:  # S
            self.camera.move(Vector2(0.0, -10.0) / self.camera.zoom)
        if k == 100 or k == 1048676:  # D
            self.camera.move(Vector2(10.0, 0.0) / self.camera.zoom)
        if k == 97 or k == 1048673:  # A
            self.camera.move(Vector2(-10.0, 0) / self.camera.zoom)
        if k == 113 or k == 1048689:  # Q
            self.camera.orientation -= 5
        if k == 101 or k == 1048677:  # E
            self.camera.orientation += 5
        if k == 114 or k == 1048690:  # R
            self.camera.zoom *= 1.1
        if k == 102 or k == 1048678:  # F
            self.camera.zoom /= 1.1
        if k == 109 or k == 1048685:  # M
            self.mode = (self.mode + 1) % 2
        if k == 112 or k == 1048688:  # P
            self.pause = not self.pause

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
