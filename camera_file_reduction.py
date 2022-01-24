#!/usr/bin/env python3

# This script prunes the external storage drive for old surveillence camera files

import re, time;
from datetime import datetime, tzinfo, timedelta, timezone;
from os import listdir;
from os.path import join;
from os.path import exists;
from sys import exit;
from influxdb import InfluxDBClient;

# debugging constants
debuglevel = 1

# paths
external_drive = "/media/external/cameras"
cameras = ["Camera1","Camera2"]

# influxdb connection
influxdb = InfluxDBClient(host="jane.maglab", port=8086)
influxdb.switch_database('maglab')

# global variables
cam_delta_dict = {}

for camera in cameras:
    # navigate down to the level where we see individual files
    # reversing the search finds the newest files rather than the oldest
    camera_dir = join(external_drive, camera);
    if (not exists(camera_dir)):
        print ("camera directory \"" + camera_dir + "\" does not exist!");
        exit(1);

    yearlist = listdir(camera_dir);
    if (not yearlist):
        print ("no years within camera directory \"" + camera_dir + "\"!");
        exit(1);
    yearlist.sort(reverse=True);
    # some "years" are actually FTP tests
    yr_index = 0;
    while (yearlist[yr_index][0].isalpha()):
        yr_index += 1;
        if (yr_index == len(yearlist)):
            print("no years within camera directory\"" + camera_dir + "\"!");
            exit(1);
    yearpath = join(camera_dir, yearlist[yr_index]);

    monthlist = listdir(yearpath);
    if (not monthlist):
        print ("no months within camera directory \"" + yearpath + "\"!");
        exit(1);
    monthlist.sort(reverse=True);
    monthpath = join(yearpath, monthlist[0]);

    daylist = listdir(monthpath);
    if (not daylist):
        print ("no days within camera directory \"" + daypath + "\"!");
        exit(1);
    daylist.sort(reverse=True);
    daypath = join(monthpath, daylist[0]);

    filename = listdir(daypath);
    filename.sort(reverse=True);
    if (not filename):
        print ("no files within camera directory \"" + datepath + "\"!");
        exit(1);
    if (debuglevel > 1):
        print("Latest filename is: \"" + filename[0] + "\"")
    pattern = re.compile("^(Camera\d)_\d{2}_(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\..{3}$");
    match = pattern.search(filename[0])
    if (not match):
        print("Match not found.  Something is wrong.")
        exit(1)
    groups = match.groups()

    camera_time = datetime(int(groups[1]), int(groups[2]), int(groups[3]), int(groups[4]),
        int(groups[5]), int(groups[6]), tzinfo=timezone(-timedelta(hours=8)));
    camera_timestamp = int(camera_time.astimezone(timezone.utc).timestamp())
    camera_delta = int(time.time()) - camera_timestamp
    if (debuglevel > 1):
        print("Camera time delta to current time: " + str(camera_delta))
    cam_delta_dict[camera] = camera_delta

body = [{
    "measurement": "cam_delta",
    "fields": cam_delta_dict
}]
if (debuglevel > 1):
    print(body)
influxdb.write_points(body)

if (debuglevel > 1):
    print("Success!")
exit(0);
