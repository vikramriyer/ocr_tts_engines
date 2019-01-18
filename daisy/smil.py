from utils import get_time_label


class SMIL():
    def __init__(self, title, elapsed_time=0, time_in_smil=0):
        self.start_content = u'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n' +\
                             u'<!DOCTYPE smil PUBLIC "-//W3C//DTD SMIL 1.0//EN" "http://www.w3.org/TR/REC-SMIL/SMIL10.dtd" []>\n' +\
                             u'<smil>\n<head>\n<meta name="ncc:generator" content="TTSDaisy_v4" />\n' +\
                             u'<meta name="dc:format" content="Daisy 2.02" />\n<meta name="dc:identifier" content="CVIT_DTB" />\n' +\
                             u'<meta name="dc:title" content="{}" />\n<meta name="ncc:totalElapsedTime" content="{}" />\n' +\
                             u'<meta name="ncc:timeInThisSmil" content="{}" />\n<layout>\n<region id="txtView" />\n' +\
                             u'</layout>\n</head>\n<body>\n<seq dur="{}s">\n'
        self.start_content = self.start_content.format(title, get_time_label(elapsed_time),
                                                       get_time_label(time_in_smil), "%.3f" % time_in_smil)

        self.end_content = u"</seq>\n</body>\n</smil>"
        self.content = []
        self.elapsed_time = 0.00000

    def add_h_element(self, page_id, element_id, html_page, mp3_file, audio_len):
        s = u'<par endsync="last" id="smil_{}">\n'.format(element_id)
        s += u'<text id="text_{}" src="{}#header_{}" />\n'.format(element_id, html_page, element_id)
        s += u'<audio src="{}" id="aud_{}" clip-begin="npt={}s" clip-end="npt={}s" />\n'.format(
             mp3_file, element_id, "%.3f" % self.elapsed_time, "%.3f" % (self.elapsed_time + audio_len)
        )
        s += u'</par>\n'
        self.elapsed_time += audio_len
        self.content.append(s)

    def add_p_element(self, page_id, element_id, html_page, mp3_file, audio_len):
        s = u'<par endsync="last" id="smil_{}">\n'.format(element_id)
        s += u'<text id="text_{}" src="{}#para_{}" />\n'.format(element_id, html_page, element_id)
        s += u'<audio src="{}" id="aud_{}" clip-begin="npt={}s" clip-end="npt={}s" />\n'.format(
             mp3_file, element_id, "%.3f" % self.elapsed_time, "%.3f" % (self.elapsed_time + audio_len)
        )
        s += u'</par>\n'
        self.elapsed_time += audio_len
        self.content.append(s)

    def gen_smil(self):
        s = self.start_content + "\n".join(self.content) + self.end_content
        return s

    def write(self, output_file):
        f = open(output_file, "wb")
        f.write(self.gen_smil().encode('utf-8'))
        f.close()


def make_smil(page, audio_lengths, title, elapsed_time, directory, tag_config):
    html_page = title.lower() + '_pg' + str(page.pagenum) + ".html"
    mp3_file = title.lower() + '_pg' + str(page.pagenum) + ".mp3"
    doc_name = title.lower() + '_pg' + str(page.pagenum) + ".smil"

    smil_page = SMIL(title, elapsed_time, sum(audio_lengths))
    for i, element in enumerate(page.content):
        if element.tag == tag_config["h1"]:
            smil_page.add_h_element(page.pagenum, i, html_page, mp3_file, audio_lengths[i])
        elif element.tag == tag_config["p"]:
            smil_page.add_p_element(page.pagenum, i, html_page, mp3_file, audio_lengths[i])

    smil_page.write(directory + doc_name)
