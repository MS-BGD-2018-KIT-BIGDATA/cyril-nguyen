#!/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

"""Mimic pyquick exercise -- optional extra exercise.
Google's Python Class

Read in the file specified on the command line.
Do a simple split() on whitespace to obtain all the words in the file.
Rather than read the file line by line, it's easier to read
it into one giant string and split it once.

Build a "mimic" dict that maps each word that appears in the file
to a list of all the words that immediately follow that word in the file.
The list of words can be be in any order and should include
duplicates. So for example the key "and" might have the list
["then", "best", "then", "after", ...] listing
all the words which came after "and" in the text.
We'll say that the empty string is what comes before
the first word in the file.

With the mimic dict, it's fairly easy to emit random
text that mimics the original. Print a word, then look
up what words might come next and pick one at random as
the next work.
Use the empty string as the first word to prime things.
If we ever get stuck with a word that is not in the dict,
go back to the empty string to keep things moving.

Note: the standard python module 'random' includes a
random.choice(list) method which picks a random element
from a non-empty list.

For fun, feed your program to itself as input.
Could work on getting it to put in linebreaks around 70
columns, so the output looks better.

"""

import random
import sys


def build_mimic_dict(filename):
    """Returns mimic dict mapping each word to list of words which follow
    it."""
    mimic_dict = {}
    file = open(filename, "rU")
    string_file = file.read()
    string_file = string_file.replace("\n", " ")
    file_words = string_file.split()
    previous_word = ""
    for i in range(len(file_words)):
        current_word = file_words[i].lower()
        append_a_word_to_mimic(mimic_dict, previous_word, current_word)
        previous_word = current_word
    append_a_word_to_mimic(mimic_dict, previous_word, current_word)
    # for key, value in mimic_dict.items():
    #     print(key, " --> ", value)
    # print(string_file)
    return mimic_dict


def append_a_word_to_mimic(mimic_dict, previous_word, current_word):
    """Given a dict and two consecutive words, add the words couple
    to the dict"""
    if previous_word not in mimic_dict:
        mimic_dict[previous_word] = [current_word]
    else:
        mimic_dict[previous_word].append(current_word)


def print_mimic(mimic_dict, word):
    """Given mimic dict and start word, prints 200 random words."""
    line = ""
    previous_word = word
    for i in range(10000):
        previous_word = random.choice(mimic_dict[previous_word])
        line = line + previous_word + " "
        if len(line) > 200:
            print(line)
            line = ""
            previous_word = ""


# Provided main(), calls mimic_dict() and mimic()
def main():
    if len(sys.argv) != 2:
        print('usage: ./mimic.py file-to-read')
        sys.exit(1)

    dict = build_mimic_dict(sys.argv[1])
    print_mimic(dict, '')


if __name__ == '__main__':
    main()