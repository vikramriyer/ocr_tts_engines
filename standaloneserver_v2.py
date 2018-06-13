#!/usr/bin/python3

from flask import Flask, request, Response
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
import os, sys, time, datetime, requests, json, subprocess as sp
from flask_cors import CORS


# main program
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content_Type'
api = Api(app)
XML_DIR = "/home/iiit/data/ocr_tts_engines/project_files" # need to add this manually before running on any server
PROJECT_HOME = "../ttsdaisy_v4"

session = requests.Session()
session.trust_env = False

def get_current_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H%M%S')

def remove_white_spaces_from_book_name(bookname):
    booknames = bookname.split(' ')
    if len(booknames) > 1:
        booknames = '_'.join(booknames)
    else:
        booknames = ''.join(booknames)
    return booknames

@app.route("/hello")
def check_server_status():
    print("The server is running..")
    return jsonify({"Status": "running"})

@app.route("/run_daisy_pipeline/", methods=['POST'])
def run_daisy_pipeline():
    '''
    Runs the bash script from command line and returns
    '''
    if request.method == 'POST':
        print("Processing the request...")
        bookname = request.form['bookname']
        title = bookname
        print("The bookname is", bookname)
        bookname = remove_white_spaces_from_book_name(bookname)
        print("The bookname after processing is", bookname)
        xmldata = request.form['xmldata']
        bookid = request.form['bookid']
        book = bookname

        bookname = bookname + '_' + get_current_timestamp() + '.xml'
        filename = os.path.join(XML_DIR, bookname)
        filename = '_'.join(filename.split(' '))
        with open(filename, 'w') as xml_file:
            xml_file.write(xmldata)
        errors = ""

        # run the bash script
        try:
            print("Running the script...")
            sp.check_call(['./app_runner.sh', filename, book])
            print("Ran the code")

            # api call to mark the book as completed
            url = "http://10.2.16.111:8000/api/update_daisy_xml/"
            #url = "http://127.0.0.1:8000/api/update_daisy_xml/"
            payload = {"bookid": bookid, "data": xmldata}
            r = session.post(url, data=payload)
            print(r)

            # create a zip of the downloadable
            #url = "http://127.0.0.1:8000/download/?title=" + title
            url = "http://10.2.16.111:8000/download/?title=" + title
            r = session.get(url)
            print(r)
        except Exception as e:
            print("Got an exception: " + str(e))
            errors = str(e)

        # populate the dict
        response_dict = {}
        response_dict["name"] = "vikram"
        response_dict["status"] = "200"
        response_dict["errors"] = errors
        response_dict["book"] = bookname
        response_dict["book_status"] = "complete"

        return jsonify(response_dict)

@app.route("/get_ocr_output", methods=['POST'])
def get_ocr_output():
    '''
    - gets the image file
    - runs the ocr script that uses tesseract
    - returns ocr result which is text
    '''
    if request.method == 'POST':
        errors = ""
        print("Processing the request...")
        input_image = PROJECT_HOME + request.form['input_image']
        print("The image path: ",input_image)
        output_path = request.form['output_path']
        print("The output path: ",output_path)
        filename = input_image.split('/')[-1].split('.')[0]
        ocr_file = output_path + filename
        print("The OCR file is: ",ocr_file)

        try:
            bashCommand = "tesseract {} {}".format(input_image, ocr_file)
            print("The command run is: ", bashCommand)
            process = sp.Popen(bashCommand.split(), stdout=sp.PIPE)
            output, error = process.communicate()
        except Exception as e:
            print("Got an exception: " + str(e))
            errors = str(e)

        # populate the dict
        response_dict = {}
        with open(ocr_file + ".txt", "r") as f:
            response_dict["ocr_text"] = f.read()
        response_dict["status"] = "200"
        response_dict["errors"] = errors

        return jsonify(response_dict)

def run_cmd(cmd):
    return_dict = {}
    try:
        process = sp.Popen(cmd, stdout=sp.PIPE)
        output, error = process.communicate()
        return_dict["error"] = error
        return_dict["output"] = output
        print("The command {} was run successfully. ".format(cmd))
    except Exception as e:
        print("exception when running the command: {}, the error message is: {}".format(
            cmd, str(e)))
        return_dict["error"] = e
    return return_dict

def do_tts(text, audio_path):
    text = text.split(" ")
    bash_cmd = []
    bash_cmd.append("espeak")
    bash_cmd.append(" ".join(text))
    bash_cmd.append("-w {}".format(audio_path))
    print("TTS cmd: ",bash_cmd)
    response = run_cmd(bash_cmd)
    print("TTS Conversion successful. ")
    return response

def convert_wav_to_mp3(wav_file_path, mp3_file_path):
    # lame bash command: lame -V0 /path_to_input/file.wav /path_to_input/file.mp3
    bash_cmd = "lame -V0 {} {}".format(wav_file_path, mp3_file_path)
    response = run_cmd(bash_cmd.split())
    print("conversion successful. ")
    return response

def create_dir(dir_path):
    bash_cmd = "mkdir -p {}".format(dir_path)
    response = run_cmd(bash_cmd.split())
    return response

def validate_error(response):
    if response["error"] != None:
        raise Exception("ERROR: " + response["error"])

@app.route("/get_tts_output", methods=['POST'])
def get_tts_output():
    print("Received the call for getting TTS output. ")
    response_dict = {}
    if request.method == 'POST':
        input_text = request.form['input_text']
        print("The text to be converted to speech is: ",input_text)
        book = request.form['book']
        audio_number = request.form['audio_number']
        time_stamp = get_current_timestamp()
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            print(dir_path)
            wav_file = "./project_files/{}_{}/speech{}.wav".format(book, time_stamp, audio_number)
            mp3_file = "./project_files/{}_{}/speech{}.mp3".format(book, time_stamp, audio_number)
            response = create_dir("./project_files/{}_{}/".format(book, time_stamp))
            validate_error(response)
            response = do_tts(input_text, wav_file)
            validate_error(response)
            response = convert_wav_to_mp3(wav_file, mp3_file)
            validate_error(response)
            print("No Errors, way to go!")
            response_dict["audio_path"] = "./project_files/{}_{}/speech{}.mp3".format(
                book, time_stamp, audio_number)
            response_dict["bookname"] = book + '_' + time_stamp
        except Exception as e:
            print("Got an exception: " + str(e))
            errors = str(e)
            response_dict["errors"] = errors
    return jsonify(response_dict)

@app.route("/hello")
def hello():
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run()

# http://blog.luisrei.com/articles/flaskrest.html
# http://www.bogotobogo.com/python/python_http_web_services.php
# https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
