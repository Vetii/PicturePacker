#!/usr/bin/python

import re #regexes
import os #mkdir function
import sys #command line arguments
import math # ceil 
import argparse # parsing command line arguments

from wand.image import Image #image processing lib
from wand.color import Color #colors

# useful functions
def make_dirs(dirnames, prefix):
    os.chdir(prefix)
    for dirname in dirnames:
        os.mkdir(dirname)

def rotate_image(source, dest):
    if(source.width > source.height):
        if( dest.width < dest.height ):
            source.rotate(-90)

    elif(source.height > source.width):
        if(dest.height < dest.width):
            source.rotate(-90)

    return source

def resize_image(source, dest):
    return 0

def crop_and_save(source, dest):
# w_offset is 0 if dest > source
    w_offset = int(get_offset(source.width, dest.width))
    h_offset = int(get_offset(source.height, dest.height))
    cropped = []

    width = min(dest.width, source.width)
    height = min(dest.height, source.height)

# should be zero if dest > source
    maxX = source.width - width 
    maxY = source.height - height 

    i = 0
    xpos = 0
    while True:
        ypos = 0

        while True: 

            img = source[xpos:xpos + width, ypos:ypos + height]
            left = int(dest.width / 2 - img.width / 2)
            top  = int(dest.height / 2 - img.height / 2)
            dest.composite(img, left, top)
            dest.save(filename=str(dest.width) + 'x' + str(dest.height) + '-' + str(i) + '.' + args['format'])
            cropped.append(dest)
            i += 1
            ypos += h_offset
            if ypos >= maxY: break

        xpos += w_offset
        if xpos >= maxX: break


    return cropped


def get_offset(d_source, d_dest):
    numtimes = math.ceil(d_source / d_dest)
    return max((d_source - d_dest) / numtimes, 0)

def process(source, dests, rotable):
    for dest in dests:
        print(dest.width, dest.height)
        if rotable:
            img = rotate_image(source, dest)
        else:
            img = source
        crop_and_save(img,dest)

# main
dimfilter = re.compile('[0-9]+')
dirfilter = re.compile('\w+$')

# parse command line arguments.
parser = argparse.ArgumentParser(description='rotate & crop pictures to fit a set of sizes')
parser.add_argument('-c', '--conf',  metavar='file', type=str, default='dimensions', help='an alternative config file')
parser.add_argument('-b', '--back',  metavar='color', type=str, default='#fff', help='an alternative background color')
parser.add_argument('-f', '--format', metavar='img format', type=str, 
        default='jpg', help='output image format')
parser.add_argument('-r', '--rotable', action='store_true')

parser.add_argument('image', type=str)
args = vars(parser.parse_args(sys.argv[1:]))

print(args['conf'])
# open file.
f = open(args['conf'], 'r')

# build a list of tuples with dimensions
bases    = []
dirnames = []

#read each line and process
for line in f:
    x = dimfilter.findall(line)
    y = dirfilter.findall(line)
    if x != []:
        dirnames.append(y)
        bases.append( Image(background=Color(args['back']), width=int(x[0]), height=int(x[1]) ) ) 

source = Image(filename=args['image'])
process(source, bases, args['rotable'])
