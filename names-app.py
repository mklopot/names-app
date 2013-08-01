#!/usr/bin/python

import copy
import random
import math
import shelve
import sys
import logging
import os

LOGFORMAT = "%(levelname)s %(funcName)s: %(message)s"
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=LOGFORMAT)

def loadprofile(profile="default"):
    profile = shelve.open(profile, writeback=True) 
    if "initdataset" in profile:
        print "Loading saved profile..."
        global replay_sequence
        replay_sequence = copy.copy(profile["saved_sequence"])
        logging.debug("Loading saved sequence into replay sequence " + str(replay_sequence))
        return profile["initdataset"], profile
    else:
        print "Saved profile not found, initializing..."
        return createprofile(profile), profile 
   
def createprofile(profile="default", filename="names.txt"):
    global replay_sequence
    replay_sequence = []
    f = open(filename)
    names = f.readlines()
    random.shuffle(names)
    names = map(lambda x: x.rstrip(), names)
    length = len(names)
    os.system('clear')
    print "Loaded "+str(length)+ " entries to sort."

    top = raw_input("How long of a list of top names do you want?\nLonger list means more questions to answer.\nNot entering a setting here will create a Top 25 list by default.\n\n>") 
    if top.isdigit():
        top = int(top)
    else:
        top = 25

    if not (0 < top <= length):
        top = 25
    logging.debug("top set to " + str(top))
    print "Entries can be shown with a title, such as Mr. or Mrs., and other preceding names, e.g. if selecting a middle name, you can enter the first name here."
    prefix = raw_input("Preceding names and/or prefixes (Press ENTER for none) >")
    print "Entries can be shown with other names following, or suffixes, such as Jr., e.g. if selecting a first name, you can enter the last name here."
    suffix = raw_input("Names following and/or suffixes (Press ENTER for none) >")

    if prefix:
        profile["prefix"] = prefix + " "
    else:
        profile["prefix"] = ""

    if suffix:
        profile["suffix"] = " " + suffix
    else:
        profile["suffix"] = ""

    profile["top"] = top 
    profile["progress_points"] = 0
    profile["initdataset"] = names
    profile["saved_sequence"] = []
    logging.debug("Initializing replay sequence")

    k = math.floor(math.log(length,2)) + 1
    profile["progress_max"] = int(1 + k * length - 2 ** k)

    logging.debug("Worst-case number of comparisons: " + str(profile["progress_max"]))
    profile.sync()
    logging.info("Created a profile to select top " + str(profile["top"]) + " out of " + str(length) + " names")
    return names

def ask_user(a, b, profile):
    os.system('clear')
    print
    print "Progress: " + str(profile["progress_points"]) + " of less than " + str(profile["progress_max"])
    print
    print "Which of these names do you like better?\nEnter (1) or (2)\n\n1. " + profile["prefix"] + a + profile["suffix"] + "\n2. " + profile["prefix"] + b + profile["suffix"]
    print
    global replay_sequence
    i=None
    if replay_sequence:
        i = replay_sequence.pop(0)
        logging.debug("Replay said " + str(i))
    if i:
        while replay_sequence and i not in ["1", "2"]:
            i = replay_sequence.pop(0)
            logging.debug("Replay said " + str(i))
    else:
        i = raw_input('>')
        while i.lower() not in ["1", "2", "exit", "quit", "bye"]:
            print "Valid inpits are '1', '2', or 'exit'"
            i = raw_input('>')
        if i.lower() in ["exit", "quit", "bye"]:
            print "Saving and closing..."
            sys.exit()

        logging.debug("Saving your selection in the database")
        profile["saved_sequence"].append(i)
        logging.debug("Database replay sequence is now" + str(profile["saved_sequence"]))
        profile["progress_points"] += 1
        profile.sync()
    os.system('clear')
    return int(i) - 1


def merge(left, right, profile):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right) and len(result) < profile["top"]:
        if ask_user(left[i], right[j], profile):
            result.append(right[j])
            j += 1
        else:
            result.append(left[i])
            i += 1
    logging.debug("Result after first phase of merge: " + str(result))
    points = len(left) - i
    points += len(right) - j - 1
    if points > 0:
        logging.debug("Maximum required progress points reduced by " + str(points))
    profile["progress_max"] -= points

    if len(result) < profile["top"]:
        result += left[i:]
        result += right[j:]
    logging.debug("Appended merge result: " + str(result))
    return result

def mergesort(lst, profile):
    if len(lst) <= 1:
        return lst
    middle = int(len(lst) / 2)
    left = mergesort(lst[:middle],profile)
    right = mergesort(lst[middle:],profile)
    result = merge(left, right, profile)
    if len(result) > profile["top"]:
        result = result[:profile["top"]]
    return result

if __name__ == "__main__":
    names, profile = loadprofile("default")
    ranking = mergesort(names, profile)
    logging.debug("Done with progress showing " + str(profile["progress_points"]) + "/" + str(profile["progress_max"]))    
    print "Done!!!"
    print
    print "Top " + str(len(ranking)) + " (Best to Worse):"
    for i in enumerate(ranking):
        number, name = i
        print str(number+1)+".   " + name
    if os.path.exists("default"):
        os.remove("default")
    if os.path.exists("default"+".db"):
        os.remove("default"+".db")    

