import cv2
from .GTElement import GTElement, Row, Column, RowSpan, ColSpan, Cell

from xml.dom import minidom
from xml.etree import ElementTree as ET

class Table(GTElement):
    """
    A class for representing a Ground Truth table.
    """

    def __init__(self, x0=0, y0=0, x1=1, y1=1):
        super().__init__(x0, y0, x1, y1)
        self.orientation = "unknown"
        self.gtSpans = []
        self.gtRows = []
        self.gtCols = []
        self.gtCells = None

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return str(self) + "\n" + \
        "\n".join([" |-" + str(elem) for elem in self.gtRows + self.gtCols + self.gtSpans])

    def remove(self, elem):
        if elem in self.gtRows:
            self.gtRows.remove(elem)
        elif elem in self.gtCols:
            self.gtCols.remove(elem)
        elif elem in self.gtSpans:
            self.gtSpans.remove(elem)
        self.evaluateCells()

    # def populate_ocr(self, ocr_data):
    #     for cell in self.gtCells:
    #         for item in cell:
    #             for bnd_box in ocr_data:
    #                 y_point = (bnd_box[3] + bnd_box[5]) // 2
    #                 x_point = bnd_box[2] + \
    #                     int((bnd_box[4] - bnd_box[2]) * 0.15)
    #                 if (
    #                     (x_point > item.x1)
    #                     and (y_point > item.y1)
    #                     and (x_point < item.x2)
    #                     and (y_point < item.y2)
    #                 ):
    #                     item.words.append(bnd_box)

    def getCellAtPoint(self, p):
        if len(self.gtCells) == 0:
            return None
        else:
            for i in range(len(self.gtCells)):
                for j in range(len(self.gtCells[i])):
                    cell = self.gtCells[i][j]
                    if (
                        p[0] >= cell.x1
                        and p[0] <= cell.x2
                        and p[1] >= cell.y1
                        and p[1] <= cell.y2
                    ):
                        return cell
        return None

    def addSpan(self, elem):
        self.gtSpans.append(elem)
        self.evaluateCells()

    def removeSpan(self, elem):
        self.gtSpans.remove(elem)
        self.evaluateCells()

    def evaluateCells(self):
        self.evaluateInitialCells()
        returnVal = [False for i in range(len(self.gtSpans))]
        for i, elem in enumerate(self.gtSpans):
            if isinstance(elem, RowSpan):
                returnVal[i] = self.executeRowSpan((elem.x1, elem.y1), (elem.x2, elem.y2))
            elif isinstance(elem, ColSpan):
                returnVal[i] = self.executeColSpan((elem.x1, elem.y1), (elem.x2, elem.y2))
            else:
                print("Unrecognized object encountered in \"gtSpans\". {}".format(elem))

        for i in range(len(self.gtSpans) - 1, -1, -1):
            if returnVal[i] is False:
                self.gtSpans.remove(self.gtSpans[i])

    def executeColSpan(self, p1, p2):
        startCell = self.getCellAtPoint(p1)
        endCell = self.getCellAtPoint(p2)
        if (
            startCell is None
            or endCell is None
            or startCell.startRow != endCell.startRow
            or startCell.endRow != endCell.endRow
            or startCell == endCell
        ):
            print("Cant add Col Span: for " + str(p1) + " ,and " + str(p2))
            return False

        startCell.endCol = endCell.endCol
        for i in range(startCell.startCol + 1, endCell.endCol + 1):
            temp = self.gtCells[startCell.startRow][i]
            temp.dontCare = True
            startCell.x2 = temp.x2
            if temp.y2 > startCell.y2:
                startCell.y2 = temp.y2

            for j in range(startCell.startRow + 1, startCell.endRow + 1):
                self.gtCells[j][i].dontCare = True
        return True

    def executeRowSpan(self, p1, p2):
        startCell = self.getCellAtPoint(p1)
        endCell = self.getCellAtPoint(p2)
        if (
            startCell is None
            or endCell is None
            or startCell.startCol != endCell.startCol
            or startCell.endCol != endCell.endCol
            or startCell == endCell
        ):
            print("Cant add Row Span: for " + str(p1) + " ,and " + str(p2))
            return False

        startCell.endRow = endCell.endRow
        for i in range(startCell.startRow + 1, endCell.endRow + 1):
            temp = self.gtCells[i][startCell.startCol]
            temp.dontCare = True
            startCell.y2 = temp.y2
            if temp.x2 > startCell.x2:
                startCell.x2 = temp.x2

            for j in range(startCell.startCol + 1, startCell.endCol + 1):
                self.gtCells[i][j].dontCare = True
        return True

    def __populateSpansFromCells(self):
        numRows = len(self.gtRows) + 1
        numCols = len(self.gtCols) + 1
        self.gtSpans.clear()

        if len(self.gtRows) == 0:
            rowCenters = [(self.y1 + self.y2) / 2]
        else:
            rowCenters = [
                (self.gtRows[i].y1 + self.gtRows[i + 1].y1) // 2
                for i in range(len(self.gtRows) - 1)
            ]
            rowCenters = (
                [(self.gtRows[0].y1 + self.y1) // 2]
                + rowCenters
                + [(self.gtRows[-1].y1 + self.y2) // 2]
            )

        if len(self.gtCols) == 0:
            colCenters = [(self.x1 + self.x2) / 2]
        else:
            colCenters = [
                (self.gtCols[i].x1 + self.gtCols[i + 1].x1) // 2
                for i in range(len(self.gtCols) - 1)
            ]
            colCenters = (
                [(self.gtCols[0].x1 + self.x1) // 2]
                + colCenters
                + [(self.gtCols[-1].x1 + self.x2) // 2]
            )

        for i in range(numRows):
            for j in range(numCols):
                cell = self.gtCells[i][j]

                if cell.dontCare is False:
                    if cell.startCol != cell.endCol:
                        cell.x2 = self.gtCells[i][j + 1].x1
                        for i1 in range(cell.startRow, cell.endRow + 1):
                            y1 = rowCenters[i1]
                            x1 = colCenters[cell.startCol]
                            x2 = colCenters[cell.endCol]
                            self.gtSpans.append(ColSpan(x1, y1, x2))
                    if cell.startRow != cell.endRow:
                        x1 = colCenters[cell.startCol]
                        y1 = rowCenters[cell.startRow]
                        y2 = rowCenters[cell.endRow]
                        self.gtSpans.append(RowSpan(x1, y1, y2))

    def evaluateInitialCells(self):
        self.gtRows.sort(key=lambda x: x.y1)
        self.gtCols.sort(key=lambda x: x.x1)

        numRows = len(self.gtRows) + 1
        numCols = len(self.gtCols) + 1

        self.gtCells = [[None for j in range(numCols)] for i in range(numRows)]

        l, t, r, b = 0, 0, 0, 0
        l = self.x1
        t = self.y1

        for i in range(numRows):
            if i < len(self.gtRows):
                b = self.gtRows[i].y1
            else:
                b = self.y2
            for j in range(numCols):
                if j < len(self.gtCols):
                    r = self.gtCols[j].x1
                else:
                    r = self.x2

                cell = Cell(l, t, r, b, i, j)

                self.gtCells[i][j] = cell

                l = r
            l = self.x1
            t = b

    @staticmethod
    def from_xml_object(obj):
        table = Table(
                int(obj.attrib["x0"]), 
                int(obj.attrib["y0"]), 
                int(obj.attrib["x1"]),
                int(obj.attrib["y1"]),
            )

        if 'orientation' in obj.attrib:
            table.orientation = obj.attrib['orientation']

        for row in obj.findall(".//Row"):
            table.gtRows.append(Row(table.x1, int(row.attrib["y0"]), table.x2))
        for col in obj.findall(".//Column"):
            table.gtCols.append(Column(int(col.attrib["x0"]), table.y1, table.y2))

        table.gtRows.sort(key=lambda x: x.y1)
        table.gtCols.sort(key=lambda x: x.x1)

        cells = []
        for cell in obj.findall(".//Cell"):
            cells.append(Cell(
                    int(cell.attrib["x0"]),
                    int(cell.attrib["y0"]),
                    int(cell.attrib["x1"]),
                    int(cell.attrib["y1"]),
                    int(cell.attrib["startRow"]),
                    int(cell.attrib["startCol"]),
                    int(cell.attrib["endRow"]),
                    int(cell.attrib["endCol"]),
                    True if cell.attrib["dontCare"]=="true" else False
                ))

        cells.sort(key=lambda cell: (cell.y1, cell.x1))

        numRows = len(table.gtRows) + 1
        numCols = len(table.gtCols) + 1

        if len(cells) != numRows * numCols:
            print("Number of cells does not match rows*columns.")
            return

        table.gtCells = [[None for j in range(numCols)] for i in range(numRows)]

        for cell in cells:
            table.gtCells[cell.startRow][cell.startCol] = cell

        table.__populateSpansFromCells()
        table.evaluateCells()
        return table

    def get_xml_object(self):
        # out_root = ET.Element("GroundTruth")
        # out_tables = ET.SubElement(out_root, "Tables")

        out_table = ET.Element("Table")
        out_table.attrib["x0"] = str(self.x1)
        out_table.attrib["x1"] = str(self.x2)
        out_table.attrib["y0"] = str(self.y1)
        out_table.attrib["y1"] = str(self.y2)
        out_table.attrib["orientation"] = self.orientation

        self.gtRows.sort(key=lambda x: x.y1)
        self.gtCols.sort(key=lambda x: x.x1)

        for row in self.gtRows:
            out_row = ET.SubElement(out_table, "Row")

            out_row.attrib["x0"] = str(self.x1)
            out_row.attrib["x1"] = str(self.x2)
            out_row.attrib["y0"] = str(row.y1)
            out_row.attrib["y1"] = str(row.y1)

        for col in self.gtCols:
            out_col = ET.SubElement(out_table, "Column")

            out_col.attrib["x0"] = str(col.x1)
            out_col.attrib["x1"] = str(col.x1)
            out_col.attrib["y0"] = str(self.y1)
            out_col.attrib["y1"] = str(self.y2)

        self.evaluateCells()
        for i in range(len(self.gtCells)):
            for j in range(len(self.gtCells[i])):
                cell = self.gtCells[i][j]
                out_cell = ET.SubElement(out_table, "Cell")

                out_cell.attrib["x0"] = str(cell.x1)
                out_cell.attrib["x1"] = str(cell.x2)
                out_cell.attrib["y0"] = str(cell.y1)
                out_cell.attrib["y1"] = str(cell.y2)

                out_cell.attrib["startRow"] = str(cell.startRow)
                out_cell.attrib["endRow"] = str(cell.endRow)
                out_cell.attrib["startCol"] = str(cell.startCol)
                out_cell.attrib["endCol"] = str(cell.endCol)

                out_cell.attrib["dontCare"] = str("true" if cell.dontCare is True else "false")
                out_cell.text = "(0,0,0)"

        return out_table

    def move(self, x, y):
        super().move(x, y)

        for elem in (self.gtRows + self.gtCols + self.gtSpans):
            elem.move(x, y)
        self.evaluateCells()

    def visualize(self, image):
        assert image.shape[2] == 3

        self.evaluateCells()

        for row in self.gtCells:
            for cell in row:
                if cell.dontCare:
                    continue

                cv2.line(image, (cell.x1, cell.y1), (cell.x2, cell.y1), (0, 0, 255), 3)
                cv2.line(image, (cell.x1, cell.y2), (cell.x2, cell.y2), (0, 0, 255), 3)

                cv2.line(image, (cell.x1, cell.y1), (cell.x1, cell.y2), (0, 255, 0), 3)
                cv2.line(image, (cell.x2, cell.y1), (cell.x2, cell.y2), (0, 255, 0), 3)