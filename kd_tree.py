import math


class Node:
    def __init__(self, point_id, point, axis):
        self.point_id = point_id
        self.point = point
        self.axis = axis
        self.left = None
        self.right = None


class KDTree:
    def __init__(self, points):
        self.root = self._build_tree(points)

    def _build_tree(self, points, depth=0):
        if not points:
            return None

        k = len(points[0]["coord"])  # Since we are dealing with 3D points
        axis = depth % k

        points.sort(key=lambda x: x["coord"][axis])
        median = len(points) // 2

        node = Node(points[median]["id"], points[median]["coord"], axis)
        node.left = self._build_tree(points[:median], depth + 1)
        node.right = self._build_tree(points[median + 1 :], depth + 1)

        return node

    def _distance(self, point1, point2):
        return math.sqrt(
            (point1[0] - point2[0]) ** 2
            + (point1[1] - point2[1]) ** 2
            + (point1[2] - point2[2]) ** 2
        )

    def nearest_neighbor(self, point):
        return self._nearest_neighbor_recursive(self.root, point)

    def _nearest_neighbor_recursive(self, node, target, best=None):
        if node is None:
            return best

        if best is None:
            best = node

        if self._distance(target, node.point) < self._distance(target, best.point):
            best = node

        axis = node.axis
        next_branch = None
        opposite_branch = None

        if target[axis] < node.point[axis]:
            next_branch = node.left
            opposite_branch = node.right
        else:
            next_branch = node.right
            opposite_branch = node.left

        best = self._nearest_neighbor_recursive(next_branch, target, best)

        if opposite_branch and (
            abs(target[axis] - node.point[axis]) < self._distance(target, best.point)
        ):
            best = self._nearest_neighbor_recursive(opposite_branch, target, best)

        return best

    def distance_to_nearest(self, point, threshold=0.0):
        nearest_node = self.nearest_neighbor(point)
        distance = self._distance(point, nearest_node.point)
        if distance <= threshold:
            return nearest_node.point_id
        else:
            return None

    def insert(self, point_dict):
        def _insert_recursive(node, point_dict, depth):
            if node is None:
                axis = depth % len(point_dict["coord"])
                return Node(point_dict["id"], point_dict["coord"], axis)

            axis = node.axis
            if point_dict["coord"][axis] < node.point[axis]:
                node.left = _insert_recursive(node.left, point_dict, depth + 1)
            else:
                node.right = _insert_recursive(node.right, point_dict, depth + 1)
            return node

        self.root = _insert_recursive(self.root, point_dict, 0)