import sushi
import sushi_utils

sushi_settings={
    # System settings help: call "sushi_utils.list_params('system')"
    "system": {
        "device_name": "MyTestBoard",
        "data_file_version": "MENU-EXAMPLE-DKC-01",
        "modem_enable": 0,
        "board_model": 0,
        "ioex_enable": 0,
        "ext_temperature_sensor_enable": 0,
        "rele_out_enable": 1, #1 rele enabled
        "keyboard_enable": 100,# keyboard connected directly to micro pins
        "lcd_enable": 1,# OLED enabled
        "buzzer_enable": 0,
        "battery_enable": 0,
        "modem_sim_sms_center": "",
        "modem_sim_pin": "",
        "modem_apn":"",
        "modem_user":"",
        "modem_passwd":"",
        "modem_status_led":"",
        "extension_modules": "",
        "system_info_log_frequency_min": 0,
        "system_info_store_frequency_min": 0,
        "system_info_send_http_post_frequency_min": 0,
        "system_info_csv_filter": "",
        "wifi_status_led": "",
        "system_status_led": "",
        "event_register_size_kb": 32,
        "time_zone_hours": 0,
        "time_auto_daylight_save_change": 0,
        "powersave_time_wifi_off_min": 0,
        "http_post_delivery_address": "",
        "ntp_server_address": "pool.ntp.org",
        "debug_mode": 0
},
    # System settings help: call "sushi_utils.list_params('wifi')"
    "wifi": {
        "wifi_mode": 2,   #wifi enabled as access point
        "ip": "192.168.1.111",
        "gateway": "192.168.1.1",
        "subnet": "255.255.255.0",
        "ap_passwd": "",
        "ap_channel": 3,
        "cli_ssid": "",
        "cli_passwd": "",
        "cli_dhcp_enable": 0,
        "cli_dns_address": "8.8.8.8"
    }
}
# set the configuration
sushi_utils.set_sushi_config(sushi_settings) #return: 0 = configuration not changed ; 1 = changed no need to restart ; 2 = changed and need to restart

