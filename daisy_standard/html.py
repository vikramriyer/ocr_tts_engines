"""Code for generating HTML files."""


class HTMLPage():
    """Class for creating a simple HTML file for page text."""
    def __init__(self):
        self.start_content = u'<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n' + \
                             u'</head>\n<body>\n<div class="page">\n'
        self.end_content = u"</div>\n</body>\n</html>"
        self.content = []

    def add_h_tag(self, content, element_id):
        s = u'<h1 class="title" id="header_{}">{}</h1>\n'
        s = s.format(element_id, content)
        self.content.append(s)

    def add_p_tag(self, content, element_id):
        s = u'<p><span class="page-normal" id="para_{}">{}</span></p>\n'
        s = s.format(element_id, content)
        self.content.append(s)

    def gen_html(self):
        s = self.start_content + "\n".join(self.content) + self.end_content
        return s

    def write(self, output_file):
        f = open(output_file, "wb")
        # output = self.clean(self.gen_html())
        f.write(self.gen_html().encode('utf-8'))
        f.close()


def make_html(page, title, page_id, directory, tag_config):
    """Make HTML page for a given parsed page with ID."""
    doc_name = title.lower() + '_pg' + str(page_id) + ".html"
    html_page = HTMLPage()
    for i, element in enumerate(page):
        if element.tag == tag_config["h1"]:
            html_page.add_h_tag(clean_content(element.text), i)
        elif element.tag == tag_config["p"]:
            html_page.add_p_tag(clean_content(element.text), i)
    html_page.write(directory + doc_name)


def clean_content(content):
    content = content.split()
    content = " ".join(content)
    content = content.split('.')
    content = ".\n".join(content)
    return content
