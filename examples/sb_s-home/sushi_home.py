this_project_ver = "1.2.2[2026-08-08]" # project version

"""
Home domotics demo project.

Features:
* Heater system thermostat: control a relay output connect to heater system
    + Local control physical interface
    + Remote control by SMS
    + Heater control by onboard relay
* Garden irrigation
    + Local control physical interface
    + Remote control by SMS
    + Auto start
    + Remote output water channels activated by http
* Main power loss detection
    + Alert by SMS
* Get status by SMS    
"""

######################################
# SETTINGS & CONFIGURATION
######################################
# APPLICATION SETTINGS 
'''
The file "sb/SUSHI_HOME.json" (self created after the 1st run) contains the application specific settings:

{	"this_cfg_ver" : "HOME-2026-07-05" ,
    "thermo" :  {
                    "enabled" : true ,
                    "temperature_target": 10
                } ,
    "modem" :   {   
                    "enabled" : true ,
                    "enabled_numbers": ["+XXXXXXXXXXXX"]
                } ,
    "power_monitor" :   
                {   
                    "enabled" : true 
                } ,
    "irrigation": { 
                    "enabled" : true ,
                    "channels": [{	"time_on_sec": 480, 
                                    "on_command": "http://...", 
                                    "off_command": "http://...", 
                                    "auto_start_time": "20:45", 
                                    "name": "Grass"
                                } ,
                               ....
                               ]
                  }
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
Then connecting to the web page it's possible change the wi-fi settin
gs for example to connect to a certain network.
The default web page user/password are "root"/"1976"
'''


##########################################
# Common global variables
##########################################
app = None  # system common class 
thermo = None	# Thermostart class
power_mon = None    # Power monitor class
modem = None      # sms management class
irrigation  = None # Garden irrigation management class

##########################################
# COMMON IMPORT
##########################################
import sushi		# main sushi library
import sushi_utils
from sushi_menu import Submenu	# class used to create custom submenus
import time
import json


######################################
# FIXED PARAMETERS
######################################
# COMMON
APP_TASK_FREQUENCY_SEC  = 15                # time between app common tasks run
APP_WATCHDOG_TIMEOUT_SEC = 45

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

# IRRIGATION
IRRIGATION_TASK_FREQUENCY_SEC = 15          #run irrigation task every this time
IRRIGATION_HTTP_REFRESH_FREQUENCY_SEC = 30
IRRIGATION_SMS_CMD_START_CHANNEL = "#START-CH"

##########################################
# Project tasks
##########################################
class app_status:
    time_last_tasks_run_ms  = 0    
    time_is_valid = False
    # debug = 0 #DEBUG

# Tasks init and main loop
def main():
    logstr = f'Sushi Home IoT ver{this_project_ver} starting...' 
    print(logstr)     # print to REPL
    sushi.cmd("log", ('S' , logstr))  # System log

    global app
    app = app_status()
    # register this application in the web interface
    sushi_utils.register_upy_module("SUSHI_HOME" , "sb/SUSHI_HOME.json" , get_system_status_callback)

    # app.time_application_started = time.ticks_ms()  # time application started from time keeper

    #check and print configuration version
    cfg_ver = sushi_utils.load_setting("sushi_home", "this_cfg_ver")
    if cfg_ver == None: 
        sushi_utils.save_setting("sushi_home", "this_cfg_ver" , "Example-config")
        cfg_ver = sushi_utils.load_setting("sushi_home", "this_cfg_ver")
    print(f"Configuration_version: {cfg_ver}")
    
    # system-init
    sushi.cmd('wd_init',APP_WATCHDOG_TIMEOUT_SEC)  #start watchdog

    #init all sub-modules
    thermostat_init()
    power_mon_init()
    modem_init()
    irrigation_init()
    # sushi.cmd('set_log',1)    # enable sushi LOG on REPL for DEBUG purposes
    beep(500)
    # main loop
    try:
        while True:
            thermostat_task()
            power_mon_task()
            irrigation_task()
            system_common_task()
            time.sleep_ms(500)
    except KeyboardInterrupt:		# manage CTRL+C pression from REPL to end main loop
        print(f'Interrupted')
        sushi.cmd('wd_init',0)  # User interruption from REPL disable watchdog

'''
return system status info as DICT
'''
def get_system_status():
    # status dict
    st = {'main_task_last_run_ticks' : app.time_last_tasks_run_ms , 
          'time_is_valid' : app.time_is_valid ,
          'app_version' : this_project_ver
        }

    return st


'''
Get system status in different formats.
    format : "JSON" , "DICT" , "TEXT"
'''
def get_system_tasks_status(format):
    if format == "TEXT":
        # get single tasks status in TEXT format
        st_thermo = get_thermostat_status("TEXT")
        if st_thermo == None : st_thermo = ""

        st_power = get_power_status("TEXT")
        if st_power == None : st_power = ""

        st_irr = get_irrigation_status("TEXT")
        if st_irr == None : st_irr = ""

        # merge all status in returned text
        text = ""
        if thermo.cfg['enabled']: text +=  f"{st_thermo} - "  
        if power_mon.cfg['enabled']: text +=  f"{st_power} - "  
        if irrigation.cfg['enabled']: text +=  f"{st_irr}"  

        # text =  f"{st_thermo} - {st_power} - {st_irr}"
        return text
    else:
        # get single tasks status in DICT format
        st_thermo = get_thermostat_status("DICT")
        st_power = get_power_status("DICT")
        st_irr = get_irrigation_status("DICT")
        st_system = get_system_status()
        # merge all status dict in one single
        st = {"system" : st_system , "thermo" : st_thermo , "power_monitor" : st_power , "irrigation" : st_irr}

        if format == "JSON":
            return json.dumps(st) #convert to JSON string

    return None

# parse commands from SMS messages
def parse_tasks_incoming_sms_commands(text):
    send_reply_message = False

    # get system status
    if get_param(text, POWER_MON_CMD_GET_STATUS): send_reply_message = True

    # check thermostat commands
    if thermo_parse_sms_commands(text): send_reply_message = True  
    
    # check status request command
    if power_mon_parse_sms_commands(text): send_reply_message = True

    # check irrigation commands
    if irrigation_parse_sms_commands(text): send_reply_message = True

    return send_reply_message


# System common tasks
def system_common_task():
    now_ms = time.ticks_ms()
    if app.time_last_tasks_run_ms != 0 and time.ticks_diff(now_ms, app.time_last_tasks_run_ms) < APP_TASK_FREQUENCY_SEC*1000:
        return # task executed every APP_TASK_FREQUENCY_SEC seconds
    
    # check if system time is synchronized
    now =  time.gmtime() # -> (year, month, day, hours, minutes, seconds, day of week , day of year)
    if now[0] >= 2026 and app.time_is_valid == False:
        print(f'Time is valid: {now}') 
        app.time_is_valid = True
    elif app.time_is_valid == False:
        print('Time is NOT valid. Waiting for synch...') 
        
    # Watchdog refresh    
    sushi.cmd('wd_refresh')

    # DEBUG
    # st_json = get_system_tasks_status("JSON")
    # print(st_json) 

    # update task task execution time
    app.time_last_tasks_run_ms = now_ms

def get_system_status_callback(id):
    return get_system_tasks_status("JSON")

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
    power_mon.cfg = sushi_utils.load_setting("sushi_home", "power_monitor")
    if power_mon.cfg == None:
        print('Warning: power monitor settings to default')
        power_mon.cfg =    {
                            "enabled" : False 
                        }
        sushi_utils.save_setting("sushi_home", "power_monitor" , power_mon.cfg)

    if not power_mon.cfg['enabled']: 
        print('Power monitor DISABLED')
        return
    
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
    if res[0] == 0: # no error
        return (True if res[1] > 0 else False)
    else:
        print("Error reading power voltage:", res[0], "(", res[1], ")")
        return None

# parse commands from SMS
def power_mon_parse_sms_commands(text):
    # No specific commands
    return False
    

# Power monitor task
def power_mon_task():
    now_ms = time.ticks_ms()
    if  (not power_mon.cfg['enabled'] or 
        (power_mon.time_last_task_run_ms != 0 and 
        time.ticks_diff(now_ms, power_mon.time_last_task_run_ms) < POWER_MON_TASK_FREQUENCY_SEC*1000)):
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
                modem_schedule_sms_send("*")    # "*" mean to every number in modem.cfg['enabled_numbers']
        else:	#program just started -> the power state is unknown
            print(f"Main power state is {new_state}")
            power_mon.state = new_state
    else:
        power_mon.num_times_stable_before_alert = 0
        
    # update task task execution time
    power_mon.time_last_task_run_ms = now_ms

'''
return thermostat status info
format : "DICT" , "TEXT"
'''
def get_power_status(format):
    if not power_mon.cfg['enabled']: return None
    # status dict
    st = {'power_active' : power_mon.state}
    if (format == "TEXT"):
        text = f"Power: {'ON' if power_mon.state else 'OFF'}"
        return text
    return st



##########################################
# Thermostat management
##########################################
# status & management class
class thermostart_status:
    temperature_actual = None
    time_last_task_run_ms = 0
    relay = None
    time_last_state_change = 0
    cfg = None

# Init thermostat
def thermostat_init():
    global thermo
    thermo = thermostart_status()
    # Load temperature target from disk
    thermo.cfg = sushi_utils.load_setting("sushi_home", "thermo")
    if thermo.cfg == None:
        print('Warning: thermo settings to default')
        thermo.cfg =    {
                            "enabled" : False ,
                            "temperature_target": THERMO_DEFAULT_TEMPERATURE_TARGET
                        }
        sushi_utils.save_setting("sushi_home", "thermo" , thermo.cfg)

    # start only if enabled
    if not thermo.cfg['enabled']: 
        print('Thermo management DISABLED')
        return

    print(f'Heater temperature target:{thermo.cfg['temperature_target']}')
    # Create new submenu added to home menu
    thermo.ui_menu = Submenu('Thermostat')

    # Add new menu entry
    thermo.temperature_entry_id = thermo.ui_menu.add_float_editable_item(   "Temperature" ,        # menu title
                            menu_thermo_onchange_callback ,                                     # callback when value change
                            thermo.cfg['temperature_target'] , 										# starting value
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
        thermo.cfg['temperature_target'] = new_temperature
        sushi_utils.save_setting("sushi_home", "thermo" , thermo.cfg)

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
        try:
            thermo.cfg['temperature_target'] = float(new_temperature)  #if "new_temperature" is not a valid float can generate an exception
            sushi_utils.save_setting("sushi_home", "thermo" , thermo.cfg)
            thermo.ui_menu.set_menu_item_value(thermo.temperature_entry_id, thermo.cfg['temperature_target']);	#synch the value managed by user interface menu
            return True   # reveived command -> must send confirmation command
        except Exception as e:
            pass
            
    return False
        

# thermostat management task (run from main loop)
def thermostat_task():
    now_ms = time.ticks_ms()
    if (not thermo.cfg['enabled'] or 
        (thermo.time_last_task_run_ms != 0 and 
        time.ticks_diff(now_ms, thermo.time_last_task_run_ms) < THERMO_TASK_FREQUENCY_SEC*1000)):
        return # task executed every THERMO_TASK_FREQUENCY_SEC seconds
    
    # check temperature to define relay state
    relay_state = 0
    temperature = read_temperature()
    if temperature != None:
        if temperature < thermo.cfg['temperature_target']:
            relay_state = 1
        elif temperature >= thermo.cfg['temperature_target']:
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


'''
return thermostat status info
format : "DICT" , "TEXT"
'''
def get_thermostat_status(format):
    if not thermo.cfg['enabled']: return None

    # status dict
    st = {'actual_temperature' : thermo.temperature_actual , 
          'target_temperature' : thermo.cfg['temperature_target'] ,
          'heater_active' : (True if thermo.relay.value() else False)
        }
    
    if (format == "TEXT"):
        temp_str = "?"
        if isinstance(st['actual_temperature'], float):
            temp_str = "{:.1f}".format(st['actual_temperature'])	#format temperatue in string with 1 decimal number (to avoid things like 23.2399991)
        text =  f"T:{temp_str}->{st['target_temperature']} - " + \
                f"Heater: {'ON' if st['heater_active'] else 'OFF'}"
        return text
    return st


##########################################
# MODEM management
##########################################
class modem_man:
    stop_any_sms = False		# DEBUG
    num_sms_in_time_slot = SMS_NUM_MAX_IN_TIME_SLOT
    actual_time_slot = 0
    cfg = None
    
# Parse commands from SMS 
def modem_parse_sms(text , number):

    # parse SMS commands
    send_message = parse_tasks_incoming_sms_commands(text)
    
    # check debug command to stop any SMS
    stop_any_sms = get_param(text, "#STOP_SMS")
    if stop_any_sms != None:
        modem.stop_any_sms = int(stop_any_sms)
        print(f'SMS STOP: {modem.stop_any_sms}')

    if send_message: modem_schedule_sms_send(number) # send the reply status message


# Schedule status SMS send
def modem_schedule_sms_send(number):
    # get status in TEXT format
    sms_text = get_system_tasks_status("TEXT")
    # message creation be carefull due to unicode encoding modem accept MAX 70 characters ! 
    if len(sms_text) > 70: 
        print(f'ERROR: SMS text is too long: {sms_text}')
        sms_text = sms_text[:69] + "."      #cut to 70 char
        sushi.cmd("log", ('E' , 'ERROR: SMS text is too long')) #adding the error to sushi events log

    # sms_text =  f"Hello ☺ !" #TEST: every unicode symbol works in SMS text: https://www.w3schools.com/charsets/ref_utf_symbols.asp
    print(f'SMS: {sms_text}')
    if number == "*":   # sending SMS to all numbers in list
        for mynumber in modem.cfg['enabled_numbers']:
            modem_send_sms(sms_text , mynumber)
    else:    # sending SMS just to "number"
        modem_send_sms(sms_text , number)
    #DEBUG :sound beep at every SMS send
    beep(1000)

# check SMS limitation rules
def can_send_sms():
    # command by SMS to disable any SMS send
    if modem.stop_any_sms > 0:
        print(f'SMS sending disabled')
        return False
    # limitation in num. max SMS in a certain time slot
    actual_time_slot = int(time.ticks_ms() / ((SMS_TIME_SLOT_SEC)*1000))
    if actual_time_slot != modem.actual_time_slot:
        modem.actual_time_slot = actual_time_slot
        print(f'SMS time slot changed:{modem.actual_time_slot}')
        modem.num_sms_in_time_slot = SMS_NUM_MAX_IN_TIME_SLOT
    
    if modem.num_sms_in_time_slot <= 0:
        print(f'Cannot send more SMS in this time slot')
        return False
    modem.num_sms_in_time_slot -= 1
    return True


# Send SMS
def modem_send_sms(text , number):
    if can_send_sms() == False:
        return False
    
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
        if number in modem.cfg['enabled_numbers']:
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
    global modem
    modem = modem_man()
    # reading enabled phone numbers
    modem.cfg = sushi_utils.load_setting("sushi_home", "modem")
    if modem.cfg == None or "enabled_numbers" not in modem.cfg :
        print('Warning: Modem config not found. Storing default example.')
        modem.cfg =   {
                        "enabled" : False ,
                        "enabled_numbers": ["+39123456789"]
                    }
        sushi_utils.save_setting("sushi_home", "modem" , modem.cfg)

    # start only if enabled
    if not modem.cfg['enabled']:
        print('Modem management DISABLED')
        return

##########################################
# Garden irrigation management
##########################################
class channelStatus:
    INIT = 0
    WAITING = 1
    MUST_START = 2
    RUNNING = 2
    DONE_TODAY = 3
    LABELS = {
        INIT: "INIT",
        WAITING: "WAITING",
        MUST_START: "MUST_START",
        RUNNING: "RUNNING",
        DONE_TODAY: "DONE_TODAY"
    }

# status & management class
class irrigation_status:
    running_channel = None
    time_last_task_run_ms = 0
    time_channel_stop_ms = 0
    time_last_http_out_refresh_ms = 0
    # log_debug_counter = 0 #DEBUG
    cfg = None

# Init Irrigation
def irrigation_init():
    global irrigation
    irrigation = irrigation_status()
    
    # Load settings from disk
    irrigation.cfg = sushi_utils.load_setting("sushi_home", "irrigation")
    if irrigation.cfg == None or "channels" not in irrigation.cfg:
        print('Warning: Irrigation config not found. Storing default example.')
        # setting default example strucure in sushi_home.json file
        irrigation.cfg =    {  
                                "enabled" : False , 
                                "channels" :     [  {    "name" : "Grass"   ,     
                                                        "time_on_sec" : 180 , 
                                                        "auto_start_time" : "00:30" ,
                                                        "on_command" : "http://..." ,
                                                        "off_command" : "http://..." 
                                                    }
                                                ]
                            }
        sushi_utils.save_setting("sushi_home", "irrigation" , irrigation.cfg)
    
    # start only if enabled
    if not irrigation.cfg['enabled']:
        print('Irrigation management DISABLED') 
        return

    # create and reset array with channels status
    irrigation.channel_status = [channelStatus.INIT] * len(irrigation.cfg['channels'])

    # create and reset array with channels auto start time in Seconds From Midnight
    irrigation.auto_start_sfm = [-1] * len(irrigation.cfg['channels'])
    pch = 0
    for ch in irrigation.cfg['channels']:
        try:
            auto_start_h, auto_start_m = map(int, ch['auto_start_time'].split(":"))
            irrigation.auto_start_sfm[pch] = (auto_start_h * 3600) + (auto_start_m * 60)
            print(f"CH#{pch}[{ch['name']}] planned start is at {ch['auto_start_time']} ({irrigation.auto_start_sfm[pch]} SFM)." )
        except Exception as e:
            irrigation.auto_start_sfm[pch] = -1
            print(f"CH#{pch}[{ch['name']}] will not auto start" )
        pch += 1

    ############################DEBUG
    '''now =  time.gmtime() # -> (year, month, day, hours, minutes, seconds, day of week , day of year)
    hour = now[3]
    min = now[4] 
    sec = now[5]
    actual_sec_from_midnight = (hour * 3600) + (min * 60) + sec
    irrigation.auto_start_sfm[0] = actual_sec_from_midnight + 5
    print(irrigation.auto_start_sfm[0])'''
    ################################[FINE DEBUG]

    # Create new submenu added to home menu
    irrigation.ui_menu = Submenu('Irrigation')

    # Create a new menu entry for STATUS
    irrigation.ui_menu.add_read_only_item("Status" , irrigation_status_print_callback)

    # Create a new menu entry to start the channels
    
    # create an array with all channels name
    channels = ["AUTO" , "ALL"]     # AUTO: start only in auto mode basing on configuration. "ALL" : start all channels 
    for ch in irrigation.cfg['channels']: channels.append(ch['name'])    
    
    irrigation.start_channel_menu_id = irrigation.ui_menu.add_enum_editable_item("Start", on_start_irrigation_channel, 0, *channels)
    

# Callback triggered when changing state from the physical device menu
def on_start_irrigation_channel(entry_id, value_index):
    if value_index == 1:   # run ALL channels
        for pch in range(0,len(irrigation.cfg['channels'])): 
            irrigation.channel_status[pch] = channelStatus.MUST_START   # sign all channels to start
    elif value_index >= 2:   # run a specific channel
        channel = value_index - 2
        irrigation.channel_status[channel] = channelStatus.MUST_START # sign the channel to start
    
    refresh_irrigator_now() # call irrigator task immediately

    # reset back the menu to "AUTO" mode
    irrigation.ui_menu.set_menu_item_value(irrigation.start_channel_menu_id, 0);	#synch the value managed by user interface menu
    
    

# Callback called when the menu is print
def irrigation_status_print_callback(node): # text max len: 16 char    
    if irrigation.running_channel != None:
        ch = irrigation.cfg['channels'][irrigation.running_channel]
        missing_seconds = int((irrigation.time_channel_stop_ms - time.ticks_ms())/1000)
        if missing_seconds < 0: missing_seconds = 0
        str = f"{missing_seconds}s {ch['name']}"
        if len(str) > 16: str = str[:15] + "."      #cut shown text if longer than 16 chars
        return str
    else: # no channels active
        return "OFF"

# parse commands from SMS
def irrigation_parse_sms_commands(text):
    channel = get_param(text, IRRIGATION_SMS_CMD_START_CHANNEL)   
    
    if channel != None:
        if channel == "*":   # run ALL channels
            for pch in range(0,len(irrigation.cfg['channels'])): 
                irrigation.channel_status[pch] = channelStatus.MUST_START   # sign all channels to start
            refresh_irrigator_now() # call irrigator task immediately
            print(f'Starting ALL irrigation channels from SMS')
            return True   # reveived command -> must send back confirmation command        
        else:
            # convert channel string to number
            try:
                channel = int(channel)  # if channel is not a valid int can generate exception -> "try...except" is required
            except Exception as e:
                channel = -1 # invalid channel number
                
            if channel > 0 and channel <= len(irrigation.cfg['channels']):   # run a specific channel
                irrigation.channel_status[channel-1] = channelStatus.MUST_START # sign the channel to start
                refresh_irrigator_now() # call irrigator task immediately
                print(f'Starting irrigation channel {channel} from SMS')
                return True   # reveived command -> must send back confirmation command
    return False

def refresh_irrigator_now():
    irrigation.time_last_task_run_ms = 0
    irrigation_task()

# irrigation management task (run from main loop)
def irrigation_task():
    now_ms = time.ticks_ms()
    if (not irrigation.cfg['enabled'] or 
        (irrigation.time_last_task_run_ms != 0 and 
        time.ticks_diff(now_ms, irrigation.time_last_task_run_ms) < IRRIGATION_TASK_FREQUENCY_SEC*1000)):
        return # task executed every IRRIGATION_TASK_FREQUENCY_SEC seconds

    if app.time_is_valid == False:
        print('Waiting time become valid...') 
        irrigation.time_last_task_run_ms = now_ms
        return 
    
    # check if auto start time
    # get actual time
    # from machine import RTC
    # now = RTC().datetime() # -> (year, month, day, day of week, hours, minutes, seconds, us)
    now =  time.gmtime() # -> (year, month, day, hours, minutes, seconds, day of week , day of year)
    hour = now[3]
    min = now[4] 
    sec = now[5]
    actual_sec_from_midnight = (hour * 3600) + (min * 60) + sec

    #print time DEBUG
    # logstr = f"Micro UTC: {hour}:{min}:{sec} ({actual_sec_from_midnight} SFM)"
    # print(logstr) #debug
    
    
    ''' #DEBUG
    irrigation.log_debug_counter += 1
    if irrigation.log_debug_counter > 10:
        irrigation.log_debug_counter = 0
        sushi.cmd("log", ('D' , logstr))
    '''

    
    #DEBUG print(irrigation.cfg)
    pch = 0 # channel pointer
    if irrigation.running_channel == None:  # no active channell by now
        for ch in irrigation.cfg['channels']:            
            if irrigation.auto_start_sfm[pch] >= 0:    # check if autostart enabled
                
                # CHECK IF PROGRAM JUST STARTED AND WE ARE BEFORE THE CHANNEL AUTO START TIME
                if irrigation.channel_status[pch] == channelStatus.INIT:    # program just starter
                    if actual_sec_from_midnight > irrigation.auto_start_sfm[pch]: # check if program started after the channel auto start time
                        irrigation.channel_status[pch] = channelStatus.DONE_TODAY  # channel task signed as already done today
                        print(f"CH#{pch}[{ch['name']}] signed as already done today." )
                    else:
                        irrigation.channel_status[pch] = channelStatus.WAITING   # setting task as waiting to be done
                        print(f"CH#{pch}[{ch['name']}] will start at {ch['auto_start_time']} ({irrigation.auto_start_sfm[pch]} SFM)." )
                
                # CHECK IF DAY CHANGED -> THE TASK IS SIGNED TO BE WAITING TO BE DONE
                if (  irrigation.channel_status[pch] == channelStatus.DONE_TODAY and 
                        actual_sec_from_midnight < irrigation.auto_start_sfm[pch]):
                    print('The day changed. Resetting the channel task flag')
                    irrigation.channel_status[pch] = channelStatus.WAITING   # the day changed
                    print(f"CH#{pch}[{ch['name']}] will start at {ch['auto_start_time']} ({irrigation.auto_start_sfm[pch]} SFM)." )

                # CHECK IF IT'S  TIME TO START CHANNEL
                if (((irrigation.channel_status[pch] == channelStatus.WAITING           # AUTO START CONDITIONS:    - channel did  not run today yet
                    and actual_sec_from_midnight > irrigation.auto_start_sfm[pch])      #                           - the actual time crossed the start time                   
                    
                    or irrigation.channel_status[pch] == channelStatus.MUST_START)      # START REQUEST FROM USER UI                    
                    
                    and irrigation.running_channel == None):                            # no other channels are running
                        irrigation.channel_status[pch] = channelStatus.RUNNING 
                        irrigation.running_channel = pch   #pointer to active channel
                        irrigation.time_last_http_out_refresh_ms = 0    #refresh output immediately
                        irrigation.time_channel_stop_ms = ch['time_on_sec'] * 1000 + now_ms # time until channel must remain ON
                        logstr = f"Starting CH#{pch}[{ch['name']}] for {ch['time_on_sec']} sec." 
                        print(logstr)
                        sushi.cmd("log", ('X' , logstr)) #adding to sushi events log
            pch += 1
    
    if irrigation.running_channel != None:
        pch = irrigation.running_channel
        ch = irrigation.cfg['channels'][pch]
        #DEBUG print(f"CH#{pch}[{ch['name']}] ON {now_ms} -> {irrigation.time_channel_stop_ms}.")  
        refresh_url = ""
        if now_ms > irrigation.time_channel_stop_ms:        # channel time on terminated
            logstr = f"CH#{pch}[{ch['name']}] time terminated."
            print(logstr)
            sushi.cmd("log", ('X' , logstr)) #adding to sushi events log
            refresh_url = ch['off_command']   
            irrigation.time_last_http_out_refresh_ms = 0    #refresh output immediately
            irrigation.running_channel = None
            irrigation.channel_status[pch] = channelStatus.DONE_TODAY #sign the task as done today
        else : 
            refresh_url = ch['on_command']
        
        if irrigation.time_last_http_out_refresh_ms == 0 or time.ticks_diff(now_ms, irrigation.time_last_http_out_refresh_ms) > IRRIGATION_HTTP_REFRESH_FREQUENCY_SEC*1000:
            print(f"Refreshing CH#{pch}[{ch['name']}] output [{refresh_url}]...")  
            sushi.cmd('http_get',(refresh_url , 2500 , "cm_http_wifi_num_max_retry = 1 ; cm_http_modem_num_max_retry = 0"))
            irrigation.time_last_http_out_refresh_ms = now_ms

    # update task task execution time
    irrigation.time_last_task_run_ms = now_ms

'''
return thermostat status info
format : "DICT" , "TEXT"
'''
def get_irrigation_status(format):
    if not irrigation.cfg['enabled']: return None

    # status dict
    st = {'active_channel' : irrigation.running_channel , 'channels' : []}

    pch = 0
    for ch in irrigation.cfg['channels']:  
        status_str = channelStatus.LABELS.get(irrigation.channel_status[pch], "Sconosciuto")
        st['channels'].append({ 'auto_start_time' : ch['auto_start_time'] ,
                                'name' : ch['name'] ,
                                'id' : (pch+1) ,
                                'status_code' : irrigation.channel_status[pch] ,
                                'status_desc' : status_str 
                            })
        pch += 1

    if (format == "TEXT"):
        irrigation_state_str = "OFF"
        if irrigation.running_channel != None: irrigation_state_str = f"ON CH#{irrigation.running_channel+1}"
        text = f"Irrig.:{irrigation_state_str}"
        return text
    
    return st

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
          
main()


