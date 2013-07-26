#!/usr/bin/python

import random
import math
import shelve

global progress_max
global progress_points
global saved_responses
saved_responses = []
global top
top = 8

def loadprofile(profile="default"):
    profile = shelve.open(profile, writeback=True) 
    if "initsequence" in profile:
        print "Loading saved profile..."
        global saved_responses
        global progress_max
        global progress_points
        global top
        saved_responses = profile["saved_responses"]
        progress_max = profile["progress_max"]
        progress_points = profile["progress_points"]
        top = profile["top"]
        return profile["initsequence"], profile
    else:
        print "Saved profile not found, initializing..."
        return createprofile(profile), profile 
   

def createprofile(profile="default", filename="names.txt"):
    global progress_max
    global progress_points
    f = open(filename)
    names = f.readlines()
    random.shuffle(names)

    length = len(names)
    k = math.floor(math.log(length,2)) + 1
    progress_max = 1 + k * length - 2 ** k
    progress_points = 0

    profile["progress_points"] = progress_points
    profile["progress_max"] = progress_max
    profile["initsequence"] = names
    profile["saved_responses"] = []
    profile["top"] = top
    profile.sync()
    
    return names

def ask_user(a, b, profile=None):
    global progress_points
    print "Progress: " + str(progress_points) + " of at most " + str(progress_max)
    print a
    print b
    print "Which of these names do you like better?\nPress (1) or (2)\n1. " + a + "\n2. " + b
    i=0
    while not (i == "1") and not (i == "2"):
        i = raw_input('>')
    if profile:
        print "Saving your choice in the database"
        profile["saved_responses"].append(i)
        profile.sync()
        
    progress_points += 1
    return int(i) - 1

def merge(left, right, profile=None):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if ask_user(left[i], right[j], profile):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    global progress_points
    points = len(left) - i
    points += len(right) - j - 1
    print "Bonus progress: " + str(points)
#    progress_points += points

    result += left[i:]
    result += right[j:]
    
    return result

def mergesort(lst, profile=None):
    if len(lst) <= 1:
        return lst
    middle = int(len(lst) / 2)
    left = mergesort(lst[:middle],profile)
    right = mergesort(lst[middle:],profile)
    result = merge(left, right, profile)
    if len(result) > top:
        result = result[-top:]
    return result

if __name__ == "__main__":

    names, profile = loadprofile()
    ranking = mergesort(names, profile)
    print "Progress: " + str(progress_points) + "/" + str(progress_max)    
    print "Top " + str(len(ranking)) + " (Worst to Best):"
    print ranking
