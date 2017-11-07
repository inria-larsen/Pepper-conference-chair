#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


from speaker import Speaker

import sys
import json

class Data:
	def __init__(self, speakers_json_file, emergencies_json_file, jokes_json_file):
		self.speakers_data = json.load(speakers_json_file)
		self.emergencies_data = json.load(emergencies_json_file)
		self.jokes_data = json.load(jokes_json_file)



	####################
	## Get all of the speakers
	####################
	def getSpeakers(self):
		self.speakers = []
		for item in self.speakers_data:
			speaker = Speaker(item['id'], item['introduction'], item['duration'], item['extraDuration'])
			self.speakers.append(speaker)
		return self.speakers



	####################
	## Get the first speaker
	####################
	def getFirstSpeaker(self):
		speakers = self.getSpeakers()
		firstId = sys.maxsize
		first = None
		for speaker in speakers:
			if speaker.id < firstId:
				firstId = speaker.id
				first = speaker
		if not first:
			print('>> No speaker availlable')
		return first



	####################
	## Get all the emergencies
	####################
	def getEmergencies(self):
		self.emergencies = []
		for item in self.emergencies_data:
			self.emergencies.append(item['text'])
		return self.emergencies



	####################
	## Get all the jokes
	####################
	def getJokes(self):
		self.jokes = []
		for item in self.jokes_data:
			self.jokes.append(item['text'])
		return self.jokes
