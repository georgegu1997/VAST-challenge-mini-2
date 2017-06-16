'''
For VAST Challenge 2017 Mini Challenge 2
Author: GU Qiao, George @ HKUST
E-mail: georgegu1997@gmail.com

This script will plot the company and the sensor on the canvas with the relative
positions the same as that on the real map. It can also print the sensor readings
as a polar bar plot or a polat scatter plot on the map.
'''

import csv

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from pprint import pprint
from datetime import datetime, timedelta

from classes_constants import *
from punchcard import *

'''
they mean the the coordinates of lefttop corner on the real map
'''
WINDOW_MARGIN = 10
WINDOW_LEFT_MAP_X = 62 - WINDOW_MARGIN
WINDOW_RIGHT_MAP_X = 120 + WINDOW_MARGIN
WINDOW_TOP_MAP_Y = 45 + WINDOW_MARGIN
WINDOW_BOTTOM_MAP_Y = 3 - WINDOW_MARGIN

'''
Determined at runtime
'''
MAIN_AXES_LEFT = 0.0
MAIN_AXES_BOTTOM = 0.0
MAIN_AXES_RIGHT = 0.0
MAIN_AXES_TOP = 0.0

'''
in the proportion of the whole canvas
'''
POLAR_PLOT_RADIUS = 0.08

WINDOW_WIDTH_IN_INCH = 12.0
WINDOW_HEIGHT_IN_INCH = WINDOW_WIDTH_IN_INCH * (WINDOW_TOP_MAP_Y - WINDOW_BOTTOM_MAP_Y) / (WINDOW_RIGHT_MAP_X - WINDOW_LEFT_MAP_X)
DPI = 240
POINT_RADIUS = 0.2

NUMBER_OF_SECTOR = 40

def cal_axe_location(point):
    x = point[0]
    y = point[1]
    left = ((x - WINDOW_LEFT_MAP_X) * 1.0 / (WINDOW_RIGHT_MAP_X - WINDOW_LEFT_MAP_X) - POLAR_PLOT_RADIUS + MAIN_AXES_LEFT) * (MAIN_AXES_RIGHT - MAIN_AXES_LEFT)
    bottom = ((y - WINDOW_BOTTOM_MAP_Y) * 1.0 / (WINDOW_TOP_MAP_Y - WINDOW_BOTTOM_MAP_Y) - POLAR_PLOT_RADIUS + MAIN_AXES_BOTTOM) * (MAIN_AXES_TOP - MAIN_AXES_BOTTOM)
    return [left, bottom, 2 * POLAR_PLOT_RADIUS, 2 * POLAR_PLOT_RADIUS]

def convert_direction(direction):
    return (450 - direction) % 360

def cal_sector_radii(sensor_index, chem_short, time_k):
    radii = np.zeros(NUMBER_OF_SECTOR)
    count = np.zeros(NUMBER_OF_SECTOR)
    start_time = TIME_INTERVAL[time_k]["start"]
    end_time = TIME_INTERVAL[time_k]["end"]
    selected_wind_record = [x for x in WindRecord.all_records if (x.time > start_time and x.time < end_time)]
    selected_sensor_record = [x for x in SensorRecord.all_records[sensor_index][chem_short] if (x.time > start_time and x.time < end_time)]
    for wind_record in selected_wind_record:
        #print "wind direction: "+str(wind_record.direction)
        sensor_record = next((x for x in selected_sensor_record if x.time == wind_record.time), None)
        if sensor_record == None:
            continue
        converted_direction = convert_direction(wind_record.direction)
        #print "converted_direction: " + str(converted_direction)
        radii_index = int(converted_direction / (360 / NUMBER_OF_SECTOR))
        radii[radii_index] += sensor_record.reading
        count[radii_index] += 1
    #print radii
    radii = np.divide(radii, count)#, where = count != 0)
    #print radii
    return radii

'''using polar bar plot'''
def draw_way_1(sensor_index, axe_location, chem_short, time_k):
    # Compute pie slices
    theta = np.linspace(0.0, 2 * np.pi, NUMBER_OF_SECTOR, endpoint=False)
    #radii = 10*np.random.rand(N)
    radii = cal_sector_radii(sensor_index, chem_short, time_k)
    #width = np.pi / 4 * np.random.rand(N)
    width = np.pi * 2 / NUMBER_OF_SECTOR

    '''
    now east is the 0, and theta increases counter-clockwise
    '''
    ax = plt.axes(axe_location, projection = "polar")
    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    ax.set_xticks([])
    #ax.set_yticks([])

    # Use custom colors and opacity
    for r, bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.viridis(r / 10.))
        bar.set_alpha(0.5)

'''using polar scatter plot'''
def draw_way_2(sensor_index, axe_location, chem_short, time_k):
    start_time = TIME_INTERVAL[time_k]["start"]
    end_time = TIME_INTERVAL[time_k]["end"]

    records = SensorRecord.all_records[sensor_index][chem_short]
    selected_record = [x for x in records if (x.time > start_time and x.time < end_time)]

    r = np.array([])
    theta = np.array([])
    colors = np.array([])

    for record in selected_record:
        wind_record = next((x for x in WindRecord.all_records if x.time == record.time), None)
        if wind_record == None:
            continue
        theta = np.append(theta, convert_direction(wind_record.direction))
        #theta.append(convert_direction(wind_record.direction))
        r = np.append(r, wind_record.speed)
        #r.append(wind_record.speed)
        colors = np.append(colors, record.reading)
        #colors.append(record.reading)

    r = np.sqrt(r)
    areas = (colors ** 2) / (colors ** 2).max() * 30
    ax = plt.axes(axe_location, projection = "polar")
    ax.set_xticks([])
    points = ax.scatter(theta, r, c = colors, s = areas, cmap = "plasma_r", alpha = 0.5)

def draw_polar_plot(sensor_index, chem_short, time_k):
    point = SENSOR_LOCATION[sensor_index]
    axe_location = cal_axe_location(point)
    #print axe_location

    draw_way_1(sensor_index, axe_location, chem_short, time_k)


def draw_sensors(ax, chem_short, time_k):
    for i in range(len(SENSOR_LOCATION)):
        point = SENSOR_LOCATION[i]
        circle = patches.Circle((point[0],point[1]), radius = POINT_RADIUS, color = 'r')
        ax.add_patch(circle)
        draw_polar_plot(i, chem_short, time_k)

def draw_company(ax):
    for k,v in COMPANY_LOCATION.items():
        circle = patches.Circle((v[0], v[1]), radius = POINT_RADIUS, color = 'b')
        ax.add_patch(circle)

def setup_main_ax():
    global MAIN_AXES_LEFT, MAIN_AXES_RIGHT, MAIN_AXES_TOP, MAIN_AXES_BOTTOM
    plt.figure(figsize=(WINDOW_WIDTH_IN_INCH, WINDOW_HEIGHT_IN_INCH), dpi=DPI)
    main_ax = plt.axes()
    main_ax.set_xlim(left = WINDOW_LEFT_MAP_X, right = WINDOW_RIGHT_MAP_X)
    main_ax.set_ylim(bottom = WINDOW_BOTTOM_MAP_Y, top = WINDOW_TOP_MAP_Y)

    '''
    Set the position of main axes to global variable
    '''
    main_position = main_ax.get_position()
    MAIN_AXES_LEFT = main_position.x0
    MAIN_AXES_BOTTOM = main_position.y0
    MAIN_AXES_RIGHT = main_position.x1
    MAIN_AXES_TOP = main_position.y1
    return main_ax

'''function for debugging'''
'''
found that the wind information between in 2016-08-01 and 2016-08-04 is partially missing
'''
def find_difference_between_two_records():
    for sensor_r in SensorRecord.all_records[1]["C"]:
        lst = [x for x in WindRecord.all_records if x.time == sensor_r.time]
        if len(lst) == 0:
            print sensor_r.time

'''The entry function for drawing'''
def draw_map_by_chem_month_and_save(suffix = "normal"):
    for time_k, time__v in TIME_INTERVAL.items():
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            main_ax = setup_main_ax()
            draw_sensors(main_ax, chem_k, time_k)
            draw_company(main_ax)
            plt.suptitle(time_k+" "+chem_v)
            plt.savefig('./plot/bar/'+chem_v+"_"+time_k+"_"+suffix+'.png')
            plt.close()

def draw_differentation_hist():
    for sensor_index in range(len(SENSOR_LOCATION)):
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            records = SensorRecord.all_records[sensor_index][chem_k]
            records_diff = []
            for i in range(1, len(records)):
                reading_diff = records[i].reading - records[i - 1].reading
                time_diff = (records[i].time - records[i - 1].time)
                if time_diff.total_seconds() == 0:
                    print "Error: repeated reading"
                    print "At", records[i].time, ", sensor", sensor_index + 1, ", ", chem_v
                    print "Readings:",records[i - 1].reading, records[i].reading
                else:
                    slope = reading_diff / (time_diff.total_seconds() / 3600.0)
                    records_diff.append(slope)
            plt.hist(records_diff, bins = 30, alpha = 0.3, label = chem_v)
        plt.ylim(0, 5)
        plt.title("Sensor "+str(sensor_index + 1))
        plt.legend()
        plt.show()

def draw_first_minus_second_diff_hist():
    for sensor_index in range(len(SENSOR_LOCATION)):
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            records = SensorRecord.all_records[sensor_index][chem_k]
            x = [r.time for r in records]
            y = [r.reading for r in records]
            dy = differentiate_y(x, y)
            d2y = differentiate_y(x, dy)
            dy = np.array(dy)
            d2y = np.array(d2y)
            judge = dy - d2y
            d_judge = differentiate_y(x,y)
            plt.hist(judge, bins = 50, alpha = 0.3, label = chem_v)
        plt.ylim(0, 5)
        plt.title("Sensor "+str(sensor_index + 1) +" first derivative - second derivative")
        plt.legend()
        #plt.show()
        plt.savefig('./plot/deri/'+"sensor_"+str(sensor_index + 1)+'.png')
        plt.close()

def eliminate_huge_change():
    for sensor_index in range(len(SENSOR_LOCATION)):
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            records = SensorRecord.all_records[sensor_index][chem_k]
            x = [r.time for r in records]
            y = [r.reading for r in records]
            dy = differentiate_y(x, y)
            d2y = differentiate_y(x, dy)
            dy = np.array(dy)
            d2y = np.array(d2y)
            judge_criteria = dy - d2y
            for i in range(len(judge_criteria)):
                if judge_criteria[i] > FIRST_MINUS_SECOND_THRESHOLD:
                    '''linear interporlation'''
                    records[i + 1].reading = (records[i].reading + records[i+2].reading)/2

def draw_all_differentation_hist():
    records_diff = []
    records_second_diff = []
    for sensor_index in range(len(SENSOR_LOCATION)):
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            records = SensorRecord.all_records[sensor_index][chem_k]
            for i in range(1, len(records)):
                reading_diff = records[i].reading - records[i - 1].reading
                time_diff = (records[i].time - records[i - 1].time)
                if time_diff.total_seconds() == 0:
                    print "Error: repeated reading"
                    print "At", records[i].time, ",sensor", sensor_index + 1, ",", chem_v
                    print "Readings:",records[i - 1].reading, records[i].reading
                else:
                    slope = reading_diff / (time_diff.total_seconds() / 3600.0)
                    records_diff.append(slope)
    for i in range(1, len(records_diff)):
        records_second_diff.append(records_diff[i] - records_diff[i-1])
    plt.hist(records_diff, bins = 100, alpha = 0.3, label = "first differentiation")
    plt.hist(records_second_diff, bins = 100, alpha = 0.3, label = "second differentiation")
    plt.ylim(0, 10)
    #plt.title("Sensor "+str(sensor_index + 1))
    plt.legend()
    plt.show()

'''
remove:
"None", do not remove any record;
"Larger", remove the larger one of repeated;
"Smaller", remove the smalled one of repeated.
"All": remove the both of the repeated
'''
def find_all_error_record(remove = "None"):
    assert(remove == "None" or remove == "Larger" or remove == "Smaller" or remove == "All")
    warning_count = 0
    for sensor_index in range(len(SENSOR_LOCATION)):
        for chem_k, chem_v in FULL_CHEM_NAME.items():
            records = SensorRecord.all_records[sensor_index][chem_k]
            records_to_be_removed = []
            for i in range(1, len(records)):
                this_r = records[i]
                last_r = records[i-1]
                time_diff = this_r.time - last_r.time
                reading_diff = this_r.reading - last_r.reading
                if time_diff.total_seconds() == 0:

                    '''find the last and the next normal records'''
                    last_normal = next_normal = []
                    last_time = next_time = this_r.time
                    while len(last_normal) != 1:
                        last_time = last_time - timedelta(hours = 1)
                        last_normal = [x for x in records if x.time == last_time]
                    last_normal = last_normal[0]
                    while len(next_normal) != 1:
                        next_time = next_time + timedelta(hours = 1)
                        next_normal = [x for x in records if x.time == next_time]
                    next_normal = next_normal[0]

                    '''calculate the linear_expectation'''
                    slope = (next_normal.reading - last_normal.reading) / (next_normal.time - last_normal.time).total_seconds()
                    linear_expectation = last_normal.reading + (this_r.time - last_normal.time).total_seconds() * slope

                    error_r = ErrorSensorRecord(
                        time=this_r.time,
                        sensor_index=sensor_index,
                        chem_k=chem_k,
                        value=[this_r.reading, last_r.reading],
                        error_t="multiple",
                        linear_expectation = linear_expectation
                    )
                    ErrorSensorRecord.all_records.append(error_r)

                    '''prepare for remove, only remove the repeated readings'''
                    if remove == "All":
                        records_to_be_removed.append(this_r)
                        records_to_be_removed.append(last_r)
                    elif remove == "Larger":
                        records_to_be_removed.append(max(this_r, last_r, key = lambda x: x.reading))
                    elif remove == "Smaller":
                        records_to_be_removed.append(min(this_r, last_r, key = lambda x: x.reading))

                if time_diff.total_seconds() != 0 and time_diff.total_seconds() != 3600 and time_diff.total_seconds() < 30*24*60*60:
                    '''find al missing data at 0:00 of a day'''

                    if this_r.time.hour == 1:
                        error_r = ErrorSensorRecord(
                            time=this_r.time - timedelta(hours = 1),
                            sensor_index=sensor_index,
                            chem_k=chem_k,
                            value=[],
                            error_t="missing",
                        )
                        ErrorSensorRecord.all_records.append(error_r)

                    ''' if missing data is at 23:00 or 01:00'''
                    if this_r.time.hour == 1 and time_diff.total_seconds() != 7200:
                        print "Warning!!"
                        warning_count += 1

                    ''' ignore the missing data at 00:00 '''
                    if this_r.time.hour != 1:
                        #print last_r.time, this_r.time
                        #print "time difference:", time_diff.total_seconds()/3600
                        missing_hours = int(time_diff.total_seconds()/3600)
                        for h in range(1, missing_hours):
                            linear_expectation = (reading_diff / time_diff.total_seconds()) * 3600 * h + last_r.reading
                            error_r = ErrorSensorRecord(
                                time=last_r.time + timedelta(hours=h),
                                sensor_index=sensor_index,
                                chem_k=chem_k,
                                value=[],
                                error_t="missing",
                                linear_expectation=linear_expectation
                            )
                            ErrorSensorRecord.all_records.append(error_r)
            '''after iteration, remove the records if told so'''
            if remove != "None":
                for record_to_be_remove in records_to_be_removed:
                    records.remove(record_to_be_remove)
    ErrorSensorRecord.sort_by_time()
    #ErrorSensorRecord.print_all()
    #print warning_count

def differentiate_y(x, y):
    dy = []
    for i in range(len(y)):
        if i == len(y) - 1:
            dy.append(0)
        else:
            dy.append((y[i+1] - y[i]) / ((x[i+1] - x[i]).total_seconds() / 3600.0))
    return dy

def plot_reading_vs_time(chem_k, sensor_index, start_time = TIME_INTERVAL["All"]["start"], end_time = TIME_INTERVAL["All"]["end"]):
    records = SensorRecord.all_records[sensor_index][chem_k]
    x = np.array([r.time for r in records])
    y = np.array([r.reading for r in records])
    dy = differentiate_y(x, y)
    d2y = differentiate_y(x, dy)
    plt.plot(x, y, label=FULL_CHEM_NAME[chem_k], alpha = 0.3)
    #plt.plot(x, dy, label=FULL_CHEM_NAME[chem_k]+"derivative", alpha = 0.3)
    #plt.plot(x, d2y, label=FULL_CHEM_NAME[chem_k]+" second derivative", alpha = 0.3)
    plt.legend()
    plt.xlabel("time")
    plt.ylabel("reading of sensor "+str(sensor_index + 1))

def analyze_error_record(records):
    '''input should be a list of ErrorSensorRecord'''
    times = [x.time for x in records]
    hours = [x.time.hour for x in records]

    '''analysis by month'''
    apr_count = len([x.time.month for x in records if x.time.month == 4])
    aug_count = len([x.time.month for x in records if x.time.month == 8])
    dec_count = len([x.time.month for x in records if x.time.month == 12])
    print "April:", apr_count
    print "August:", aug_count
    print "December:", dec_count
    '''analysis by hour'''
    x = []
    y = []
    for h in range(24):
        x.append(h)
        y.append(len([r for r in hours if r == h]))
    plt.plot(x, y)

    '''analysis by time'''
    '''
    plt.hist(hours, bins = 22)
    '''
    '''analysis by punchcard'''
    '''
    infos = {}
    for d in range(7):
        for h in range(24):
            infos[(d, h)] = 0
    for time in times:
        infos[(time.weekday(), time.hour)] += 1
    draw_punchcard(infos)
    plt.savefig("./error_punchcard.png")
    '''

def eliminate_sensor4_offset():
    sensor4_records = SensorRecord.all_records[4 - 1]
    for chem_k, chem_v in FULL_CHEM_NAME.items():
        for month_k, month_v in TIME_INTERVAL.items():
            if month_k == "All":
                continue
            start_time = month_v["start"]
            end_time = month_v["end"]
            records = [x for x in sensor4_records[chem_k] if x.time >= start_time and x.time <= end_time]
            min_r = min(records, key= lambda x: x.reading)
            min_reading = min_r.reading
            print min_r.reading
            for record in records:
                record.reading -= min_reading

def cal_linear_regression(x, y):
    x = np.array(x)
    y = np.array(y)
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y)[0]
    return m, c


def plot_linear_regression(sensor_index, chem_k):
    records = SensorRecord.all_records[sensor_index][chem_k]
    x = np.array([(r.time - datetime(year=2016, month=4, day=1)).total_seconds()/3600.0/24 for r in records])
    y = np.array([r.reading for r in records])
    m, c = cal_linear_regression(x, y)
    plt.plot(x, y, label='Original data of sensor ' + str(sensor_index + 1) + " for " + FULL_CHEM_NAME[chem_k])
    plt.plot(x, m*x + c, label='Fitted line of sensor ' + str(sensor_index + 1) + " for " + FULL_CHEM_NAME[chem_k])
    plt.legend()

def main():
    SensorRecord.read_all_data()
    WindRecord.read_all_data()
    WindRecord.linear_interpolation()
    '''
    draw_map_by_chem_month_and_save("original")
    '''
    find_all_error_record("All")
    #eliminate_huge_change()
    #eliminate_huge_change()
    eliminate_sensor4_offset()
    #plot_linear_regression(3, "A")
    plot_reading_vs_time("A", 3)
    #plot_reading_vs_time("G", 3)
    #plot_reading_vs_time("C", 3)
    #plot_reading_vs_time("M", 3)
    plt.show()


    '''plot all possibilities'''
    '''
    draw_map_by_chem_month_and_save("repeated_all_removed")
    eliminate_huge_change()
    draw_map_by_chem_month_and_save("repeated_all_removed_eliminate_once")
    eliminate_huge_change()
    draw_map_by_chem_month_and_save("repeated_all_removed_eliminate_twice")
    '''

    '''analyze the error record'''
    '''
    analyzed_records = [x for x in ErrorSensorRecord.all_records if x.error_t == "multiple"]
    analyze_error_record(analyzed_records)
    plt.show()
    '''
    #ErrorSensorRecord.print_all()
    #eliminate_huge_change()
    #eliminate_huge_change()
    #draw_first_minus_second_diff_hist()
    '''
    start_time = datetime(2016, 4, 1)
    end_time = datetime(2016, 5, 1)
    plot_reading_vs_time("M", 2, start_time, end_time)
    plt.show()
    '''
    #draw_map_by_chem_month_and_save("eliminate_once")
    #draw_differentation_hist()
    #WindRecord.print_all()
    #print len(SensorRecord.all_records[1]["C"])
    #print len(WindRecord.all_records)
    #find_difference_between_two_records()
    #pprint(sensor_data)

    #plt.show()

if __name__ == "__main__":
    main()
