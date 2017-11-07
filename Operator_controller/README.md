# Pepper conference chair

This is the main application for the Operator controlling the Pepper in a Wizard of Oz fashion.

## Requirement

* Python 2.7 (https://www.python.org/downloads/release/python-2713/)
* NAOqi (http://doc.aldebaran.com/2-4/dev/python/install_guide.html#python-install-guide)
* Tkinter (http://www.tkdocs.com/tutorial/install.html)

Note: for the moment it has only been tested in Ubuntu 16.04

## Installation

TBD

# Use

## General

A basic step-by-step sequence to use the more automatic mode:

* 1- Launch the main script (__python main.py__)
 * If you want to use your own configuration file, use __python main.py --config yourfilename__ (_python main.py --config humanoid_ will use humanoids.cfg insteed of demo.cfg and dialog/humanoids\_speaker.json insteed of demo\_speakers.json
* 2- Move the robot with the keyboard (details in __Pilot__ subsection in __Commands__ section)
* 3- Save the three locations: __Save speaking__, __Save waiting__, __Save asking__
* 4- Initialise to prepare the presentation: __Initialisation__
* 5- Launch the presentation: __Launch__
* 6- Inform robot that it can start the introduction: __Speaker ready__
* 7- Inform robot that the speaker has finished his presentation: __Break listen__
 * Automatic if the speaker takes more time than he has
* 8- Optional and repeatable: ask if someone has a question: __More questions__
* 9- Optional and repeatable: robot points one direction and says that there is a questions from that side: __Left__, __Center__, __Right__
* 10- Inform robot that nobody has another question: __Break questions__
* 11- Repeat from step 6 until every speaker has done his presentation
* 12- Exit the program: __Exit__

For a more customized use:

* 1- Launch the main script (__python main.py__)
* 2- Move the robot with the keyboard (details in __Pilot__ subsection in __Commands__ section)
* 3- Save the three locations: __Save speaking__, __Save waiting__, __Save asking__
* 4- Use button as you want
 * See __Buttons__ subsection of __Commands__ section
* 5- Exit the program: __Exit__

We can also use the fast speaking feature at any time. To do this we have two ways.

The first one:
* 1- Write in the text area
* 2- Click on __Say__ button and Pepper will say the sentence in the text area

The second one:
* 1- Select a pre-created sentence in the list
* 2 (optional)- edit the sentence in the text area
* 3- Click on __Say__ button and Pepper will say the sentence in the text area


## Configuration

* Edit __config/demo.cfg__ file for the robot ip/port
 * Create a new file for a new configuration (see __General__ sub section for more details about its using)
* Edit __dialog/global.cfg__ file for the global sentence (__like The next speaker can start preparing the presentation.__ or __Thank you.__)
* Edit __dialog/demo_speaker.json__ file for the speakers informations
 * Create a new file for a new configuration (see __General__ sub section for more details about its using)
* Edit __dialog/emergencies.json__ file for the pre created emergency sentences
* Edit __dialog/jokes.json__ file for the pre created jokes sentences

# Commands

## Management mode

**Pilot**

You need to focus the window that appear to use commands

* z: move forward
* s: move backward
* q: turn left
* d: turn right
* a: straf left
* e: straf right

**Buttons**

Presentation
* Initialisation: prepare robot and check if it's ready to present (all locations saved or not)
* Launch: launch the presentation
* Introduce: introduce the current speaker
* Listen: inform and display the remaining time for the current speaker for his presentation
* Ask: ask if someone has questions
* More questions: ask if someone has more questions
* Break listen: break the __listen__ state
* Break questions: break the __asking__ state (can only be used during __questionsTime__ state, sub state of __asking__ state)
* Left: robot points to the left and say 'We have a question over there' (can only be used during __questionsTime__ state, sub state of __asking__ state)
* Center: robot points to the center and say 'We have a question over there' (can only be used during __questionsTime__ state, sub state of __asking__ state)
* Right: robot points to the right and say 'We have a question over there' (can only be used during __questionsTime__ state, sub state of __asking__ state)
* Go to speaking: move the robot to the speaking location
* Go to waiting: move the robot to the waiting location
* Go to asking: move the robot to the asking location
* Save speaking: save the current location as speaking location
* Save waiting: save the current location as waiting location
* Save asking: save the current location as asking location
* Speaker ready: inform robot that it can start the introduction 
* First speaker: put the first speaker as current speaker
* Next speaker: put the next speaker as current speaker
* Previous speaker: put the previous speaker as current speaker

Fast speaking
* Say: the robot say the sentence in the text area
* Sentences list: put the sentence in the text area

Loop:
* Stop: stop the current action
* Pause: pause the current action
* Resume: resume the last paused action
* Exit: leave program and release robot

# TODO
