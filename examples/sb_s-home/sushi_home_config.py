import sushi
import sushi_utils

#############################
# SUSHI BOARD CONFIGURATION
#############################

# Settings & pinout online help: https://github.com/sushi-iot/sushi-iot-framework/blob/main/examples/sushi-quick-reference.md
# Setting & pinout REPL help: "sushi_utils.list_params('system')" ; "sushi_utils.list_params('wifi')"
# Setup can be done by microPython with this file or by web UI (JSON file or interface)

sushi_settings={
    # System settings
    "system": {
        "device_name": "SushiHome",
        "data_file_version": "SB-HOME-01",  # data file version
        "modem_enable": 1,  # 0=none;1=SIMCOM7672X
        "board_model": 0,   # 0=ESP32-DevKitC
        "ioex_enable": 1,   # 0=none;1=PCF8575
        "ext_temperature_sensor_enable": 1, # 0=none;1=DS18B20
        "rele_out_enable": 2,   # 2 relays enabled
        "keyboard_enable": 4, # 0=none;1...N=N keys on I/O-Expander;100=4 keys on GPIN
        "lcd_enable": 1,    # 0=none;1=OLED_SSD1306
        "buzzer_enable": 1, # 0=none;1=buzzer enabled
        "battery_enable": 2,    # 0=none;1=reserved;2=1 li-ion cell (1S) ~3.0–4.2V;3=3 li-ion cells (3S) ~9–12.6V
        "modem_sim_sms_center": "+393519999600", # Modem settings
        "modem_sim_pin": "1234",
        "modem_apn":"iliad",
        "modem_user":"iliad",
        "modem_passwd":"",
        "modem_status_led":"",
        "extension_modules": "",    # Not used
        "system_info_log_frequency_min": 0,     # system info log disabled
        "system_info_store_frequency_min": 0, # system info store to file disabled
        "system_info_send_http_post_frequency_min": 0, # system info remote post disabled
        "system_info_csv_filter": "",    # filter used when system_info_store_frequency_min > 0
        "wifi_status_led": "",  # wi-fi status LED. Not used.
        "system_status_led": "", # system status LED. Not used.
        "event_register_size_kb": 32,   # 32K events register 
        "time_zone_hours": 0,   # Time zone offset from UTC
        "time_auto_daylight_save_change": 0, # daylight saving automatic change disabled (European rules)
        "powersave_time_wifi_off_min": 0, # Auto wi-fi power-off after inactivity (minutes). Disabled.
        "http_post_delivery_address": "",   # Server address for status HTTP POST every system_info_send_http_post_frequency_min. Disabled.
        "ntp_server_address": "pool.ntp.org", # ntp server for time-synch
        "use_wifi_for_http_post": 1, # when sending http POST data,  before use the modem (4G) if available try use wi-fi.
        "debug_mode": 0 # reserved DEBUG functions (disabled)
},
    # Wifi settings
    "wifi": {
        "wifi_mode": 2,   # 0=Disabled;1=Client;2=Access point
        "ip": "192.168.1.111",
        "gateway": "192.168.1.1",
        "subnet": "255.255.255.0",
        # Access point settins (if wifi_mode = 2)
        "ap_passwd": "",
        "ap_channel": 3,
        # client settings (if wifi_mode = 1)
        "cli_ssid": "",
        "cli_passwd": "",
        "cli_dhcp_enable": 0,
        "cli_dns_address": "8.8.8.8"
    }
}
# set the configuration
sushi_utils.set_sushi_config(sushi_settings) #return: 0 = configuration not changed ; 1 = changed no need to restart ; 2 = changed and need to restart

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


######################################
# MODEM
######################################
# phone numbers enabled to send/receive SMS
# MODEM_ENABLED_NUMBERS = ["+XXXXXXXXXXXX" , "+XXXXXXXXXXXX"]
MODEM_ENABLED_NUMBERS = ["+XXXXXXXXXXXX"]

##########################################
# Main power monitor
##########################################
POWER_MON_TASK_FREQUENCY_SEC=5          # time between power status check
POWER_MON_CMD_GET_STATUS = "#STATUS?"   # SMS text to ask for status

