"""Test code for testing XML."""
import pdb
from daisy import BookPage
import numpy as np
import re
from settings import yaml_config
import subprocess as sp
import sys
from utils import clean_xml
import xml.etree.ElementTree as ET
from yaml import load


def process_type(error):
    """Find the type of error."""
    words = error.split(":")
    if words[2].strip() == "parser error":
        if len(words) > 4:
            return words[3].strip()
    return "Other"


def test_linter(filepath):
    """Check using XML Linter."""
    p = sp.Popen(['xmllint', filepath], stdout=sp.PIPE, stderr=sp.PIPE)
    output = p.communicate()[1].decode('utf-8')
    output = output.split("\n")

    start = 0
    cleaned_output = {}
    type_ = process_type(output[0])
    for i, s in enumerate(output[1::]):
        if filepath in s:
            error = "\n".join(output[start:i+1])
            start = i
            if type_ in cleaned_output:
                cleaned_output[type_].append(error)
            else:
                cleaned_output[type_] = [error]
            type_ = process_type(s)

    error = "\n".join(output[start:i+1])
    if type_ in cleaned_output:
        cleaned_output[type_].append(error)
    else:
        cleaned_output[type_] = [error]
    if 'Opening and ending tag mismatch' in cleaned_output:
        for x in cleaned_output['Opening and ending tag mismatch']:
            print("[!Error] " + x.strip())
    return None


def test_parser(filepath, pagenums):
    """Code to check the XML file."""
    tag_config = load(open(yaml_config))
    tagged_xml = open(filepath).read()
    tagged_xml = clean_xml(tagged_xml)
    try:
        root = ET.fromstring(tagged_xml)
    except ET.ParseError as err:
        print("[!Error] Error parsing XML file: {}".format(err))
        return 0
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
            pages.append(page)
            page = BookPage(0)
        else:
            page.add(tag)
    pages.append(page)
    page_ids = np.array(page_ids)
    counted = len(page_ids)

    for i in range(len(page_ids)-1):
        if page_ids[i+1] - page_ids[i] != 1:
            print("[!Error] Page Jump from pg {} to pg {}, unclosed tags present in pages.".format(page_ids[i], page_ids[i+1]))

    if pagenums != counted:
        print("\n\t[!Error] There were {} pagenum tags found, parser only parsed {} pages,".format(pagenums, counted),
              " please check skipped over pages for open tags.\n")

    return counted


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        print("\nUsage: \n\n\tpython test_xml.py [filepath]\n")
        sys.exit(0)

    f = open(filepath).read()
    pagenums = len([x for x in re.finditer('</pagenum>', f)])
    test_linter(filepath)
    counted = test_parser(filepath, pagenums)
    print("[!Parser] successfully parsed {} pages".format(counted))
    if counted == pagenums:
        print("\n\t[!Success] There were {} pagenum tags found, parser parsed {} pages,".format(pagenums, counted))
