from simulation.simulation_object import SimulationObject
from simulation.vector2 import Vector2

from simulation.layout.spawner import Spawner


class Lane(SimulationObject):

    EPSILON = 0.001

    next_node_hash = {}

    def __init__(self, road):
        super(Lane, self).__init__(position=Vector2(0, 0),
                                   orientation=0,
                                   color=(0.5, 0.5, 0.5),
                                   mesh=[])
        self.road = road  # type: Road
        self.left = []  # type: [Vector2]
        self.center = []  # type: [Vector2]
        self.right = []  # type: [Vector2]
        self.accumulated_distance = []  # type: [Vector2]
        self.vehicles = []  # type: [Vehicle]
        self.neighboring_lanes = []  # type: [Lane]
        self.left_neighbor = None  # type: Lane
        self.right_neighbor = None  # type: Lane
        self.back_connection = None  # type: Lane
        self.front_connection = None  # type: Lane
        self.lane_change_threshold = 0.0
        self.closest_node_hash = {}
        self.closest_segment_hash = {}

    def reset_hashes(self):
        self.closest_node_hash = {}
        self.closest_segment_hash = {}

    def find_back_vehicle(self, position):
        _, lane = self.find_closest_node(position)
        travel_dist = lane.projected_travelled_distance(position)
        while lane is not None:
            for vehicle in reversed(lane.vehicles):
                if travel_dist >= lane.projected_travelled_distance(vehicle.position) and vehicle.position != position:
                    return vehicle
            lane = lane.back_connection
        return None

    def find_front_vehicle(self, position):
        _, lane = self.find_closest_node(position)
        travel_dist = lane.projected_travelled_distance(position)
        while lane is not None:
            for vehicle in lane.vehicles:
                if travel_dist <= lane.projected_travelled_distance(vehicle.position) and vehicle.position != position:
                    return vehicle
            lane = lane.front_connection
        return None

    def fix_vehicle_position(self, vehicle):
        """Fix the position of the given agent, by placing it back on it's path.

        Fixing is needed whenever a agent 'reaches' a target by overshooting it.
        A new target is selected after fixing the position.
        If the fixed position would be behind the last lane node, the agent is removed.
        If the agent is on a trajectory, follow the trajectory before following the lane.

        :param vehicle: agent to fix
        :return: None
        """
        distance = (vehicle.position - vehicle.target).length()
        if vehicle.trajectory:
            fixed_pos = self.traverse_trajectory(vehicle.position, vehicle.trajectory, distance)
            vehicle.position = fixed_pos
            if not vehicle.trajectory:
                self.fix_vehicle_position(vehicle)
            else:
                vehicle.target = vehicle.trajectory[0]
        else:
            fixed_pos = self.traverse(vehicle.target, distance)
            if fixed_pos is None:
                self.remove_vehicle(vehicle)
                return
            vehicle.position = fixed_pos
            target = self.find_next_node(vehicle.position)
            if target is None:
                print("target is None for " + str(vehicle.position))
                self.remove_vehicle(vehicle)
                return
            vehicle.target = target

    def traverse_trajectory(self, position, trajectory, distance):
        if not trajectory:
            return None
        curr = position
        succ = trajectory[0]
        while succ is not None:
            succ_dist = (succ - curr).length()
            direction = succ - curr
            direction.normalize()
            if distance < succ_dist:
                return curr + distance * direction
            distance -= succ_dist
            curr = succ
            trajectory.pop(0)
            succ = None if not trajectory else trajectory[0]
        return curr + distance * direction

    def traverse(self, position, distance):
        """Calculate a new position based on the given one, by traversing the lane.

        Start at 'position' and travel 'distance' meters along the lane.
        If the initial position is not on the lane, reach the lane before
        continuing the traversal.

        :param position: start position
        :param distance: travel distance
        :return: new position after traversing
        """
        curr = position
        succ = self.find_next_node(curr)
        while succ is not None:
            if curr == succ:
                print("'find_next_node' returned same node again! " + str(succ))
                exit(1)
            succ_dist = (succ - curr).length()
            if distance < succ_dist:
                direction = succ - curr
                direction.normalize()
                return curr + distance * direction
            distance -= succ_dist
            curr = succ
            succ = self.find_next_node(curr)
        return None

    def remove_vehicle(self, vehicle):
        """Remove the given agent from this lane.

        Removed vehicles are deactivated and returned to the spawnpool

        :param vehicle: agent to remove
        :return: None
        """
        if vehicle in self.vehicles:
            vehicle.active = False
            vehicle.lane = None
            self.vehicles.remove(vehicle)
            if vehicle.respawn:
                Spawner.add_vehicle(vehicle)
        else:
            print("Attempted to remove agent from wrong lane.")

    def projected_position(self, position):
        """Project the given position on the lane.

        The projection is on either segment adjacent to the nearest node
        or on the nearest not itself.

        :param position: position to project
        :return: projected position
        """
        first, second, closest_lane = self.find_closest_segment(position)
        if second is None:
            return closest_lane.center[first].copy()
        return position.projection(closest_lane.center[first], closest_lane.center[second])

    def projected_travelled_distance(self, position):
        """Calculate the distance from the start of the lane to the projected position.

        :param position: position to calculate the projected travel distance of
        :return: travelled distance
        """
        first, second, lane = self.find_closest_segment(position)
        if second is None:
            return lane.accumulated_distance[first]
        projection = lane.projected_position(position)
        distance = lane.accumulated_distance[first]
        distance += lane.center[first].distance(projection)
        return distance

    def projected_distance(self, pos1, pos2):
        if pos1 is None or pos2 is None:
            return None
        return abs(self.projected_travelled_distance(pos1) - self.projected_travelled_distance(pos2))

    def projected_bumper_distance(self, v1, v2):
        if v1 is None or v2 is None:
            return None
        return self.projected_distance(v1.position, v2.position) - v1.length/2.0 - v2.length/2.0

    def projected_velocity(self, vehicle):
        """Project the velocity ot the given agent on the lane.

        :param vehicle: agent of which to project the velocity
        :return: projected velocity
        """
        if vehicle is None:
            return None
        first, second, lane = self.find_closest_segment(vehicle.position)
        if second is None:
            if first == 0:
                first, second = 0, 1
            else:
                first, second = first - 1, first
        if first > second:
            first, second = second, first
        direction = (lane.center[second] - lane.center[first])
        direction.normalize()
        heading = Vector2(0, 1)
        heading.rotate(vehicle.orientation)
        directed_velocity = vehicle.velocity * heading
        projected_velocity = directed_velocity.dot(direction)
        if projected_velocity < 0.0:
            projected_velocity *= -1
        return projected_velocity

    def approaching_velocity(self, v1, v2):
        """Calculate the signed approaching velocity of a agent in relation to another agent.
        The approaching velocity takes direction into account.
        Parameter order is relevant for the result.

        :param v1: first agent
        :param v2: second agent
        :return: signed approaching velocity
        """
        if v1 is None or v2 is None:
            return None
        return self.projected_velocity(v1) - self.projected_velocity(v2)

    def find_closest_segment(self, position):
        """Return the closest lane segment. A segment may be a single
        node in which case the second return value is 'None'.

        :param position: given position
        :return: first_node, second_node, closest_lane
        """
        if position in self.closest_segment_hash:
            return self.closest_segment_hash[position]
        closest_node, closest_lane = self.find_closest_node(position)
        if closest_node > 0:
            if position.check_projection(closest_lane.center[closest_node - 1], closest_lane.center[closest_node]):
                self.closest_segment_hash[position] = closest_node - 1, closest_node, closest_lane
                return closest_node - 1, closest_node, closest_lane
        elif closest_lane.back_connection is not None:
            if position.check_projection(closest_lane.back_connection.center[-2], closest_lane.back_connection.center[-1]):
                length = len(closest_lane.back_connection.center)
                self.closest_segment_hash[position] = length - 2, length - 1, closest_lane.back_connection
                return length - 2, length - 1, closest_lane.back_connection
        if closest_node < len(closest_lane.center) - 1:
            if position.check_projection(closest_lane.center[closest_node], closest_lane.center[closest_node + 1]):
                self.closest_segment_hash[position] = closest_node, closest_node + 1, closest_lane
                return closest_node, closest_node + 1, closest_lane
        elif closest_lane.front_connection is not None:
            if position.check_projection(closest_lane.front_connection.center[0], closest_lane.front_connection.center[1]):
                self.closest_segment_hash[position] = 0, 1, closest_lane.front_connection
                return 0, 1, closest_lane.front_connection
        self.closest_segment_hash[position] = closest_node, None, closest_lane
        return closest_node, None, closest_lane

    def init_accumulated_distances(self):
        self.accumulated_distance = []
        dist = 0.0
        self.accumulated_distance.append(dist)
        for i in range(1, len(self.center)):
            dist += self.center[i].distance(self.center[i-1])
            self.accumulated_distance.append(dist)

    def find_closest_node(self, position):
        """Find the closest node on the closest lane to the given position.
        Use euclidean distance metric.

        :param position: position to find closest node from
        :return: closest_node, closest_lane
        """
        if position in self.closest_node_hash:
            return self.closest_node_hash[position]
        closest = None, None
        dist = float("inf")
        lane = self
        while lane is not None:
            for i, node in enumerate(lane.center):
                if position.distance(node) < dist:
                    dist = position.distance(node)
                    closest = i, lane
            lane = lane.front_connection
        lane = self
        while lane is not None:
            for i, node in enumerate(lane.center):
                if position.distance(node) < dist:
                    dist = position.distance(node)
                    closest = i, lane
            lane = lane.back_connection
        self.closest_node_hash[position] = closest
        return closest

    def find_next_node(self, position):
        """Find the closest node which lies ahead of the given position
        in terms of travelled distance.

        The next node may be None if the end of the lane is reached.

        :param position: position to find next node from
        :return: closest node ahead of given position
        """
        if position in Lane.next_node_hash:
            return Lane.next_node_hash[position]
        travel_dist = self.projected_travelled_distance(position)
        closest_node, closest_lane = self.find_closest_node(position)
        if closest_lane.accumulated_distance[closest_node] - Lane.EPSILON > travel_dist:
            return closest_lane.center[closest_node]
        if closest_node < len(closest_lane.center) - 1:
            return closest_lane.center[closest_node + 1]
        if closest_lane.front_connection is not None:
            return closest_lane.front_connection.center[1]
        return None

    def add_vehicle(self, vehicle):
        back = self.find_back_vehicle(vehicle.position)
        if back is None or back not in self.vehicles:
            self.vehicles.insert(0, vehicle)
            return
        index = self.vehicles.index(back)
        self.vehicles.insert(index + 1, vehicle)

    def set_up_hashes(self):
        for i in range(len(self.center) - 1):
            Lane.next_node_hash[self.center[i]] = self.center[i+1]
