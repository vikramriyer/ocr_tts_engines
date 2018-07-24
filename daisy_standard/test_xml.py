from utils import clean_xml
import xml.etree.ElementTree as ET


def test(filename):
	tagged_xml = open(filename).read()
	tagged_xml = clean_xml(tagged_xml)
	root = ET.fromstring(tagged_xml)


if __name__ == "__main__":
	filename = "/home/iiit/corrected_ocr/7.xml"
	test(filename)