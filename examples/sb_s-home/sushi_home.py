# Sushi Home IoT [v1.0.0 - 2026-01-04]

"""
Home domotics demo project.

Features:
* Heater system thermostat: control a relay output connect to heater system
    + Local control physical interface
    + Remote control by SMS
* Main power loss detection
    + Alert by SMS
"""
# Common global variables
this_project_ver = "1.0.0[2026-01-04]" # project version

# COMMON IMPORT
import sushi		# main sushi library
import sushi_home_config  # set the system configuration by "s-home_config.py" module
import sushi_utils
from sushi_menu import Submenu	# class used to create custom submenus
import time

##########################################
# Tasks init and main loop
##########################################
print(f'Sushi Home IoT ver{this_project_ver} starting...')
thermo = None	# Thermostart class
power_mon = None    # Power monitor class
def main():
    thermostat_init()
    power_mon_init()
    modem_init()
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
    return get_param(text, sushi_home_config.POWER_MON_CMD_GET_STATUS)
    

# Power monitor task
def power_mon_task():
    now_ms = time.ticks_ms()
    if power_mon.time_last_task_run_ms != 0 and time.ticks_diff(now_ms, power_mon.time_last_task_run_ms) < sushi_home_config.POWER_MON_TASK_FREQUENCY_SEC*1000:
        return # task executed every POWER_MON_TASK_FREQUENCY_SEC seconds
    # read voltage
    power_mon.voltage = power_mon_get_voltage()
    # read state
    new_state = power_mon_get_state()
    # print(f"Main power voltage: {power_mon.voltage}. State: {new_state}") #DEBUG
    if new_state != power_mon.state:
        if power_mon.state != None:		#if None just started -> send SMS
            print(f"Main power state changed to {new_state}")
            power_mon.state = new_state
            modem_schedule_sms_send("*")    # "*" mean to every number in MODEM_ENABLED_NUMBERS
        else:	#program just started -> the power state is unknown
            print(f"Main power state is {new_state}")
            power_mon.state = new_state

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
        thermo.temperature_target = sushi_home_config.THERMO_DEFAULT_TEMPERATURE_TARGET

    print(f'Heater temperature target:{thermo.temperature_target}')
    # Create new submenu added to home menu
    thermo.ui_menu = Submenu('Thermostat')

    # Add new menu entry
    thermo.temperature_entry_id = thermo.ui_menu.add_float_editable_item(   "Temperature" ,        # menu title
                            menu_thermo_onchange_callback ,                                     # callback when value change
                            thermo.temperature_target , 										# starting value
                            sushi_home_config.THERMO_DEFAULT_TEMPERATURE_MIN,                   # min value
                            sushi_home_config.THERMO_DEFAULT_TEMPERATURE_MAX,                   # max value
                            sushi_home_config.THERMO_DEFAULT_TEMPERATURE_STEP)                  # step value
    
    # define the pin to control the relay
    from machine import Pin
    thermo.relay = Pin(sushi_home_config.THERMO_RELAY_OUT_PIN, Pin.OUT) # Sushi board relay 1 out
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
    res = sushi.cmd("read_temperature", sushi_home_config.THERMO_TEMPERATURE_SENSOR)
    if res[0] == 0:
        return res[1]
    return None

# parse commands from SMS
def thermo_parse_sms_commands(text):
    # check if the SMS text contain the command to set the temperature target
    new_temperature = get_param(text, sushi_home_config.THERMO_SMS_CMD_NEW_TEMP)
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
    if thermo.time_last_task_run_ms != 0 and time.ticks_diff(now_ms, thermo.time_last_task_run_ms) < sushi_home_config.THERMO_TASK_FREQUENCY_SEC*1000:
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
    if relay_state != thermo.relay.value() and time.ticks_diff(now_ms, thermo.time_last_state_change) > sushi_home_config.THERMO_MIN_ON_OFF_TIME_SEC*1000:
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
# Parse commands from SMS 
def modem_parse_sms(text , number):
    send_message = False
    # check thermostat commands
    if thermo_parse_sms_commands(text):
        send_message = True   # Received command from this number -> send confirmation SMS
    # check status request command
    if power_mon_parse_sms_commands(text):
        send_message = True

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
        for mynumber in sushi_home_config.MODEM_ENABLED_NUMBERS:
            modem_send_sms(sms_text , mynumber)
    else:    # sending SMS just to "number"
        modem_send_sms(sms_text , number)

# Send SMS
def modem_send_sms(text , number):
    print(f'Sending sms to {number} : {text}')
    
    res = sushi.cmd("send_sms", (text, number)) # sushi command to send the SMS
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
        if number in sushi_home_config.MODEM_ENABLED_NUMBERS:
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

##########################################
# Start program main loop
##########################################
main()

