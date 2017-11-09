#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


import sys
import time
import math
import threading

class Engine(threading.Thread):





	####################
	####################
	## Class running functions
	####################
	####################





	####################
	## Initiate class
	####################
	def __init__(self, cmds, cmd):

		# Thread init.
		threading.Thread.__init__(self)
		self.currentThread = threading.current_thread()

		# Thread active tag
		self.active = True

		# Variable to stop thread
		self.stop_v = False

		# Variable to pause thread
		self.pause_v = False

		# Thread command
		self.command = cmd

		# Link to commands class
		self.commands = cmds

		# Get the services for movements and speechs
		self.movement_service = self.commands.movement_service
		self.speech_service = self.commands.speech_service
		self.tablet_service = self.commands.tablet_service
		self.data_service = self.commands.data_service

		# Get the services for movements and speechs
		self.movement_service.stop_v = False
		self.speech_service.stop_v = False

		# Initiate state of presentation
		self.setState('standby')



	####################
	## Run the thread
	####################
	def run(self):

		command_to_execute = getattr(self, self.command)
		command_to_execute()

		self.active = False
		self.stopMovements()
		self.active = False
		self.commands.refreshThreadsList()





	####################
	####################
	## Direct function of commands: thread already created
	####################
	####################





	####################
	## Pause the thread
	####################
	def pause(self):
		self.pause_v = True
		self.speech_service.pause()
		self.tablet_service.pause()



	####################
	## Do the pause if required
	####################
	def doPause(self):
		while self.pause_v:
			self.movement_service.updateMovement(0, 0, 0)
			time.sleep(0.5)
		return True



	####################
	## Resume the thread
	####################
	def resume(self):
		self.pause_v = False
		self.speech_service.resume()
		self.tablet_service.resume()



	####################
	## Stop the thread
	####################
	def stop(self):
		self.pause_v = False
		self.stop_v= True
		self.active = False
		self.movement_service.stop()
		self.speech_service.stop()
		self.tablet_service.stop()
		self.commands.refreshThreadsList()





	####################
	####################
	## Direct function of commands: thread just created
	####################
	####################





	####################
	## Initiate and check if robot can start the presentation
	####################
	def init(self):

		# Initiate the robot's status
		self.commands.readyToPresent = True

		# Initiate the first speaker
		self.firstSpeaker()

		# Prepare robot to execute command
		self.movement_service.prepareRobot()
		self.speech_service.prepareRobot()
		self.tablet_service.prepareRobot()

		# Check if speaking location is defined
		if self.commands.speakingLocation is None:
			self.commands.readyToPresent = False
			print('>> init - no speaking location defined')

		# Check if waiting location is defined
		if self.commands.waitingLocation is None:
			self.commands.readyToPresent = False
			print('>> init - no waiting location defined')

		# Check if asking location is defined
		if self.commands.askingLocation is None:
			self.commands.readyToPresent = False
			print('>> init - no asking location defined')

		self.setState('standby')

		print('>> init - ready to present: '+str(self.commands.readyToPresent))

		print('>> Robot initialisation complete')



	####################
	## Launch the presentation
	####################
	def launch(self):

		if self.commands.readyToPresent:

			previousState = self.getState()
			self.setState('launch')

			while not self.stop_v:
				self.doPause()
				if not self.stop_v:

					self.speakerPreparation()
					self.introduce()
					self.listen()
					self.asking()
					if not self.next():
						self.speech_service.sayGlobal(finishMeeting)
						break

			self.setState(previousState)

		else:
			print('I am not sure I am ready to start, please do the initialisation to check it.')

		print('>> Presentation complete')



	####################
	## Introduce speaker phase
	####################
	def introduce(self):

		self.doPause()
		if not self.stop_v:

			previousState = self.getState()
			self.setState('introduce')

			self.speech_service.say(self.commands.currentSpeaker.introduction)

			self.setState(previousState)

		print('>> Introduction complete')



	####################
	## Listen & timer for speaker phase
	####################
	def listen(self):

		self.doPause()
		if not self.stop_v:

			previousState = self.getState()
			self.setState('listen')

			self.goWait()
			self.timer()

			self.setState(previousState)

		print('>> Listening complete')



	####################
	## Question to speaker phase
	####################
	def asking(self):

		self.doPause()
		if not self.stop_v:

			previousState = self.getState()
			self.setState('asking')

			self.goQuestion()
			self.speech_service.sayGlobal('askQuestions')
			self.questionsTime()
			self.speech_service.sayGlobal('finishQuestions')

			self.setState(previousState)

		print('>> Asking complete')



	####################
	## Activate timer of current speaker
	####################
	def timer(self):

		self.doPause()
		if not self.stop_v:

			duration = self.commands.currentSpeaker.duration
			extraDuration = self.commands.currentSpeaker.extraDuration

			self.speech_service.sayGlobal('timeLeft', duration)
			self.tablet_service.showTimer()
			self.tablet_service.updateTimer(duration)

			timerAvailable = 0
			timerExtra = 0

			while timerAvailable < (duration*60) and self.state != 'asking' and not self.stop_v:
				self.doPause()
				time.sleep(1)
				timerAvailable += 1
				self.commands.updateTimer(duration*60 - timerAvailable)
				self.tablet_service.updateTimer(duration*60 - timerAvailable)

			if not self.stop_v and self.state != 'asking':

				self.tablet_service.showExpired()
				self.speech_service.sayGlobal('askFinishPresentation')

				while timerExtra < (extraDuration*60) and self.state != 'asking' and not self.stop_v:
					self.doPause()
					time.sleep(1)
					timerExtra += 1
					self.commands.updateTimer(timerExtra, True)
					self.tablet_service.updateTimer(timerExtra, True)

				if not self.stop_v and self.state != 'asking':
					self.speech_service.sayGlobal('breakPresentation')
					self.breakListen()

			self.tablet_service.timerClean()
			self.speech_service.sayGlobal('finishPresentation')



	####################
	## Questions time
	####################
	def questionsTime(self):

		previousState = self.getState()
		self.setState('questionsTime')
		self.movement_service.setMoveHead(True)

		while not self.stop_v and self.state != 'breakQuestionsTime':
			if self.state == 'askMoreQuestions':
				self.movement_service.setMoveHead(True)
				self.speech_service.sayGlobal('askMoreQuestion')
				self.setState('questionsTime')
			elif self.state == 'pointLeft':
				self.movement_service.setMoveArmLeft(True)
				self.speech_service.sayGlobal('questionPointing')
				self.setState('questionsTime')
			elif self.state == 'pointCenter':
				self.movement_service.setMoveArmCenter(True)
				self.speech_service.sayGlobal('questionPointing')
				self.setState('questionsTime')
			elif self.state == 'pointRight':
				self.movement_service.setMoveArmRight(True)
				self.speech_service.sayGlobal('questionPointing')
				self.setState('questionsTime')
			else:
				self.doPause()
				time.sleep(0.5)
				self.movement_service.setMoveArmLeft(False)
				self.movement_service.setMoveArmCenter(False)
				self.movement_service.setMoveArmRight(False)

		self.setState(previousState)

		print('>> Questions time complete')



	####################
	## Robot point the left
	####################
	def pointLeft(self):
		self.setState('pointLeft')



	####################
	## Robot point the center
	####################
	def pointCenter(self):
		self.setState('pointCenter')



	####################
	## Robot point the right
	####################
	def pointRight(self):
		self.setState('pointRight')



	####################
	## Ask if more questions
	####################
	def moreQuestions(self):
		self.setState('askMoreQuestions')



	####################
	## Break questions time
	####################
	def breakQuestions(self):
		self.setState('breakQuestionsTime')

	
	####################
	## Set Introduce State
	####################
	def introduceState(self):
		self.setState('introduce')
		print('>> [DEBUG]  Set state = introduce')

	####################
	## Set Listen State
	####################
	def listenState(self):
		self.setState('listen')
		print('>> [DEBUG]  Set state = listen')

	####################
	## Set Asking State
	####################
	def askingState(self):
		self.setState('asking')
		print('>> [DEBUG] Set state = asking')



	####################
	## Questions time
	####################
	def speakerPreparation(self):

		previousState = self.getState()
		self.setState('speakerPreparation')
		self.speech_service.sayGlobal('askSpeakerPreparation')
		self.goSpeak()

		while not self.stop_v and self.state != 'speakerReady':
			self.doPause()
			time.sleep(0.5)

		self.setState(previousState)

		print('>> Speaker preparation complete')



	####################
	## Speaker ready
	####################
	def speakerReady(self):
		self.setState('speakerReady')



	####################
	## Set the current speaker as the next speaker if exist
	####################
	def next(self):
		speakers = self.data_service.getSpeakers()
		nextIdSpeaker = sys.maxsize
		nextSpeaker = None
		for speaker in speakers:
			if speaker.id > self.commands.currentSpeaker.id:
				if speaker.id < nextIdSpeaker:
					nextIdSpeaker = speaker.id
					nextSpeaker = speaker
		if not nextSpeaker:
			print('>> No speaker after current')
			return False
		else:
			self.commands.currentSpeaker = nextSpeaker
			self.commands.currentTimer = self.commands.currentSpeaker.duration
			self.commands.updateGui()
			return True



	####################
	## Set the current speaker as the previous speaker if exist
	####################
	def previous(self):
		speakers = self.data_service.getSpeakers()
		previousIdSpeaker = 0
		previousSpeaker = None
		for speaker in speakers:
			if speaker.id < self.commands.currentSpeaker.id:
				if speaker.id > previousIdSpeaker:
					previousIdSpeaker = speaker.id
					previousSpeaker = speaker
		if not previousSpeaker:
			print('>> No speaker before current')
		else:
			self.commands.currentSpeaker = previousSpeaker
			self.commands.currentTimer = self.commands.currentSpeaker.duration
			self.commands.updateGui()



	####################
	## Engage question time
	####################
	def breakListen(self):
		self.setState('asking')



	####################
	## Find and preload the first speaker
	####################
	def firstSpeaker(self):
		self.commands.currentSpeaker = self.data_service.getFirstSpeaker()
		self.commands.updateGui()



	####################
	## Rest robot
	####################
	def rest(self):
		self.movement_service.rest()

		print('>> Rest mode complete')



	####################
	## Robot go to speaking location
	####################
	def goSpeak(self):
		if self.commands.speakingLocation is not None:
			self.goTo(self.commands.speakingLocation)
			print('>> Go to speaking position complete')
		else:
			print('>> [ERR] Could not go to speaking location - No speaking location defined')

		



	####################
	## Robot go to waiting location
	####################
	def goWait(self):
		if self.commands.waitingLocation is not None:
			self.goTo(self.commands.waitingLocation)
			print('>> Go to waiting position complete')
		else:
			print('>> [ERR] Could not go to waiting location - No waiting location defined')

		



	####################
	## Robot go to asking location
	####################
	def goQuestion(self):
		if self.commands.askingLocation is not None:
			self.goTo(self.commands.askingLocation)
			print('>> Go to asking position complete')
		else:
			print('>> [ERR] Could not go to asking location - No asking location defined')

		



	####################
	## Move the robot: RIGHT
	####################
	def moveRobotRight(self):
		# TODO
		print('>> Robot moving right')

	####################
	## Move the robot: LEFT
	####################
	def moveRobotLeft(self):
		# TODO
		print('>> Robot moving left')

	####################
	## Move the robot: FORWARD
	####################
	def moveRobotForward(self):
		# TODO
		print('>> Robot moving forward')

	####################
	## Move the robot: BACKWARD
	####################
	def moveRobotBackward(self):
		# TODO
		print('>> Robot moving backward')

	####################
	## Move the robot: TURN RIGHT
	####################
	def moveRobotTurnRight(self):
		# TODO
		print('>> Robot turning right')

	####################
	## Move the robot: TURN LEFT
	####################
	def moveRobotTurnLeft(self):
		# TODO
		print('>> Robot turning left')


	####################
	## Save position as speaking location
	####################
	def saveSpeak(self):
		self.commands.speakingLocation = self.movement_service.getPosition()

		print('>> Speaking location saved')



	####################
	## Save position as waiting location
	####################
	def saveWait(self):
		self.commands.waitingLocation = self.movement_service.getPosition()

		print('>> Waiting location saved')



	####################
	## Save position as asking location
	####################
	def saveQuestion(self):
		self.commands.askingLocation = self.movement_service.getPosition()

		print('>> Asking location saved')



	####################
	## Robot go to the position
	####################
	def goTo(self, targetPosition):

		reach = False
		arrived = False
		cpt = 0
		f = 7
		while (not reach) and (not self.stop_v):
			self.doPause()
			if not self.stop_v:
				cpt += 1
				robotPosition = self.movement_service.getPosition()
				dx = targetPosition.x - robotPosition.x
				dy = targetPosition.y - robotPosition.y
				dtheta = targetPosition.theta - robotPosition.theta

				alpha = 0
				if dx == 0:
					if dy > 0:
						alpha = math.pi/2
					elif dy < 0:
						alpha = math.pi/2
				else:
					alpha_inter_tan = dy / dx
					alpha_inter = math.atan(alpha_inter_tan)
					if dx < 0:
						if dy < 0:
							alpha = -math.pi + alpha_inter
						else:
							alpha = math.pi + alpha_inter
					elif dx > 0:
						alpha = alpha_inter
					else:
						if dy < 0:
							alpha = math.pi

				angleToMove = alpha - robotPosition.theta
				xToMove = math.sqrt(math.pow(dx,2) + math.pow(dy,2))
				epsilon = 0.01
				if abs(angleToMove) > epsilon*10 and (xToMove > epsilon*10):
					self.movement_service.updateMovement(0, 0, angleToMove)
					f = 7

				elif xToMove > epsilon*f:
					self.movement_service.updateMovement(xToMove, 0, angleToMove)

				elif abs(xToMove) > epsilon*10 or abs(dtheta) > epsilon:
					f = 10
					self.movement_service.updateMovement(dx, dy, 0)
					if dtheta > math.pi:
						dtheta = dtheta - 2*math.pi
					elif dtheta < -math.pi:
						dtheta = dtheta + 2*math.pi
					self.movement_service.updateMovement(0, 0, dtheta)

				elif abs(xToMove) <= epsilon*10 and abs(dtheta) <= epsilon:
					reach = True

				else:
					print('ERROR, you cannot come here -> engine.goTo()')

		self.stopMovements()
		#print('>> Go To position complete')



	####################
	## Stop robotMovement	
	####################
	def stopMovements(self):
		self.movement_service.standby()
		self.speech_service.standby()



	####################
	## Set the current state and share it with command	
	####################
	def setState(self, s):
		self.state = s
		self.commands.currentState.set('State: ' + str(self.state))



	####################
	## Get the current state
	####################
	def getState(self):
		return self.state
