import string
from Bio import Alphabet
COUNT = 1
FREQ = 2
##################################################################
# A class to handle frequency tables
# Copyright Iddo Friedberg idoerg@cc.huji.ac.il
# Biopython (http://biopython.org) license applies
# Methods to read a letter frequency or a letter count file:
# Example files for a DNA alphabet:
#
# A count file (whitespace seperated):
#
# A  50
# C  37
# G  23
# T  58
#
# The same info as a frequency file:
#
# A 0.2976
# C 0.2202
# G 0.1369
# T 0.3452
# 
# Functions:
#   read_count(f): read a count file from stream f. Then convert to
#   frequencies
#   read_freq(f): read a frequency data file from stream f. Of course, we then
#   don't have the counts, but it is usually the letter frquencies which are
#   interesting.
#
# Methods:
#   (all internal)
# Attributes:
#   alphabet: The IUPAC alphabet set (or any other) whose letters you are
#   using. Common sets are: IUPAC.protein (20-letter protein),
#   IUPAC.unambiguous_dna (4-letter DNA). See Bio/alphabet for more.
#   data: frequency dictionary.
#   count: count dictionary. Empty if no counts are provided.
#
# Example of use:
#   >>> from SubsMat import FreqTable
#   >>> ftab = FreqTable.FreqTable(my_frequency_dictionary,FreqTable.FREQ)
#   >>> ftab = FreqTable.FreqTable(my_count_dictionary,FreqTable.COUNT)
#   >>> ftab = FreqTable.read_count(open('myDNACountFile'))
#
#  
##################################################################
class FreqTable(dict):
    
    def _freq_from_count(self):
        sum = 0.
        for i in self.count.values():
            sum = sum + i
        for i in self.count.keys():
            self[i] = self.count[i] / sum

    def _alphabet_from_input(self):
        s = ''
        letters_list = self.keys()
        letters_list.sort()
        for i in letters_list:
            s = s + i
        return s

    def __init__(self,in_dict,dict_type,alphabet=None):
        self.alphabet = alphabet
        if dict_type == COUNT:
            self.count = in_dict
            self._freq_from_count()
        elif dict_type == FREQ:
            self.count = {}
            self.update(in_dict)
        else:
            raise ValueError,"bad dict_type"
        if not alphabet:
            self.alphabet = Alphabet.Alphabet()
            self.alphabet.letters = self._alphabet_from_input()

def read_count(f):
    l = map(string.split,map(string.strip,f.readlines()))
    count = {}
    for i in l:
        count[i[0]] = int(i[1])
    freq_table = FreqTable(count,COUNT)
    return freq_table

def read_freq(f):
    freq_dict = {}
    l = map(string.split,map(string.strip,f.readlines()))
    for i in l:
        freq_dict[i[0]] = float(i[1]) 
    return FreqTable(freq_dict,FREQ)

