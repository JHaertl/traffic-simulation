from unittest import TestCase
from vector2 import Vector2
import math


class TestVector2(TestCase):

    def test_eq(self):
        v = Vector2(3, 2)
        u = Vector2(3, 2)
        w = Vector2(7, 6)
        self.assertTrue(v == u)
        self.assertFalse(u == v)
        self.assertFalse(v == w)
        self.assertFalse(w == u)

    def test_add(self):
        v = Vector2(3, 2)
        u = Vector2(4, 4)
        w = Vector2(7, 6)
        self.assertTrue(v + u == w)
        self.assertTrue(u + v == w)

    def test_sub(self):
        v = Vector2(3, 2)
        u = Vector2(4, 4)
        w = Vector2(7, 6)
        self.assertTrue(w - u == v)
        self.assertFalse(u - w == v)

    def test_mul(self):
        v = Vector2(3, 2)
        u = Vector2(6, 4)
        w = Vector2(-3, -2)
        self.assertTrue((v * 2 == 2 * v) and (v * 2 == u))
        self.assertTrue((v * -1 == -1 * v) and (v * -1 == w))
        v *= 2
        self.assertTrue(v == u)

    def test_truediv(self):
        v = Vector2(3, 2)
        u = Vector2(6, 4)
        w = Vector2(-3, -2)
        self.assertTrue(v / 0.5 == u)
        self.assertTrue(v / -1 == w)
        u /= 2
        self.assertTrue(v == u)

    def test_abs(self):
        v = Vector2(1, 0)
        u = Vector2(0, -1)
        w = Vector2(1, 1)
        eps = 0.001
        self.assertTrue(abs(v) == 1)
        self.assertTrue(abs(u) == 1)
        self.assertTrue(abs(abs(w) - math.sqrt(2)) < eps)

    def test_getitem(self):
        v = Vector2(1, 2)
        self.assertTrue(v[0] == v.x)
        self.assertTrue(v[1] == v.y)

    def test_setitem(self):
        v = Vector2(1, 2)
        v[0] = 4
        v[1] = 5
        self.assertTrue(v.x == 4)
        self.assertTrue(v.y == 5)

    def test_str(self):
        v = Vector2(1, 1)
        self.assertTrue(str(v) == "(1, 1)")

    def test_length(self):
        v = Vector2(1, 0)
        u = Vector2(0, -1)
        w = Vector2(1, 1)
        eps = 0.001
        self.assertTrue(v.length() == 1)
        self.assertTrue(u.length() == 1)
        self.assertTrue(abs(w.length() - math.sqrt(2)) < eps)

    def test_length_squared(self):
        v = Vector2(1, 0)
        u = Vector2(0, -1)
        w = Vector2(1, 1)
        self.assertTrue(v.length_squared() == 1)
        self.assertTrue(u.length_squared() == 1)
        self.assertTrue(w.length_squared() == 2)

    def test_normalize(self):
        v = Vector2(0.5, 0)
        u = Vector2(0, -0.5)
        w = Vector2(1, 1)
        v.normalize()
        u.normalize()
        w.normalize()
        eps = 0.001
        self.assertTrue(v == Vector2(1, 0))
        self.assertTrue(u == Vector2(0, -1))
        self.assertTrue(abs(w.x - 1/math.sqrt(2)) < eps and w.x == w.y)

    def test_dot(self):
        v = Vector2(1, 0)
        u = Vector2(0, 1)
        w = Vector2(2, 1)
        self.assertTrue(v.dot(u) == 0)
        self.assertTrue(u.dot(v) == 0)
        self.assertTrue(v.dot(w) == 2)

    def test_rotate(self):
        v = Vector2(1, 0)
        u = Vector2(0, 1)
        w = Vector2(1/math.sqrt(2), 1/math.sqrt(2))
        eps = 0.001
        v.rotate(-90)
        self.assertTrue(abs(v.x - u.x) < eps and abs(v.y - u.y) < eps)
        u.rotate(45)
        self.assertTrue(abs(w.x - u.x) < eps and abs(w.y - u.y) < eps)

    def test_distance(self):
        v = Vector2(1, 0)
        u = Vector2(0, 1)
        w = Vector2(-1, 0)
        eps = 0.001
        self.assertTrue(abs(v.distance(u) - math.sqrt(2)) < eps)
        self.assertTrue(abs(u.distance(v) - math.sqrt(2)) < eps)
        self.assertTrue(abs(v.distance(w) - 2) < eps)

    def test_distance_squared(self):
        v = Vector2(1, 0)
        u = Vector2(0, 1)
        w = Vector2(-1, 0)
        eps = 0.001
        self.assertTrue(abs(v.distance_squared(u) - 2) < eps)
        self.assertTrue(abs(u.distance_squared(v) - 2) < eps)
        self.assertTrue(abs(v.distance_squared(w) - 4) < eps)

    def test_distance_angular_signed(self):
        v = Vector2(1, 0)
        u = Vector2(0, 2)
        w = Vector2(-3, 0)
        t = Vector2(-3, -0.1)
        s = Vector2(-3, 0.1)
        eps = 0.001
        self.assertTrue(abs(v.distance_angular_signed(u)) - 90 < eps and v.distance_angular_signed(u) < 0)
        self.assertTrue(abs(u.distance_angular_signed(v)) - 90 < eps and u.distance_angular_signed(v) > 0)
        self.assertTrue(abs(v.distance_angular_signed(w)) - 180 < eps and v.distance_angular_signed(w) > 0)
        self.assertTrue(abs(v.distance_angular_signed(t)) - 178.0908 < eps and v.distance_angular_signed(t) > 0)
        self.assertTrue(abs(v.distance_angular_signed(s)) - 178.0908 < eps and v.distance_angular_signed(s) < 0)

    def test_distance_angular_unsigned(self):
        v = Vector2(1, 0)
        u = Vector2(0, 2)
        w = Vector2(-3, 0)
        t = Vector2(-3, -0.1)
        s = Vector2(-3, 0.1)
        eps = 0.001
        self.assertTrue(abs(v.distance_angular_unsigned(u)) - 90 < eps and v.distance_angular_unsigned(u) > 0)
        self.assertTrue(abs(u.distance_angular_unsigned(v)) - 90 < eps and u.distance_angular_unsigned(v) > 0)
        self.assertTrue(abs(v.distance_angular_unsigned(w)) - 180 < eps and v.distance_angular_unsigned(w) > 0)
        self.assertTrue(abs(v.distance_angular_unsigned(t)) - 178.0908 < eps and v.distance_angular_unsigned(t) > 0)
        self.assertTrue(abs(v.distance_angular_unsigned(s)) - 178.0908 < eps and v.distance_angular_unsigned(s) > 0)