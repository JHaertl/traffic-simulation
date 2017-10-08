# Documentation

## Interactive controls

WASD or drag with right mouse button to move camera  
Q/E for left and right rotation  
F/R for zoom in and zoom out  
P un-/pause simulation  
M change render mode  
ESC quit

## Creating custom simulation worlds

### Roads

A road is defined by a list of vectors and the amount of lanes to create. The given list is used
as the center line of the right-most lane of the road. The first and last vector in the list are
used to specify the orientation of the road endings. A road is therefore defined by at least 4 vectors.
Driving direction is fixed according to the order of vectors.

<p align="center"><img src="./images/road_setup.svg"></p>

### Connections

Roads can be connected by declaring a connection between individual lanes. The road segments
are automatically combined, they do not need to be spatially connected prior to creating the connection.
To create smooth transitions the connection may change the orientation of the connected road endings.

### Vehicles

Custom vehicle types with custom drivers can be declared in 'vehicle_types.py'. Any number
of these vehicles can be added to the world. Check **Employed traffic models** for an explanation of the
driver parameters.

### Spawners

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

___

## Employed traffic models

### IDM

Car-following model. Acceleration of each agent solely depends on the agent's state and the
state of the most relevant target in front (MRTF).

|  IDM Parameter  | Description                                                             |
|-----------------|-------------------------------------------------------------------------|
|   v_0           | Desired velocity on free road                                           |
|   a_max         | Maximum acceleration                                                    |
|   min_spacing   | Minimum desired distance to front vehicle                               |
|   time_headway  | Minimum desired time headway to front vehicle                           |
|   comf_break    | Comfortable breaking deceleration                                       |
|   delta         | Steepness of asymptotic approach to max velocity on free road           |

### MOBIL

Enhances IDM with lane changing capability. MRTF and MRTB on the current and target lane are 
considered for lane change decisions.

| MOBIL Parameter | Description                                                             |
|-----------------|-------------------------------------------------------------------------|
|   p             | Politeness factor to weigh personal gain against disadvantage of others |
|   b_safe        | Maximum safe breaking deceleration to impose on back vehicle            |
|   a_thr         | Threshold to prevent lane changes with little to no gain                |

### Custom

Using only MOBIL vehicles would instantly perform any lane change decisions.
Support for delayed lane changes with turn signals was added.
Turn signals add more complexity and represent another valuable input feature for deep learning applications.
