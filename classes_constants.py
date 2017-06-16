'''
For VAST Challenge 2017 Mini Challenge 2
Author: GU Qiao, George @ HKUST
E-mail: georgegu1997@gmail.com

This script defines the classes and constants used in other scripts of Mini Challenge 2
'''

import csv
import numpy as np
from datetime import datetime, timedelta

'''
predefined constant for the script, do not change
'''

FULL_COMPANY_NAME = {
    "RFE": "Roadrunner Fitness Electronics",
    "KOF": "Kasioc Office Furniture",
    "RCT": "Radiance ColourTek",
    "ISB": "Indigo Sol Boards"
}

FULL_CHEM_NAME = {
    "A": "Appluimonia",
    "C": "Chlorodinine",
    "M": "Methylosmolene",
    "G": "AGOC-3A"
}

'''
the coordinates on the map
'''
COMPANY_LOCATION = {
    "RFE": [89, 27],
    "KOF": [90, 21],
    "RCT": [109, 26],
    "ISB": [120, 22]
}

SENSOR_LOCATION = [
    [62, 21], #note that the number of the sensors starts from 1
    [66, 35],
    [76, 41],
    [88, 45],
    [103, 43],
    [102, 22],
    [89, 3],
    [74, 7],
    [119, 42]
]

TIME_INTERVAL = {
    "Apr": {
        "start": datetime(year=2016, month=4, day=1),
        "end": datetime(year=2016, month=5, day=1)
    },
    "Aug": {
        "start": datetime(year=2016, month=8, day=1),
        "end": datetime(year=2016, month=9, day=1)
    },
    "Dec": {
        "start": datetime(year=2016, month=12, day=1),
        "end": datetime(year=2017, month=1, day=1)
    },
    "All":{
        "start": datetime(year=2016, month=4, day=1),
        "end": datetime(year=2017, month=1, day=1)
    }
}

'''for abnormal values detection'''
FIRST_MINUS_SECOND_THRESHOLD = 50

class SensorRecord:
    '''static variable and method'''
    all_records = []

    @staticmethod
    def init_sensor_data():
        data = []
        '''
        The number of sensors will start from 0 instead of 1
        '''
        for i in range(len(SENSOR_LOCATION)):
            data.append({
                "A":[],
                "C":[],
                "M":[],
                "G":[]
            })
        return data

    @staticmethod
    def read_all_data(file_name = "Sensor_Data.csv"):
        data = SensorRecord.init_sensor_data()
        with open(file_name, "rb") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",")
            i = 0
            for row in spamreader:
                i += 1
                if i == 1:
                    continue #ignore the title of the table
                chem_full = row[0]
                #find key by value
                for k, v in FULL_CHEM_NAME.items():
                    if chem_full == v:
                        chem = k
                assert(chem != None)
                sensor_index = int(row[1]) - 1 #sensor index starts from 0 instea of 1
                dt = datetime.strptime(row[2], "%m/%d/%y %H:%M")
                reading = float(row[3])
                record = SensorRecord(chem, sensor_index, dt, reading)
                data[sensor_index][chem].append(record)
        SensorRecord.all_records = data

    @staticmethod
    def sort_by_time():
        for sensor in all_records:
            for k, v in sensor:
                v.sort(key = lambda x: x.time)

    def __init__(self, chemical, sensor_index, time, reading):
        '''
        chemical will be in ["A", "C", "M", "G"]
        '''
        self.chemical = chemical
        self.sensor_index = sensor_index
        self.time = time
        self.reading = reading

class WindRecord:
    '''static variable and method'''
    all_records = []

    @staticmethod
    def read_all_data(file_name = "Meteorological_Data.csv"):
        data = []
        with open(file_name, "rb") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=",")
            i = 0
            for row in spamreader:
                i += 1
                if i == 1:
                    continue #ignore the title
                dt = datetime.strptime(row[0], "%m/%d/%y %H:%M")
                '''handle the situation where data is missing'''
                if len(row[1]) == 0:
                    direction = speed = -1
                else:
                    direction = float(row[1])
                    speed = float(row[2])
                record = WindRecord(time = dt, direction = direction, speed = speed)
                data.append(record)
        WindRecord.all_records = data

    @staticmethod
    def sort_by_time():
        WindRecord.all_records.sort(key = lambda x: x.time)

    @staticmethod
    def linear_interpolation():
        WindRecord.sort_by_time()
        new_data = []
        for i in range(len(WindRecord.all_records)):
            this_r = WindRecord.all_records[i]
            if i != len(WindRecord.all_records) - 1 and (WindRecord.all_records[i + 1].time - this_r.time).total_seconds() == 3*60*60:
                next_r = WindRecord.all_records[i + 1]
                first_direction = (this_r.direction * 2 + next_r.direction * 1) / 3
                first_speed = (this_r.speed * 2 + next_r.speed * 1) / 3
                second_direction = (this_r.direction * 1 + next_r.direction * 2) / 3
                second_speed = (this_r.speed * 1 + next_r.speed * 2) / 3
            else:
                last_r = WindRecord.all_records[i - 1]
                direction_slope = (this_r.direction - last_r.direction) / 3
                speed_slope = (this_r.speed - last_r.speed) / 3
                first_direction = this_r.direction + direction_slope * 1
                first_speed = this_r.speed + speed_slope * 1
                second_direction = this_r.direction + direction_slope * 2
                second_speed = this_r.speed + speed_slope *2
            first = WindRecord(this_r.time + timedelta(hours = 1), first_direction, first_speed)
            second = WindRecord(this_r.time + timedelta(hours = 2), second_direction, second_speed)
            new_data.append(first)
            new_data.append(second)
        WindRecord.all_records += new_data
        WindRecord.sort_by_time()

    @staticmethod
    def print_all():
        for record in WindRecord.all_records:
            print record.time.strftime("%Y-%m-%d %H:%M:%S") + ": " + str(record.direction) + " degree, " + str(record.speed) + " m/s"

    def __init__(self, time, direction, speed):
        self.time = time
        self.direction = direction # in degree with the same rule as source data
        self.speed = speed # in meter/second

class ErrorSensorRecord:
    all_records = []

    @staticmethod
    def print_all():
        for record in ErrorSensorRecord.all_records:
            print record.time, "Sensor", record.sensor_index, "Chemical: " + FULL_CHEM_NAME[record.chem_k]
            print record.error_t, record.value
            if record.linear_expectation != None:
                print "linear expectation:", record.linear_expectation

    @staticmethod
    def sort_by_time():
        ErrorSensorRecord.all_records.sort(key = lambda x: x.time)

    def __init__(self, time, sensor_index, chem_k, value, error_t, linear_expectation = None):
        self.time = time
        self.sensor_index = sensor_index
        self.chem_k = chem_k
        self.value = value # a list of all value, if missing, it will be an enpty list
        self.error_t = error_t # "multiple" or "missing"
        self.linear_expectation = linear_expectation # what this reading should be if we use linear interporlation
