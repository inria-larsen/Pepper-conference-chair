#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1

import time
import math

class Tablet:
	def __init__(self, session, configFile):
		self.tablet_service = session.service("ALTabletService")
		self.stop_v = False
		self.pause_v = False
		self.configParser = configFile
		ip = self.configParser.get('connect', 'ipTablet')
		uid = self.configParser.get('connect', 'uidTablet')
		self.appPath = 'http://' + ip + '/apps/'+ uid
		self.timerPath = self.configParser.get('connect', 'timerPath')
		self.imagePath = self.configParser.get('connect', 'imagePath')
		self.logo()



	####################
	## Prepare the robot to display something on the tablet, empty for now
	####################
	def prepareRobot(self):
		self.stop_v = False
		self.pause_v = False



	####################
	## Stop service
	####################
	def stop(self):
		self.pause_v = False
		self.stop_v = True



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
		self.stop()
		self.tablet_service.hideWebview()
		time.sleep(1)
		self.tablet_service.hideImage() # Sometimes the image stay after the global exit, need more test to know the reason



	####################
	## Display the timer of the current speaker
	####################
	def showTimer(self):
		url = self.appPath + self.timerPath
		self.tablet_service.loadUrl(url)
		self.tablet_service.showWebview()
		time.sleep(2)



	####################
	## Display the logo
	####################
	def updateTimer(self, time, negative = False):
		# Time calculations for hours, minutes and seconds
		minutes = math.trunc(time / 60);
		seconds = math.trunc(time % 60);
		script = 'document.getElementById("countDown").innerHTML = '
		if negative:
			script += '"- "+'
		script += str(minutes) + ' + "m " + ' + str(seconds) + ' + "s ";'
		# inject and execute the javascript in the current web page displayed
		self.tablet_service.executeJS(script)



	####################
	## Display the logo
	####################
	def showExpired(self):
		script = 'document.getElementById("expired").innerHTML = "EXPIRED";'
		# inject and execute the javascript in the current web page displayed
		self.tablet_service.executeJS(script)



	####################
	## Display the logo
	####################
	def logo(self):
		self.tablet_service.setBackgroundColor('#FFFFFF') # Put a white background
		url = self.appPath + self.imagePath
		self.tablet_service.showImage(url)



	####################
	## Hide the tablet view to engage questions part
	####################
	def timerClean(self):
		self.tablet_service.hideWebview()
