"""
TO DO:
 - train good models
 - figure out a way to detect "mp3"
 - run on CommandHandlerThread (close stream when recognized -> run sarmata -> open stream again)
"""

import pyaudio as pa
import numpy as np
from python_speech_features import mfcc, delta


CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100
DEVICE_INDEX = 0
INPUT = True
LEVEL_THRESHOLD = 0.0005
LIKE_THRESHOLD = -40


def computeMFCC(data, fs):

    cfg = {
        'window_length': 0.020,
        'window_step': 0.01,
        'cepstrum_number': 13,
        'filter_number': 26,
        'preemphasis_filter': 0.97,
        'window_function': 'hamming',
        'delta_sample': 4,
        'use_delta': True,
        'delta_delta_sample': 4,
        'use_delta_delta': True
    }

    fft_size = 2
    while fft_size < cfg['window_length'] * fs:
        fft_size *= 2

    data_mfcc = mfcc(data, samplerate=fs, nfft=fft_size, winlen=cfg['window_length'], winstep=cfg['window_step'],
                     numcep=cfg['cepstrum_number'], nfilt=cfg['filter_number'], preemph=cfg['preemphasis_filter'],
                     winfunc=cfg['window_function'])

    if cfg['use_delta'] or cfg['use_delta_delta']:
        data_mfcc = np.concatenate((data_mfcc, delta(data_mfcc, cfg['delta_sample'])), axis=1)

    if cfg['use_delta_delta']:
        data_mfcc = np.concatenate((data_mfcc, delta(data_mfcc, cfg['delta_delta_sample'])), axis=1)

    return data_mfcc


def recognize(data, model):
    if model.score(data) > LIKE_THRESHOLD:
        return True


def run_detection():
    p = pa.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input_device_index=DEVICE_INDEX,
                    input=INPUT)

    concatenated = False
    audiochunk = np.array([], dtype=np.int16)
    for i in range(100):
        samps = np.fromstring(stream.read(CHUNK), dtype=np.int16)
        energy = np.mean((samps / np.iinfo(np.int16).max) ** 2)
        if LEVEL_THRESHOLD < energy:
            if not concatenated:
                print("tap")
                concatenated = True
            audiochunk = np.concatenate((audiochunk, samps))
        else:
            if concatenated:
                print(audiochunk, audiochunk.shape)
                concatenated = False
                audiochunk = np.array([], dtype=np.int16)


if __name__ == "__main__":
    run_detection()
