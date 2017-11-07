#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


from Tkinter import *

from engine import Engine
from movement import Movement
from speech import Speech
from tablet import Tablet
from data import Data
from logger import Logger

import ConfigParser
import math

class Commands():



	####################
	## Initiate class
	####################
	def __init__(self, sess, configFilePath, speakersFilePath, speakingFilePath, emergenciesFilePath, jokesFilePath):

		self.session = sess

		# Initiate shut down variable
		self.shut = False

		# Initiate stack for engine theads
		self.threads = []

		# Read the config file (connect)
		self.configParser = ConfigParser.RawConfigParser()
		self.configParser.read(configFilePath)

		# Read the config file (global speaking)
		self.configParserGlobal = ConfigParser.RawConfigParser()
		self.configParserGlobal.read(speakingFilePath)

		# Create service for movement
		self.movement_service = Movement(self.session)

		# Create service for speech
		self.speech_service = Speech(self.session, self.configParser, self.configParserGlobal)
		self.session.service('ALSpeechRecognition').pause(True)

		# Create service for tablet
		self.tablet_service = Tablet(self.session, self.configParser)

		# Initiate speakers data access
		speakersFile = open(speakersFilePath)
		emergenciesFile = open(emergenciesFilePath)
		jokesFile = open(jokesFilePath)
		self.data_service = Data(speakersFile, emergenciesFile, jokesFile)

		# Initiate logger
		self.log = Logger()

		# Create main gui
		self.rootGui = Tk()
		self.rootGui.title('Pepper chair manager')
		self.rootGui['bg']='white'
		self.rootGui.resizable(width = False, height = True)
		self.rootGui.minsize(width = 900, height = 500)
		self.rootGui.maxsize(width = 900, height = 50000)

		# Initialise variables used
		self.speakingLocation = None
		self.waitingLocation = None
		self.askingLocation = None
		self.readyToPresent = False
		self.currentSpeaker = self.data_service.getFirstSpeaker()
		self.currentTimer = self.currentSpeaker.duration

		# Get autonomous life activation status from .cfg
		autonomousBlinking_status = self.configParser.get('autonomousLife', 'AutonomousBlinking')
		backgroundMovement_status = self.configParser.get('autonomousLife', 'BackgroundMovement')
		basicAwareness_status = self.configParser.get('autonomousLife', 'BasicAwareness')
		listeningMovement_status = self.configParser.get('autonomousLife', 'ListeningMovement')
		speakingMovement_status = self.configParser.get('autonomousLife', 'SpeakingMovement')

		# Set autonomous life activation life status on the robot
		self.life_service = self.session.service('ALAutonomousLife')
		self.life_service.setAutonomousAbilityEnabled('AutonomousBlinking', autonomousBlinking_status == 'True')
		self.life_service.setAutonomousAbilityEnabled('BackgroundMovement', backgroundMovement_status == 'True')
		self.life_service.setAutonomousAbilityEnabled('BasicAwareness', basicAwareness_status == 'True')
		self.life_service.setAutonomousAbilityEnabled('ListeningMovement', listeningMovement_status == 'True')
		self.life_service.setAutonomousAbilityEnabled('SpeakingMovement', speakingMovement_status == 'True')

		self.runGui()



	####################
	## GUI
	####################
	def runGui(self):

		buttonSize = 12

		# Allow keyboard control
		self.rootGui.bind('<KeyPress>', self.pilotPress)
		self.rootGui.bind('<KeyRelease>', self.pilotRelease)

		self.frame = Frame(self.rootGui, borderwidth = 2, relief = GROOVE)
		self.frame.pack(side = TOP, fill = 'both', expand = 'yes')

		# Information panels group
		self.informationGroup = LabelFrame(self.frame, text = 'Informations', padx = 10, pady = 10)
		self.informationGroup.pack(side = TOP, fill = 'both', expand = 'yes')

		self.idCurrentSpeaker = StringVar()
		self.idCurrentSpeaker.set('Speaker: ' + str(self.currentSpeaker.id))
		Label(self.informationGroup, textvariable = self.idCurrentSpeaker).pack(side = TOP, anchor = W)

		self.durationCurrentSpeaker = StringVar()
		self.durationCurrentSpeaker.set('Duration: ' + str(self.currentSpeaker.duration) + ' with ' + str(self.currentSpeaker.extraDuration) + ' extra')
		Label(self.informationGroup, textvariable = self.durationCurrentSpeaker).pack(side = TOP, anchor = W)

		self.timerLeft = StringVar()
		self.timerLeft.set('Timer left: ' + str(self.currentTimer))
		Label(self.informationGroup, textvariable = self.timerLeft).pack(side = TOP, anchor = W)

		intro = ""
		for introdution in self.currentSpeaker.introduction:
			intro += introdution + ' '
		self.introCurrentSpeaker = StringVar()
		self.introCurrentSpeaker.set('Introduction: ' + intro)
		Label(self.informationGroup, textvariable = self.introCurrentSpeaker, wraplength = 850, justify=LEFT).pack(side = TOP, anchor = W)

		self.currentState = StringVar()
		self.currentState.set('State: ')
		Label(self.informationGroup, textvariable = self.currentState).pack(side = TOP, anchor = W)

		# Presentation buttons group
		self.presentationButtonsGroup = LabelFrame(self.frame, text = 'Presentation', padx = 10, pady = 10)
		self.presentationButtonsGroup.pack(side = TOP, fill = 'both')

		# Automatique sub-group
		self.buttonInit = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Initialisation', command = lambda x = 1: self.checkEngine('init'))
		self.buttonInit.grid(row = 1, column = 1)

		self.buttonLaunch = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Launch', command = lambda x = 1: self.checkEngine('launch'))
		self.buttonLaunch.grid(row = 1, column = 2)

		# Commands sub-group
		self.buttonIntroduce = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Introduce', command = lambda x = 1: self.checkEngine('introduce'))
		self.buttonIntroduce.grid(row = 1, column = 5)
		self.buttonListen = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Listen', command = lambda x = 1: self.checkEngine('listen'))
		self.buttonListen.grid(row = 2, column = 5)
		self.buttonAsk = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Ask', command = lambda x = 1: self.checkEngine('asking'))
		self.buttonAsk.grid(row = 3, column = 5)

		# Breakers sub-group
		self.buttonBreakAsk = Button(self.presentationButtonsGroup, width = buttonSize, text='More questions', command = lambda x = 1: self.executeCommandOnCurrentThread('moreQuestions'))
		self.buttonBreakAsk.grid(row = 1, column = 6)
		self.buttonBreakListen = Button(self.presentationButtonsGroup, width = buttonSize, text='Break listen', command = lambda x = 1: self.executeCommandOnCurrentThread('breakListen'))
		self.buttonBreakListen.grid(row = 2, column = 6)
		self.buttonBreakAsk = Button(self.presentationButtonsGroup, width = buttonSize, text='Break questions', command = lambda x = 1: self.executeCommandOnCurrentThread('breakQuestions'))
		self.buttonBreakAsk.grid(row = 3, column = 6)

		# Go to locations sub-group
		self.buttonGoToSpeak = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Go to speaking', command = lambda x = 1: self.checkEngine('goSpeak'))
		self.buttonGoToSpeak.grid(row = 1, column = 3)
		self.buttonGoToWait = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Go to waiting', command = lambda x = 1: self.checkEngine('goWait'))
		self.buttonGoToWait.grid(row = 2, column = 3)
		self.buttonGoToQuestion = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Go to asking', command = lambda x = 1: self.checkEngine('goQuestion'))
		self.buttonGoToQuestion.grid(row = 3, column = 3)

		# Save locations sub-group
		self.buttonSaveSpeak = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Save speaking', command = lambda x = 1: self.checkEngine('saveSpeak'))
		self.buttonSaveSpeak.grid(row = 1, column = 4)
		self.buttonSaveWait = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Save waiting', command = lambda x = 1: self.checkEngine('saveWait'))
		self.buttonSaveWait.grid(row = 2, column = 4)
		self.buttonSaveQuestion = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Save asking', command = lambda x = 1: self.checkEngine('saveQuestion'))
		self.buttonSaveQuestion.grid(row = 3, column = 4)

		# Speaker sub-group
		self.buttonSpeakerReady = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Speaker ready', command = lambda x = 1: self.executeCommandOnCurrentThread('speakerReady'))
		self.buttonSpeakerReady.grid(row = 2, column = 1)
		self.buttonSpeakerFirst = Button(self.presentationButtonsGroup, width = buttonSize, text = 'First speaker', command = lambda x = 1: self.checkEngine('firstSpeaker'))
		self.buttonSpeakerFirst.grid(row = 2, column = 2)
		self.buttonSpeakerNext = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Next speaker', command = lambda x = 1: self.checkEngine('next'))
		self.buttonSpeakerNext.grid(row = 3, column = 1)
		self.buttonSpeakerPrevious = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Previous speaker', command = lambda x = 1: self.checkEngine('previous'))
		self.buttonSpeakerPrevious.grid(row = 3, column = 2)

		# Arms sub-group
		self.buttonPointLeft = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Left', command = lambda x = 1: self.executeCommandOnCurrentThread('pointLeft'))
		self.buttonPointLeft.grid(row = 1, column = 7)
		self.buttonPointCenter = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Center', command = lambda x = 1: self.executeCommandOnCurrentThread('pointCenter'))
		self.buttonPointCenter.grid(row = 2, column = 7)
		self.buttonPointRight = Button(self.presentationButtonsGroup, width = buttonSize, text = 'Right', command = lambda x = 1: self.executeCommandOnCurrentThread('pointRight'))
		self.buttonPointRight.grid(row = 3, column = 7)

		# Fast edit speak
		self.fastSpeakingGroup = LabelFrame(self.frame, text = 'Fast speaking', padx = 10, pady = 10)
		self.fastSpeakingGroup.pack(side = TOP, fill = 'both')

		self.fastSpeakingButtonsGroup = Frame(self.fastSpeakingGroup)
		self.fastSpeakingButtonsGroup.pack(side = TOP, fill = 'both')

		self.fastSpeakingButton = Button(self.fastSpeakingButtonsGroup, text = 'Say', command = self.fastSpeaking)
		self.fastSpeakingButton.pack(side = LEFT)

		self.fastSpeakingText = StringVar()
		self.fastSpeakingEntry = Entry(self.fastSpeakingButtonsGroup, textvariable = self.fastSpeakingText, width = 100)
		self.fastSpeakingEntry.pack(side = LEFT)

		# Pre edited fast speak
		self.preEditedFastSpeakingGroup = Frame(self.fastSpeakingGroup)
		self.preEditedFastSpeakingGroup.pack(side = TOP, fill = 'both')

		def myfunction(event):
			self.preEditedFastSpeakingGroupCanvas.configure(scrollregion = self.preEditedFastSpeakingGroupCanvas.bbox("all"), height = 250)

		self.preEditedFastSpeakingGroupCanvas = Canvas(self.preEditedFastSpeakingGroup, width = 750)
		self.preEditedFastSpeakingGroupSubFrame = Frame(self.preEditedFastSpeakingGroupCanvas)
		self.scrollbar = Scrollbar(self.preEditedFastSpeakingGroup, orient = 'vertical', command = self.preEditedFastSpeakingGroupCanvas.yview)
		self.preEditedFastSpeakingGroupCanvas.configure(yscrollcommand = self.scrollbar.set)

		self.scrollbar.pack(side = "right", fill = "y")
		self.preEditedFastSpeakingGroupCanvas.pack(side="left", fill = 'both')
		self.preEditedFastSpeakingGroupCanvas.create_window((0,0), window = self.preEditedFastSpeakingGroupSubFrame, anchor='nw')
		self.preEditedFastSpeakingGroupSubFrame.bind("<Configure>",myfunction)

		Label(self.preEditedFastSpeakingGroupSubFrame, text = 'Emergencies:').pack(side = TOP, anchor = W)

		indice = 0
		emergencies = self.data_service.getEmergencies()
		dic = {}
		for emergencie in emergencies:
			indice += 1
			a = 'preEditedFastSpeakingNum'+str(indice)
			b = 'buttonPreEditedFastSpeakingNum'+str(indice)
			dic[a] = emergencie
			dic[b] = Button(self.preEditedFastSpeakingGroupSubFrame, text = dic[a], relief=FLAT, command = lambda x = dic[a]: self.loadInFastSpeaking(x))
			dic[b].pack(side = TOP, anchor = W)

		Label(self.preEditedFastSpeakingGroupSubFrame, text = 'Jokes:').pack(side = TOP, anchor = W)

		indice = 0
		jokes = self.data_service.getJokes()
		dic = {}
		for joke in jokes:
			indice += 1
			a = 'preEditedFastSpeakingNum'+str(indice)
			b = 'buttonPreEditedFastSpeakingNum'+str(indice)
			dic[a] = joke
			dic[b] = Button(self.preEditedFastSpeakingGroupSubFrame, text = dic[a], relief=FLAT, command = lambda x = dic[a]: self.loadInFastSpeaking(x))
			dic[b].pack(side = TOP, anchor = W)

		# Bottom buttons group
		self.bottom = LabelFrame(self.frame, text = 'Loop', padx = 10, pady = 10)
		self.bottom.pack(side = BOTTOM, fill = 'both')

		self.buttonStop = Button(self.bottom, width = buttonSize, text = 'Stop', command = lambda x = 1: self.executeCommandOnCurrentThread('stop'))
		self.buttonStop.pack(side = LEFT)

		self.buttonPause = Button(self.bottom, width = buttonSize, text = 'Pause', command = lambda x = 1: self.executeCommandOnCurrentThread('pause'))
		self.buttonPause.pack(side = LEFT)

		self.buttonResume = Button(self.bottom, width = buttonSize, text = 'Resume', command = lambda x = 1: self.executeCommandOnCurrentThread('resume'))
		self.buttonResume.pack(side = LEFT)

		self.buttonExit = Button(self.bottom, width = buttonSize, text = 'Exit', command = self.shutDownWindows)
		self.buttonExit.pack(side = LEFT)

		# Allow mouse focus control
		self.informationGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.presentationButtonsGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.bottom.bind('<Button-1>', self.disableFastSpeakingTextFocus)

		self.rootGui.mainloop()



	####################
	## Load the pre edited sentence into the fast speaking area
	####################
	def loadInFastSpeaking(self, sentence):
		self.log.addLog('load in fast speaking', sentence)
		self.fastSpeakingText.set(sentence)



	####################
	## Execute the command on the current thread
	####################
	def executeCommandOnCurrentThread(self, command):
		if self.threads != []:
			self.log.addLog(command, self.threads[-1].command)
			command_to_execute = getattr(self.threads[-1], command)()



	####################
	## Check if engine is valid
	####################
	def checkEngine(self, command):

		self.refreshThreadsList()

		self.log.addLog(command)

		# Check if another engine is running
		if self.threads != []:
			currentEngine = self.threads[-1]

			# Put current engine in pause
			currentEngine.pause()

			# Create and start new engine
			engine = self.newEngine(command)
			self.threads.append(engine)
			engine.start()

		else:
			# Create and start new engine
			engine = self.newEngine(command)
			self.threads.append(engine)
			engine.start()

		self.refreshThreadsList()



	####################
	## Create a new engine
	####################
	def newEngine(self, cmd):
		engine = Engine(self, cmd)
		return engine



	####################
	## Shut down program
	####################
	def shutDown(self):
		self.shut = True
		self.movement_service.exit()
		self.speech_service.exit()
		self.tablet_service.exit()
		while self.threads != []:
			engine = self.threads.pop()
			engine.resume()
			engine.stop()
			engine.join()
		self.log.closeFile()
		self.session.service('ALSpeechRecognition').pause(False)
		self.life_service.setAutonomousAbilityEnabled('All', True)

		print('>> Exit completed')



	####################
	## Shut down program and close window
	####################
	def shutDownWindows(self):
		self.shutDown()
		self.rootGui.quit()

		print('>> Window closed')



	####################
	## Refresh current thread
	####################
	def refreshThreadsList(self):
		for thread in self.threads:
			if not thread.active:
				self.threads.remove(thread)



	####################
	## Unfocus the text area for fast speaking
	####################
	def disableFastSpeakingTextFocus(self, event):
		self.rootGui.focus_set()



	####################
	## Get the text to say it
	####################
	def fastSpeaking(self):
		self.log.addLog('fast speaking', self.fastSpeakingEntry.get())
		self.speech_service.say(self.fastSpeakingEntry.get())



	####################
	## Pilot the robot with the keyboard (classical zqsd)
	## Keys press part
	####################
	def pilotPress(self, event):

		if not self.fastSpeakingEntry == self.fastSpeakingEntry.focus_get():
			x = 0
			y = 0
			theta = 0
			stopControl = False

			key = event.keysym

			if key == 'z':
				x = 0.6
			elif key == 's':
				x = -0.6
			if key == 'a':
				y = 0.6
			elif key == 'e':
				y = -0.6
			if key == 'q':
				theta = 0.8
			elif key == 'd':
				theta = -0.8

			if x == 0:
				if y == 0:
					if theta == 0:
						pass
					else:
						self.movement_service.updateMovementTheta(theta)
				else:
					if theta == 0:
						self.movement_service.updateMovementY(y)
					else:
						self.movement_service.updateMovementY(y)
						self.movement_service.updateMovementTheta(theta)
			else:
				if y == 0:
					if theta == 0:
						self.movement_service.updateMovementX(x)
					else:
						self.movement_service.updateMovementX(x)
						self.movement_service.updateMovementTheta(theta)
				else:
					if theta == 0:
						self.movement_service.updateMovementX(x)
						self.movement_service.updateMovementY(y)
					else:
						self.movement_service.updateMovementX(x)
						self.movement_service.updateMovementY(y)
						self.movement_service.updateMovementTheta(theta)




	####################
	## Pilot the robot with the keyboard (classical zqsd - french keyboards)
	## Keys release part
	####################
	def pilotRelease(self, event):

		if not self.fastSpeakingEntry == self.fastSpeakingEntry.focus_get():
			x = 0
			y = 0
			theta = 0
			stopControl = False

			key = event.keysym

			if key == 'z' or key == 's':
				self.movement_service.updateMovementX(0)
			if key == 'a' or key == 'e':
				self.movement_service.updateMovementY(0)
			if key == 'q' or key == 'd':
				self.movement_service.updateMovementTheta(0)



	####################
	## Refresh current thread
	####################
	def updateGui(self):

		self.idCurrentSpeaker.set('Speaker: ' + str(self.currentSpeaker.id))

		intro = ""
		for introdution in self.currentSpeaker.introduction:
			intro += introdution + ' '
		self.introCurrentSpeaker.set('Introduction: ' + intro)
		self.durationCurrentSpeaker.set('Duration: ' + str(self.currentSpeaker.duration) + ' with ' + str(self.currentSpeaker.extraDuration) + ' extra')
		self.timerLeft.set('Timer left: ' + str(self.currentTimer))



	####################
	## Update the value of the timer displayed on Pepper's tablet
	####################
	def updateTimer(self, time, negative = False):
		# Time calculations for hours, minutes and seconds
		minutes = math.trunc(time / 60);
		seconds = math.trunc(time % 60);
		if negative:
			self.currentTimer = '- ' + str(minutes) + ' m ' + str(seconds) + ' s'
		else:
			self.currentTimer = str(minutes) + ' m ' + str(seconds) + ' s'
		self.updateGui()
