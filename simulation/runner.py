#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2009-2023 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

def numberv(lane):
    nb = 0
    for _ in traci.lane.getLastStepVehicleIDs(lane):
        nb += 1
    return nb

def getLaneVehicleCount(lane):
    vehicles = list(s[:-4] for s in traci.lane.getLastStepVehicleIDs(lane))
    return list(vehicles.count("car_top"), vehicles.count("bicycle_top"), vehicles.count("truck_top"), vehicles.count("bus_top"))

def getSignalDuration(road):
    vehicle_count_list_0 = getLaneVehicleCount(road + "_0")
    vehicle_count_list_1 = getLaneVehicleCount(road + "_1")
    vehicle_count_list_2 = getLaneVehicleCount(road + "_2")
    vehicle_count_list = [sum(x) for x in zip(vehicle_count_list_0, vehicle_count_list_1, vehicle_count_list_2)]
    cars = vehicle_count_list[0]
    bicycle = vehicle_count_list[1]
    truck = vehicle_count_list[2]
    bus = vehicle_count_list[3]
    gst = ((cars * 6.325) + (bicycle * 5.774) + (truck * 5.547) + (bus * 5.774))/3
    return (gst * 100)

def run():
    step = 0
    next_timer = 1000                                # 10 seconds timer for even phases
    phase = 0
    traci.trafficlight.setPhase("center", phase)
    roads = ["t2c", "r2c", "d2c", "l2c"]

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        next_phase = (phase + 1) % 4
        count = next_timer
        next_timer = getSignalDuration(next_phase)
        print("Current Phase: {}, Duration: {}".format(phase, count//100))
        while count > 0:
            traci.trafficlight.setPhase("center", phase)
            count -= 1
        phase = next_phase

        step += 1

    traci.close()
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')


    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/intersection1.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()