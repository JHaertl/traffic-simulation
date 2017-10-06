# traffic-simulation

Agent-based, space continuous, time discrete traffic simulation.
Driver decisions based on [IDM][1] and [MOBIL][2] models.

## Getting Started

The [config](config.ini) file is used to configure the simulation environment.

### Requirements

Python 3.x
Numpy and OpenCV (only for rendering)

### Running the simulation

Simply execute run_simulation.py
```
python run_simulation.py
```

## Creating custom road layouts

### Road

A road is defined by a list of vectors and the amount of lanes to create. The given list is used
as the center line of the right-most lane of the road. The first and last vector in the list are
used to specify the orientation of the road endings. A road is therefore defined by at least 4 vectors.

### Connections

Roads can be connected by declaring a connection between individual lanes. The road segments
are automatically combined, they do not need to be spatially connected prior to creating the connection.
To create smooth transitions the connection may change the orientation of the connected road endings.

### Vehicles

Custom vehicle types with custom drivers can be declared in 'vehicle_types.py'. Any number
of these vehicles can be added to the world.

### Spawner

A spawner can be placed anywhere on a road. By default the very beginning of the road is chosen.
All spawners share the same pool of vehicles.

### Examples

In 'traffic_simulation.py' various functions are declared to create different worlds.
To replace the current world with any other world simply save it in the 'world' instance variable
in the init method of 'TrafficSimulation'. These example worlds depict more complex scenarios
and show e.g. how 'Obstacles' are used to create road narrowings.
```
self.world = TrafficSimulation.create_test01_world()
```
Currently road layouts containing cycles are not supported.

## Author

**Jonathan Härtl**

[1]:https://arxiv.org/abs/cond-mat/0002177
[2]:http://www.mtreiber.de/publications/MOBIL_TRB.pdf
