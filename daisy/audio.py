"""Audio generation."""
import contextlib
import httplib2
# from mutagen.mp3 import MP3
import wave
import librosa

from urllib.parse import urlencode

from utils import cleanup
from utils import random_alpha_numeric_generator
from utils import run_cmd
from text import clean_str
import pdb

h_mary = httplib2.Http()


class TTSEngine(object):
    """TTS Engine."""

    def __init__(self, tts_call):
        """Init.

        Parameters:
            tss_call: [type function] Main TTS function.
            [
                Function definition:
                    A function that takes a text file and
                    outputs the audio in a .wav file
                Parameters:
                    text_path: [class String] Path to file containing text to convert.
                    audio_path: [class String] Path to output .wav file.
            ]

        """
        self.tts = tts_call

    def make_audio(self, page, title, directory):
        """Generate audio files."""
        rand = random_alpha_numeric_generator()
        output_file = directory + title.lower() + '_pg' + str(page.pagenum)

        self.audio_files = []
        self.audio_lengths = []

        for i, element in enumerate(page.content):
            with open(directory + rand + str(i), "w") as f:
                f.write(element.text)
                f.close()
            self.do_tts(directory + rand + str(i),
                        directory + rand + str(i) + ".wav")

            self.audio_files.append(directory + rand + str(i))

        self.get_lengths()

        self.merge_audio_files(directory + rand)
        self.convert_wav_to_mp3(directory + rand, output_file)
        cleanup(directory, rand)

        return self.audio_lengths, self.audio_files

    def merge_audio_files(self, output_file):
        """Merge audio files."""
        # cd  command = "ffmpeg -f concat -safe 0 -i {} -c copy {}".format(tempfile, output_file)
        command = "sox " + " ".join([x + ".wav" for x in self.audio_files]) + \
                  " " + output_file + ".wav"
        response = run_cmd(command.split())
        return response

    def do_tts(self, text_path, audio_path):
        """Convert text into audio files."""
        # espeak -ven-us+f1 -s 150 'Hello, how are you?' -w /home/chris/new.mp3
        self.tts(text_path, audio_path)

    def get_lengths(self):
        """Find lenght of MP3 file."""
        # for audio_file in self.audio_files:
        #     audio = MP3(audio_file + ".mp3")
        #     lengths.append(audio.info.length)
        for audio_file in self.audio_files:
            duration = librosa.get_duration(filename=audio_file+".wav")
            self.audio_lengths.append(duration)

    def convert_wav_to_mp3(self, input_file, audio_file):
        """Convert .wav to .mp3."""
        bash_cmd = "lame -V0 {}.wav {}.mp3".format(input_file, audio_file)
        response = run_cmd(bash_cmd.split())
        return response


def espeaktts(text_path, audio_path):
    """Espeak TTS caller."""
    bash_cmd = []
    bash_cmd.append("espeak")
    bash_cmd.append("-ven-us+f1")
    bash_cmd.append("-s 150")
    bash_cmd.append("-f " + text_path)
    bash_cmd.append("-w {}".format(audio_path))
    response = run_cmd(bash_cmd)
    return response


def marytts(text, audio_path):
    """Mary TTS caller."""
    # Mary server info
    global h_mary
    mary_host = "localhost"
    mary_port = "59125"

    # Input text
    input_text = clean_str(open(text).read().strip())

    # Build the query
    query_hash = {"INPUT_TEXT": input_text,
                  "INPUT_TYPE": "TEXT",
                  "LOCALE": "en_US",
                  "VOICE": "cmu-slt-hsmm",
                  "OUTPUT_TYPE": "AUDIO",
                  "AUDIO": "WAVE",
                  }
    query = urlencode(query_hash)
    # print("query = \"http://%s:%s/process?%s\"" % (mary_host, mary_port, query))

    try:
        resp, content = h_mary.request("http://%s:%s/process?" % (mary_host, mary_port), "POST", query)
    except ConnectionRefusedError:
        print("MaryTTS is offline, please start the server on {}:{}".format(mary_host, mary_port))
        return None

    #  Decode the wav file or raise an exception if no wav files
    if (resp["content-type"] == "audio/x-wav"):
        # Write the wav file
        f = open(audio_path, "wb")
        f.write(content)
        f.close()
        return "Done"
    else:
        raise OSError("No output generated")


if __name__ == "__main__":
    sample_text = "samples/test.txt"
    output = "samples/test.wav"
    marytts(sample_text, output)
