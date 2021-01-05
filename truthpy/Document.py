import os 

from xml.dom import minidom
from xml.etree import ElementTree as ET

from .GTElement import GTElement, Row, Column, Cell
from .Table import Table

class Document:
    def __init__(self, path=None):
        self.tables = []
        self.input_file = "N/A"
        
        if path:
            tree = ET.parse(path)
            root = tree.getroot()

            if "InputFile" in root.attrib:
                self.input_file = root.attrib["InputFile"]
                
            for i, obj in enumerate(root.findall(".//Table")):
                self.tables.append(Table.from_xml_object(obj))

    def write_to(self, path):
        out_root = ET.Element("GroundTruth")
        out_root.attrib['InputFile'] = self.input_file
        
        out_tables = ET.SubElement(out_root, "Tables")
        for table in self.tables:
            table_xml = table.get_xml_object()
            if table_xml is None:
                continue
            out_tables.append(table_xml)
        
        out_data = minidom.parseString(ET.tostring(out_root)).toprettyxml(indent="    ")

        with open(os.path.join(path), "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
            f.write('\n'.join(out_data.split('\n')[1:]))