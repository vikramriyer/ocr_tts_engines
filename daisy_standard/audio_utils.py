from mutagen.mp3 import MP3
import glob, os, shutil
import requests

def get_length(audio_path):
    audio = MP3(audio_path)
    length = audio.info.length
    return "%.3f" % length

def concatenate_audio(dir_path, output_fir_path, number):
    os.chdir(dir_path)
    destination = open(output_fir_path + '/concat1.mp3', 'wb')
    for file in glob.glob("*.mp3"):
        shutil.copyfileobj(open(file,'rb'), destination)
    destination.close()

def get_tts(input_text, bookname, audio_number):
    """
    get input_text, give a service call and get path of the audio file
    espeak is used for now, will be changed soon
    """
    session = requests.Session()
    session.trust_env = False
    audio_path = ''
    url = "http://10.2.16.111:5000/get_tts"
    payload = {
    "input_text": input_text,
    "book": bookname,
    "audio_number": audio_number
    }
    try:
        r = session.post(url, data=payload)
        print("Response: ", r.content.decode())
        j = json.loads(r.text)
        print(j)
        audio_path = get_pre_loaded_xml(j["ocr_text"], page_position, bookname, page_number)
    except Exception as e:
        print("Error message is: " + str(e))
    return audio_path

# print(get_length("/home/raavan/Music/Alaipaydue Kanada Adi - TamilWire.com.mp3"))
# concatenate_audio("/home/raavan/Music/")
# print(os.path.dirname(os.path.realpath(__file__)))
