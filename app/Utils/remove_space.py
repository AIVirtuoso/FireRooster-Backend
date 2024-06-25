# ruff: noqa
import datetime
import io
import os
from pprint import pprint
from random import sample
import logging as log

import librosa
import noisereduce as nr
import requests
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import split_on_silence

TEMP_FOLDER = "audios"


async def remove_noise(filename):
    # file_path.seek(0)
    data, rate = librosa.load(filename, sr=None)

    # Perform noise reduction
    reduced_noise_audio = nr.reduce_noise(y=data, sr=rate)

    # Construct the output filename by adding '-nc' before the file extension
    output_filename = filename.rsplit(".", 1)[0] + "_nc.wav"

    # Save the processed audio data as a .wav file
    sf.write(output_filename, reduced_noise_audio, rate, format="wav")
    
    os.remove(filename)
    print("========= Deleted original wav file ==========")
    
    return output_filename


def get_file_type(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower()


async def remove_silence_from_audio(audio_file_name, silence_thresh=-15, min_silence_len=1000):
    ###### Remove noise from the audio
    noise_reduced_filename = await remove_noise(audio_file_name)
    # file_type = get_file_type(noise_reduced_stream)
    # # print(file_type)

    # Load the noise-reducced audio file
    audio = AudioSegment.from_file(noise_reduced_filename, format="wav")
    ##################################

    # temp_folder_name = "temp_audio"
    # temp_file_name = f"{file}.wav"
    # temp_file_path = os.path.join(temp_folder_name, temp_file_name)
    # # print("file", file)

    # audio = AudioSegment.from_file(temp_file_path, format="wav")

    # Split the audio on silence
    audio_chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,  # minimum length of silence to be considered as a break
        silence_thresh=silence_thresh,  # silence threshold
        seek_step=10,  # step size for iterating over the audio
    )

    # Combine non-silent audio chunks
    combined_audio = AudioSegment.empty()
    for i, chunk in enumerate(audio_chunks):
        combined_audio += chunk

    print("===== Processing audio file =====")
    output_filename = audio_file_name.rsplit(".", 1)[0] + "_p.mp3"  # processed
    # Export the processed audio
    combined_audio.export(output_filename, format="mp3")
    
    
    os.remove(noise_reduced_filename)
    print("===== Deleted _nc.wav file =====")
    
    
    print("===== Finished processing audio file =====")
    
    return output_filename

async def process_archive_silence(audio_file_name):
    audio_file_name = await remove_silence_from_audio(audio_file_name, silence_thresh=-30)
    return audio_file_name


async def process_audio(audio_file_name):
    return await process_archive_silence(audio_file_name)
