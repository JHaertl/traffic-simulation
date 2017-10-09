import math
import copy


class Vector2:

    DEG_2_RAD = math.pi / 180.0
    RAD_2_DEG = 180.0 / math.pi
    EPSILON = 0.001

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self):
        return copy.deepcopy(self)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def __abs__(self):
        return self.length()

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            IndexError("Index {0} out of bounds. Vector2 supports [0] and [1].".format(key))

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            IndexError("Index {0} out of bounds. Vector2 supports [0] and [1].".format(key))

    def __hash__(self):
        return hash((self.x, self.y))

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def __iter__(self):
        return (x for x in [self.x, self.y])

    def length(self):
        return math.sqrt(self.length_squared())

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    def normalize(self):
        """Normalize this vector

        Normalized vectors have a length of 1

        :return: None
        """
        length = self.length()
        self.x /= length
        self.y /= length

    def dot(self, other):
        """Calculate the dot product

        The dot product is sensitive to vector lengths!
        a * b = |a||b|cos(theta)

        :param other: reference vector
        :return: scalar result of the dot product
        """
        return self.x * other.x + self.y * other.y

    def perp(self, other):
        """Calculate the perp dot product

        a' * b = |a||b|sin(theta),
        where a' is a after being rotated 90 degrees
        :param other: reference vector
        :return: scalar result of the perp dot product
        """
        return self.x * other.y - self.y * other.x

    def rotate(self, degrees):
        """Rotate this vector according to 'degrees'

        Negative values infer an anti-clockwise rotation,
        positive values infer a clockwise rotation.

        :param degrees:
        :return:
        """
        radians = degrees * Vector2.DEG_2_RAD
        c, s = math.cos(radians), math.sin(radians)
        self.x, self.y = c * self.x + s * self.y, -s * self.x + c * self.y

    def distance(self, other):
        return math.sqrt(self.distance_squared(other))

    def distance_squared(self, other):
        return ((self.x - other.x) * (self.x - other.x) +
                (self.y - other.y) * (self.y - other.y))

    def distance_angular_signed(self, other):
        """Calculate the signed angular distance between two vectors in (-180, 180] degrees.

        Negative values infer an anti-clockwise rotation,
        positive values infer a clockwise rotation.

        :param other: reference vector
        :raises ZeroDivisionError: if one of the vectors is (0, 0)
        :return: signed angular difference in degrees
        """
        angle = self.distance_angular_unsigned(other)
        if self.x * other.y - self.y * other.x > 0:
            angle = -angle
        return angle

    def distance_angular_unsigned(self, other):
        """Calculate the unsigned angular distance between two vectors in [0, 180] degrees.

        :param other: reference vector
        :raises ZeroDivisionError: if one of the vectors is (0, 0)
        :return: unsigned angular difference in degrees
        """
        value = self.dot(other) / (self.length() * other.length())
        return Vector2.RAD_2_DEG * math.acos(min(1, max(-1, value)))

    def projection(self, v1, v2):
        """Calculate the projection of this vector onto the given line.
        The projection is not limited to the line segment between v1 and v2.

        :param v1: first vector on line
        :param v2: second vector on line
        :return: vector projected on given line
        """
        u = v2 - v1
        return v1 + ((self - v1).dot(u) / u.dot(u)) * u

    def projection_restricted(self, v1, v2):
        """Calculate the projection of this vector onto the given line segment.

        :param v1: first vector of segment
        :param v2: second vector of segment
        :return: vector projected on given line segment or None if there is no such projection
        """
        if not self.check_projection(v1, v2):
            return None
        return self.projection(v1, v2)

    def check_projection(self, v1, v2):
        """Check whether the projection of this vector onto the given line
        would fall between the two given vectors.

        :param v1: first vector on line
        :param v2: second vector on line
        :return: 'True' if projection falls on the line segment, 'False' if it would be outside
        """
        s = v2 - v1
        u = self - v1
        return 0 <= s.dot(u) <= s.dot(s)
