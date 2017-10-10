import cv2
import numpy as np
from simulation.io.camera2d import Camera2D
from simulation.io.input_controller import InputController
from simulation.io.renderer import Renderer
from simulation.vector2 import Vector2
from simulation.layout.world import World


class SimpleRenderer(Renderer, InputController):

    def __init__(self, camera: Camera2D):
        Renderer.__init__(self, camera)
        InputController.__init__(self)
        if self.interactive:
            cv2.namedWindow('Simulation')
            cv2.setMouseCallback('Simulation', self.mouse_callback)
        self.mouse_drag = False
        self.ix, self.iy = -1, -1
        self.last_position = self.camera.position.copy()
        self.render_image = np.full((self.camera.viewport.y, self.camera.viewport.x, 3),
                                    self.background_brightness, np.float32)  # type: np.ndarray

    def render_surfaces(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = self.camera.apply_transform(lane)
                cv2.fillPoly(self.render_image, pts=[poly], color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            poly = self.camera.apply_transform(vehicle)
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            cv2.fillPoly(self.render_image, pts=[poly], color=color)

    def render_wireframes(self, world: World) -> None:
        for road in world.roads:
            for lane in road.lanes:
                poly = self.camera.apply_transform(lane)
                cv2.polylines(self.render_image, pts=[poly], isClosed=True, color=lane.color)
                for node in poly:
                    cv2.circle(self.render_image, center=(int(node[0]), int(node[1])), radius=3, color=lane.color)
        for vehicle in world.vehicles:
            if not vehicle.active:
                continue
            color = vehicle.color
            if vehicle.TURN_SIGNAL_NONE != vehicle.turn_signal:
                color = [0, 0.7, 1.0]
            poly = self.camera.apply_transform(vehicle)
            cv2.polylines(self.render_image, pts=[poly], isClosed=True, color=color)
            for node in poly:
                cv2.circle(self.render_image, center=(int(node[0]), int(node[1])), radius=3, color=color)

    def render(self, world: World) -> None:
        render_function = {
            Renderer.Mode.SURFACE: self.render_surfaces,
            Renderer.Mode.WIREFRAME: self.render_wireframes,
        }.get(self.mode, self.render_surfaces)
        render_function(world)
        camera_pos_string = '(%.2f, %.2f)' % (self.camera.position.x, self.camera.position.y)
        SimpleRenderer.draw_text(self.render_image, camera_pos_string, self.camera.viewport.x * 0.05, self.camera.viewport.y)
        if self.pause:
            SimpleRenderer.draw_text(self.render_image, 'P', self.camera.viewport.x * 0.95, self.camera.viewport.y)
        cv2.imshow('Simulation', self.render_image)
        cv2.waitKey(1)
        self.render_image.fill(self.background_brightness)

    def mouse_callback(self, event: int, x: int, y: int, flags: int, param: int) -> None:
        window_position = Vector2(x, y)
        world_position = self.camera.apply_inverse_view_transform(window_position)
        if event == cv2.EVENT_LBUTTONDBLCLK:
            print('(' + str(world_position.x) + ', ' + str(world_position.y) + ')')
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
            self.mode = Renderer.Mode((self.mode.value + 1) % len(Renderer.Mode))
        if k == 112 or k == 1048688:  # P
            self.pause = not self.pause

    @staticmethod
    def draw_text(image: np.ndarray, text: str, x: float, y: float) -> None:
        cv2.putText(image, text, (int(x), int(y)), cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA)
