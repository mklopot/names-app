#!/usr/bin/python

top = 8

import random
import math

global progress_max
global progress_points

def loadfile(filename = "names.txt"):
    global progress_max
    global progress_points
    f = open(filename)
    names = f.readlines()
    random.shuffle(names)

    length = len(names)
    k = math.floor(math.log(length,2)) + 1
    progress_max = 1 + k * length - 2 ** k
    #progress_max = length * math.ceil(math.log(length,2))       
    progress_points = 0

    return names

def ask_user(a, b):
    global progress_points
    print "Progress: " + str(progress_points) + " of at most " + str(progress_max)
    print "Which of these names do you like better?\nPress (1) or (2)\n1. " + a + "\n2. " + b
    i=0
    while not (i == "1") and not (i == "2"):
        i = raw_input('>')
    progress_points += 1
    return int(i) - 1

def merge(left, right):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if ask_user(left[i], right[j]):
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

def mergesort(lst):
    if len(lst) <= 1:
        return lst
    middle = int(len(lst) / 2)
    left = mergesort(lst[:middle])
    right = mergesort(lst[middle:])
    result = merge(left, right)
    if len(result) > top:
        result = result[-top:]
    return result

if __name__ == "__main__":

    names = loadfile()
    ranking = mergesort(names)
    print "Progress: " + str(progress_points) + "/" + str(progress_max)    
    print "Ranking (Worst to Best):"
    print len(ranking)
    print ranking
