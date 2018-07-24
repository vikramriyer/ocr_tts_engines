from yaml import load
import xml.etree.ElementTree as ET
from lxml import etree
import datetime

from html import make_html
from audio import make_audio
from smil import make_smil
from ncc import NCC
from utils import get_current_timestamp, create_dir, clean_xml
import re
import pdb


class DaisyBook:
    """Daisy Audio Book Class."""
    def __init__(self, yaml_file, output_dir, xml_file=None):
        self.output_folder = output_dir
        self.tag_config = load(open(yaml_file))
        if xml_file:
            self.read(xml_file)
        self.smil_headers = []
        self.elapsed_time = 0
        self.audio_files = []
        self.html_files = []

    def read(self, input_file):
        print("Reading data from XML file and parsing...")
        self.tagged_xml = open(input_file).read()
        self.tagged_xml = clean_xml(self.tagged_xml)
        self.title, self.pages = self.parse_xml()
        pdb.set_trace()
        self.title = re.sub(r'[^0-9a-zA-Z_-]', "", self.title)

    def parse_xml(self):
        """Parse tagged XML."""
        parser = etree.XMLParser(encoding='UTF-8', recover=True)
        root = etree.fromstring(self.tagged_xml.encode(), parser=parser)
        book = root.findall(self.tag_config['book'])[0]
        frontmatter = book.findall(self.tag_config['frontmatter'])[0]
        title = frontmatter.findall(self.tag_config['doctitle'])[0].text
        bodymatter = book.findall(self.tag_config['bodymatter'])[0]
        level1 = bodymatter.findall(self.tag_config['level1'])[0]

        content = level1.getchildren()
        pdb.set_trace()
        pages = []
        page = []
        pid = 0
        for tag in content:
            if tag.tag == self.tag_config["pagenum"]:
                print("Page number {}".format(pid))
                pid += 1
                pages.append(page)
                page = []
            else:
                page.append(tag)
        pages.append(page)
        return title, pages[1::]

    def build(self):
        """Create daisy book."""
        print("Building DaisyBook...")
        self.folder_name = self.title + '_' + get_current_timestamp() + '/'
        create_dir(self.output_folder + self.folder_name)
        print("All files stored in ", self.output_folder+self.folder_name)

        self.elapsed_time = 0
        print("Processing Pages....")
        for i, page in enumerate(self.pages):
            print("----Generating [HTML] file; Pg {}".format(i))
            html_file = make_html(page, self.title, i, self.output_folder+self.folder_name,
                                  self.tag_config)
            print("----Generating [MP3] file; Pg {}".format(i))
            audio_lengths, audio_file = make_audio(page, self.title, i,
                                                   self.output_folder+self.folder_name)
            print("----Generating [SMIL] file; Pg {}".format(i))
            smil_header = make_smil(page, i, audio_lengths, self.title, self.elapsed_time,
                                    self.output_folder+self.folder_name, self.tag_config)

            self.audio_files.append(audio_file)
            self.html_files.append(html_file)
            self.smil_headers.append(smil_header)

            self.elapsed_time += sum(audio_lengths)
        print("----Generating [NCC] file; Book: {}".format(self.title))
        self.make_ncc()

    def make_ncc(self):
        ncc_file = NCC(title=self.title, lang="en", num_pages=len(self.pages), total_time=self.elapsed_time)
        for i, page in enumerate(self.pages):
            smil_file = self.title.lower() + "_pg{}.smil".format(i)
            if page[0].tag == self.tag_config["h1"]:
                ncc_file.add_h_entry(i, smil_file)
            elif page[0].tag == self.tag_config["p"]:
                ncc_file.add_p_entry(i, smil_file)

        self.ncc_file = ncc_file
        self.ncc_file.write(self.output_folder + self.folder_name + "ncc.html")


if __name__ == "__main__":
    from settings import output_folder, yaml_config
    Book = "sample.xml"
    Dtb = DaisyBook(yaml_config, output_folder, Book)
    Dtb.build()
