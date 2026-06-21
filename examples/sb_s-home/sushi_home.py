# Sushi Home IoT [v1.1.2 - 2026-06-21]

"""
Home domotics demo project.

Features:
* Heater system thermostat: control a relay output connect to heater system
    + Local control physical interface
    + Remote control by SMS
* Main power loss detection
    + Alert by SMS
"""

######################################
# SETTINGS & CONFIGURATION
######################################
# APPLICATION SETTINGS 
'''
The file "sb/SUSHI_HOME.json" (self created after the 1st run) contains the application specific settings:

{
    "modem_enabled_numbers": ["+391111111111", "+342222222222"],	# List of phone numbers enabled to send/receive SMS.
    "thermo_temperature_target": 10									# Target temperature (no need to edit here, normally set by SMS or UI).
}
'''

# SUSHIPYTHON SYSTEM SETTINGS
'''
System setting are stored into "sb/SYSTEM.json", and can be set in 3 ways:
* editing the system setting file "sb/SYSTEM.json".
* by web page (if board is connected to wifi) sending a JSON file or by the user interface.
* with micropython call "sushi_utils.set_sushi_config(...)" that sets certain setting to "sb/SYSTEM.json"

Important settings for this script are:
* System
    - "modem_enable": 1  (# 0=none;<>0 = modem model)
* Modem SIM setting:
    - "modem_sim_sms_center" : operator SMS center number (necessary to let the modem manage SMS messages)
    - "modem_sim_pin" : your SIM pin
    - "modem_apn" : SIM operator APN
    - "modem_user" : SIM operator user (if required)
    - "modem_passwd" : SIM operator password (if required)
'''

# WI-FI SETTINGS (optional)
'''
Wifi settings normally must be changed by the web interface. 
For testing purpose can be hardcoded and set by "sushi_utils.set_sushi_config(...)"

If wifi settings are unknown it's possible force access point mode (no password) pressing the board button for about 15 seconds.
Then connecting to the web page it's possible change the wi-fi settings for example to connect to a certain network.
The default web page user/password are "root"/"1976"
'''


##########################################
# Common global variables
##########################################
this_project_ver = "1.1.2[2026-06-21]" # project version
thermo = None	# Thermostart class
power_mon = None    # Power monitor class
sms = None

##########################################
# COMMON IMPORT
##########################################
import sushi		# main sushi libraryt
import sushi_utils
from sushi_menu import Submenu	# class used to create custom submenus
import time


######################################
# FIXED PARAMETERS
######################################

# THERMOSTAT
THERMO_TASK_FREQUENCY_SEC = 15		#run thermostat task every this time
THERMO_DEFAULT_TEMPERATURE_TARGET = 10
THERMO_DEFAULT_TEMPERATURE_MIN = 5		#min temperature
THERMO_DEFAULT_TEMPERATURE_MAX = 35		#max temperature
THERMO_DEFAULT_TEMPERATURE_STEP = 0.5	#step while editing
THERMO_RELAY_OUT_PIN = 15	# ESP32 GPIO 15
THERMO_MIN_ON_OFF_TIME_SEC = 15		#Min time between ON/OFF changes to avoid relay stress under every condition
THERMO_TEMPERATURE_SENSOR = 0	# [0=DS18B20-1,1=DS18B20-2]
THERMO_SMS_CMD_NEW_TEMP = "#SET-TEMP"

# Main power monitor
POWER_MON_TASK_FREQUENCY_SEC=5          # time between power status check
POWER_MON_CMD_GET_STATUS = "#STATUS?"   # SMS text to ask for status
POWER_MON_NUM_CONFIRM_BEFORE_SMS=3		# number of check with state stable before send aler SMS

# SMS MANAGEMENT
SMS_TIME_SLOT_SEC=3600				#1 hour
SMS_NUM_MAX_IN_TIME_SLOT=10			#max 10 SMS/hour

##########################################
# Tasks init and main loop
##########################################
def main():
    thermostat_init()
    power_mon_init()
    modem_init()
    #DEBUG
    # sushi.cmd('set_log',1)
    beep(500)
    ##########
    # main loop
    try:
        while True:
            thermostat_task()
            power_mon_task()
            time.sleep_ms(500)
    except KeyboardInterrupt:		# manage CTRL+C pression from REPL to end main loop
        print(f'Interrupted')

##########################################
# Main power monitor
##########################################
# power monitor class
class power_mon_status:
    time_last_task_run_ms = 0
    voltage = None
    state = None
    num_times_stable_before_alert = 0

# Init power monitor
def power_mon_init():
    global power_mon
    power_mon = power_mon_status()

# --- Read main power state ---
def power_mon_get_state():
    res = sushi.cmd("read_power_state")
    if res[0] == 0:
        return res[1]
    else:
        print("Error reading power state:", res[0], "(", res[1], ")")
        return None

# --- Read main power voltage ---
def power_mon_get_voltage():
    res = sushi.cmd("read_power_voltage")
    if res[0] == 0:
        return res[1]
    else:
        print("Error reading power voltage:", res[0], "(", res[1], ")")
        return None

# parse commands from SMS
def power_mon_parse_sms_commands(text):
    # check if the SMS text contain the command to request status info
    return get_param(text, POWER_MON_CMD_GET_STATUS)
    

# Power monitor task
def power_mon_task():
    now_ms = time.ticks_ms()
    if power_mon.time_last_task_run_ms != 0 and time.ticks_diff(now_ms, power_mon.time_last_task_run_ms) < POWER_MON_TASK_FREQUENCY_SEC*1000:
        return # task executed every POWER_MON_TASK_FREQUENCY_SEC seconds
    # read voltage
    power_mon.voltage = power_mon_get_voltage()
    # read state
    new_state = power_mon_get_state()
    # print(f"Main power voltage: {power_mon.voltage}. State: {new_state}") #DEBUG
    if new_state != power_mon.state:
        if power_mon.state != None:		#if None just started
            power_mon.num_times_stable_before_alert += 1
            if power_mon.num_times_stable_before_alert >= POWER_MON_NUM_CONFIRM_BEFORE_SMS:# need input stable for N reads before send SMS
                print(f"Main power state changed to {new_state}")
                power_mon.state = new_state
                modem_schedule_sms_send("*")    # "*" mean to every number in MODEM_ENABLED_NUMBERS
        else:	#program just started -> the power state is unknown
            print(f"Main power state is {new_state}")
            power_mon.state = new_state
    else:
        power_mon.num_times_stable_before_alert = 0
        
    # update task task execution time
    power_mon.time_last_task_run_ms = now_ms

##########################################
# Thermostat management
##########################################
# status & management class
class thermostart_status:
    temperature_target = None
    temperature_actual = None
    time_last_task_run_ms = 0
    relay = None
    time_last_state_change = 0

# Init thermostat
def thermostat_init():
    global thermo
    thermo = thermostart_status()
    # Load temperature target from disk
    thermo.temperature_target = sushi_utils.load_setting("sushi_home", "thermo_temperature_target")
    if thermo.temperature_target == None:	# assign default target
        print('Temperature target to default')
        thermo.temperature_target = THERMO_DEFAULT_TEMPERATURE_TARGET
        sushi_utils.save_setting("sushi_home", "thermo_temperature_target" , thermo.temperature_target)

    print(f'Heater temperature target:{thermo.temperature_target}')
    # Create new submenu added to home menu
    thermo.ui_menu = Submenu('Thermostat')

    # Add new menu entry
    thermo.temperature_entry_id = thermo.ui_menu.add_float_editable_item(   "Temperature" ,        # menu title
                            menu_thermo_onchange_callback ,                                     # callback when value change
                            thermo.temperature_target , 										# starting value
                            THERMO_DEFAULT_TEMPERATURE_MIN,                   # min value
                            THERMO_DEFAULT_TEMPERATURE_MAX,                   # max value
                            THERMO_DEFAULT_TEMPERATURE_STEP)                  # step value
    
    # define the pin to control the relay
    from machine import Pin
    thermo.relay = Pin(THERMO_RELAY_OUT_PIN, Pin.OUT) # Sushi board relay 1 out
    thermo.relay.value(0)  # Init relay OFF
    
# Callback called when the temperature from user menu change
def menu_thermo_onchange_callback(node , new_temperature):
    print(f'Temperature changed !')
    if node == thermo.temperature_entry_id:
        print(f'New target temperature:{new_temperature }')
        thermo.temperature_target = new_temperature
        sushi_utils.save_setting("sushi_home", "thermo_temperature_target" , thermo.temperature_target)

# read temperature sensor
def read_temperature():
    res = sushi.cmd("read_temperature", THERMO_TEMPERATURE_SENSOR)
    if res[0] == 0:
        return res[1]
    return None

# parse commands from SMS
def thermo_parse_sms_commands(text):
    # check if the SMS text contain the command to set the temperature target
    new_temperature = get_param(text, THERMO_SMS_CMD_NEW_TEMP)
    if new_temperature != None: 
        print(f'New target temperature:{new_temperature }')
        thermo.temperature_target = float(new_temperature)
        sushi_utils.save_setting("sushi_home", "thermo_temperature_target" , thermo.temperature_target)
        thermo.ui_menu.set_menu_item_value(thermo.temperature_entry_id, thermo.temperature_target);	#synch the value managed by user interface menu
        return True   # reveived command -> must send confirmation command
    return False
        

# thermostat management task (run from main loop)
def thermostat_task():
    now_ms = time.ticks_ms()
    if thermo.time_last_task_run_ms != 0 and time.ticks_diff(now_ms, thermo.time_last_task_run_ms) < THERMO_TASK_FREQUENCY_SEC*1000:
        return # task executed every THERMO_TASK_FREQUENCY_SEC seconds
    
    # check temperature to define relay state
    relay_state = 0
    temperature = read_temperature()
    if temperature != None:
        if temperature < thermo.temperature_target:
            relay_state = 1
        elif temperature >= thermo.temperature_target:
            relay_state = 0
    else:
        print(f'Error reading temperature.')
    
    if temperature != None and temperature != thermo.temperature_actual:
        print(f'Enviroment temperature: {temperature}.')
        thermo.temperature_actual = temperature
    # update relay output (min THERMO_MIN_ON_OFF_TIME_SEC seconds between every change)
    if relay_state != thermo.relay.value() and time.ticks_diff(now_ms, thermo.time_last_state_change) > THERMO_MIN_ON_OFF_TIME_SEC*1000:
        thermo.time_last_state_change = now_ms
        thermo.relay.value(relay_state)
        print(f'Relay state changed to {relay_state}.')
    
    if relay_state != thermo.relay.value():
        print(f'Waiting THERMO_MIN_ON_OFF_TIME_SEC before change relay state.')
    
    # update task task execution time
    thermo.time_last_task_run_ms = now_ms

##########################################
# SMS management
##########################################
class sms_man:
    MODEM_ENABLED_NUMBERS = None
    stop_any_sms = False		# DEBUG
    num_sms_in_time_slot = SMS_NUM_MAX_IN_TIME_SLOT
    actual_time_slot = 0
    
# Parse commands from SMS 
def modem_parse_sms(text , number):
    send_message = False
    # check thermostat commands
    if thermo_parse_sms_commands(text):
        send_message = True   # Received command from this number -> send confirmation SMS
    # check status request command
    if power_mon_parse_sms_commands(text):
        send_message = True
    
    # check debug command to stop any SMS
    stop_any_sms = get_param(text, "#STOP_SMS")
    if stop_any_sms != None:
        sms.stop_any_sms = int(stop_any_sms)
        print(f'SMS STOP: {sms.stop_any_sms}')

    if send_message:
        modem_schedule_sms_send(number) # send the message


# Schedule status SMS send
def modem_schedule_sms_send(number):
    # message creation be carefull due to unicode encoding modem accept MAX 70 characters ! 
    temp_str = "?"
    if thermo.temperature_actual is not None:
        temp_str = "{:.1f}".format(thermo.temperature_actual)	#format temperatue in string with 1 decimal number (to avoid things like 23.2399991)
    heater_status_str = f"{'ON' if thermo.relay.value() else 'OFF'}"
    power_state_str = f"{'ON' if power_mon.state else 'OFF'}"
    
    sms_text =  f"Temp. actual/target: {temp_str}/{thermo.temperature_target} - " + \
                f"Heater: {heater_status_str} - " + \
                f"Power: {power_state_str}"
    # sms_text =  f"Hello ☺ !" #TEST: every unicode symbol works in SMS text: https://www.w3schools.com/charsets/ref_utf_symbols.asp
    print(f'SMS: {sms_text}')
    if number == "*":   # sending SMS to all numbers in list
        for mynumber in sms.MODEM_ENABLED_NUMBERS:
            modem_send_sms(sms_text , mynumber)
    else:    # sending SMS just to "number"
        modem_send_sms(sms_text , number)
    #DEBUG :sound beep at every SMS send
    beep(1000)

# check SMS limitation rules
def can_send_sms():
    # command by SMS to disable any SMS send
    if sms.stop_any_sms > 0:
        print(f'SMS sending disabled')
        return False
    # limitation in num. max SMS in a certain time slot
    actual_time_slot = int(time.ticks_ms() / ((SMS_TIME_SLOT_SEC)*1000))
    if actual_time_slot != sms.actual_time_slot:
        sms.actual_time_slot = actual_time_slot
        print(f'SMS time slot changed:{sms.actual_time_slot}')
        sms.num_sms_in_time_slot = SMS_NUM_MAX_IN_TIME_SLOT
    
    if sms.num_sms_in_time_slot <= 0:
        print(f'Cannot send more SMS in this time slot')
        return False
    sms.num_sms_in_time_slot -= 1
    return True


# Send SMS
def modem_send_sms(text , number):
    if can_send_sms() == False:
        return False
    
    print(f'Sending sms to {number} : {text}')
    res = sushi.cmd("send_sms", (text, number)) # sushi command to send the SMS
    return False

    if res[0] == 0:
        print("SMS command accepted, ID:", res[1])
        return True
    else:
        print(f'Send SMS error:{res[0]} ({res[1]})')
        return False

# --- Callback executed on modem events ---
# a[0] = event type (0=SMS received, 1=Incoming call, 2=SMS TX result)
# a[1..] = event-specific data
def modem_callback(a):
    if a[0] == 0:  # SMS received
        number = a[1]
        text   = a[2]
        time   = a[3]
        print(f'SMS received from "{number}" ; Time : "{time}" ; Text : "{text}"')
        if number in sms.MODEM_ENABLED_NUMBERS:
            modem_parse_sms(text , number)
        else:
            print(f'Number {number} not in enabled array. SMS ignored')
    elif a[0] == 2:  # SMS TX result
        sms_id = a[1]
        tx_status = a[2]
        if tx_status == 1:
            status_text = "OK"
        else:
            status_text = "ERROR"
        print(f'SMS ID {sms_id} send result: {status_text} ')
    else:
        # ignore other events
        pass

def modem_init():
    # Register callback ---
    sushi.cmd("set_modem_hnd", modem_callback)
    
    
    global sms
    sms = sms_man()
    
    # reading enabled phone numbers
    sms.MODEM_ENABLED_NUMBERS = sushi_utils.load_setting("sushi_home", "modem_enabled_numbers")
    if sms.MODEM_ENABLED_NUMBERS == None:
        print('Waring: No SMS enabled numbers')
        sushi_utils.save_setting("sushi_home", "modem_enabled_numbers" , ["+391111111111" , "+342222222222"])
        sms.MODEM_ENABLED_NUMBERS = []


##########################################
# Misc functions
##########################################
# get param or command in string in key-value format like "PARAM1=12;PARAM2=HELLO;DO_SOMETHING;"
def get_param(command_str, key):
    """
    Parses a command string to extract a key's value, check for a flag, 
    or determine if the key is absent.
    
    Example: 
    - get_param("#CMD1=3;#FLAG", "#CMD1") -> "3" (str)
    - get_param("#CMD1=3;#FLAG", "#FLAG") -> True (bool)
    - get_param("#CMD1=3;#FLAG", "#NON_EXISTENT") -> None
    
    Args:
        command_str (str): The input string containing commands (e.g., "#K=V;#FLAG").
        key (str): The key or flag to search for (e.g., "#CMD1", "#FLAG").
        
    Returns:
        str/bool/None: The parameter value (str), True (if it's a flag), or None (if not found).
    """
    # 1. Split the string into individual blocks using the main delimiter ';'
    blocks = command_str.split(';')
    for block in blocks:
        clean_block = block.strip() # Remove surrounding whitespace
        # 2. Check for Key-Value Assignment (e.g., "#CMD1=3")
        # We check if the block starts with the key followed by the assignment operator '='
        if clean_block.startswith(f'{key}='):
            # Key-value found. Extract the value part.
            # Calculate the start index of the value: length of key + '=' (1)
            start_index = len(key) + 1 
            value = clean_block[start_index:].strip()
            return value
        # 3. Check for Flag Presence (e.g., "#DO_SOMETHING")
        # We check for an exact match, meaning no '=' follows the key.
        elif clean_block == key:
            # Found a standalone flag.
            return True
    # 4. No Match Found
    return None

# sound beep
def beep(duration_ms):
    from machine import Pin
    buzzer_out = Pin(25, Pin.OUT) # Sushi board relay 1 out
    buzzer_out.value(1)  # Init relay ON
    time.sleep_ms(duration_ms)
    buzzer_out.value(0)  # Init relay OFF
    
##########################################
# Start program main loop
##########################################
print(f'Sushi Home IoT ver{this_project_ver} starting...')
main()



