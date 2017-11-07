#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1


from __future__ import print_function
from commands import Commands

import qi
import argparse
import sys
import ConfigParser



if __name__=="__main__":

	# Check option's command
	parser = argparse.ArgumentParser()
	parser.add_argument("--config", type=str, default='demo', help="Config file name")
	args = parser.parse_args()

	# Read the config file
	configParser = ConfigParser.RawConfigParser()
	configFilePath = 'config/' + args.config + '.cfg'
	configParser.read(configFilePath)
	ip = configParser.get('connect', 'ipRobot')
	port = configParser.get('connect', 'portRobot')
	defaultGui = 'yes'
	speakersFilePath = 'dialog/' + args.config + '_speakers.json'
	emergenciesFilePath = 'dialog/emergencies.json'
	jokesFilePath = 'dialog/jokes.json'
	speakingFilePath = 'dialog/global.cfg'

	# Create connection session
	session = qi.Session()

	try:
		session.connect("tcp://" + ip + ":" + port)
	except RuntimeError:
		print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + port +".\n"+"Please check your script arguments. Run with -h option for help.")
		sys.exit(1)
    
	# Start robot program
	Commands(session, configFilePath, speakersFilePath, speakingFilePath, emergenciesFilePath, jokesFilePath)
