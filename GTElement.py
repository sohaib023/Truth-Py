from .Rect import Rect


class GTElement(Rect):
    """
    An abstract class that represents a Ground Truth Bounding Box
    """

    def __init__(self, x0=0, y0=0, x1=1, y1=1):
        super().__init__(x0, y0, x1, y1)


class Row(GTElement):
    """
    A class that represents a Row seperator in table (rectangle with height=1)
    """

    def __init__(self, x0=0, y0=0, x1=1):
        super().__init__(x0, y0, x1, y0 + 1)


class Column(GTElement):
    """
    A class that represents a Column seperator in table (rectangle with width=1)
    """

    def __init__(self, x0=0, y0=0, y1=1):
        super().__init__(x0, y0, x0 + 1, y1)


class ColSpan(Row):
    pass


class RowSpan(Column):
    pass


class Cell(GTElement):
    """
    A class that represents a Cell in table
    """

    def __init__(self, x0=0, y0=0, x1=1, y1=1, startRow=-1, startCol=-1, endRow=-1, endCol=-1, dontCare=False):
        super().__init__(x0, y0, x1, y1)

        self.startRow = startRow
        self.startCol = startCol

        self.endRow = endRow if endRow != -1 else startRow 
        self.endCol = endCol if endCol != -1 else startCol

        self.words = []

        self.dontCare = dontCare

    # def assumeDontCare(self):
    #     if self.endRow - self.startRow < 0 or self.endCol - self.startCol < 0:
    #         self.dontCare = True
    #     else:
    #         self.dontCare = False

    def getCenter(self):
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def __repr__(self):
        return type(self).__name__ + repr(list(self) + [self.startRow, self.startCol, self.endRow, self.endCol, self.dontCare])