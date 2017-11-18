from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from audiostream_source_arecord import AudiostreamSource
from audiostream_sink_aplay import AudiostreamSink
import numpy
import os
import time
import librosa


dataset_path="nyumaya_lj-speech"

from threading import Thread

class LoginScreen(GridLayout):

	def __init__(self, **kwargs):
		super(LoginScreen, self).__init__(**kwargs)
		self.cols = 2
		self.index = 0
		self.isRecording = False
		self.isPlayback = False


		self.audio_buffer = b''

		self.AudiostreamSinkInstance = AudiostreamSink()
		self.AudiostreamSourceInstance = AudiostreamSource()

		if(self.AudiostreamSinkInstance == None):
			print("Error no Audiosink")

		if(self.AudiostreamSourceInstance == None):
			print("Error no Audiosource")


		layout = BoxLayout(orientation='vertical')
		button_layout = BoxLayout(orientation='horizontal')

		layout.add_widget(button_layout)

		self.textList = {}
		self.updateList = {}

		self.recordButton = Button(text='RECORD', on_press=lambda a:self.record())
		self.playButton = Button(text='REPLAY', on_press=lambda a:self.playback())

		self.nextButton = Button(text='NEXT', on_press=lambda a:self.next())
		self.prevButton = Button(text='PREVIOUS', on_press=lambda a:self.previous())
		self.updateButton = Button(text='UPDATE SET', on_press=lambda a:self.update())

		self.displayText = Label(text='This is as sample recording text')
		self.displayText.font_size='30sp'


		self.read_thread = Thread(target=self.read_thread, args=())
		self.read_thread.daemon = True 
		self.read_thread.start() 

		self.play_thread = Thread(target=self.write_thread, args=())
		self.play_thread.daemon = True 
		self.play_thread.start() 

		index = 0
		with open("./" + dataset_path +"/list.txt") as f:
			for line in f:
				
				line_a = line.lstrip("( ")
				line_c= line_a.replace(" ", "|",1)
				parts = line_c.strip().split('|')
				filename= parts[0]
				text = parts[1]
				text =text.lstrip('"')
				text = text[:-3]
				self.textList[index] = text
				index+=1

		button_layout.add_widget(self.recordButton)
		button_layout.add_widget(self.playButton)
		button_layout.add_widget(self.nextButton)
		button_layout.add_widget(self.prevButton)
		button_layout.add_widget(self.updateButton)


	
		layout.add_widget(self.displayText)
		self.add_widget(layout)
		
		self.advance_index()

		self.displayText.text = str(self.index) + " " + self.textList[self.index]

	def advance_index(self):
		while(os.path.isfile("./" + dataset_path + "/wavs/" + str(self.index) + ".wav")):
			self.index+=1

	def save_buffer(self,index):
		path = "./" + dataset_path + "/wavs/" + str(index) + ".wav"
		librosa.output.write_wav(path,numpy.fromstring(self.audio_buffer, numpy.int16),48000)
	

	def load_buffer(self,path):
		pass

	def read_thread(self):

		while(True):
			if (self.isRecording == True):
				data,channels,samplerate = self.AudiostreamSourceInstance.read()
				self.audio_buffer += data
			else:
				time.sleep(0.5)

	
	def write_thread(self):

		while(True):
			if(self.isPlayback == True):
				self.AudiostreamSinkInstance.writeSamples(self.audio_buffer,1,48000)
				self.AudiostreamSinkInstance.run()
				self.isPlayback = False
			else:
				time.sleep(0.5)

	def record(self):
		if(self.isRecording == False):
			self.isRecording = True
			self.AudiostreamSourceInstance.start()

			self.recordButton.text="STOP"
			self.audio_buffer = b''
		
		else:
			self.isRecording = False
			self.recordButton.text="RECORD"
			self.AudiostreamSourceInstance.stop()

	def update(self):
		for key, value in self.textList.iteritems():
			if(os.path.isfile("./" + dataset_path + "/wavs/" + str(key) + ".wav")):
				self.updateList[key] = value

		raw = open("./" + dataset_path + "/train.txt", "w+")
		raw.seek(0)
		raw.truncate()
		for key,value in self.updateList.iteritems():
			raw.write('( ' + str(key) + ' "' + value + '" )' + '\n')


	def playback(self):
		if(self.isPlayback == False):
			self.AudiostreamSinkInstance.start()
			self.isPlayback = True
	
		else:
			self.isPlayback = False
			self.AudiostreamSinkInstance.stop()


	def next(self):

		if(len(self.audio_buffer) != 0):#only save if buffer is not empty
			self.save_buffer(self.index)

		self.index += 1 
		self.advance_index()
		
		self.displayText.text = str(self.index) + " " + self.textList[self.index]


	def previous(self):
		if(self.index > 0):
			self.index -= 1
			self.displayText.text = str(self.index) + " " + self.textList[self.index]
		



class MyApp(App):

	def build(self):
		return LoginScreen()


if __name__ == '__main__':
	MyApp().run()

