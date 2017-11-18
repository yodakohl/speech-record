import numpy
from threading import Thread, Lock

import os
import subprocess

audio_length = 40
samplerate= 48000
channels = 1
input_device = 'default'
bytes_per_sample=2

blocksize = ((samplerate) * (audio_length) / 1000) * channels *2

# * @param sample_count Number of samples in this frame. Valid numbers here are
# * ((sample rate) * (audio length) / 1000), where audio length can be
# * 2.5, 5, 10, 20, 40 or 60 millseconds.
# * @param channels Number of audio channels. Supported values are 1 and 2.
# * @param sampling_rate Audio sampling rate used in this frame. Valid sampling
# * rates are 8000, 12000, 16000, 24000, or 48000.
print("Blocksize: " + str(blocksize))


class AudiostreamSource():

    running = False

    def __init__(self):



        self._cmd = [
            'arecord',
            '-q',
            '-t', 'raw',
            '-D', input_device,
            '-c', str(channels),
            '-f', 's16',
            '-B', '160',
            '-r', str(samplerate),
        ]

        self._arecord = None
        self.this_chunk = b''


    def set_volume(self,volume):
        self.volume = volume

    def print_status(self):
        pass

    def start(self):
        self._arecord = subprocess.Popen(self._cmd, stdout=subprocess.PIPE)
        self.running = True

    def set_callback(self,callback):
        self.callback = callback


    def stop(self):
        self.running = False



    def read(self):
        while self._arecord != None:
            if self.running == False:
                if(self._arecord != None):
                    self._arecord.kill()
                    self._arecord = None
                    return None, channels,samplerate 

            input_data = self._arecord.stdout.read(blocksize)
            if not input_data:
                print("No chunk")
                return None, channels,samplerate


            return input_data, channels, samplerate
            self.this_chunk += input_data

            if len(self.this_chunk) >= blocksize:
                data_new = (self.this_chunk[:blocksize])
                self.this_chunk = self.this_chunk[blocksize:]
                return data_new, channels, samplerate










