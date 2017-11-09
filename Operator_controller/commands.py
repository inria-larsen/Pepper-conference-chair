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

		print ("*** GUI init")

		# Initiate shut down variable
		self.shut = False

		# Initiate stack for engine theads
		self.threads = []

		print ("*** GUI parse config file")
		# Read the config file (connect)
		self.configParser = ConfigParser.RawConfigParser()
		self.configParser.read(configFilePath)

		print ("*** GUI parse speak file")
		# Read the config file (global speaking)
		self.configParserGlobal = ConfigParser.RawConfigParser()
		self.configParserGlobal.read(speakingFilePath)

		print ("*** GUI create movement service")
		print (" IMPORTANT: if the program is stuck here, please check if the power plug of the Pepper is open - check behind, close to the rear wheel!!!!!")
		# Create service for movement
		self.movement_service = Movement(self.session)

		print ("*** GUI create speech service")
		# Create service for speech
		self.speech_service = Speech(self.session, self.configParser, self.configParserGlobal)
		self.session.service('ALSpeechRecognition').pause(True)

		print ("*** GUI connect to tablet")
		# Create service for tablet
		self.tablet_service = Tablet(self.session, self.configParser)

		# Initiate speakers data access
		speakersFile = open(speakersFilePath)
		emergenciesFile = open(emergenciesFilePath)
		jokesFile = open(jokesFilePath)
		self.data_service = Data(speakersFile, emergenciesFile, jokesFile)

		# Initiate logger
		self.log = Logger()


		print ("*** GUI creation")
		# Create main gui
		self.rootGui = Tk()
		self.rootGui.title('Pepper chair manager')
		self.rootGui['bg']='white'
		self.rootGui.resizable(width = True, height = True)
		self.rootGui.minsize(width = 900, height = 500)
		self.rootGui.maxsize(width = 900, height = 50000)
		# important bug fix
		# to close the GUI you need to disconnect from the robot before
		# otherwise the robot stays in a zombie status and needs to be rebooted
		# not even Choreographe can recover the robot
		self.rootGui.protocol("WM_DELETE_WINDOW", self.shutDownWindows)

		# Initialise variables used
		self.speakingLocation = None
		self.waitingLocation = None
		self.askingLocation = None
		self.readyToPresent = False
		self.currentSpeaker = self.data_service.getFirstSpeaker()
		self.currentTimer = self.currentSpeaker.duration

		print ("*** GUI autonomous life settings")
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

		print ("*** GUI run")
		self.runGui()



	####################
	## GUI
	####################
	def runGui(self):

		buttonSize = 12
		longButtonSize = 20
		longerButtonSize = 28

		# Allow keyboard control
		self.rootGui.bind('<KeyPress>', self.pilotPress)
		self.rootGui.bind('<KeyRelease>', self.pilotRelease)

		self.frame = Frame(self.rootGui, borderwidth = 2, relief = GROOVE)
		self.frame.pack(side = TOP, fill = 'both', expand = 'yes')

		#--------------------------------------------------------------------
		# Information panels group
		self.informationGroup = LabelFrame(self.frame, text = 'Speakers information', padx = 10, pady = 10)
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

		# Speaker sub-group
		self.buttonSpeakerInfoReady = Button(self.informationGroup, width = buttonSize, text = 'Speaker ready', command = lambda x = 1: self.executeCommandOnCurrentThread('speakerReady'))
		self.buttonSpeakerInfoReady.pack(side = LEFT)
		self.buttonSpeakerInfoFirst = Button(self.informationGroup, width = buttonSize, text = 'First speaker', command = lambda x = 1: self.checkEngine('firstSpeaker'))
		self.buttonSpeakerInfoFirst.pack(side = LEFT)
		self.buttonSpeakerInfoNext = Button(self.informationGroup, width = buttonSize, text = 'Next speaker', command = lambda x = 1: self.checkEngine('next'))
		self.buttonSpeakerInfoNext.pack(side = LEFT)
		self.buttonSpeakerInfoPrevious = Button(self.informationGroup, width = buttonSize, text = 'Previous speaker', command = lambda x = 1: self.checkEngine('previous'))
		self.buttonSpeakerInfoPrevious.pack(side = LEFT)

		#--------------------------------------------------------------------
		# Move robot group
		self.moveRobotGroup = LabelFrame(self.frame, text = 'Move robot', padx = 10, pady = 10)
		self.moveRobotGroup.pack(side = TOP, fill = 'both')

		self.infoSaveLocation = StringVar()
		self.infoSaveLocation.set('Move the robot with the keyboard to identify the 3 basic locations. ')
		Label(self.moveRobotGroup, textvariable = self.infoSaveLocation).pack(side = TOP, anchor = W)

		self.buttonMoveRight = Button(self.moveRobotGroup, width = buttonSize, text = 'E: Move right', command = lambda x = 1: self.checkEngine('moveRobotRight'))
		self.buttonMoveRight.pack(side = LEFT)
		self.buttonMoveLeft = Button(self.moveRobotGroup, width = buttonSize, text = 'A: Move left', command = lambda x = 1: self.checkEngine('moveRobotLeft'))
		self.buttonMoveLeft.pack(side = LEFT)
		self.buttonMoveForward = Button(self.moveRobotGroup, width = buttonSize, text = 'Z: Move forward', command = lambda x = 1: self.checkEngine('moveRobotForward'))
		self.buttonMoveForward.pack(side = LEFT)
		self.buttonMoveBackward = Button(self.moveRobotGroup, width = buttonSize, text = 'S: Move backward', command = lambda x = 1: self.checkEngine('moveRobotBackward'))
		self.buttonMoveBackward.pack(side = LEFT)
		self.buttonTurnRight = Button(self.moveRobotGroup, width = buttonSize, text = 'D: Turn right', command = lambda x = 1: self.checkEngine('moveRobotTurnRight'))
		self.buttonTurnRight.pack(side = LEFT)
		self.buttonTurnLeft = Button(self.moveRobotGroup, width = buttonSize, text = 'Q: Turn left', command = lambda x = 1: self.checkEngine('moveRobotTurnLeft'))
		self.buttonTurnLeft.pack(side = LEFT)

		#--------------------------------------------------------------------
		# Save basic locations group
		self.locationGroup = LabelFrame(self.frame, text = 'Save key locations', padx = 10, pady = 10)
		self.locationGroup.pack(side = TOP, fill = 'both')

		self.infoSaveLocation = StringVar()
		self.infoSaveLocation.set('Click on the buttons to save the locations. ')
		Label(self.locationGroup, textvariable = self.infoSaveLocation).pack(side = TOP, anchor = W)

		self.buttonSaveSpeakLocation = Button(self.locationGroup, width = buttonSize, text = 'Save speaking', command = lambda x = 1: self.checkEngine('saveSpeak'))
		self.buttonSaveSpeakLocation.pack(side = LEFT)
		self.buttonSaveWaitLocation = Button(self.locationGroup, width = buttonSize, text = 'Save waiting', command = lambda x = 1: self.checkEngine('saveWait'))
		self.buttonSaveWaitLocation.pack(side = LEFT)
		self.buttonSaveQuestionLocation = Button(self.locationGroup, width = buttonSize, text = 'Save asking', command = lambda x = 1: self.checkEngine('saveQuestion'))
		self.buttonSaveQuestionLocation.pack(side = LEFT)

		#--------------------------------------------------------------------
		# Presentation buttons group
		self.presentationButtonsGroup = LabelFrame(self.frame, text = 'Presentation', padx = 10, pady = 10)
		self.presentationButtonsGroup.pack(side = TOP, fill = 'both')

		# Commands sub-group
		self.buttonIntroduce = Button(self.presentationButtonsGroup, width = longerButtonSize, text = '[speak] Say text for this speaker', command = lambda x = 1: self.checkEngine('introduce'))
		self.buttonIntroduce.grid(row = 1, column = 3)
		self.buttonListen = Button(self.presentationButtonsGroup, width = longerButtonSize, text = '[wait] Say time + countdown', command = lambda x = 1: self.checkEngine('listen'))
		self.buttonListen.grid(row = 2, column = 3)
		self.buttonAsk = Button(self.presentationButtonsGroup, width = longerButtonSize, text = '[ask] Ask any questions', command = lambda x = 1: self.checkEngine('asking'))
		self.buttonAsk.grid(row = 3, column = 3)

		# Breakers sub-group
		self.buttonBreakListen = Button(self.presentationButtonsGroup, width = longerButtonSize, text='Break listen + stop countdown + Thanks', command = lambda x = 1: self.executeCommandOnCurrentThread('breakListen'))
		self.buttonBreakListen.grid(row = 2, column = 4)
		self.buttonBreakAsk = Button(self.presentationButtonsGroup, width = longerButtonSize, text='Break questions + Thanks again', command = lambda x = 1: self.executeCommandOnCurrentThread('breakQuestions'))
		self.buttonBreakAsk.grid(row = 3, column = 4)

		# Go to locations sub-group
		self.buttonGoToSpeak = Button(self.presentationButtonsGroup, width = longButtonSize, text = 'Go to speaking location', command = lambda x = 1: self.checkEngine('goSpeak'))
		self.buttonGoToSpeak.grid(row = 1, column = 1)
		self.buttonGoToWait = Button(self.presentationButtonsGroup, width = longButtonSize, text = 'Go to waiting location', command = lambda x = 1: self.checkEngine('goWait'))
		self.buttonGoToWait.grid(row = 2, column = 1)
		self.buttonGoToQuestion = Button(self.presentationButtonsGroup, width = longButtonSize, text = 'Go to asking location', command = lambda x = 1: self.checkEngine('goQuestion'))
		self.buttonGoToQuestion.grid(row = 3, column = 1)

		self.buttonStateIntroduce = Button(self.presentationButtonsGroup, width = buttonSize, text = 'State speak', command = lambda x = 1: self.checkEngine('introduceState'))
		self.buttonStateIntroduce.grid(row = 1, column = 2)
		self.buttonStateListen = Button(self.presentationButtonsGroup, width = buttonSize, text = 'State listen', command = lambda x = 1: self.checkEngine('listenState'))
		self.buttonStateListen.grid(row = 2, column = 2)
		self.buttonStateAsk = Button(self.presentationButtonsGroup, width = buttonSize, text = 'State questions', command = lambda x = 1: self.checkEngine('askingState'))
		self.buttonStateAsk.grid(row = 3, column = 2)

		#--------------------------------------------------------------------
		# Questions buttons group
		self.questionsButtonsGroup = LabelFrame(self.frame, text = 'Question time', padx = 10, pady = 10)
		self.questionsButtonsGroup.pack(side = TOP, fill = 'both')

		self.buttonBreakAsk = Button(self.questionsButtonsGroup, width = buttonSize, text='Any questions', command = lambda x = 1: self.executeCommandOnCurrentThread('moreQuestions'))
		self.buttonBreakAsk.pack(side = LEFT)
		
		# Arms pointing gestures sub-group
		self.buttonPointLeft = Button(self.questionsButtonsGroup, width = longButtonSize, text = 'Question/Point Left', command = lambda x = 1: self.executeCommandOnCurrentThread('pointLeft'))
		self.buttonPointLeft.pack(side = LEFT)
		self.buttonPointCenter = Button(self.questionsButtonsGroup, width = longButtonSize, text = 'Question/Point Center', command = lambda x = 1: self.executeCommandOnCurrentThread('pointCenter'))
		self.buttonPointCenter.pack(side = LEFT)
		self.buttonPointRight = Button(self.questionsButtonsGroup, width = longButtonSize, text = 'Question/Point Right', command = lambda x = 1: self.executeCommandOnCurrentThread('pointRight'))
		self.buttonPointRight.pack(side = LEFT)

		#--------------------------------------------------------------------
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

		Label(self.preEditedFastSpeakingGroupSubFrame, text = 'Text for Emergencies:').pack(side = TOP, anchor = W)

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


		#--------------------------------------------------------------------
		# Autonomous mode group
		self.automaticLoopGroup = LabelFrame(self.frame, text = 'Autonomous mode (loop)', padx = 10, pady = 10)
		self.automaticLoopGroup.pack(side = TOP, fill = 'both')

		self.infoAutoMode = StringVar()
		self.infoAutoMode.set('These buttons are useful if you want the Pepper to run in autonomous mode using the timings for each speaker. ')
		Label(self.automaticLoopGroup, textvariable = self.infoAutoMode).pack(side = TOP, anchor = W)

		self.buttonAutoInit = Button(self.automaticLoopGroup, width = buttonSize, text = 'Initialisation', command = lambda x = 1: self.checkEngine('init'))
		self.buttonAutoInit.pack(side = LEFT)

		self.buttonAutoLaunch = Button(self.automaticLoopGroup, width = buttonSize, text = 'Launch', command = lambda x = 1: self.checkEngine('launch'))
		self.buttonAutoLaunch.pack(side = LEFT)

		self.buttonAutoStop = Button(self.automaticLoopGroup, width = longButtonSize, text = 'Stop a current action', command = lambda x = 1: self.executeCommandOnCurrentThread('stop'))
		self.buttonAutoStop.pack(side = LEFT)

		self.buttonAutoPause = Button(self.automaticLoopGroup, width = buttonSize, text = 'Pause action', command = lambda x = 1: self.executeCommandOnCurrentThread('pause'))
		self.buttonAutoPause.pack(side = LEFT)

		self.buttonAutoResume = Button(self.automaticLoopGroup, width = buttonSize, text = 'Resume action', command = lambda x = 1: self.executeCommandOnCurrentThread('resume'))
		self.buttonAutoResume.pack(side = LEFT)

		#----------------------------------------------------------------------------------------------------
		# Bottom buttons group
		self.bottom = LabelFrame(self.frame, text = 'Execution mode', padx = 10, pady = 10)
		self.bottom.pack(side = BOTTOM, fill = 'both')

		self.buttonStop = Button(self.bottom, width = longButtonSize, text = 'Stop a current action', command = lambda x = 1: self.executeCommandOnCurrentThread('stop'))
		self.buttonStop.pack(side = LEFT)

		self.buttonPause = Button(self.bottom, width = buttonSize, text = 'Pause action', command = lambda x = 1: self.executeCommandOnCurrentThread('pause'))
		self.buttonPause.pack(side = LEFT)

		self.buttonResume = Button(self.bottom, width = buttonSize, text = 'Resume action', command = lambda x = 1: self.executeCommandOnCurrentThread('resume'))
		self.buttonResume.pack(side = LEFT)

		self.buttonExit = Button(self.bottom, width = buttonSize, text = 'EXIT Application', command = self.shutDownWindows)
		self.buttonExit.pack(side = LEFT)

		# Allow mouse focus control
		self.informationGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.moveRobotGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.locationGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.presentationButtonsGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.questionsButtonsGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
		self.automaticLoopGroup.bind('<Button-1>', self.disableFastSpeakingTextFocus)
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
