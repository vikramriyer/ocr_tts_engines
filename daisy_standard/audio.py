from mutagen.mp3 import MP3

from utils import random_alpha_numeric_generator
from utils import cleanup, run_cmd


def make_audio(page, title, id_, directory):
    rand = random_alpha_numeric_generator()
    audio_name = title.lower() + '_pg' + str(id_) + ".mp3"
    tempfile = directory + rand + ".txt"
    output_file = directory + audio_name
    audio_files = []

    for i, element in enumerate(page):
        with open(directory + rand + str(i), "w") as f:
            f.write(element.text)
            f.close()
        do_tts(directory + rand + str(i),
               directory + rand + str(i) + ".wav")
        audio_files.append(directory + rand + str(i))

    convert_wav_to_mp3(audio_files)
    audio_lengths = get_length(audio_files)

    with open(tempfile, "w") as f:
        for file_ in audio_files:
            f.write("file '{}.mp3'\n".format(file_))
        f.close()

    merge_audio_files(audio_files, output_file, tempfile)
    cleanup(directory, rand)

    return audio_lengths, audio_files


def merge_audio_files(audio_files, output_file, tempfile):
    command = "ffmpeg -f concat -safe 0 -i {} -c copy {}".format(tempfile, output_file)
    response = run_cmd(command.split())
    return response


def do_tts(text, audio_path):
    """Convert text into audio files."""
    # espeak -ven-us+f1 -s 150 'Hello, how are you?' -w /home/chris/new.mp3
    bash_cmd = []
    bash_cmd.append("espeak")
    bash_cmd.append("-ven-us+f1")
    bash_cmd.append("-s 150")
    bash_cmd.append("-f " + text)
    bash_cmd.append("-w {}".format(audio_path))
    response = run_cmd(bash_cmd)
    return response


def get_length(audio_files):
    lengths = []
    for audio_file in audio_files:
        audio = MP3(audio_file + ".mp3")
        lengths.append(audio.info.length)

    return lengths


def convert_wav_to_mp3(audio_files):
    for audio_file in audio_files:
        bash_cmd = "lame -V0 {}.wav {}.mp3".format(audio_file, audio_file)
        response = run_cmd(bash_cmd.split())
    return response
