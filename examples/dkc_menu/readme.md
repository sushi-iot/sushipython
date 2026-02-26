## Sushi - IoT MicroPython example

### Project
* **Project**: Menu example
* **Description**: Add a custom menu to physical user interface to switch ON/OFF a relay OUTPUT
* **Video demo** : [Sushi IoT on instagram](https://www.instagram.com/sushi_board_iot/)

---
### Source files
* **"menu_example.py"** : main example code
* **"menu_example_config.py"** : sushi IoT configuration

---
### Instructions

* Connect the components on the breadboard.
* Download and flash the [SushiPython IoT Firmware](https://github.com/sushi-iot/sushipython/releases) onto the board. 
* Connect ESP32DevKitC to your PC by the USB connector (or use WebREPL if you prefer). 
* If you are new to MicroPython see this [basic MicroPython  guide](https://sushi-iot.github.io/sushipython/coding/).    
* Transfer the '.py' example source files to the board using your favourite MicroPython interface.  
* Run the main script file. Note that it's normal on the first run (and in general, if the device configuration has changed): the device will store the settings and restart itself.

---
### Hardware components
This project uses the following hardware:

* CPU : [ESP32DevKitC-WROVER module](https://github.com/sushi-iot/sushi-iot-board/blob/main/hardware/modules/ESP32DevKitC-WROVER.md)
* Display : [SSD1306 OLED](https://github.com/sushi-iot/sushi-iot-board/blob/main/hardware/modules/OLED_SSD1306.md)
* Relay: [D1 mini relay module](https://github.com/sushi-iot/sushi-iot-board/blob/main/hardware/modules/relay_d1_mini.md)
* Keypad : [1x4 membrane keypad](https://github.com/sushi-iot/sushi-iot-board/blob/main/hardware/modules/keypad_4k.md)

In each component overview file there are some brief info.
All components can be found widely on the web, so just as example it's provided some link where can be bought.

---
### Overview
<img src="menu_example.jpg" width=25% >

---
### Hardware connections table

| Pin | Connected To | Type | Note |
|:--|:--|:--|:--|
| ESP32.USB | USB Power suppplier | `5V Power` | Powers the board and peripherals |
| ESP32.GND | BB.GND | `GND` | Common ground network (1)|
| ESP32.5V | BB.VCC | `5V` | Shared power rail (1)|
| Relay.VCC | BB.VCC | `5V` | Power supply for relay module |
| Relay.GND | BB.GND | `GND` | Common ground |
| Relay.IN | ESP32.GPIO15 | `Digital` | Relay control signal |
| Keypad.GND | BB.GND | `GND` | Common ground |
| Keypad.K1 | ESP32.GPIO19 | `Digital` | Button 1 |
| Keypad.K2 | ESP32.GPIO18 | `Digital` | Button 2 |
| Keypad.K3 | ESP32.GPIO5 | `Digital` | Button 3 |
| Keypad.K4 | ESP32.GPIO4 | `Digital` | Button 4 |
| OLED.VCC | BB.VCC | `5V` | Power supply (2) |
| OLED.GND | BB.GND | `GND` | Common ground |
| OLED.SDA | ESP32.GPIO21 | `SDA` | I2C data |
| OLED.SCL | ESP32.GPIO22 | `SCL` | I2C clock |

**Notes:**  
* (1) “BB.VCC” & “BB.GND”  indicates a connection to the breadboard power or ground rails.  
* (2) Some OLED may require 3.3V, in this case connect to ESP32.3V3 pin.

---

### Resources
[SushiPython IoT Firmware download](https://github.com/sushi-iot/sushipython/releases)  
[Online coding manual](https://sushi-iot.github.io/sushipython/coding/)  
[SushiPython IoT project overview](https://sushi-iot.github.io/sushipython/)  

**Quick reference**  
In the REPL, run:
```python
  sushi.help()
```
or see the result directly [here](https://github.com/sushi-iot/sushipython/tree/main/examples/sushi-quick-reference.md).