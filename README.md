# MPVScreensaver
A simple Python script to launch MPV in fullscreen mode with looping.

## Dependencies

* Python 3
* MPV

## Installation

 1. Download the script file `screensaver.py` from this repository to a directory where you have execution permissions.
 1. Open it in a text editor and adjust the configuration section.
 1. Give the script executable permissions. For example, `chmod u+x screensaver.py`
 1. Test it by running `screensaver.py some_video.mkv` in a terminal.
 1. Configure your desktop environment (DE) to run the script when idle. In KDE, this can be found in System Settings → Power Management → Other settings.

## Usage

```
screensaver.py [video1 video2 ...]
```
The script can play videos, music, and images in any combination. Paths can be provided as arguments or defined in a special variable within the script.

## Known Issues

Videos play normally when you run the script yourself, but when the script is started on idle, elements of the desktop environment are seen over the videos. This is an effect of a feature called "Focus stealing prevention". When the system thinks the window appeared without a user input, it prevents this window from taking the focus. To solve, disable the feature globally or only for the windows with the word MPVScreensaver as a part of the title. 


Mouse pointer sometimes does not hide until the mouse is moved. Working on it. 


On multimonitor systems, two videos start on the same monitor - tell me if you encounter this reliably. 

## Other
* This project was written with the use of DeepSeek AI. 
* This project is managed with `UV`

