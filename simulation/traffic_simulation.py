from datetime import datetime
import simulation.config_reader as cr
import simulation.agent.vehicle_types as vehicle_types
from simulation.io.camera2d import Camera2D
from simulation.io.input_controller import InputController
from simulation.io.simple_renderer import OpenCVRenderer
from simulation.io.renderer import Renderer
from simulation.vector2 import Vector2
from simulation.layout.road import Road
from simulation.layout.spawner import Spawner
from simulation.layout.world import World


class TrafficSimulation:

    def __init__(self):
        self.time_step = cr.CONFIG.getfloat('simulation', 'time_step')
        if self.time_step == 0.0:
            self.time_step = None
        self.camera = Camera2D()  # type: Camera2D
        self.step = 0  # type: int
        self.renderer = OpenCVRenderer(self.camera)  # type: Renderer
        self.input_controller = self.renderer  # type: InputController
        self.renderer.mode = Renderer.MODE_SURFACE  # type: int
        self.world = TrafficSimulation.create_train_world()  # type: World
        self.renderer.locations = self.world.camera_locations  # type: [Vector2]

    def simulate(self):
        delta_time = 0.0
        while not self.input_controller.quit:
            before = datetime.now()
            self.input_controller.handle_input()
            self.camera.update(delta_time)
            if not self.input_controller.pause:
                self.world.update(delta_time)
            self.renderer.update(delta_time)
            self.renderer.render(self.world)
            after = datetime.now()
            delta_time = self.time_step
            if self.time_step is None:
                delta_time = (after - before).total_seconds()
            self.step += 1

    @staticmethod
    def create_world():
        world = World()

        path = [Vector2(-110, -4),
                Vector2(-100, -4),
                Vector2(-50, -4),
                Vector2(50, -4),
                Vector2(100, -4),
                Vector2(110, -4)]

        road = Road(path, 3)

        spawner_main = Spawner(road=road, delay=6.0)
        world.add_road(road)
        world.add_spawner(spawner_main)

        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(20):
            world.add_vehicle(vehicle_types.Truck())
        return world

    @staticmethod
    def create_test01_world():
        world = World()
        spawn = [Vector2(-310.0, 4.0), Vector2(-300.0, 4.0),
                 Vector2(300.0, 4.0), Vector2(310.0, 4.0)]
        road_spawn = Road(spawn, 3)
        world.add_spawner(Spawner(road_spawn))
        world.add_road(road_spawn)
        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(2):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(10):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = [(Vector2(0.0, 8.0), 0.0)]
        return world

    @staticmethod
    def create_test02_world():
        world = World()
        spawn = [Vector2(-310.0, 4.0), Vector2(-300.0, 4.0),
                 Vector2(10.0, 4.0), Vector2(20.0, 4.0)]
        end = [Vector2(20.0, 4.0), Vector2(30.0, 4.0),
                 Vector2(300.0, 4.0), Vector2(310.0, 4.0)]
        road_spawn = Road(spawn, 3)
        road_end = Road(end, 2)
        world.add_spawner(Spawner(road_spawn))
        world.add_road(road_spawn)
        world.add_road(road_end)
        road_spawn.connect(road_end, [(0, 0), (1, 1)])
        obstacle = vehicle_types.Obstacle(road_spawn.lanes[-1].center[-1])
        road_spawn.lanes[-1].add_vehicle(obstacle)
        for i in range(6):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(6):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(16):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = [(Vector2(-50.0, 8.0), 0.0)]
        return world

    @staticmethod
    def create_test03_world():
        world = World()
        spawn = [Vector2(-310.0, -2.0), Vector2(-300.0, 0.0),
                 Vector2(10.0, 2.0), Vector2(20.0, 4.0)]
        side = [Vector2(-169.838190331, 100.0847745615),
                Vector2(-169.838190331, 95.0847745615),
                Vector2(-169.838190331, 62.1064851769),
                Vector2(-143.455558823, 40.6705970769),
                Vector2(-110.477269438, 25.8303668538),
                Vector2(-77.4989800538, 19.5857945077),
                Vector2(-37.9250327923, 13.6390511),
                Vector2(-6.59565787692, 12.6390511),
                Vector2(-2.59565787692, 12.6390511)]
        end = [Vector2(20.0, 4.0), Vector2(30.0, 4.0),
               Vector2(120.0, 8.0),
               Vector2(300.0, 4.0), Vector2(310.0, 4.0)]
        road_spawn = Road(spawn, 2)
        road_side = Road(side, 1)
        road_end = Road(end, 3)
        world.add_spawner(Spawner(road_spawn))
        world.add_spawner(Spawner(road_side))
        world.add_road(road_spawn)
        world.add_road(road_side)
        world.add_road(road_end)
        road_spawn.connect(road_end, [(0, 0), (1, 1)])
        road_side.connect(road_end, [(0, 2)])
        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(2):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(10):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = [(Vector2(40.0, 8.0), 0.0)]
        return world

    @staticmethod
    def create_test04_world():
        world = World()
        spawn = [Vector2(-310.0, 4.0), Vector2(-300.0, 4.0),
                 Vector2(5.0, 4.0), Vector2(20.0, 4.0)]
        middle = [Vector2(5.0, 4.0), Vector2(10.0, 4.0),
                Vector2(20.0, 4.0), Vector2(30.0, 4.0)]
        end = [Vector2(20.0, 4.0), Vector2(30.0, 4.0),
               Vector2(120.0, 4.0),
               Vector2(300.0, 4.0), Vector2(310.0, 4.0)]
        road_spawn = Road(spawn, 3)
        road_middle = Road(middle, 2)
        road_end = Road(end, 3)
        world.add_spawner(Spawner(road_spawn))
        world.add_road(road_spawn)
        world.add_road(road_middle)
        world.add_road(road_end)
        road_spawn.connect(road_middle, [(0, 0), (1, 1)])
        road_middle.connect(road_end, [(0, 0), (1, 1)])
        obstacle = vehicle_types.Obstacle(road_spawn.lanes[-1].center[-1])
        road_spawn.lanes[-1].add_vehicle(obstacle)
        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(2):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(10):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = [(Vector2(20.0, 8.0), 0.0)]
        return world

    @staticmethod
    def create_test05_world():
        world = World()
        spawn = [Vector2(-310.0, 4.0), Vector2(-300.0, 4.0),
                 Vector2(-98.4615384615, 1.53846153846),
                 Vector2(-88.4615384615, -3.07692307692),
                 Vector2(-82.8321159917, -5.07410700446),
                 Vector2(-78.1447192208, -6.41336322471),
                 Vector2(-72.9551013674, -7.25039836236),
                 Vector2(-68.2677045965, -7.41780538989),
                 Vector2(-62.9106797155, -6.58077025224),
                 Vector2(-58.8929110548, -5.07410700446),
                 Vector2(-53.2010721187, -4.06966483928),
                 Vector2(-49.0158964304, -2.22818753644),
                 Vector2(-44.3284996596, -0.888931316189),
                 Vector2(-38.8040677511, 1.11995301418),
                 Vector2(-35.7907412555, 1.95698815184),
                 Vector2(-32.9448217875, 2.2918022069),
                 Vector2(-29.7323132792, 2.43621605914),
                 Vector2(-27.8423752242, 2.09259095824),
                 Vector2(-25.3846153846, 1.77692307692),
                 Vector2(-21.3950437514, -0.859062752263),
                 Vector2(-19.5904520955, -2.12992446608),
                 Vector2(-17.4373411099, -3.35959094445),
                 Vector2(-15.2842301243, -5.00073911352),
                 Vector2(-11.3368599841, -6.79499826818),
                 Vector2(-8.1071935057, -7.87155376097),
                 Vector2(5.38461538462, -6.92307692308),
                 Vector2(15.3846153846, -4.84615384615),
                 Vector2(20.7692307692, -3.61538461538),
                 Vector2(24.507939196, -3.10160561569),
                 Vector2(28.7841317207, -2.88657039171),
                 Vector2(34.0507568068, -3.08913289502),
                 Vector2(38.4615384615, -3.53846153846),
                 Vector2(42.9568475184, -5.85216657396),
                 Vector2(46.9230769231, -6.92307692308),
                 Vector2(58.4615384615, -5.38461538462),
                 Vector2(70.7692307692, 0.0),
                 Vector2(80.0, 0.84615384615),
                 Vector2(90.7692307692, 0.30769230769),
                 Vector2(96.1538461538, -1.53846153846),
                 Vector2(300.0, 4.0), Vector2(310.0, 4.0)]
        road_spawn = Road(spawn, 3)
        world.add_spawner(Spawner(road_spawn))
        world.add_road(road_spawn)
        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(2):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(10):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = [(Vector2(0.0, 1.0), 0.0)]
        return world

    @staticmethod
    def create_validation_world():
        world = World()
        spawn = [Vector2(200.0, -54.0), Vector2(190.0, -54.0),
                 Vector2(150.0, -54.0), Vector2(110.0, -54.0),
                 Vector2(94.0, -54.0)]
        path0 = [Vector2(127.692307692, -62.0769230769),
                 Vector2(94.6153846154, -54.3846153846),
                 Vector2(59.2307692308, -45.9230769231),
                 Vector2(18.4615384615, -46.6923076923),
                 Vector2(-30.0, -59.0)]
        path1 = [Vector2(-30.0, -59.0),
               Vector2(-66.9230769231, -56.6923076923),
               Vector2(-114.615384615, -58.2307692308),
               Vector2(-154.615384615, -63.6153846154),
               Vector2(-193.076923077, -76.6923076923),
               Vector2(-234.615384615, -76.6923076923)]
        end = [Vector2(-234.0, -76.0), Vector2(-250.0, -76.0),
               Vector2(-300.0, -76.0), Vector2(-350.0, -76.0),
               Vector2(-360.0, -76.0)]
        road_spawn = Road(spawn, 3)
        road_path0 = Road(path0, 3)
        road_path1 = Road(path1, 3)
        road_end = Road(end, 3)
        road_spawn.connect(road_path0, [(0, 0), (1, 1), (2, 2)])
        road_path0.connect(road_path1, [(0, 0), (1, 1), (2, 2)])
        road_path1.connect(road_end, [(0, 0), (1, 1), (2, 2)])
        #obstacle = vehicle_types.Obstacle(road_path0.lanes[-1].center[-1])
        #road_path0.lanes[-1].add_vehicle(obstacle)
        world.add_spawner(Spawner(road_spawn))
        world.add_road(road_spawn)
        world.add_road(road_path0)
        world.add_road(road_path1)
        world.add_road(road_end)
        for i in range(4):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(2):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(10):
            world.add_vehicle(vehicle_types.Minivan())
        world.camera_locations = TrafficSimulation.locations_from_road(path0, 0, len(path0))
        world.camera_locations += TrafficSimulation.locations_from_road(path1, 0, len(path1))
        return world

    @staticmethod
    def create_train_world():
        world = World()

        spawn = [Vector2(-500.0, -23.0), Vector2(-490.0, -23.0), Vector2(-360.0, -23.0), Vector2(-350.0, -23.0)]
        road_spawn = Road(spawn, 3)

        path0 = [Vector2(-330.218669385, -23.8417247666), Vector2(-325.218669385, -23.8417247666),
                 Vector2(-270.218669385, -23.8417247666), Vector2(-260.218669385, -23.8417247666),
                 Vector2(-233.948921101, -25.4179096636), Vector2(-214.509307372, -29.0956744232),
                 Vector2(-194.018903711, -28.0448844919), Vector2(-178.782449707, -22.2655398696),
                 Vector2(-160.919020874, -12.8084304876), Vector2(-144.106381973, -8.07987579663),
                 Vector2(-126.24295314, -4.92750600264), Vector2(-112.582684033, -3.35132110564),
                 Vector2(-94.1938602344, -2.30053117431), Vector2(-90, -2),
                 Vector2(-50, -2), Vector2(-30, -2)]
        road_path0 = Road(path0, 3)

        path1 = [Vector2(70, -2), Vector2(90, -2),
                 Vector2(101.538461538, -2.69230769231), Vector2(113.846153846, -5.76923076923),
                 Vector2(126.923076923, -13.4615384615), Vector2(139.230769231, -24.2307692308),
                 Vector2(144.757330429, -38.0015384615), Vector2(148.852715044, -52.3353846154),
                 Vector2(145.781176583, -66.6692307692), Vector2(132.471176583, -78.9553846154),
                 Vector2(111.994253506, -86.1223076923), Vector2(81.2788688905, -87.1461538462),
                 Vector2(58.7542535059, -88.17)]
        road_path1 = Road(path1, 2)

        path2 = [Vector2(81.2788688905, -87.1461538462), Vector2(58.7542535059, -88.17),
                 Vector2(42.3076923077, -90.6923076923), Vector2(26.1538461538, -95.3076923077),
                 Vector2(12.3076923077, -103.0), Vector2(-3.07692307692, -109.153846154),
                 Vector2(-20.7692307692, -111.461538462), Vector2(-46.1538461538, -111.461538462),
                 Vector2(-73.0769230769, -111.461538462), Vector2(-101.538461538, -114.538461538),
                 Vector2(-122.307692308, -111.461538462), Vector2(-150.0, -110.692307692)]
        road_path2 = Road(path2, 3)

        side = [Vector2(199.230769231, -170.538461538), Vector2(196.153846154, -153.615384615),
                Vector2(190.769230769, -142.846153846), Vector2(182.307692308, -132.076923077),
                Vector2(170.0, -121.307692308), Vector2(157.692307692, -113.615384615),
                Vector2(143.846153846, -105.923076923), Vector2(130.0, -100.538461538),
                Vector2(113.076923077, -97.4615384615), Vector2(90.7692307692, -96.6923076923),
                Vector2(70.3760010455, -95.8844097781)]
        road_side = Road(side, 1)

        end = [Vector2(-150.0, -110.0), Vector2(-160.0, -110.0), Vector2(-200.0, -110.0), Vector2(-300.0, -110.0),
               Vector2(-310.0, -110.0)]
        road_end = Road(end, 3)

        obstacle = vehicle_types.Obstacle(road_path0.lanes[-1].center[-1])
        road_path0.lanes[-1].add_vehicle(obstacle)

        road_spawn.connect(road_path0, [(0, 0), (1, 1), (2, 2)])
        road_path0.connect(road_path1, [(0, 0), (1, 1)])
        road_path1.connect(road_path2, [(0, 0), (1, 1)])
        road_side.connect(road_path2, [(0, 2)])
        road_path2.connect(road_end, [(0, 0), (1, 1), (2, 2)])

        world.add_road(road_spawn)
        world.add_road(road_path0)
        world.add_road(road_path1)
        world.add_road(road_path2)
        world.add_road(road_side)
        world.add_road(road_end)
        world.add_spawner(Spawner(road_spawn))
        world.add_spawner(Spawner(road_side))

        for i in range(12):
            world.add_vehicle(vehicle_types.Sportscar())
        for i in range(6):
            world.add_vehicle(vehicle_types.Truck())
        for i in range(32):
            world.add_vehicle(vehicle_types.Minivan())

        world.camera_locations = TrafficSimulation.locations_from_road(path0, 0, len(path0))
        world.camera_locations += TrafficSimulation.locations_from_road(path1, 0, 5)
        world.camera_locations += TrafficSimulation.locations_from_road(path2, 0, len(path2))

        return world

    @staticmethod
    def locations_from_road(path, start, end):
        locations = []
        for i, vector in enumerate(path[start:end]):
            if i == start or i == end-1:
                continue
            normal = Road.calc_road_normal(path[i-1], path[i], path[i+1])
            angle = Vector2(0, 1).distance_angular_signed(normal)
            locations.append((vector, angle))
        return locations

    @staticmethod
    def place_test_vehicle(world, road, lane, node):
        v1 = vehicle_types.Minivan()
        v1.max_velocity = 0.0001
        v1.velocity = 5.0
        v1.position = road.lanes[lane].center[node].copy()
        v1.target = road.lanes[lane].find_next_node(v1.position)
        v1.active = True
        road.lanes[lane].add_vehicle(v1)
        world.add_vehicle(v1)
        return v1
