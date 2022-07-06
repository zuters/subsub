    #!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

""" Extract subsub segmentation model
"""

import sys
import argparse
#import time

#from io import open
argparse.open = open

from word_tree_subsub import subsub_learn
from tools.voc_tools import extract_frequent_vocabulary

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="learn subsub segmentation model")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input text (default: standard input)")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('wb'), default=sys.stdout,
        metavar='PATH',
        help="Output file for subsub model")
    parser.add_argument(
        '--bestendings', '-e', type=int, default=300,
        help="Rate of right substrings to become potential endings")
    parser.add_argument(
        '--maxforms', '-f', type=int, default=10,
        help="Maximum amount of right substrings for a stem to collect initial set of potential endings")
    return parser

if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.input.name != '<stdin>':
        args.input = open(args.input.name, 'r', encoding='utf-8')
    voc = extract_frequent_vocabulary(args.input,alphaonly=0,tolower=True,addwordend=False)
    subsub_learn(voc,args.output.name,args.maxforms,args.bestendings)
    