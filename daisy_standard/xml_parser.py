import xml.etree.ElementTree as ET
from django.conf import settings
from yaml import load, dump, Loader
import audio_utils, requests, time, datetime

# init
with open('/data/django_u/django_projects/code_along/ttsdaisy/ttsdaisy_v4/daisy_standard/tag_config.yaml') as stream:
    tag_config = load(stream)

def get_current_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')

def build_smil():
    pass

def build_html():
    pass

def create_mp3(audio_list, h1_number):
    for text in audio_list:
        audio_utils.get_tts(text, bookname, h1_number)
    audio_utils.concatenate_audio()

def parse_xml(tagged_xml, language="en"):
    # tagged_xml = "/data/django_u/django_projects/code_along/ttsdaisy/ttsdaisy_v4/daisy_standard/Whats_in_the_name_2018-05-09_104006.xml"
    tagged_xml = "/data/django_u/project_files/Whats_in_the_name_2018-05-09_104006.xml"
    bookname = "demo101"
    with open(tagged_xml) as f:
        tree = ET.parse(f)
    root = tree.getroot()

    # parsing the required elements
    head = root.findall(tag_config['head'])[0]
    book = root.findall(tag_config['book'])[0]
    bodymatter = book.findall(tag_config['bodymatter'])[0]
    level1 = bodymatter.findall(tag_config['level1'])[0]

    # parsing logic
    flag = False
    pagenum = -1
    audio_content = []
    counter = 1
    for x in level1.getchildren():
        if x.tag == tag_config['pagenum']:
            # pagenum = int(x.text)
            pass
        elif x.tag == tag_config['h1'] and not flag:
            if audio_content != []:
                create_mp3(audio_content, counter)
                counter += 1
                audio_content = []
            flag = True
            audio_content.append(x.text)
        elif x.tag == tag_config['p'] and flag:
            audio_content.append(x.text)
        elif x.tag == tag_config['h1'] and flag:
            if audio_content != []:
                create_mp3(audio_content, counter)
                counter += 1
                audio_content = []
            flag = False
            audio_content.append(x.text)
        elif x.tag == tag_config['p'] and not flag:
            audio_content.append(x.text)
    print(audio_content)

# parse_xml("abc")

# TODO: Information required in general to run TTS
'''
0. path of the input file
1. language (need to get this via http)
2. all the specific content from the xml (xml)
3. tagged_xml to save the results to (http or custom funtion depending on book name and language)
4. name of the book and author (xml and http, prefer http as the annotator might have done some mistake in writing)
'''
