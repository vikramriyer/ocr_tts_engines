from utils import get_date, get_time_label


class NCC:
    def __init__(self, title, lang, num_pages, total_time):
        self.start_content = \
            u'<?xml version="1.0" encoding="utf-8"?>\n' +\
            u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "xhtml1-transitional.dtd">\n' +\
            u'<html xmlns="http://www.w3.org/1999/xhtml">\n' +\
            u'<head>\n' +\
            u'<title>{}</title>\n'.format(title) +\
            u'<meta name="dc:title" content="{}"/>\n'.format(title) +\
            u'<meta name="dc:format" content="Daisy 2.02"/>\n' +\
            u'<meta name="dc:identifier" content="CVIT_DTB"/>\n' +\
            u'<meta name="dc:publisher" content="TTSDaisy_v4"/>\n' +\
            u'<meta name="dc:date" content="{}" scheme="yyyy-mm-dd"/>\n'.format(get_date()) +\
            u'<meta name="dc:language" content="{}" scheme="ISO 639"/>\n'.format(lang) +\
            u'<meta name="ncc:charset" content="utf-8"/>\n' +\
            u'<meta name="ncc:footnotes" content="0"/>\n' +\
            u'<meta name="ncc:pageFront" content="0"/>\n' +\
            u'<meta name="ncc:pageNormal" content="{}"/>\n'.format(num_pages) +\
            u'<meta name="ncc:pageSpecial" content="0"/>\n' +\
            u'<meta name="ncc:prodNotes" content="0"/>\n' +\
            u'<meta name="ncc:sidebars" content="0"/>\n' +\
            u'<meta name="ncc:setInfo" content="1 of 1"/>\n' +\
            u'<meta name="ncc:tocItems" content="{}"/>\n'.format(num_pages) +\
            u'<meta name="ncc:totalTime" content="{}" scheme="hh:mm:ss"/>\n'.format(get_time_label(total_time, False)) +\
            u'<meta name="ncc:files" content="{}"/>\n'.format(3*num_pages + 1) +\
            u'<meta name="ncc:generator" content="TTSDaisy_v4"/>\n' +\
            u'<meta name="ncc:narrator" content="espeak"/>\n' +\
            u'<meta http-equiv="Content-type" content="text/html; charset=utf-8"/>\n' +\
            u'</head>\n<body>\n'

        self.content = []

        self.end_content = u'</body>\n</html>\n'

    def add_h_entry(self, page_id, smil_file):
        s = u'<h1 class="title" id="ncc_{}"><a href="{}#text_0">Pg:{}</a></h1>'.format(page_id, smil_file, page_id)
        self.content.append(s)

    def add_p_entry(self, page_id, smil_file):
        s = u'<span class="page-normal" id="ncc_{}"><a href="{}#text_0">Pg. {}</a></span>\n'
        s = s.format(page_id, smil_file, page_id)
        self.content.append(s)

    def gen_html(self):
        s = self.start_content + "\n".join(self.content) + self.end_content
        return s

    def write(self, output_file):
        f = open(output_file, "wb")
        f.write(self.gen_html().encode('utf-8'))
        f.close()
