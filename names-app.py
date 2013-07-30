#!/usr/bin/python

import copy
import random
import math
import shelve
import sys
import logging

LOGFORMAT = "%(levelname)s %(funcName)s: %(message)s"
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOGFORMAT)

global replay_sequence
replay_sequence = []

def loadprofile(profile="default"):
    profile = shelve.open(profile, writeback=True) 
    if "initdataset" in profile:
        print "Loading saved profile..."
        global progress_points
        global replay_sequence
        replay_sequence = copy.copy(profile["saved_sequence"])
        logging.debug("Loading saved sequence into replay sequence " + str(replay_sequence))
        progress_points = profile["progress_points"]
  
        return profile["initdataset"], profile
    else:
        print "Saved profile not found, initializing..."
        return createprofile(profile), profile 
   

def createprofile(profile="default", filename="names.txt"):
    global progress_points
    global replay_sequence

    f = open(filename)
    names = f.readlines()
    random.shuffle(names)
    names = map(lambda x: x.rstrip(), names)
    profile["top"] = 10
    profile["progress_points"] = 0
    
    profile["initdataset"] = names
    profile["saved_sequence"] = []
    logging.debug("Initializing replay sequence")


    length = len(names)
    k = math.floor(math.log(length,2)) + 1
    profile["progress_max"] = int(1 + k * length - 2 ** k)
    logging.debug("Worst-case number of comparisons: " + str(profile["progress_max"]))
    profile.sync()
    print "Created a profile to select top " + str(top) + " out of " + str(length) + " names"
    
    return names

def replay():
    global replay_sequence
    logging.debug("replay_sequence is " + str(replay_sequence))
    if replay_sequence:
        yield replay_sequence.pop(0)
    else:
        yield None

def ask_user(a, b, profile):
    global progress_points
    print
    print 17 * "_"
    print
    print "Progress: " + str(profile["progress_points"]) + " of less than " + str(profile["progress_max"])
    print "Which of these names do you like better?\nPress (1) or (2)\n1. " + a + "\n2. " + b
    i=0
    i = next(replay())
    logging.debug("Replay said " + str(i))
    if i:
        while i and i not in ["1", "2"]:
            i = next(repay())
            logging.debug("Replay said " + str(i))
    else:
        i = raw_input('>')
        while i not in ["1", "2"]:
            i = raw_input('>')

        logging.debug("Saving your selection in the database")
        profile["saved_sequence"].append(i)
        logging.debug("Database replay sequence is now" + str(profile["saved_sequence"]))
        profile["progress_points"] += 1
        profile.sync()
    return int(i) - 1


def merge(left, right, profile):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if ask_user(left[i], right[j], profile):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    global progress_max
    points = len(left) - i
    points += len(right) - j - 1
    if points > 0:
        print "BONUS!!! " + str(points) + " Progress Points!!!"
    profile["progress_max"] -= points

    result += left[i:]
    result += right[j:]
    
    return result

def mergesort(lst, profile):
    if len(lst) <= 1:
        return lst
    middle = int(len(lst) / 2)
    left = mergesort(lst[:middle],profile)
    right = mergesort(lst[middle:],profile)
    result = merge(left, right, profile)
    if len(result) > profile["top"]:
        result = result[-profile["top"]:]
    return result

if __name__ == "__main__":

    names, profile = loadprofile()
    ranking = mergesort(names, profile)
    print "Progress: " + str(progress_points) + "/" + str(progress_max)    
    print "Top " + str(len(ranking)) + " (Worst to Best):"
    print ranking
