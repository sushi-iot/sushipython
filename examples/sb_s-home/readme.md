## Sushi Home project

### Description

Home domotics demo project.

**Features**
* Heater system thermostat: control a relay output connect to heater system
    - Local control on physical interface
    - Remote control by SMS
* Main power loss/return detection
    - Alert by SMS
* Get status by SMS

**Version** : `v1.1.0 - 2026-02-28`  

**Video demo** : [Sushi IoT on instagram](https://www.instagram.com/sushi_board_iot/)

---
### Source files
* **"sushi_home.py"** : main program script file.
* **"sushi_home_config.py"** : sushi IoT configuration e project settings

**Optional**
* **"../common/sushi_board_setup.py"** : board complete system setup reset (see note "SYSTEM SETUP FROM THIS SCRIPT" in "sushi_home_config.py")

---
### Instructions

**Start guide**
* Assemble the Sushi Board (see hardware components section).
* Download and flash the latest [Sushi IoT Firmware](https://github.com/sushi-iot/sushipython/releases) onto the board. 
* Connect the ESP32DevKitC board to your PC by the USB connector (or use WebREPL if you prefer). 
* If you are new to MicroPython see this [basic MicroPython  guide](https://sushi-iot.github.io/sushipython/coding/).    
* Transfer the '.py' project source files (see source files list) to the board using your favourite MicroPython interface.  
* Run the main script file.
* From the REPL output it's possible check the script execution output.
* To interrupt the script execution and return to the REPL prompt press "CTRL+C" (as you can see from the py code to manage all the tasks the script run a main loop).

**Setup**
* Application specific setting are into file "sb/SUSHI_HOME.json" (self created after the 1st script run):
    - "modem_enabled_numbers" : List of phone numbers enabled to send/receive SMS.
* Required system settings (file "sb/SYSTEM.json"):
  Modem SIM parameters:  
    - "modem_sim_sms_center" : operator SMS center number (necessary to let the modem manage SMS messages)
    - "modem_sim_pin" : your SIM pin
    - "modem_apn" : SIM operator APN
    - "modem_user" : SIM operator user (if required)
    - "modem_passwd" : SIM operator password (if required)  

For more details about settings see comments in "sushi_home_config.py" file

**Testing the project**

* **Heater system**
  - When the heater must start, it switches on the relay output. This is visible from the red LED on it.
  - By scrolling the user menu, enter "Thermostat". This menu is added by this project. From here it is possible to set the heater target temperature.
  - From the "DIAGNOSTIC" menu it is possible to check the actual temperature read from the sensor.
  - It is possible to set the target temperature by sending an SMS with the text "#SET-TEMP=...", for example "#SET-TEMP=22.5". Note: the source number must be included in the `MODEM_ENABLED_NUMBERS` list.

* **Main power loss/return detection**
  - By plugging or unplugging the main power supply, the script sends a status SMS message informing about the change to every number defined in the `MODEM_ENABLED_NUMBERS` list.

* **SMS status monitor**
  - It is always possible to check the system status by sending an SMS with the text "#STATUS?". The script replies only to this number (if it is included in the `MODEM_ENABLED_NUMBERS` list) with a status SMS.

---
### Hardware components

This project uses a Sushi IoT Board PCBA.  
Since Sushi Board PCBA just connect **common commercial modules** this project can be built even using a breadboard or a custom protoboard.  
All details about used modules, components & schematics are in Sushi Board doc:  

* [Sushi Board overview](https://sushi-iot.github.io/sushi-iot-board/)
* [Sushi-Iot-Board schematic & components](https://github.com/sushi-iot/sushi-iot-board)

---
### Overview

[Sushi IoT on instagram](https://www.instagram.com/sushi_board_iot/)

---
### Hardware connections table

For test/demo purposes, this project does not require any external hardware.
In a real application, the heater system must be connected to the relay output and an external DS18B20 cabled temperature sensor is recommended to measure the environment correctly (for test purpose by default is used the onboard DS18B20 sensor).

---
### Resources

[Sushi-Iot-Board](https://github.com/sushi-iot/sushi-iot-board)  
[Sushi IoT Firmware download](https://github.com/sushi-iot/sushipython/releases)  
[Online coding manual](https://sushi-iot.github.io/sushipython/coding/)  
[Sushi IoT project overview](https://sushi-iot.github.io/sushipython/)  
[Sushi IoT Framework microPython quick reference](https://github.com/sushi-iot/sushipython/tree/main/examples/sushi-quick-reference.md)  