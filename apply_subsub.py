    #!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Jānis Zuters

""" Segment document using obtained splitting scheme
"""

import sys
import argparse

#from io import open
argparse.open = open

from word_tree_subsub import subsub_load,subsub_segment_document

def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="learn LVSEG main-forms")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help="Input corpus (default: standard input)")
    parser.add_argument(
        '--segmodel', '-s', type=argparse.FileType('rb'),
        metavar='PATH',
        help="Learned segmentation vocabulary.")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help="Output file for segmented corpus (default: standard output)")
    parser.add_argument(
        '--marker1', '-m', type=str, default='9474', metavar='STR',
        help="Segmentation marker (default: '%(default)s'))")
    parser.add_argument(
        '--marker2', '-n', type=str, default='9553', metavar='STR',
        help="Uppercase marker (default: '%(default)s'))")
    parser.add_argument(
        '--wordocc', '-w', type=float, default=1.0,
        help="Word occurrence rate to suppress segmentation")
    return parser

if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.input.name != '<stdin>':
        args.input = open(args.input.name, 'r', encoding='utf-8')
    if args.output.name != '<stdout>':
        args.output = open(args.output.name, 'w', encoding='utf-8')

    nnn,endcontext,paircontext,endsuffixes2,endsuffixes2x = subsub_load(args.segmodel.name)
    subsub_segment_document(args.input, args.output,
                            nnn, endcontext, paircontext, endsuffixes2, endsuffixes2x,
                            args.marker1, args.marker2,
                            args.wordocc)
    nnn.clean()
