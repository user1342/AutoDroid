import json
import subprocess
import sys
import time

import frida as frida
from androguard.misc import AnalyzeAPK


class AndroidInterface():
    """
    A class for automating interaction with Android devices.
    """

    # A boolean on if device IDs are being used.
    _using_devices = False
    # A boolean defining if application ids are being used.
    _using_apps = False
    # A global variable defining the key value pairs, where the key is replaced by the value
    _variables = {}
    # A global variable defining the current device being used
    _active_device_id = None

    def __init__(self):
        pass

    def _clean_terminal_response(self, byte_to_clean):
        """
        Used to clean a response. Primarily decodes a byte to string and removes uncesseary new line characters
        :param byte_to_clean:
        :return: a string without newline characters.
        """
        return byte_to_clean.decode().replace("\r", "").replace("\n", "")

    def _is_adb_available(self):
        """
        Runs a simple adb command to check if a device is connected via adb.
        :return: True if a device is connected via adb
        """
        adb_available = True

        result = self._execute_command("adb")
        if result is None or str(result).startswith("error"):
            adb_available = False

        return adb_available

    def _get_all_devices(self):
        '''
        A function for returning all connected device. Used if the config provides a '*' to the config.
        :return: a list of device IDs
        '''

        devices = self._execute_command("adb devices")
        device_ids = []
        for device in devices:
            device = self._clean_terminal_response(device)
            device_split = device.split("\t")
            id = device_split[0]

            if not id.startswith("List"):
                device_ids.append(id)
        return device_ids

        raise Exception("All devices not implemented")

    def _get_list_of_device_packages(self):
        """
        Runs a series of commands to identify which application packages are installed on a device.
        :return: a list of the installed packages
        """
        packages = self._execute_command("adb -s {} shell pm list packages".format(self._active_device_id))

        iterator = 0
        for package in packages:
            package = self._clean_terminal_response(package)
            packages[iterator] = package.replace("package:", "")
            iterator = iterator + 1

        return packages

    def _get_paths(self, list_of_packages):
        """
        Identifies the apk path of for a list of packages
        :param list_of_packages: a list of packages
        :return: a list of APK locations relating to the provided package names
        """
        list_of_paths = []

        for package in list_of_packages:
            package = package.replace("package:", "")
            paths = self._execute_command("adb -s {} shell pm path {}".format(self._active_device_id, package))

            for path in paths:
                path = self._clean_terminal_response(path)
                path = path.replace("package:", "")
                list_of_paths.append(path)

        return list_of_paths

    def _execute_blocks(self, blocks_dict):
        '''
        A function used for executing all blocks of commads. :param blocks_dict: a dictionary of key value pairs,
        where the key is the block name and the value is the list of commands.
        '''
        for block in blocks_dict:
            self._execute_block(blocks_dict[block], blocks_dict)

    def _execute_block(self, block_list, blocks_dict):
        '''
        A function for executing a single block of commands.
        :param block_list: a list of commads belonging to the block being executed.
        :param blocks_dict: The dictionary of all blocks.
        '''
        for command in block_list:
            try:
                if command.startswith("block:"):
                    command = command.replace("block:", "")
                    command = command.strip()
                    self._execute_block(blocks_dict[command], blocks_dict)

                elif command.startswith("sleep:"):
                    command = self._construct_command(command)
                    time_to_sleep = command.replace("sleep:", "").strip()
                    time.sleep(int(time_to_sleep))

                elif command.startswith("frida:"):
                    command = self._construct_command(command)
                    frida_command = command.replace("frida:", "").strip()
                    java_script_code_path, package_name = frida_command.split(";")

                    def my_message_handler(message, payload):
                        print(message)
                        print(payload)

                    # Opens a session with the device/ process/ gaget
                    session = frida.get_usb_device().attach(package_name)

                    # Reads and executes the javascript code
                    with open(java_script_code_path) as f:
                        file_data = self._construct_command(f.read())
                        script = session.create_script(file_data)
                    script.on("message", my_message_handler)
                    script.load()

                elif command.startswith("reverse:"):
                    command = self._construct_command(command)
                    apk_path = command.replace("reverse:", "").strip()
                    a, d, dx = AnalyzeAPK(apk_path)
                    a.new_zip("{}.zip".format(apk_path))

                else:
                    formatted_command = self._construct_command(command)
                    self._execute_command(formatted_command)
            except:
                print("Command {} failed".format(command))

    def _execute_command(self, command):
        """
        Runs a command provided as a string with subprocess.popen.
        :param command: a string representation of a shell command
        :return: a list of the result of the provided command
        """
        proc = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        lines = proc.stdout.readlines()
        print("Run command: '{}'".format(command))
        if lines is not None and len(lines) > 0:
            print("\tResult: '{}...".format(lines[0]))
        else:
            print("No response from command")
        return lines

    def _construct_command(self, command):
        '''
        A function for replacing all defined variable/ wildcards in the command
        :param command:
        :return: a command that has been replaced with the provided variables/ wildcards
        '''
        for variable in self._variables:
            # replace the variable
            command = command.replace(variable, self._variables[variable])
        return command

    def _initialise_commands(self, devices, apps, blocks):
        '''
        Initialises the commands
        :param devices: a list of devices to target from the config.
        :param apps: a list of applications being targeted.
        :param blocks: a list of command blocks.
        '''

        # If using devices and apps, have a nested loop and set the variables
        if self._using_devices and self._using_apps:

            for device in devices:

                if device == '':
                    continue

                self._active_device_id = device
                self._variables["!device_id"] = device

                if apps[0] == "*":
                    self._using_apps = True
                    apps = self._get_list_of_device_packages()
                elif len(apps) > 0:
                    self._using_apps = True
                else:
                    self._using_apps = False


                for app in apps:
                    self._variables["!app_id"] = app
                    paths = self._get_paths([app])
                    self._variables["!app_path"] = paths[0]
                    self._execute_blocks(blocks)

        # If using just devices loop through them and set device variable
        elif self._using_devices and not self._using_apps:
            for device in devices:
                self._active_device_id = device
                self._variables["!device_id"] = device
                self._execute_blocks(blocks)

        # If using just apps loop through them and set the app variable
        elif not self._using_devices and self._using_apps:

            if apps[0] == "*":
                self._using_apps = True
                apps = self._get_list_of_device_packages()
            elif len(apps) > 0:
                self._using_apps = True
            else:
                self._using_apps = False

            for app in apps:
                self._variables["!app_id"] = app
                self._execute_blocks(blocks)

    def _read_config(self, config_file_path):
        '''
        A function for reading the JSON config
        :param config_file_path: the path to the config file
        :return: devices, apps, blocks
        '''
        devices = []  # generates !device-id variable. loop for amount off devices selected
        blocks = {}
        commands = []
        variables = {}  # adb, block, frida, reverse, bash/ normal
        apps = []  # none, all, class paths # generates !app variable. loop for amount off apps selected
        with open(config_file_path) as json_file:
            config_data = json.load(json_file)

            # Set devices being used
            devices = config_data["devices"]

            if devices[0] == "*":
                self._using_devices = True
                devices = self._get_all_devices()
            elif len(devices) > 0:
                self._using_devices = True
            else:
                self._using_devices = False

            if "variables" in config_data:
                self._variables = config_data["variables"]

            # Set apps being used
            apps = config_data["apps"]

            if len(apps) > 0:
                self._using_apps = True
            else:
                self._using_apps = False

            # Set blocks
            if type(config_data["commands"]) == dict:
                blocks = config_data["commands"]

                for block in blocks:
                    for command in block:
                        commands.append(command)

            # create a main block if none given
            elif type(config_data["commands"]) == list:
                blocks["main"] = config_data["commands"]

        return devices, apps, blocks

    def run(self, conig_path):
        if self._is_adb_available():
            devices, apps, blocks = self._read_config(conig_path)
            self._initialise_commands(devices, apps, blocks)
        else:
            raise Exception("ADB not available")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        device_manager = AndroidInterface()
        device_manager.run(sys.argv[1])
    else:
        raise Exception("Please provide a configuration json file")