class Rect:
    def __init__(self, x1=0, y1=0, x2=1, y2=1, prob=0.0, text=None):
        self.x1, self.y1, self.x2, self.y2 = [None] * 4

        self.prob = prob
        self.text = text
        self.set_coordinates(x1, y1, x2, y2)

    @property
    def w(self):
        return (self.x2 - self.x1)

    @w.setter
    def w(self, val):
        assert val > 0
        self.x2 = self.x1 + val

    @property
    def h(self):
        return (self.y2 - self.y1)

    @h.setter
    def h(self, val):
        assert val > 0
        self.y2 = self.y1 + val

    def set_coordinates(self, x1, y1, x2, y2):
        w = x2 - x1
        h = y2 - y1
        if x1 > x2 or y1 > y2:
            print((x1, y1, x2, y2))
            raise ValueError("Coordinates are invalid")
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def area_diff(self, other):
        """calculates the area of box that is non-intersecting with 'other' rect"""
        return self.area() - self.intersection(other).area()

    def area(self):
        """calculates the area of the box"""
        return self.w * self.h

    def intersection(self, other):
        """calculates the intersecting area of two rectangles"""
        a, b = self, other
        x1 = max(a.x1, b.x1)
        y1 = max(a.y1, b.y1)
        x2 = min(a.x2, b.x2)
        y2 = min(a.y2, b.y2)
        if x1 <= x2 and y1 <= y2:
            return type(self)(x1, y1, x2, y2)
        else:
            return type(self)(0, 0, 0, 0)

    __and__ = intersection

    def union(self, other):
        """takes the union of the two rectangles"""
        a, b = self, other
        x1 = min(a.x1, b.x1)
        y1 = min(a.y1, b.y1)
        x2 = max(a.x2, b.x2)
        y2 = max(a.y2, b.y2)
        if x1 <= x2 and y1 <= y2:
            return type(self)(x1, y1, x2, y2)

    __or__ = union
    __sub__ = area_diff

    def contains(p1):
        if p1[0] < self.x2 and p1[0] > self.x1:
            if p1[1] < self.y2 and p1[1] > self.y1:
                return True
        return False

    def __iter__(self):
        yield self.x1
        yield self.y1
        yield self.x2
        yield self.y2

    def __eq__(self, other):
        return isinstance(other, Rect) and tuple(self) == tuple(other)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return type(self).__name__ + repr(tuple(self))

    def __repr__(self):
        return type(self).__name__ + repr(tuple(self))

    def move(self, x, y, inplace=True):
        if inplace:
            self.x1 += x
            self.y1 += y
            self.x2 += x
            self.y2 += y
            return self
        else:
            rect = type(self)()
            rect.set_coordinates(self.x1 + x, self.y1 + y, self.x2 + x, self.y2 + y)
            rect.prob = self.prob
            rect.text = self.text
            return rect


    def scale(self, x, y, inplace=True):
        if inplace:
            self.x1 = int(self.x1 * x)
            self.y1 = int(self.y1 * y)
            self.x2 = int(self.x2 * x)
            self.y2 = int(self.y2 * y)
            return self
        else:
            rect = type(self)()
            rect.set_coordinates(*tuple(map(int, [self.x1 * x, self.y1 * y, self.x2 * x, self.y2 * y])))
            rect.prob = self.prob
            rect.text = self.text
            return rect