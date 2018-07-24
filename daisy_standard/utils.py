import random
import datetime
import time
import subprocess as sp
from xml.sax.saxutils import escape, unescape
# import xml.etree.ElementTree as ET
import re
import pdb
from lxml import etree


def random_alpha_numeric_generator():
    """Random 8 character string."""
    return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(8))


def create_dir(dir_path):
    """Create directory."""
    bash_cmd = 'mkdir -p "{}"'.format(dir_path)
    response = run_cmd(bash_cmd.split())
    return response


def clean_xml(tagged_xml, reverse=False):
    html_escape_table = {
        "&": "&amp;"
    }
    if reverse:
        html_unescape_table = {v: k for k, v in html_escape_table.items()}
        for k, v in html_unescape_table.items():
            tagged_xml = tagged_xml.replace(k, v)
        tagged_xml = tagged_xml.replace("&lt;", "< ")
        return tagged_xml
    else:
        for k, v in html_escape_table.items():
            tagged_xml = tagged_xml.replace(k, v)
        tagged_xml = re.sub(r'<\s', "&lt; ", tagged_xml)
        return tagged_xml


def get_date():
    """Get date in YYYY-MM-DD format."""
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_current_timestamp():
    """Get current timestamp in YYYY-MM-DD_HHMMSS format."""
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')


def run_cmd(cmd):
    """Run a give bash command on shell."""
    return_dict = {}
    try:
        process = sp.Popen(" ".join(cmd), stdout=sp.PIPE, shell=True)
        output, error = process.communicate()
        return_dict["error"] = error
        return_dict["output"] = output
    except Exception as e:
        print("exception when running the command: {}, the error message is: {}".format(
            cmd, str(e)))
        return_dict["error"] = e
    return return_dict


def cleanup(directory, keyword):
    """Delete all files that contain a keyword from directory."""
    bash_cmd = "rm " + directory + '*' + keyword + "*"
    response = run_cmd(bash_cmd.split())
    return response


def get_time_label(elapsed_time, milliseconds=True):
    """Convert seconds from float to HH:MM:SS.sss format."""
    time_stamp = time.strftime("%H:%M:%S", time.gmtime(int(elapsed_time)))
    if not milliseconds:
        return time_stamp
    diff = "%.3f" % (elapsed_time - int(elapsed_time))
    return time_stamp + diff[1::]


if __name__ == "__main__":
    input_file = "sample.xml"
    tagged_xml = open(input_file).read()
    tagged_xml = clean_xml(tagged_xml)
    tagged_xml = tagged_xml.encode()
    parser = etree.XMLParser(encoding='UTF-8', recover=True)
    root = etree.fromstring(tagged_xml, parser=parser)
    # print(etree.tostring(root).decode("utf-8"))
    pdb.set_trace()
