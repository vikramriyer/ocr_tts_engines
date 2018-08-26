from utils import clean_xml
from yaml import load
import xml.etree.ElementTree as ET
import pdb
from settings import yaml_config
from daisy import BookPage


def test(filename):
    tag_config = load(open(yaml_config))
    tagged_xml = open(filename).read()
    tagged_xml = clean_xml(tagged_xml)
    root = ET.fromstring(tagged_xml)
    book = root.findall(tag_config['book'])[0]
    bodymatter = book.findall(tag_config['bodymatter'])[0]
    level1 = bodymatter.findall(tag_config['level1'])[0]
    content = level1.getchildren()
    page = BookPage(0)
    pages = []
    for tag in content:
        if tag.tag == tag_config["pagenum"]:
            pages.append(page)
            page = BookPage(0)
        else:
            page.add(tag)
    pages.append(page)
    pdb.set_trace()


if __name__ == "__main__":
    filename = "/home/chrizandr/annotated_xml/2done.xml"
    test(filename)
