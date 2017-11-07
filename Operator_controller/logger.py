#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


import time
import datetime

class Logger:
	def __init__(self):
		ts = time.time()
		path = 'logs/log_' + str(ts) + '.txt'
		self.file = open(path, 'a')



	####################
	## Add a log into the file
	####################
	def addLog(self, command, details = None):
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		log = st
		if details is None:
			log += ' ' + command
		else:
			log += ' ' + command + ' on ' + details
		log += '\n'
		self.file.write(log)



	####################
	## Add a log into the file
	####################
	def closeFile(self):
		self.file.close()

