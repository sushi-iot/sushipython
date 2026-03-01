import sushi
import sushi_utils

######################################
# SUSHI_HOME.json settings
######################################
'''
The file "sb/SUSHI_HOME.json" (self created after the 1st run) contains the application specific settings:

{
    "modem_enabled_numbers": ["+391111111111", "+342222222222"],	# List of phone numbers enabled to send/receive SMS.
    "thermo_temperature_target": 10									# Target temperature (no need to edit here, normally set by SMS or UI).
}
'''

######################################
# SUSHI Python configuration 
######################################
# SYSTEM SETTINGS
'''
System setting are stored into "sb/SYSTEM.json", and can be set in 3 ways:
* editing the system setting file "sb/SYSTEM.json".
* by web page (if board is connected to wifi) sending a JSON file or by the user interface.
* with micropython call "sushi_utils.set_sushi_config(...)" that sets certain setting to "sb/SYSTEM.json"

Important settings for this script are:
* Modem SIM setting:
    - "modem_sim_sms_center" : operator SMS center number (necessary to let the modem manage SMS messages)
    - "modem_sim_pin" : your SIM pin
    - "modem_apn" : SIM operator APN
    - "modem_user" : SIM operator user (if required)
    - "modem_passwd" : SIM operator password (if required)
'''

# SYSTEM SETUP FROM THIS SCRIPT (OPTIONAL)

# import sushi_board_setup as sbs
# sushi_utils.set_sushi_config(sbs.sushi_board_system_settings) #return: 0 = configuration not changed ; 1 = changed no need to restart ; 2 = changed and need to restart
''' 
Uncommenting the above code certain system setting are always forced at each script run. 
This is not in general the best way to set the system settings (because these parameters are hardcoded) but can be useful in certain situations like during debug/development.
Editing 'sushi_board_system_settings' list into 'sushi_board_setup.py' it's possible change any parameter.
'''

# WI-FI (optional)
'''
Wifi settings for testing purpose can be hardcoded in "sushi_board_setup.py" (above code).
Normally must be changed by the web interface.
If wifi settings are unknown it's possible force access point mode (no password) pressing the board button for about 15 seconds.
Then connecting to the web page it's possible change the wi-fi settings for example to connect to a certain network.
The default web page user/password are "root"/"1976"
'''


######################################
# THERMOSTAT
######################################
THERMO_TASK_FREQUENCY_SEC = 15		#run thermostat task every this time
THERMO_DEFAULT_TEMPERATURE_TARGET = 10
THERMO_DEFAULT_TEMPERATURE_MIN = 5		#min temperature
THERMO_DEFAULT_TEMPERATURE_MAX = 35		#max temperature
THERMO_DEFAULT_TEMPERATURE_STEP = 0.5	#step while editing
THERMO_RELAY_OUT_PIN = 15	# ESP32 GPIO 15
THERMO_MIN_ON_OFF_TIME_SEC = 15		#Min time between ON/OFF changes to avoid relay stress under every condition
THERMO_TEMPERATURE_SENSOR = 0	# [0=DS18B20-1,1=DS18B20-2]
THERMO_SMS_CMD_NEW_TEMP = "#SET-TEMP"


##########################################
# Main power monitor
##########################################
POWER_MON_TASK_FREQUENCY_SEC=5          # time between power status check
POWER_MON_CMD_GET_STATUS = "#STATUS?"   # SMS text to ask for status


