#!/usr/bin/env python3

'''
Intended for use with HeroDesigner.

This script takes in an XML file and converts any non-TAIL text, attributes, and nodes and converts
them into another format, with the ability to restore it to valid XML; and vice versa.

It ignores pretty much everything about XML that isn't currently being used by HeroDesigner, so
TAIL text, namespaces, and so on will all be lost. Do not use this with production data.
'''

import argparse

from hero.parse import parse, serialize

__VERSION__ = "0.2.0"


def main(filename, input_format="hdt", output_format="yaml"):
    '''
    Checks for command-line arguments and then performs the requested conversion,
    returning the result as a string (which can then be piped into a file if desired,
    or just looked at.
    '''

    data = parse(open(filename, 'rb'), input_format)
    output = serialize(data, output_format)
    print(output)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-format", "-i", default="hdt", help="hdt|yaml")
    parser.add_argument("--output-format", "-o", default="yaml", help="hdt|yaml")
    parser.add_argument("filename", help="the file to be used as input")
    args = parser.parse_args()

    main(args.filename, args.input_format, args.output_format)
