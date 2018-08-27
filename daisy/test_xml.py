from utils import clean_xml
from yaml import load
import xml.etree.ElementTree as ET
import pdb
from settings import yaml_config
from daisy import BookPage
import numpy as np


def test(filename):
    tag_config = load(open(yaml_config))
    tagged_xml = open(filename).read()
    tagged_xml = clean_xml(tagged_xml)
    root = ET.fromstring(tagged_xml)
    book = root.findall(tag_config['book'])[0]
    bodymatter = book.findall(tag_config['bodymatter'])[0]
    level1 = bodymatter.findall(tag_config['level1'])[0]
    content = level1.getchildren()

    pagenum = 0
    page = BookPage(0)
    pages = []
    page_ids = []

    for tag in content:
        if tag.tag == tag_config["pagenum"]:
            pg_id = int(tag.attrib["id"].strip("page"))
            page_ids.append(pg_id)
            pagenum += 1
            # if pagenum != pg_id:
            #     pdb.set_trace()
            pages.append(page)
            page = BookPage(0)
        else:
            page.add(tag)
    pages.append(page)
    page_ids = np.array(page_ids)
    ids = np.arange(len(pages))[1::]
    diff = ids - page_ids
    uvals = np.unique(diff)

    for val in uvals:
        if val != 0:
            pg = (diff == val).nonzero()[0][0]
            print("Jump from pg {} to pg {}".format(page_ids[pg-1], page_ids[pg]))
    pdb.set_trace()


if __name__ == "__main__":
    filename = "/home/chris/annotated_xml/9.xml"
    test(filename)
