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

if __name__ == '__main__':
    app.run()

# http://blog.luisrei.com/articles/flaskrest.html
# http://www.bogotobogo.com/python/python_http_web_services.php
# https://www.codementor.io/sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq
