#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

import sys
import codecs
import argparse

from io import open
argparse.open = open

from word_tree_subsub import subsub_unprocess_document

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="unprocess LVSEG segmentation")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input file (default: standard input)")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help="Output file (default: standard output)")
    parser.add_argument(
        '--marker1', '-m', type=str, default='9474', metavar='STR',
        help="Segmentation marker (default: '%(default)s'))")
    parser.add_argument(
        '--marker2', '-n', type=str, default='9553', metavar='STR',
        help="Uppercase marker (default: '%(default)s'))")
    return parser

if __name__ == '__main__':

    sys.stderr = codecs.getwriter('UTF-8')(sys.stderr.buffer)
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout.buffer)
    sys.stdin = codecs.getreader('UTF-8')(sys.stdin.buffer)

    parser = create_parser()
    args = parser.parse_args()

    # read/write files as UTF-8
    if args.input.name != '<stdin>':
        args.input = codecs.open(args.input.name, encoding='utf-8')
    if args.output.name != '<stdout>':
        args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

    subsub_unprocess_document(args.input,args.output,args.marker1,args.marker2)
