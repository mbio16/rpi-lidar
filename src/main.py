import configparser
from pyrplidar import PyRPlidar
import time
import json
from datetime import datetime
import logging
CONFIGURATION_FILE = "./../config.ini"

def set_log_level(level:str)->None:
    FORMAT = '%(levelname)s %(asctime)s %(message)s'
    if level == "INFO":
        logging.basicConfig(level=logging.INFO,format=FORMAT)
    elif level == "DEBUG":
        logging.basicConfig(level=logging.DEBUG,format=FORMAT)
    elif level == "WARNING":
        logging.basicConfig(level=logging.WARNING,format=FORMAT)
    elif level == "ERROR":
        logging.basicConfig(level=logging.ERROR,format=FORMAT)

def log_config(config:configparser.ConfigParser)->None:
    logging.info("Lidar port: {}".format(config["lidar"]["port"]))
    logging.info("Lidar baudrate: {}".format(config["lidar"]["baudrate"]))
    logging.info("Lidar timeout: {}".format(config["lidar"]["count"]))
    logging.info("Lidar motor pwm: {}".format(config["lidar"]["motor_pwm"]))
    logging.info("Output file: {}".format(config["file"]["file_path"]))
    
def read_config(path_to_config_file:str):
    config = configparser.ConfigParser()
    config.read(path_to_config_file)
    return config

def write_param_to_file(file)->None:
    dict_from_json = json.loads(scan)
    degre = dict_from_json["degre"]
    distance = dict_from_json["distance"]
    quality = dict_from_json["quality"]
    now = datetime.now()
    logging.debug("Degre: {} Distance: {} quality: {}".format(str(degre),str(distance),str(quality)))
    if quality > 0:
        file.write(str(now) + "," + str(degre) + "," + str(distance) + "," + str(quality))

def simple_express_scan(config:configparser.ConfigParser):

    lidar = PyRPlidar()
    lidar.connect(
        port=config["lidar"]["port"],
        baudrate=int(config["lidar"]["baudrate"]),
        timeout=int(config["lidar"]["timeout"])
        )
                      
    lidar.set_motor_pwm(int(config["lidar"]["motor_pwm"]))
    time.sleep(2)
    
    scan_generator = lidar.start_scan_express(4)
    with open(config["file"]["file_path"],"a") as file:
        for count, scan in enumerate(scan_generator()):
            param_list = get_params_from_scan(scan)
            if count == int(config["lidar"]["count"]): break

    lidar.stop()
    lidar.set_motor_pwm(0)  
    lidar.disconnect()


if __name__ == "__main__":
    config = read_config(CONFIGURATION_FILE)
    set_log_level(config["log"]["level"])
    log_config(config)
    simple_express_scan()