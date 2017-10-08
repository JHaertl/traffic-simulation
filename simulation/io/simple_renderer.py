import cv2
import numpy as np
import simulation.config_reader as cr
from simulation.io.camera2d import Camera2D
from simulation.io.input_controller import InputController
from simulation.io.renderer import Renderer
from simulation.vector2 import Vector2
from simulation.layout.world import World


class OpenCVRenderer(Renderer, InputController):

    def __init__(self, camera: Camera2D):
        Renderer.__init__(self)
        InputController.__init__(self)
        self.camera = camera  # type: Camera2D
        self.camera.viewport = Vector2(cr.CONFIG.getint('renderer', 'width'), cr.CONFIG.getint('renderer', 'height'))
        self.camera.zoom = cr.CONFIG.getfloat('renderer', 'zoom')  # type: float
        self.mode = Renderer.MODE_SURFACE  # type: int
        self.background_brightness = 1.0  # type: int
        self.render_image = np.full((self.camera.viewport.y, self.camera.viewport.x, 3),
                                    self.background_brightness, np.float32)  # type: np.ndarray
        self.interactive = True
        cv2.namedWindow('Simulation')
        cv2.setMouseCallback('Simulation', self.mouse_callback)
        self.mouse_drag = False
        self.ix, self.iy = -1, -1
        self.last_position = self.camera.position.copy()

    def render_surfaces(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = Renderer.apply_transform(lane, self.camera)
                cv2.fillPoly(self.render_image, pts=[poly], color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            poly = Renderer.apply_transform(vehicle, self.camera)
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            cv2.fillPoly(self.render_image, pts=[poly], color=color)

    def render_wireframes(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = Renderer.apply_transform(lane, self.camera)
                cv2.polylines(self.render_image, pts=[poly], isClosed=True, color=lane.color)
                for node in poly:
                    cv2.circle(self.render_image, center=(int(node[0]), int(node[1])), radius=3, color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            poly = Renderer.apply_transform(vehicle, self.camera)
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
        display = self.render_image
        camera_pos_string = '(%.2f, %.2f)' % (self.camera.position.x, self.camera.position.y)
        Renderer.draw_text(display, camera_pos_string, self.camera.viewport.x * 0.05, self.camera.viewport.y)
        if self.pause:
            self.draw_text(display, 'P', self.camera.viewport.x * 0.95, self.camera.viewport.y)
        cv2.imshow('Simulation', display)
        cv2.waitKey(1)
        self.render_image.fill(self.background_brightness)

    def mouse_callback(self, event: int, x: int, y: int, flags: int, param: int) -> None:
        window_position = Vector2(x, y)
        world_position = self.camera.apply_inverse_view_transform(window_position)
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print('worldbla(' + str(world_position.x) + ', ' + str(world_position.y) + ')')
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
