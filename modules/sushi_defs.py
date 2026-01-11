# sushi_defs.py
# Ver.2026-01-06@1911

##########################
# params help/definition
##########################
PARAMETERS = {
    "SYSTEM": [
        #system
        ("device_name", {"desc": "Device name/description", "range": "String", "type": str , "cat":"system-config"}),
        ("data_file_version", {"desc": "Configuration file version", "range":"String", "type": str , "cat":"system-config"}),
		#system-datetime
        ("time_zone_hours", {"desc": "Time zone offset from UTC", "range": "-12…+14", "type": int , "cat":"system-datetime"}),
        ("time_auto_daylight_save_change", {"desc": "Enable automatic daylight saving change (European rules)", "range": "0=disabled;1=enabled", "type": int , "cat":"system-datetime"}),
        ("ntp_server_address", {"desc": "NTP server address", "range": "String. Example: 'pool.ntp.org'", "type": str , "cat":"system-datetime"}),
        #hardware 
        ("board_model", {"desc": "Board model. Call 'sushi_utils.pinout()' to see the pinout.", "range": "0=ESP32-DevKitC on Sushi Board", "type": int , "cat":"hardware-setup"}),
        ("ioex_enable", {"desc": "Enable I/O expander management", "range": "0=none;1=PCF8575", "type": int , "cat":"hardware-setup"}),
        ("ext_temperature_sensor_enable", {"desc": "Enable temperature sensor", "range": "0=none;1=DS18B20", "type": int , "cat":"hardware-setup"}),
        ("rele_out_enable", {"desc": "Enable relay outputs", "range": "0=none;1..2=number of relays", "type": int , "cat":"hardware-setup"}),
        ("keyboard_enable", {"desc": "Enable keypad management", "range": "0=none;1...N=N keys on I/O-Expander;100=4 keys on GPIN", "type": int , "cat":"hardware-setup"}),
        ("lcd_enable", {"desc": "Enable display", "range": "0=none;1=OLED_SSD1306", "type": int , "cat":"hardware-setup"}),
        ("buzzer_enable", {"desc": "Enable buzzer", "range": "0=none;1=buzzer enabled", "type": int , "cat":"hardware-setup"}),
        ("battery_enable", {"desc": "Battery level range", "range": "0=none;1=reserved;2=1 li-ion cell (1S) ~3.0–4.2V;3=3 li-ion cells (3S) ~9–12.6V", "type": int , "cat":"hardware-setup"}),
        #system-health&monitor
		("event_register_size_kb", {"desc": "Event register file size", "range": "0=no event file;N=Max KB", "type": int , "cat":"system-health&monitor"}),
        ("system_info_log_frequency_min", {"desc": "System info log frequency (minutes)", "range": "0=never;N=minutes", "type": int , "cat":"system-health&monitor"}),
        ("system_info_store_frequency_min", {"desc": "System info storage frequency (minutes). Requires system_info_csv_filter.", "range": "0=never;N=minutes", "type": int , "cat":"system-health&monitor"}),
        ("system_info_csv_filter", {"desc": "Filter for system status entries stored when system_info_store_frequency_min ≠ 0", "range": "String: '<entry_info_1>*<entry_info_2>*...'", "type": str , "cat":"system-health&monitor"}),
        ("system_info_send_http_post_frequency_min", {"desc": "HTTP POST system info frequency (minutes). Posts are sent to http_post_delivery_address.", "range": "0=never;N=minutes", "type": int , "cat":"system-health&monitor"}),
		#system-interface
        ("wifi_status_led", {"desc": "Assign wi-fi status to an external LED", "range": "String: 'GPIO_1..N', 'GPO_1..N' - see HW pinout", "type": str , "cat":"system-interface"}),
        ("system_status_led", {"desc": "Assign system status to an external LED", "range": "String: 'GPIO_1..N', 'GPO_1..N' - see HW pinout", "type": str , "cat":"system-interface"}),
		("modem_status_led", {"desc": "Assign modem status to an external LED", "range": "String: 'GPIO_1..N', 'GPO1..N' - see HW pinout", "type": str , "cat":"system-interface"}),
        #data manager
        ("http_post_delivery_address", {"desc": "Server address for HTTP POST. Custom application-specific data can be sent by the Sushi-IoT-Framework API", "range": "String. Example: 'https://your_web_server/post_data.php'", "type": str , "cat":"http-data-manager"}),
        ("use_wifi_for_http_post", {"desc": "Use wi-fi before modem for HTTP POST", "range": "0=disabled;1=enabled", "type": int , "cat":"http-data-manager"}),
        #modem        
        ("modem_enable", {"desc": "Enable modem management", "range": "0=none;1=SIMCOM7672X", "type": int , "cat":"modem"}),
        ("modem_sim_sms_center", {"desc": "SIM SMS center number", "range": "String. Example: '+393519999600'", "type": str , "cat":"modem"}),
        ("modem_sim_pin", {"desc": "SIM PIN code", "range": "String. Example: '1234'", "type": str , "cat":"modem"}),
        ("modem_apn", {"desc": "SIM APN name", "range": "String. Example: 'iliad'", "type": str , "cat":"modem"}),
        ("modem_user", {"desc": "APN user", "range": "String. Optional", "type": str , "cat":"modem"}),
        ("modem_passwd", {"desc": "APN password", "range": "String. Optional", "type": str , "cat":"modem"}),
        #debug/experimental/reserved
        ("powersave_time_wifi_off_min", {"desc": "Auto wi-fi power-off after inactivity (minutes)", "range": "0=disabled;N=minutes", "type": int , "cat":"debug-experimental-reserved"}),
		("debug_mode", {"desc": "Debug", "range": "Reserved", "type": int , "cat":"debug-experimental-reserved"}),
        ("extension_modules", {"desc": "Enable extra experimental modules", "range": "Reserved", "type": str , "cat":"debug-experimental-reserved"})
    ] ,
	"WIFI": [
		#common
		("wifi_mode", {"desc": "Wifi mode", "range": "0=Disabled;1=Client;2=Access point", "type": int , "cat":"common"}),
		("ip", {"desc": "IP address", "range": "IP address string", "type": str , "cat":"common"}),
		("subnet", {"desc": "Subnet mask", "range": "IP address string", "type": str , "cat":"common"}),		
		("gateway", {"desc": "Gateway", "range": "IP address string", "type": str , "cat":"common"}),
		#client only
		("cli_ssid", {"desc": "Network SSID", "range": "String", "type": str , "cat":"wifi-client-mode"}),
		("cli_passwd", {"desc": "Network password", "range": "String", "type": str , "cat":"wifi-client-mode"}),
		("cli_dhcp_enable", {"desc": "Enable DHCP client", "range": "0=disabled;1=enabled", "type": int , "cat":"wifi-client-mode"}),
		("cli_dns_address", {"DNS address": "Subnet mask", "range": "IP address string", "type": str , "cat":"wifi-client-mode"}),
		#access point only
		("ap_passwd", {"desc": "Access point password", "range": "String", "type": str , "cat":"wifi-access-point-mode"}),
		("ap_channel", {"desc": "Access point channel", "range": "String", "type": int , "cat":"wifi-access-point-mode"})
	]
	
}

##########################
#board specific help
##########################
BOARD_ID_0_HELP = """
**system(always present)**
* ON-BOARD-BUTTON: GPIO0
* I2C_SDA_PIN:GPIO21
* I2C_SCL_PIN:GPIO22
* REPL_UART1_TX:GPIO1(TX)
* REPL_UART1_RX:GPIO3(RX)
* VIN-ADC:GPIO36(VP)

**GPIO(free I/O pins)**
* GPIO_1:GPIO19
* GPIO_2:GPIO18
* GPIO_3:GPIO5
* GPIO_4:GPIO4
* GPIO_5:GPIO13

**GPI(free Input only pins)**
* GPI_1:GPIO39(VN)
* GPI_2:GPIO35

**GPO(free Output only pins)**
* GPO_1:GPIO2

**power(if 'battery_enable' > 0)**
* BATT-ADC:GPIO34[3]

**modem(if 'modem_enable' > 0)**
* MODEM_UART_TX:GPIO27[1]
* MODEM_UART_RX:GPIO26[1]
* MODEM_PWKEY:GPIO32[1]
* MODEM_POWER:GPIO23[1]

**io-expander(if 'ioex_enable' > 0)**
* IOEXP_I2C_INT_PIN:GPIO14[1]

**direct 4B keyboard(if 'keyboard_enable'=100)**
* COMMON: GND
* IN_1(-): GPIO_1
* IN_2(+): GPIO_2
* IN_3(BACK): GPIO_3
* IN_4(ENT): GPIO_4

**relays**
* RELE_1_PIN:GPIO15 (if 'rele_out_enable'>0) [2]
* RELE_2_PIN:GPIO12 (if 'rele_out_enable'=2) [2]

**temperature sensor(if 'ext_temperature_sensor_enable' > 0)**
* DS18B20_DATA:GPIO33[1]

**buzzer(if 'buzzer_enable' > 0)**
* BUZZER_PIN:GPIO25[1]

**notes/syntax**
[1] : altenative use is GPIO
[2] : altenative use is GPO
[3] : altenative use is GPI
GPIOXX : logical ESP32 function name. XX is the pin number to be used in the code.

**ONLINE DOC**
* [ESP32-DevKitC official doc](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
* [Sushi Board on GitHub](https://github.com/sushi-iot/sushi-iot-board)

"""

BOARDS = [ {	"desc":"ESP32-DevKitC on Sushi Board" ,
                "board_model_id" : 0 ,
                "help":BOARD_ID_0_HELP
            } 
        ]
        
