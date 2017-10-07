from simulation.simulation_object import SimulationObject
from simulation.vector2 import Vector2

from simulation.layout.lane import Lane


class Road(SimulationObject):

    LANE_WIDTH = 4.0

    def __init__(self, path, num_lanes):
        super(Road, self).__init__(position=Vector2(),
                                   orientation=0,
                                   color=(0.5, 0.5, 0.5),
                                   mesh=[])
        self.lanes = []  # type: [Lane]
        self.create_lanes(path, num_lanes)
        for node in self.lanes[0].right:
            self.mesh.append(node)
        for node in reversed(self.lanes[-1].left):
            self.mesh.append(node)

    def reset_hashes(self):
        for lane in self.lanes:
            lane.reset_hashes()

    def create_lanes(self, path, num_lanes):
        """Create lanes based on a single path, which represents the right most center(!) line

        All additional lanes are created to the left of the given path
        Exceeding the maximum curvature (which changes with num_lanes) is not handled

        :param path: right most center line
        :param num_lanes: number of lanes to create
        :return: None
        """
        for i in range(num_lanes):
            self.lanes.append(Lane(self))
        for i, node in enumerate(path):
            if i == 0 or i == len(path)-1:
                continue
            pred = path[i - 1]
            succ = path[i + 1]
            direction = Road.calc_road_normal(pred, node, succ)
            for j in range(num_lanes):
                center = node + direction * Road.LANE_WIDTH * j
                self.lanes[j].center.append(center)
                left = center + direction * Road.LANE_WIDTH / 2.0
                self.lanes[j].left.append(left)
                right = center - direction * Road.LANE_WIDTH / 2.0
                self.lanes[j].right.append(right)
        for i in range(num_lanes):
            self.lanes[i].init_accumulated_distances()
            self.calc_neighboring_lanes(self.lanes[i])
            self.lanes[i].set_up_hashes()
        self.create_lane_meshes()

    @staticmethod
    def calc_road_normal(pred, current, succ):
        """Calculate the normal of the road at 'current'

        The returned direction is normalized.
        The normal is facing to the left in relation to the road's direction.

        :param pred: predecessor of 'current'
        :param current: node to calculate the normal for
        :param succ: successor of 'current'
        :raises ZeroDivisionError: if current == pred or current == succ
        :return: normal at 'current'
        """
        ahead = succ - current
        back = pred - current
        angle = ahead.distance_angular_signed(back)
        if angle > 0:
            angle -= 360.0
        normal = ahead
        normal.rotate(angle / 2.0)
        normal.normalize()
        return normal

    def create_lane_meshes(self):
        for lane in self.lanes:
            lane.mesh = []
            for node in lane.right:
                lane.mesh.append(node)
            for node in reversed(lane.left):
                lane.mesh.append(node)
        # TODO: ROAD MESH MAKES NO SENSE ATM
        self.mesh = []
        for lane in self.lanes:
            self.mesh.append(lane.left[0])
            self.mesh.append(lane.right[0])
        for node in self.lanes[0].right:
            self.mesh.append(node)
        for lane in self.lanes:
            self.mesh.append(lane.right[-1])
            self.mesh.append(lane.left[-1])
        for node in reversed(self.lanes[-1].left):
            self.mesh.append(node)

    def get_lane_index(self, lane):
        for i, l in enumerate(self.lanes):
            if self.lanes[i] == lane:
                return i
        return -1

    def calc_neighboring_lanes(self, lane):
        index = self.get_lane_index(lane)
        if index < 0:
            return
        neighbors = []
        if index > 0:
            lane.right_neighbor = self.lanes[index-1]
            neighbors.append(self.lanes[index-1])
        if index < len(self.lanes)-1:
            lane.left_neighbor = self.lanes[index + 1]
            neighbors.append(self.lanes[index+1])
        lane.neighboring_lanes = neighbors

    def connect(self, road, connections):
        """Connect this road with the given road according to the list of lane connections.
        Update the lane meshes, accumulated distances and hashes afterwards.

        :param road: road to connect to
        :param connections: list of lane connections
        :return: None
        """
        for connection in connections:
            pred_lane = self.lanes[connection[0]]
            succ_lane = road.lanes[connection[1]]
            # reposition end notes
            pred_normal = Road.calc_road_normal(pred_lane.center[-2], pred_lane.center[-1], succ_lane.center[0])
            pred_lane.left[-1] = pred_lane.center[-1] + pred_normal * Road.LANE_WIDTH / 2.0
            pred_lane.right[-1] = pred_lane.center[-1] - pred_normal * Road.LANE_WIDTH / 2.0
            succ_normal = Road.calc_road_normal(pred_lane.center[-1], succ_lane.center[0], succ_lane.center[1])
            succ_lane.left[0] = succ_lane.center[0] + succ_normal * Road.LANE_WIDTH / 2.0
            succ_lane.right[0] = succ_lane.center[0] - succ_normal * Road.LANE_WIDTH / 2.0
            i = 1
            # if multiple lanes are connected, position changes may have ripple effects through neighboring lanes
            while connection[0] + i < len(self.lanes):
                if (connection[0] + i, connection[1] + i) in connections:
                    self.lanes[connection[0] + i].center[-1] = pred_lane.center[-1] + pred_normal * i * Road.LANE_WIDTH
                    self.lanes[connection[0] + i].left[-1] = self.lanes[connection[0] + i].center[
                                                                 -1] + pred_normal * Road.LANE_WIDTH / 2.0
                    self.lanes[connection[0] + i].right[-1] = self.lanes[connection[0] + i].center[
                                                                  -1] - pred_normal * Road.LANE_WIDTH / 2.0
                    road.lanes[connection[1] + i].center[0] = succ_lane.center[0] + succ_normal * i * Road.LANE_WIDTH
                    road.lanes[connection[1] + i].left[0] = road.lanes[connection[1] + i].center[
                                                                0] + succ_normal * Road.LANE_WIDTH / 2.0
                    road.lanes[connection[1] + i].right[0] = road.lanes[connection[1] + i].center[
                                                                 0] - succ_normal * Road.LANE_WIDTH / 2.0
                i += 1
            # perform the connection on vertex level
            pred_lane.center.append(succ_lane.center[0])
            pred_lane.left.append(succ_lane.left[0])
            pred_lane.right.append(succ_lane.right[0])
            # update pred lane accumulated distance for new node
            distance = pred_lane.center[-1].distance(pred_lane.center[-2])
            self.lanes[connection[0]].accumulated_distance.append(
                self.lanes[connection[0]].accumulated_distance[-1] + distance)
        self.create_lane_meshes()
        road.create_lane_meshes()
        # perform the connection on a logical level
        for connection in connections:
            self.lanes[connection[0]].front_connection = road.lanes[connection[1]]
            road.lanes[connection[1]].back_connection = self.lanes[connection[0]]
            self.lanes[connection[0]].set_up_hashes()
            road.lanes[connection[1]].set_up_hashes()
            Road.add_accumulated_distance(road.lanes[connection[1]], self.lanes[connection[0]].accumulated_distance[-1])

    @staticmethod
    def add_accumulated_distance(lane, value):
        while lane is not None:
            lane.accumulated_distance = [x + value for x in lane.accumulated_distance]
            lane = lane.front_connection
