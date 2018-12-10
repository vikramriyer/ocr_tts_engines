"""Daisy book code."""
from lxml import etree
from yaml import load

from audio import TTSEngine
from audio import espeaktts, maryttsenglish, maryttstelugu
from html import make_html
from ncc import NCC
from smil import make_smil
from utils import get_current_timestamp, create_dir, clean_xml
import re
import pdb


class BookPage(object):
    """Book page class."""

    def __init__(self, pagenum):
        """Init."""
        self.content = []
        self.pagenum = pagenum

    def add(self, item):
        """Add new item to page."""
        if item.text.strip():
            self.content.append(item)


class DaisyBook(object):
    """Daisy Audio Book Class."""

    def __init__(self, yaml_file, output_dir, tts, xml_file=None):
        """Init."""
        self.output_folder = output_dir
        self.tag_config = load(open(yaml_file))
        self.pages = []
        self.title = ""
        self.num_pages = 0
        self.elapsed_time = 0
        self.smil_headers = []
        self.audio_files = []
        self.html_files = []
        self.tts = tts
        if xml_file:
            self.read(xml_file)

    def read(self, input_file):
        """Read the input file and extract all book pages from Tagged XML.

        Parameters:
            input_file: [class String] Path to the input file.

        """
        print("Parsing xml file : {}".format(input_file))
        self.tagged_xml = open(input_file).read()
        self.tagged_xml = clean_xml(self.tagged_xml)
        self.parse_xml()
        self.title = re.sub(r'[^0-9a-zA-Z_-]', "", self.title)

    def extract_content(self, root):
        """Extract the book contents from the XML Tree.

        Parameters:
            root: [class lxml.etree.ElementTree] Root node of XML tree.

        """
        book = root.findall(self.tag_config['book'])[0]
        frontmatter = book.findall(self.tag_config['frontmatter'])[0]
        self.title = frontmatter.findall(self.tag_config['doctitle'])[0].text
        bodymatter = book.findall(self.tag_config['bodymatter'])[0]
        level1 = bodymatter.findall(self.tag_config['level1'])[0]
        return level1.getchildren()

    def parse_xml(self):
        """Parse tagged XML."""
        parser = etree.XMLParser(encoding='UTF-8', ns_clean=True, recover=True)
        root = etree.fromstring(self.tagged_xml.encode(), parser=parser)
        content = self.extract_content(root)
        page = BookPage(self.num_pages)
        for tag in content:
            if tag.tag == self.tag_config["pagenum"]:
                self.num_pages += 1
                self.pages.append(page)
                page = BookPage(self.num_pages)
            else:
                page.add(tag)
        self.pages.append(page)
        self.pages = self.pages[1::]

    def build(self):
        """Build daisy book."""
        print("Building DaisyBook...")
        self.folder_name = self.title + '_' + get_current_timestamp() + '/'
        create_dir(self.output_folder + self.folder_name)
        print("All files stored in ", self.output_folder+self.folder_name)

        self.elapsed_time = 0
        print("Processing Pages....")
        for page in self.pages:
            if len(page.content) == 0:
                continue

            print("----Generating [HTML] file; Pg {}".format(page.pagenum))
            html_file = make_html(page, self.title, self.output_folder+self.folder_name,
                                  self.tag_config)

            print("----Generating [MP3] file; Pg {}".format(page.pagenum))
            audio_lengths, audio_file = self.tts.make_audio(page, self.title,
                                                            self.output_folder+self.folder_name)

            # pdb.set_trace()
            print("----Generating [SMIL] file; Pg {}".format(page.pagenum))

            smil_header = make_smil(page, audio_lengths, self.title, self.elapsed_time,
                                    self.output_folder+self.folder_name, self.tag_config)

            self.audio_files.append(audio_file)
            self.html_files.append(html_file)
            self.smil_headers.append(smil_header)

            self.elapsed_time += sum(audio_lengths)
        print("----Generating [NCC] file; Book: {}".format(self.title))
        self.make_ncc()

    def make_ncc(self):
        """Create NCC index file for DTB player."""
        ncc_file = NCC(title=self.title, lang="en", num_pages=len(self.pages), total_time=self.elapsed_time)
        for page in self.pages:
            if len(page.content) == 0:
                continue

            smil_file = self.title.lower() + "_pg{}.smil".format(page.pagenum)
            if page.content[0].tag == self.tag_config["h1"]:
                ncc_file.add_h_entry(page.pagenum, smil_file)
            elif page.content[0].tag == self.tag_config["p"]:
                ncc_file.add_p_entry(page.pagenum, smil_file)

        self.ncc_file = ncc_file
        self.ncc_file.write(self.output_folder + self.folder_name + "ncc.html")


if __name__ == "__main__":
    from settings import output_folder, yaml_config
<<<<<<< HEAD
    Book = "/home/chris/audio_books/Telugu_Five.xml"
    tts = TTSEngine(maryttstelugu)
=======
    Book = "test.xml"
    tts = TTSEngine(marytts)
>>>>>>> f8765ea19ecb92c0519cf85bd61ea2eb88247302
    Dtb = DaisyBook(yaml_config, output_folder, tts, Book)
    Dtb.build()
