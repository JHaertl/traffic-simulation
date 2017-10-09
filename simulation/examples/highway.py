from simulation.layout.world import World
from simulation.layout.road import Road
from simulation.layout.spawner import Spawner
import simulation.agent.vehicle_types as vehicle_types
from simulation.vector2 import Vector2


def create_world():
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

    return world
