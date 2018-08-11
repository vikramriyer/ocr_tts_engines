from yaml import load
from lxml import etree

from html import make_html
from audio import make_audio
from smil import make_smil
from ncc import NCC
from utils import get_current_timestamp, create_dir, clean_xml
import re
# import pdb


class BookPage:
    def __init__(self, pagenum):
        self.content = []
        self.pagenum = pagenum

    def add(self, item):
        self.content.append(item)


class DaisyBook:
    """Daisy Audio Book Class."""
    def __init__(self, yaml_file, output_dir, xml_file=None):
        self.output_folder = output_dir
        self.tag_config = load(open(yaml_file))
        if xml_file:
            self.read(xml_file)
        self.elapsed_time = 0
        self.pages = []
        self.title = ""
        self.num_pages = 0
        self.smil_headers = []
        self.audio_files = []
        self.html_files = []

    def read(self, input_file):
        """
        Read the input file and extract all book pages from Tagged XML.
        Parameters:
            input_file: [class String] Path to the input file.
        """
        self.tagged_xml = open(input_file).read()
        self.tagged_xml = clean_xml(self.tagged_xml)
        self.parse_xml()
        self.title = re.sub(r'[^0-9a-zA-Z_-]', "", self.title)

    def extract_content(self, root):
        """
        Extract the book contents from the XML Tree
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
                print("Page number {}".format(self.num_pages))
                self.num_pages += 1
                self.pages.append(page)
                page = BookPage(self.num_pages)
            else:
                page.add(tag)
        self.pages.append(page)

    def build(self):
        """Build daisy book."""

        print("Building DaisyBook...")
        self.folder_name = self.title + '_' + get_current_timestamp() + '/'
        create_dir(self.output_folder + self.folder_name)
        print("All files stored in ", self.output_folder+self.folder_name)

        self.elapsed_time = 0

        print("Processing Pages....")
        for page in enumerate(self.pages):

            print("----Generating [HTML] file; Pg {}".format(page.pagenum))
            html_file = make_html(page, self.title, self.output_folder+self.folder_name,
                                  self.tag_config)

            print("----Generating [MP3] file; Pg {}".format(page.pagenum))
            audio_lengths, audio_file = make_audio(page, self.title,
                                                   self.output_folder+self.folder_name)

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
        for i, page in enumerate(self.pages):
            smil_file = self.title.lower() + "_pg{}.smil".format(i)
            if page[0].tag == self.tag_config["h1"]:
                ncc_file.add_h_entry(i, smil_file)
            elif page[0].tag == self.tag_config["p"]:
                ncc_file.add_p_entry(i, smil_file)

        self.ncc_file = ncc_file
        self.ncc_file.write(self.output_folder + self.folder_name + self.title + "_ncc.html")


if __name__ == "__main__":
    from settings import output_folder, yaml_config
    Book = "samples/sample.xml"
    Dtb = DaisyBook(yaml_config, output_folder, Book)
    Dtb.build()
