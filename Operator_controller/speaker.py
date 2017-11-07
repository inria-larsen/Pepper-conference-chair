#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pepper co-chair
# Authors: Baptiste Meunier, Serena Ivaldi (Inria)
# Copyright: Cecill v2.1

class Speaker:
	def __init__(self, id_speaker, intro, dura, extraDura):
		self.id = id_speaker
		self.introduction = intro
		self.duration = dura
		self.extraDuration = extraDura
