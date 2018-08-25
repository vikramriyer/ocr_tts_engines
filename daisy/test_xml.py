from utils import clean_xml
import xml.etree.ElementTree as ET
import pdb


def test(filename):
    tagged_xml = open(filename).read()
    tagged_xml = clean_xml(tagged_xml)
    ET.fromstring(tagged_xml)
    pdb.set_trace()


if __name__ == "__main__":
    filename = "/home/chris/annotated_xml/1done.xml"
    test(filename)
