#!/usr/bin/python

import pydemod.app.rds as rds
import argparse


parser = argparse.ArgumentParser(description='Generates RDS bitstreams, or RDS baseband samples')

parser.add_argument("--ps", type=str, default="PyDemod", help='Program Service Name')
parser.add_argument("--pi", type=str, default="FFFF", help='PI code')
parser.add_argument("--len", type=int, default=2, help='Duration in seconds')
parser.add_argument("--bitstream", help='Generates a bitstream', action="store_true")
parser.add_argument("--baseband", help='Generates basedband samples at 228 kHz', action="store_true")

args = parser.parse_args()

bitstream = rds.bitstream(rds.generate_basic_wordstream(int(args.pi, 16), args.ps), args.len)

if args.bitstream:
    print("".join(map(str, bitstream)))
else:
    print("Either --bitstream or --baseband must be provided.")
