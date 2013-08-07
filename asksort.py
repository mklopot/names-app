#!/usr/bin/python

""" This module adapts a sorting algorithm to applications where a user is asked
    to make the comparisons that drive the algorithm. 
"""

import math
import sys
import logging
import os

LOGFORMAT = "%(levelname)s %(funcName)s: %(message)s"
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=LOGFORMAT)

class Mergesort():
    """ An instance of this class represents a sort in progress. 
        The instance is created with the sequence to be sorted,
        and optionally, if not the entire sequence needs to be ranked,
        the top N items that are desired.

        >>> sorter = Mergesort(['Munster', 'Cheddar', 'Stilton', 'Brie', 'Mozzarella'], 3)

        The pending selection can be obtained like this:
  
        >>> sorter.get_selections()
        ('Munster', 'Cheddar')

        Tracking progress:

        >>> sorter.progress
        0
        >>> sorter.percent_done()
        0

        Making a selection (since this is mergesort, processing a selection is a merge operation):

        >>> sorter.merge('Munster')

        Providing input that is not part of the selection does nothing:

        >>> sorter.get_selections()
        ('Stilton', 'Brie')
        >>> sorter.merge('Edam')
        >>> sorter.get_selections()
        ('Stilton', 'Brie')

        Continue on with mergesort until the sorted sequence of Top N items is returned:

        >>> sorter.merge('Brie')
        >>> sorter.merge('Brie')
        >>> sorter.merge('Munster')
        >>> sorter.merge('Stilton')
        >>> sorter.merge('Brie')
        >>> sorter.merge('Mozzarella')
        ['Brie', 'Mozzarella', 'Munster']

        Top three best cheeses are returned.
    """

    def __init__(self, initsequence, top=25):
        self.sequence = initsequence
        self.level = 1
        self.counter = 0
        self.mergeresult = []
        self.premerge_left = [self.sequence[0]]
        self.premerge_right = [self.sequence[1]]
        self.top = top
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
        logging.debug("Level counter is "+str(self.level)+", index counter is "+str(self.counter))
        if self.level >= len(self.sequence):
            logging.debug("The level counter is already greater or equal to sequence length, returning sorted sequence and exiting")
            return self.sequence
        logging.debug("First pre-merge sequence " + str(self.premerge_left))
        logging.debug("Second pre-merge sequence " + str(self.premerge_right))
        logging.debug("Attempting a merge...")
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
            i = self.counter * self.level
            self.sequence[i:i+2*self.level] = self.mergeresult
            self.mergeresult = []
            logging.debug("Main sequence updated to "+str(self.sequence))
            if i < len(self.sequence):
                self.counter += 2
                logging.debug("Counter incremented to "+str(self.counter))
                self.premerge_left = self.sequence[self.counter*self.level:(self.counter+1)*self.level]
                self.premerge_right = self.sequence[(self.counter+1)*self.level:(self.counter+2)*self.level]
                logging.debug("Loaded new pre-merge sequences: "+str(self.premerge_left)+" and "+str(self.premerge_right))
            if self.counter*self.level >= len(self.sequence) and self.level < len(self.sequence):
                self.level *= 2
                logging.debug("Incrementing level, now set to "+str(self.level))
                self.counter = 0
                logging.debug("Counter reset to zero")
                self.premerge_left = self.sequence[self.counter*self.level:(self.counter+1)*self.level]
                self.premerge_right = self.sequence[(self.counter+1)*self.level:(self.counter+2)*self.level]
                logging.debug("Loaded new pre-merge sequences: "+str(self.premerge_left)+" and "+str(self.premerge_right))
            if self.level >= len(self.sequence):
                logging.debug("The level counter is now greater or equal to sequence length, returning sorted sequence and exiting")
                return self.sequence

if __name__ == "__main__":
    import doctest
    doctest.testmod()
