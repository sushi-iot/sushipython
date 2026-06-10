# SushiPython IoT Framework examples & projects

## Resources
[Quick uPy code examples](https://sushi-iot.github.io/sushipython/manual/#examples)
[Firmware download](https://github.com/sushi-iot/sushipython/releases)    
[Online manual](https://sushi-iot.github.io/sushipython/manual)    
[SushiPython IoT project overview](https://sushi-iot.github.io/sushipython/)  

## Examples & projects for Sushi Board  
<img src="img/sushi_board_1.png" width=20% >

The Sushi Board PCBA integrates **common commercial modules**; therefore, all projects and examples can be built even using a breadboard or a custom protoboard.  

* [Sushi Board overview](https://sushi-iot.github.io/sushi-iot-board/)
* [Sushi-Iot-Board schematic & components](https://github.com/sushi-iot/sushi-iot-board)

### Basic examples
|Name|Description|
|--------|--------|
[sb_ext_gpin](sb_ext_gpin)|Read IO-Expander input and detect changes via interrupt callback
[sb_read_sensors](sb_read_sensors)|Reads the board’s main sensors (voltage, battery, temperature) and prints the values to the REPL.
[sb_send_sms](sb_send_sms)|Sends an SMS via the modem and shows the result using a callback
[sb_receive_sms](sb_receive_sms)|receive SMS messages and print them to the REPL
[sb_menu](sb_menu)|Add a custom menu (by 'sushi_menu' module) to user interface to switch ON/OFF a relay OUTPUT

### Demo projects 
|Name|Description|
|--------|--------|
[sb_s-home](sb_s-home)|Home domotics demo project

---
## Examples & projects on bread board with ESP32DevKitC (Espressif official dev board)  
<img src="img/ESP32DevKitC-WROVER.png" width=20% >   

**[Espressif ESP32DevKitC board](https://github.com/sushi-iot/sushi-iot-board/blob/main/hardware/modules/ESP32DevKitC-WROVER.md)**

### Basic examples

|Name|Description|
|--------|--------|
[dkc_menu](dkc_menu)|Add a custom menu (by 'sushi_menu' module) to user interface to switch ON/OFF a relay OUTPUT

