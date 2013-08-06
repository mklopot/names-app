#!/usr/bin/python

import copy
import random
import math
import shelve
import sys
import logging
import os

LOGFORMAT = "%(levelname)s %(funcName)s: %(message)s"
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=LOGFORMAT)

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

    top = raw_input("By default, a Top 25 list will be created.\nIf you want a different number, enter it here.\nOhterwise, please press ENTER\n>") 
    if top.isdigit():
        top = int(top)
    else:
        top = 25

    if not (0 < top <= length):
        top = 25
    logging.debug("top set to " + str(top))
    print "Selections can be shown with an optional title, such as Mr. or Mrs.,\nor other names preceding it.\nFor example, if selecting a middle name, you can enter the first name here.\n"
    prefix = raw_input("(Press ENTER for none) >")
    print "Selections can be displayed with other names following, or any suffixes, such as Jr. or III.\nIf selecting a first name, you can enter the last name here.\n"
    suffix = raw_input("(Press ENTER for none) >")

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
    print "Which of these names do you like better?\nEnter (1) or (2), or (f) to fail both selections.\n\n1. " + profile["prefix"] + a + profile["suffix"] + "\n2. " + profile["prefix"] + b + profile["suffix"]
    print
    global replay_sequence
    i=None
    if replay_sequence:
        i = replay_sequence.pop(0)
        logging.debug("Replay said " + str(i))
    if i:
        while replay_sequence and i not in ["1", "2", "f", "flush"]:
            i = replay_sequence.pop(0)
            logging.debug("Replay said " + str(i))
    else:
        i = raw_input('>')
        while i.lower() not in ["1", "2", "f", "flush", "exit", "quit", "bye"]:
            print "Valid inpits are '1', '2', 'f', or 'exit'"
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
    if i in ["f", "flush"]:
        return "f"
    else:
        return int(i) - 1


def merge(left, right, profile):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right) and len(result) < profile["top"]:
        input = ask_user(left[i], right[j], profile)
        if input == "f":
            return result
        else:
            if input:
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

class Mergesort():
    def __init__(self, initsequence, profile):
        self.sequence = initsequence
        self.profile = profile
        self.level = 1
        self.counter = 1
        self.mergeresult = []
        self.premerge_left = [self.sequence[0]]
        self.premerge_right = [self.sequence[1]]
        self.progress = 0

        length = len(self.sequence)
        k = math.floor(math.log(length,2)) + 1
        self.max_progress = int(1 + k * length - 2 ** k)

    def percent_done(self):
        return int(math.floor(100 * self.progress / self.max_progress))
    
    def get_selections(self):
        return (self.premerge_left[0], self.premerge_right[0])
        
    def merge(self, choice):
        logging.debug("Called with choice="+str(choice))
        logging.debug("Sequence is "+str(self.sequence))
        logging.debug("First pre-merge sequence " + str(self.premerge_left))
        logging.debug("Second pre-merge sequence " + str(self.premerge_right))
        logging.debug("Level counter is "+str(self.level)+", index counter is "+str(self.counter))
        logging.debug("Merging...")
        if choice == self.premerge_left[0]:
            self.mergeresult.append(self.premerge_left.pop(0))
        elif choice == self.premerge_right[0]:
            self.mergeresult.append(self.premerge_right.pop(0))
        logging.debug("Merge result list is "+str(self.mergeresult))
        if self.premerge_left == [] or self.premerge_right == []:
            logging.debug("One of the pre-merge queues is empty, extending the merge result to include the other one")
            self.mergeresult.extend(self.premerge_left)
            self.mergeresult.extend(self.premerge_right)
            logging.debug("Merge result is now "+str(self.mergeresult))
            i = 2 * self.counter * self.level
            self.sequence[i:i+self.level] = self.mergeresult
            logging.debug("Main sequence updated to "+str(self.sequence))
            if i < len(self.sequence):
                self.counter += 1
                logging.debug("Incremented the counter, now set to "+str(self.counter))
                self.premerge_left = self.sequence[2*(self.counter-2)*self.level:2*(self.counter-1)*self.level]
                self.premerge_right = self.sequence[2*(self.counter-1)*self.level:2*(self.counter)*self.level]
                logging.debug("Loaded new pre-merge sequences: "+str(self.premerge_left)+" and "+str(self.premerge_right))
            elif i == len(self.sequence) and level < len(self.sequence):
                self.level *= 2
                self.counter = 1
            elif level >= len(sequence):
                return self.sequence

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

