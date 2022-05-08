
<p align="center">
    <img width=100% src="cover.png">
  </a>
</p>
<p align="center"> 📱 A tool for automating interactions with Android devices - including ADB, AndroGuard, and Frida interactivity.  📦</p>

<br>

AutoDroid is a Python tool for programatically scripting bulk interactions with an Android device, possibly use cases include:
- Downloading and extracting all APKs from all connected devices.
- Testing a developed application on a multiple devices at once.
- Testing potential malware against a suite of AV products.

# Getting Started
First things first you will need to install the dependancies of AutoDroid, these are specified in the requirements file and can be installed by following the below command.

```bash
pip install -r REQUIREMENTS.txt
```

AutoDroid needs to be provided a valid Json configuration file as a command line argument. The below shows a simple configuration file example that will retrieve all applications from all connected devices one at a time and extract the APKs to zips using AndroGuard.

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": ["adb pull !app_path !app_id.apk","reverse: !app_id.apk"]
}
```

Once you have created a valid AutoDroid configuration file you can begin device interaction by running the ```AutoDroid.py``` python file with the configuration file as it's command line paramiter.

```bash
python AutoDroid.py config.json
```
# Commands and blocks
The AutoDroid configuration file can be provided with a series of commands to execute on the target devices, these commands are run locally on your machine and so the programs and files being called must be present. These commands can be in either a list format (as can be seen in the example above) or as a key value pair map. These key value pairs are defined as blocks of commands, where the constant (escribed below) ```block:<block name>``` can be used to run a block. An example of using blocks can be seen below.

```json 
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": {
      "test_user_input":["adb shell monkey -v 5 -p !app_id"],
      "retrieve_apk":["adb pull !app_path !app_id.apk","sleep:5"]
    }
}
```

# Devices and apps
Two additional fields that are instramental to AutoDroid are the ```devices``` and ```apps``` fields. These fields define the adb device ID for the device(s) being targeted (a list of strings) and the application reverse domain notation name (i.e. ```com.example.application```) for the applications provided (a list of strings). Both of these fields can be empty or defined as ```*``` where all available devices and apps will be targeted. In the backend the way this works is when a value is provided in these fields the program will loop through all commands in order for each application on each device. An example of specifiying a specific device and app can be seen below:

```json
{
  "devices": ["09261JEC216934"],
    "apps": ["com.google.android.networkstack.tethering"],
    "commands": ["adb pull !app_path !app_id.apk"]
}
```

When the devices fields is not empty (i.e. ```"devices":[],```) a variable (see below) of ```!device_id``` is created. This variable can be used in your commands to denote the ADB device ID for the current targeted device. Similarly the variables ```!app_id```, and ```!app_path``` are added when the app field is not empty and can be used in commands to define the app reverse domain notation name and the path to that application's APK file.

# Variables
To save time, AutoDroid allows for an infinate amount of variables to be set in a script. These variables can be throught of as wildcards and are constructed in a key value pair format. When the key of a variable is located in a command it will be replaced for the value. An example configuration that utilises variables can be seen below, in this configuration file the variable ```!test``` has been added as short hand for a ```monkey``` adb command and the built-in variable ```!app_id``` is also used. 

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "variables": {"!test": "adb shell monkey -v 500 -p"},
    "commands": ["!test !app_id"]
}
```

The preffered standard for using variables is to presede them with a ```!``` and to use ```_``` instead of spaces. The following variables are reserved and should not be included in your configuration file: ```!device_id```, ```!app_id```, and ```!app_path```. 

# Constants
Constants are commands specific to AutoDroid and relate to specific functionality. Normally broken down into a keyword followed by a ```:``` and then one or more variables delimiated by a ```;``. These constants must be used at the start of a command and should always be in lower case. Examples will be given in the individual setions.

## Frida 
AutoDroid has built in functionality to run Frida JavaScript files as part of an AutoDroid run. This constant is defined as ```frida:``` and must be provided the path to the Javascript file being used, followed by a ```;``` and then the application reverse notation name of the application being targeted. In addition to applying variables to the command, variables are also applied to the contents of the file provided. 

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": ["frida:myJavascript.js;!app_id"]
}
```

***note*** while the Frida itegration is implemented, it is currently untested. 

## AndroGuard 
AutoDroid supports reverse engineering APKs via AndroGuard. This constant is structures as ```reverse:``` and takes a path to a locally stored APK. 

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": ["adb pull !app_path !app_id.apk","reverse: !app_id.apk"]
}
```

## Sleep 
This constant provides simple functionality for pausing execution of the tooling for a specific amount of time. This constant is structured as ```sleep:``` followed by the amount of seconds to wait.

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": ["adb pull !app_path !app_id.apk","sleep:5"]
}
```

## Block
The block constant provides simple looping and callback functionality. This constant is structures as ```block:``` followed by the name of the block of commands to execute. If no blocks have been provided in the config then use ```main```.

```json 
{
  "devices": ["*"],
    "apps": ["*"],
    "commands": {
      "test_user_input":["adb shell monkey -v 5 -p !app_id"],
      "retrieve_apk":["adb pull !app_path !app_id.apk"],
      "test_again": ["block: test_user_input","sleep:5"]
    }
}
```

# More complex configs
