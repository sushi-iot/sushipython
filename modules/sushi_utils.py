# sushi_utils.py
this_file_version="2026-01-06@1132"

"""
CHANGELOG
    * "2026-01-06@1132"
        - help centralized to sushi.help()
    * "2025-12-14@1552"
        - load_setting fix in case that both file and parameter do  not exists
"""

import sushi
import ujson as json  # MicroPython
import sushi_defs

"""
def param_exists(module, param):
    # Check if a module and parameter exist in PARAMETERS.
    # Returns:
        # 0 -> module and parameter exist
        # 2 -> module exists but parameter not found
        # 1 -> module not found
    mod = module.upper()
    if mod not in PARAMETERS:
        return 1
    if param not in PARAMETERS[mod]:
        return 2
    return 0
"""

def load_setting(module, setting):
    """
    Reads a setting from a JSON file named '<module>.json'.
    """
    filename = f"sb/{module.upper()}.json"
    err = None
    data = None
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except OSError:
        err = (1, "file not found")
    except ValueError:
        err = (2, "invalid JSON")
    
    if err == None and setting not in data:
        err = (3, "param not found")

    if err == None:
        return data[setting]
    return None;

def save_setting(module, setting, value):
    """
    Sets the value of a configuration for a specific module in '<module>.json'.
    """
    filename = f"sb/{module.upper()}.json"
    mod = module.upper()
    # --- Load existing data or create new ---
    try:
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except ValueError:
                return -1 # "invalid JSON"
    except OSError:
        data = {}  # file not found -> create new

    # --- Update or add parameter ---
    if setting not in data or data[setting] != value:
        data[setting] = value
        try:
            with open(filename, "w") as f:
                json.dump(data, f)
        except OSError:
            return -2 # "file write error"
        return 1  # changed

    return 0  # no change


def set_sushi_config(config):    
    err = 0
    if not isinstance(config, dict):
        return (1, "invalid input type")
    # params(dict) -> json
    json_str = json.dumps(config)
    err,res = sushi.cmd("send_struct", ('cfg' , json_str ))
    if err == 0:
        if res == 2:
            print("Configuration changed. Restarting...")
        return res  #return 0 : not changed ; 1 : changed, no restart ; 2 : changed, need restart.
    if type(res) == int and res < 0:
        return res        
    return -1

def get_sushi_config():    
    err,json_str = sushi.cmd("get_struct", "cfg")
    if err == 0:
        return json.loads(json_str)
    return None

def get_sushi_status():    
    err,json_str = sushi.cmd("get_struct", "st")
    if err == 0:
        return json.loads(json_str)
    return None


def pinout(board_id=None):
    """Mostra l'elenco delle board o il pinout di una board specifica."""
    if board_id is None:
        print("Available boards:\n")
        for b in sushi_defs.BOARDS:
            print(f"*  ID {b['board_model_id']}: {b['desc']}")
        print("\nUse pinout(<ID>) to view details.\n")
        return

    # cerca la board con quell'ID
    board = None
    for b in sushi_defs.BOARDS:
        if b["board_model_id"] == board_id:
            board = b
            break

    if board is None:
        print(f"Board ID {board_id} not found.\n")
    else:
        print(f"### Pinout for {board['desc']} [`board_model` ID: {board_id}] ###\n")
        print(board["help"])
        

def list_params(mod=None):
    if isinstance(mod, str) and (mod.upper() in sushi_defs.PARAMETERS):
      print(f"### Parameters for module '{mod}':")
      current_cat = None
      for param, info in sushi_defs.PARAMETERS[mod.upper()]:                
        cat = info.get("cat", "")
        if cat != current_cat and cat != "":
            print()                                   
            print(f"**{cat.upper()} params**  ")
            current_cat = cat

        desc = info.get("desc", "")
        typ  = info.get("type", type(None)).__name__
        rng  = info.get("range", "")
        print(f"* `{param}` ({typ}): {desc}  \n"
              f"  Values: {rng}")
    else:
        if mod is not None:    
            print(f"No help available for module '{mod}'")
            print()
        print("Available modules:")
        for mod in sushi_defs.PARAMETERS:
            print(f"* '{mod.lower()}'")
        print("\nCall list_params('MODULE') to see parameters of a module")

def print_md_help_appendix():
    
    def output_repl_command(title , command):
        print("```")
        print("*********************************************")
        print(f">>>REPL command `{title}`")
        print("*********************************************")
        print("```")
        exec(command)
        print()
        print("---")
        print()
        
    # print base help
    # sushi.help()
    # print()

    # appendix
    print(f"# Appendix – Detailed References #")
    print()
    # pinout section
    print(f"## PINOUT ##")
    print()    
    output_repl_command('sushi_utils.pinout()' , 'pinout()')
    output_repl_command('sushi_utils.pinout(0)' , 'pinout(0)')
    
    # params section
    print(f"## Parameters Reference  ##")
    print()
    output_repl_command('sushi_utils.list_params()' , 'list_params()')
    output_repl_command('sushi_utils.list_params("system")' , 'list_params("system")')
    output_repl_command('sushi_utils.list_params("wifi")' , 'list_params("wifi")')
    

def help():
    # Version
    print(f"Module 'sushi_utils.py'")
    print()
    print(f"* Description: System setup, status & utilities")
    print(f"* Version:'{this_file_version}'")
    print(f"* Functions: call `sushi.help()`")
    print(f"* [Source code]('https://github.com/sushi-iot/sushi-iot-framework/blob/main/modules/sushi_utils.py')")

"""
## SETUP & STATUS ##
* `sushi_utils.get_sushi_config()` -> dict or None (if error)  
  Return full configuration structure
* `sushi_utils.set_sushi_config(settings:dict )` -> int [0 = value not changed ; 1 = value changed no restart ; 2 = value changed need restart; < 0 = error]  
  Set configuration parameters (self restart if settings changed).
* `sushi_utils.list_params(module:str ['system' , 'wifi'])`  
  List the available configuration params
* `sushi_utils.get_sushi_status()` -> dict or None (if error)  
  Return full status structure
* `sushi_utils.load_setting(module:str, setting_str)`  -> str or int or None (if error)  
  Load a custom configuration parameter
* `sushi_utils.save_setting(module:str, setting:str, value:int or str)`  -> int [0 = value not changed ; 1 = value changed ; < 0 = error]  
  Save a custom configuration parameter  
  
## GPIO & SENSORS ##
* `sushi_utils.pinout()` -> str  
  Return the board pinout for integrated & general purpose functions


## CORE CALLS ##
! These are lower level calls used in this module.

* `sushi.cmd("get_struct", type:str ['st'=status,'cfg'=configuration])` -> str [JSON]
  Get a system structure
* `sushi.cmd("send_struct", (type:str ['cfg'=configuration , 'cmd'=command] , data:str [JSON] ))` 
  Send a system structure


## USAGE EXAMPLES ##
import sushi
import sushi_utils as su

# Reading sushi configuration
data = su.get_sushi_config()    #return a dict with all parameters
if data != None:
    print(data['system']['data_file_version'])
else:
    print("Error")

# Setting sushi configuration
cfg = {'system': {'time_zone_hours': 2 , 'data_file_version' : '20251011@2309'}}
res = su.set_sushi_config(cfg)    
if res == 2:
    print('Restarting...')
elif res < 0 :
     print(f"Error: {res}")
else:
    print("OK")
    
# Reading sushi status
data = su.get_sushi_status()    #return a dict with all parameters
print(data)
print(data['system']['framework_ver'])

# Setting a custom parameter
res = su.save_setting('my_module', 'my_param', 'test-value')
if res < 0:
    print(f"Write error:'{res}'")
else:
    print("OK")

# Getting a custom parameter
value = su.load_setting('my_module', 'my_param')
if value != None:
    print(f"Read value:'{value}'")
else:
    print("Error")
"""
