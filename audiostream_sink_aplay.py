import os
import subprocess
import numpy
import Queue

output_device = 'default'
dtype = 'int16'
channels = 1


class AudiostreamSink():

    def __init__(self):
        running = False
        self.samplerate = 48000
        self.cmd = [
            'aplay',
            '-q',
            '-t', 'raw',
            '-D', output_device,
            '-c', '1',
            '-f', 's16',
            '-r', str(self.samplerate),
        ]
        self.rBuffer = Queue.Queue()


    def start(self):
        self.audio_stream = subprocess.Popen(self.cmd, stdin=subprocess.PIPE)
        self.running = True

    def stop(self):
        self.audio_stream.stdin.close()
        self.audio_stream = None
        self.running = False

    def writeSamples(self,data,channels_value,sample_rate):
        if(self.samplerate != sample_rate):
            self.samplerate = sample_rate
            self.stop()
            self.start()


        if(self.audio_stream != None and self.running == True):
            self.rBuffer.put(numpy.fromstring(data, numpy.int16))

    def run(self):
        if(self.audio_stream != None and self.running == True):
            data = self.rBuffer.get(True,10)
            self.audio_stream.stdin.write(data)

 
