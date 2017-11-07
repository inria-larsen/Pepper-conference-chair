#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


import threading
import math
import random
import qi
import almath
import time

class Movement: 



	####################
	## Initiate class
	####################
	def __init__(self, session):

		# Get the services ALMotion
		self.motion_service  = session.service("ALMotion")
		self.posture_service  = session.service("ALRobotPosture")
		self.compass_service  = session.service("ALVisualCompass")

		# Initiate movement's variables
		self.standby()

		self.ptask = qi.PeriodicTask()
		self.lock = threading.RLock()

		# Body movement
		period = 0.1
		us_period = int(period*1000000)

		self.ptask.compensateCallbackTime(True)
		self.ptask.setCallback(self.run)
		self.ptask.setUsPeriod(us_period)
		self.ptask.start(True)

		# Head movement
		periodHead = 2
		us_periodHead = int(periodHead*1000000)



	####################
	## Put robot in standby mode
	####################
	def standby(self):
		self.x = 0
		self.y = 0
		self.theta = 0
		self.xNext = 0
		self.yNext = 0
		self.thetaNext = 0
		self.setMoveBody(False)
		self.setMoveHead(False)
		self.setMoveArmLeft(False)
		self.setMoveArmCenter(False)
		self.setMoveArmRight(False)
		self.stop_v = False
		self.motion_service.moveToward(0, 0, 0)
		self.motion_service.waitUntilMoveIsFinished()
		self.posture_service.goToPosture("StandInit", 0.5)



	####################
	## Stop movements
	####################
	def stop(self):
		self.stop_v = True
		self.setMoveBody(False)
		self.setMoveHead(False)
		self.setMoveArmLeft(False)
		self.setMoveArmCenter(False)
		self.setMoveArmRight(False)
		self.x = 0
		self.y = 0
		self.theta = 0
		self.motion_service.moveToward(0, 0, 0)
		self.motion_service.waitUntilMoveIsFinished()



	####################
	## Prepare the robot to move
	####################
	def prepareRobot(self):
		self.motion_service.wakeUp()
		self.posture_service.goToPosture("StandInit", 0.5)
		self.x = 0
		self.y = 0
		self.theta = 0
		self.xNext = 0
		self.yNext = 0
		self.thetaNext = 0
		self.setMoveBody(False)
		self.setMoveHead(False)
		self.setMoveArmLeft(False)
		self.setMoveArmCenter(False)
		self.setMoveArmRight(False)
		self.stop_v = False



	####################
	## Do movement
	####################
	def run(self):
		with self.lock:

			if self.moveBody:

				self.motion_service.setMoveArmsEnabled(True, True)
				period = 0.5
				epsilon = 0.0001
				dx = math.fabs(self.xNext - self.x)
				dy = math.fabs(self.yNext - self.y)
				dt = math.fabs(self.thetaNext - self.theta)

				# Update moveToward parameters
				if(dx > epsilon or dy > epsilon or dt > epsilon):
					self.x = self.xNext
					self.y = self.yNext
					self.theta = self.thetaNext

					self.motion_service.moveToward(self.x, self.y, self.theta)

				names  = ["HeadYaw", "HeadPitch"]
				if self.theta < 0:
					angles  = [-0.4, -0.2]
				elif self.theta > 0:
					angles  = [0.4, -0.2]
				else:
					angles  = [0, -0.2]
				fractionMaxSpeed  = 0.2
				self.motion_service.setAngles(names, angles, fractionMaxSpeed)

			elif self.moveHead:

				angle = random.uniform(-0.7, 0.7)
				names  = ["HeadYaw", "HeadPitch"]
				angles  = [angle, -0.2]
				fractionMaxSpeed  = 0.2
				self.motion_service.setAngles(names, angles, fractionMaxSpeed)
				time.sleep(1.5)

			elif self.moveArmLeft:
				names  = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LWristYaw', 'LElbowRoll', 'HeadYaw', 'HeadPitch']
				angles  = [0.8, 0.75, -2, -1, -0.5, 0.7, -0.2]
				fractionMaxSpeed  = 0.2
				self.motion_service.setAngles(names, angles, fractionMaxSpeed)
				self.motion_service.openHand('LHand')

			elif self.moveArmCenter:
				names  = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RWristYaw', 'RElbowRoll', 'HeadYaw', 'HeadPitch']
				angles  = [0.5, 0.02, 1.5, 1, 0.8, 0, -0.2]
				fractionMaxSpeed  = 0.2
				self.motion_service.setAngles(names, angles, fractionMaxSpeed)
				self.motion_service.openHand('RHand')

			elif self.moveArmRight:	
				names  = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RWristYaw', 'RElbowRoll', 'HeadYaw', 'HeadPitch']
				angles  = [0.8, -0.75, 2, 1, 0.5, -0.7, -0.2]
				fractionMaxSpeed  = 0.2
				self.motion_service.setAngles(names, angles, fractionMaxSpeed)
				self.motion_service.openHand('RHand')



	####################
	## Update Head movement
	####################
	def updateMovementHead(self):
		pass



	####################
	## Update movement velocity
	####################
	def updateMovement(self, x = 0, y = 0, theta = 0):
		with self.lock:
			self.ptask.start(True)
			self.stop_v = False
			self.setMoveBody(True)
			rx = 1
			ry = 1
			if x < -1 or x > 1 or y < -1 or y > 1:
				if x < -1:
					rx = -1
				if y < -1:
					ry = -1
				mxy = max(abs(x), abs(y))
				x = (rx*(abs(x))/mxy)*0.8
				y = (ry*(abs(y))/mxy)*0.8
			self.xNext = x
			self.yNext = y
			if theta < -0.6:
				self.thetaNext = -0.6
			elif theta > 0.6:
				self.thetaNext = 0.6
			else:
				self.thetaNext = theta



	####################
	## Update movement velocity
	####################
	def updateMovementX(self, x):
		with self.lock:
			self.ptask.start(True)
			self.stop_v = False
			self.setMoveBody(True)

			self.xNext = x



	####################
	## Update movement velocity
	####################
	def updateMovementY(self, y):
		with self.lock:
			self.ptask.start(True)
			self.stop_v = False
			self.setMoveBody(True)

			self.yNext = y



	####################
	## Update movement velocity
	####################
	def updateMovementTheta(self, theta):
		with self.lock:
			self.ptask.start(True)
			self.stop_v = False
			self.setMoveBody(True)

			self.thetaNext = theta



	####################
	## Set dynamic head movements
	####################
	def setMoveBody(self, value):
		self.moveBody = value
		if(value == True):
			self.setMoveHead(False)
			self.setMoveArmLeft(False)
			self.setMoveArmCenter(False)
			self.setMoveArmRight(False)



	####################
	## Set move head movements
	####################
	def setMoveHead(self, value):
		self.moveHead = value
		if(value == True):
			self.setMoveBody(False)
			self.setMoveArmLeft(False)
			self.setMoveArmCenter(False)
			self.setMoveArmRight(False)



	####################
	## Set move head movements
	####################
	def setMoveArmLeft(self, value):
		self.moveArmLeft = value
		if(value == True):
			self.setMoveBody(False)
			self.setMoveHead(False)
			self.setMoveArmCenter(False)
			self.setMoveArmRight(False)



	####################
	## Set move head movements
	####################
	def setMoveArmCenter(self, value):
		self.moveArmCenter = value
		if(value == True):
			self.setMoveBody(False)
			self.setMoveHead(False)
			self.setMoveArmLeft(False)
			self.setMoveArmRight(False)



	####################
	## Set move head movements
	####################
	def setMoveArmRight(self, value):
		self.moveArmRight = value
		if(value == True):
			self.setMoveBody(False)
			self.setMoveHead(False)
			self.setMoveArmLeft(False)
			self.setMoveArmCenter(False)



	####################
	## Stop & clean service
	####################
	def exit(self):
		with self.lock:
			self.ptask.stop()
			self.stop()



	####################
	## Get robot position
	####################
	def getPosition(self):
		return almath.Pose2D(self.motion_service.getNextRobotPosition())



	####################
	## Put robot in rest mode
	####################
	def rest(self):
		self.motion_service.rest()
