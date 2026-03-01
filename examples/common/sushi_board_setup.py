# sushi_board_setup.py
this_file_version="2026-02-18@1935"

import sushi
import sushi_utils

##########################################################
# SUSHI BOARD CONFIGURATION PROFILE
##########################################################

# Settings & pinout online help: https://github.com/sushi-iot/sushi-iot-framework/blob/main/examples/sushi-quick-reference.md
# Setting & pinout REPL help: "sushi_utils.list_params('system')" ; "sushi_utils.list_params('wifi')"
# Setup can be done by microPython with this file or by web UI (JSON file or interface)

sushi_board_system_settings={
    # System settings
    "system": {
        "device_name": "SushiBoardIoT",
        "data_file_version": "SB-DEFAULT-01",  # data file version
        "modem_enable": 1,  # 0=none;1=SIMCOM7672X
        "board_model": 0,   # 0=ESP32-DevKitC
        "ioex_enable": 1,   # 0=none;1=PCF8575
        "ext_temperature_sensor_enable": 1, # 0=none;1=DS18B20
        "rele_out_enable": 2,   # 2 relays enabled
        "keyboard_enable": 4, # 0=none;1...N=N keys on I/O-Expander;100=4 keys on GPIN
        "lcd_enable": 1,    # 0=none;1=OLED_SSD1306
        "buzzer_enable": 1, # 0=none;1=buzzer enabled
        "battery_enable": 2,    # 0=none;1=reserved;2=1 li-ion cell (1S) ~3.0–4.2V;3=3 li-ion cells (3S) ~9–12.6V
        # SIM SETTINGS
        # Modem SIM setting can change depending on the used card, so are not here hardcoded but can be set in 2 ways:
        # * editing the system setting file "sb/SYSTEM.json"
        # * by web interface (possible if wifi is active)
        # For testing/debug purpose it's possible uncomment and hardcode the setting here below.
        
        #"modem_sim_sms_center": "+393519999600", # Modem settings
        #"modem_sim_pin": "1234",
        #"modem_apn":"iliad",
        #"modem_user":"iliad",
        #"modem_passwd":"",
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
    # These settings can be hardcoded here for testing purpose. Normally must be changed by the web interface.
    # If wifi settings are unknown it's possible force access point mode (no password) pressing the board button for about 15 seconds.
    # Then connecting to the web page it's possible change the wi-fi settings for example to connect to a certain network.
    # The default web page user/password are "root"/"1976"
    "wifi": {
#         "wifi_mode": 1,   # 0=Disabled;1=Client;2=Access point
#         "ip": "192.168.1.121",
#         "gateway": "192.168.1.1",
#         "subnet": "255.255.255.0",
        #Access point settins (if wifi_mode = 2)
#         "ap_passwd": "",	# access point password
#         "ap_channel": 3,	# access point channel
        #client settings (if wifi_mode = 1)
#         "cli_ssid": "PingoPallino",
#         "cli_passwd": "HelloVera2012",
#         "cli_dhcp_enable": 0,
#         "cli_dns_address": "8.8.8.8"
    }
}


