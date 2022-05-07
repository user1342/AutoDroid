
<p align="center">
    <img width=100% src="image.png">
  </a>
</p>
<p align="center"> 📱 A tool for automating interactions with Android devices - including ADB, AndroGuard, and Frida interactivity.  📦</p>

<br>
# AndroidInterface
## Instalation
Use the provided requirements file to install all required dependancies. 

```
pip install -r REQUIREMENTS.txt
```

## Usage
Running the python file with a json configuration file will begin automating device interaction.

```
python AndroidInterface.py config.json
```

An example config can be seen below:

```json
{
  "devices": ["*"],
    "apps": ["*"],
    "variables": {},
    "commands": {
      "begining": ["adb -s !device_id shell monkey -p !app_id 1"],
      "middle": ["adb pull !app_path !app_id.apk"],
      "again": ["block:begining"]
    }
}

```


### Config fields
The Json config contains several paramiters for configuring an interaction with a device.
- apps - This field defines what applications the tooling targets. This can be empty, a list of reverse notation paths such as ```com.example.application```, or ```*``` which will target all applications on the device. When using this the ```app_path``` and ```app_id``` variables are added to the variable list.
- devices - This field defines what devices the tooling targets over adb. This can be empty, a list of device IDs, or ```*``` which will target all connected devices. When using this the ```!device_id``` variable is added to variables and can be used to access the device id.
- variables - This is a map of key value pairs. During execution of commands all keys will be replaced with their values. I.e. adding ```{"!script":"ls"}``` will replace the ```!script``` string with ```ls``` in all commands.  
- commands - A dictionary or list of blocks to be executed. If a list is provided it is defined as a block with name ```name```. Outside of this a map can be provided with keys for the command block name and the value being a list of commands to execute. In addition to this a command can be started with ```block:``` to run anouther block provided after the ```:```, ```reverse:``` to run AndroGuard on an APK on the path after the ```:```, and ```Frida:``` followed by the Javascript file a ```;``` and the package name to use a frida javascript script.
