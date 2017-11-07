#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1

import time
import ConfigParser

class Speech:
	def __init__(self, session, configFile, globalConfigFile):
		self.textToSpeech_service = session.service('ALTextToSpeech')
		self.animatedSpeech_service = session.service('ALAnimatedSpeech')
		self.audioDevice_service = session.service('ALAudioDevice')
		self.audioDevice_service.closeAudioInputs()
		self.textToSpeech_service.setLanguage('English')
		self.movement = 'contextual'
		self.ids = []
		self.stop_v = False
		self.pause_v = False
		self.configParser = configFile
		self.configParserGlobal = globalConfigFile
		self.audioDevice_service.muteAudioOut(True)



	####################
	## Empty
	####################
	def standby(self):
		pass




	####################
	## Prepare the robot to speak, empty for now
	####################
	def prepareRobot(self):
		self.stop_v = False
		self.pause_v = False



	####################
	## Robot say the sentence s
	####################
	def say(self, sentences, animated = True):
		print('> ' + str(sentences))

		if self.audioDevice_service.isAudioOutMuted():
			self.audioDevice_service.muteAudioOut(False)

		if isinstance(sentences, basestring):
			while self.pause_v:
				time.sleep(0.5)
			if not self.stop_v:
				sentence = "\RSPD=70\ "
				sentence += "\VCT=100\ "
				sentence += sentences.encode('utf-8')
				sentence +=  "\RST\ "	
				if animated:
					idSpeech = self.animatedSpeech_service.say(str(sentence), self.movement)
				else:
					idSpeech = self.textToSpeech_service.say(str(sentence))
		else:
			for s in sentences:
				while self.pause_v:
					time.sleep(0.5)
				if not self.stop_v:
					sentence = "\RSPD=80\ "
					sentence += "\VCT=100\ "
					sentence += s.encode('utf-8')
					sentence +=  "\RST\ "
					if animated:
						idSpeech = self.animatedSpeech_service.say(str(sentence), self.movement)
					else:
						idSpeech = self.textToSpeech_service.say(str(sentence))
				else:
					break

		if not self.audioDevice_service.isAudioOutMuted():
			self.audioDevice_service.muteAudioOut(True)



	####################
	## Robot say the sentences of the category
	####################
	def sayGlobal(self, category, adds = None):

		messages = self.configParserGlobal.get('speaking', category)
		messages = messages.split('§')
		toSay = ''

		if isinstance(messages, basestring):
			toSay += str(messages)
			if not adds == None:
				toSay += str(adds)
		else:
			for i in range(len(messages)):
				toSay += messages[i]
				if not adds == None:
					if isinstance(adds, list):
						toSay += str(adds[i])
					else:
						toSay += str(adds)
						adds = ''
		if category == 'questionPointing':
			self.say(toSay, False)
		else:
			self.say(toSay)



	####################
	## Stop service
	####################
	def stop(self):
		self.stop_v = True
		self.pause_v = False



	####################
	## Pause service
	####################
	def pause(self):
		self.pause_v = True



	####################
	## Do the pause if required
	####################
	def doPause(self):
		while self.pause_v:
			self.movement_service.updateMovement(0, 0, 0)
			time.sleep(0.5)



	####################
	## Resume service
	####################
	def resume(self):
		self.stop_v = False
		self.pause_v = False



	####################
	## Stop & clean service
	####################
	def exit(self):
		self.stop_v = True
		self.pause_v = False
    #self.textToSpeech_service.setLanguage('French')
        self.textToSpeech_service.setLanguage('English')
		self.audioDevice_service.muteAudioOut(False)
		self.audioDevice_service.openAudioInputs()
