import configparser
from pyrplidar import PyRPlidar
import time
import json
from datetime import datetime
import logging
from io import TextIOWrapper
import os.path

CONFIGURATION_FILE = "./../config.ini"
MOTOR_STOP_PWM = 0
SLEEP_TIME = 2
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

def calculate_scanning_count(pwm:int,seconds:int)->int:
    return int(pwm*seconds)
    
def read_config(path_to_config_file:str):
    config = configparser.ConfigParser()
    config.read(path_to_config_file)
    return config

def write_param_to_file(file: TextIOWrapper,scan:dict)->None:
    dict_from_json = eval(scan)
    degre = dict_from_json["angle"]
    distance = dict_from_json["distance"]
    quality = dict_from_json["quality"]
    now = datetime.now()
    logging.debug("Degre: {} Distance: {} quality: {}".format(str(degre),str(distance),str(quality)))
    if quality > 0:
        file.write(str(now) + ";" + str(degre) + ";" + str(distance) + ";" + str(quality) + "\n")

def file_check(file_path:str)->None:
    if not os.path.isfile(file_path):
        logging.warning("File does not exists. Creating one...")
        with open(file_path,"w") as file:
            logging.info("Writting header in file")
            file.write("time;degre;distnace;quality\n")
    else:
        logging.info("File exists. Appending file...")

def simple_express_scan(config:configparser.ConfigParser)->None:

    lidar = PyRPlidar()
    lidar.connect(
        port=config["lidar"]["port"],
        baudrate=int(config["lidar"]["baudrate"]),
        timeout=int(config["lidar"]["timeout"])
        )
    logging.info("Connected to lidar")
    logging.info("Stopping lidar...")  
    lidar.stop()
    lidar.set_motor_pwm(MOTOR_STOP_PWM)           
    logging.info("Setting lidar pwm to {}".format(config["lidar"]["motor_pwm"]))     
    lidar.set_motor_pwm(int(config["lidar"]["motor_pwm"]))
    time.sleep(SLEEP_TIME)
    count_to_run = calculate_scanning_count(config["lidar"]["pwm"],config["lidar"]["seconds_to_run"])
    try:
        scan_generator = lidar.start_scan_express(4)
        file_check(config["file"]["file_path"])
        with open(config["file"]["file_path"],"a") as file:
            for count, scan in enumerate(scan_generator()):
                write_param_to_file(file,str(scan))
                if count == count_to_run: break
    except Exception as ex:
        logging.error(str(ex))
    logging.info("Stopping lidar...")
    lidar.stop()
    lidar.set_motor_pwm(MOTOR_STOP_PWM)  
    logging.info("Lidar stoped")
    lidar.disconnect()
    logging.info("Lidar disconected")

if __name__ == "__main__":
    config = read_config(CONFIGURATION_FILE)
    set_log_level(config["log"]["level"])
    log_config(config)
    simple_express_scan(config)