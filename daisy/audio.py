from mutagen.mp3 import MP3

from utils import random_alpha_numeric_generator
from utils import cleanup, run_cmd

import httplib2
from urllib.parse import urlencode, quote

import pygame
import math


class TTSEngine:
    def __init__(self, tts_call):
        """
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
        rand = random_alpha_numeric_generator()
        audio_name = title.lower() + '_pg' + str(page.pagenum) + ".mp3"
        tempfile = directory + rand + ".txt"
        output_file = directory + audio_name
        self.audio_files = []

        for i, element in enumerate(page.content):
            with open(directory + rand + str(i), "w") as f:
                f.write(element.text)
                f.close()
            self.do_tts(directory + rand + str(i),
                        directory + rand + str(i) + ".wav")
            self.audio_files.append(directory + rand + str(i))

        self.audio_lengths = self.get_lengths()
        self.convert_wav_to_mp3()

        with open(tempfile, "w") as f:
            for file_ in self.audio_files:
                f.write("file '{}.mp3'\n".format(file_))
            f.close()

        self.merge_audio_files(output_file, tempfile)
        cleanup(directory, rand)

        return self.audio_lengths, self.audio_files

    def merge_audio_files(self, audio_files, output_file, tempfile):
        command = "ffmpeg -f concat -safe 0 -i {} -c copy {}".format(tempfile, output_file)
        response = run_cmd(command.split())
        return response

    def do_tts(self, text_path, audio_path):
        """Convert text into audio files."""
        # espeak -ven-us+f1 -s 150 'Hello, how are you?' -w /home/chris/new.mp3
        self.tts(text_path, audio_path)

    def get_lengths(self):
        lengths = []
        for audio_file in self.audio_files:
            audio = MP3(audio_file + ".mp3")
            lengths.append(audio.info.length)

        return lengths

    def convert_wav_to_mp3(self):
        for audio_file in self.audio_files:
            bash_cmd = "lame -V0 {}.wav {}.mp3".format(audio_file, audio_file)
            response = run_cmd(bash_cmd.split())
        return response


def espeaktts(text_path, audio_path):
    bash_cmd = []
    bash_cmd.append("espeak")
    bash_cmd.append("-ven-us+f1")
    bash_cmd.append("-s 150")
    bash_cmd.append("-f " + text_path)
    bash_cmd.append("-w {}".format(audio_path))
    response = run_cmd(bash_cmd)
    return response


def marytts(text, audio_path):
    pass
