# Pepper conference chair

This software is about using Pepper as a conference chair or co-chair. It can be used for conferences, workshops, lab meetings etc. Pepper's laptop is used to show the conference logo, or team logo; while a speaker is presenting, the laptop is used to show the remaining time for the presentation, in the form of a countdown. Configuration files are used to specify the robot's sentences, the speakers list and time for each presentation. In the ideal case, the robot follows a finite state machine consisting of:
1) iintroducing speaker
2) countodown for the presentation
3) thanking the speaker
4) asking if there are questions
However our lab experience is that there is always something unpredictable happening...
Therefore we provide a GUI to pilot the robot in a Wizard of Oz mode, if needed. Actually, in most occasions you may need to tele-operate the robot if you are aiming to have timely and appropriate behaviors.
Future works include trying to make this demo as much as autonomous as it can be, considering that:
- the speech recognition of Pepper does not work in a lab meeting room, you need to be very close to the robot and pronounce things almost perfectly;
- from the oboard camera it is very difficult to identify human behavioral cues that indicate "I want to ask a question", especially in a lab meeting room with dim lights
- making it robust to real situations


## Requirements

* Python 2.7 (https://www.python.org/downloads/release/python-2713/)
* NAOqi (http://doc.aldebaran.com/2-4/dev/python/install_guide.html#python-install-guide)
* Tkinter (http://www.tkdocs.com/tutorial/install.html)

Note: for the moment it has only been tested in Ubuntu 16.04

## Installation

* Time_on_Pepper is the application that should be installed bia Choreographe on the robot.
* Operator_controller is the main application and GUI providing the commands and controls for the operator.

Instructions for installation are inside each application folder.


## License

CeCILL FREE SOFTWARE LICENSE v2.1 - visit http://www.cecill.info


## Acknowledgments

The software was mostly coded by Baptiste Mounier, with the help of Olivier Rochel and Serena Ivaldi.
