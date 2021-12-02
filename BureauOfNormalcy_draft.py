#!/usr/bin/python3

# Title: BureauOfNormalcy.py
# Date Began: 11:12 AM 11/30/2021
# Author: Ilde Senesence
# Keywords: normalizer, csv, example, assignment
# Description: python based script to normalize csv files, repair UTF encoding,
#   validate data on preassigned parameters
# Depends: Python 3.9+, ftfy, dateutil.tz, dateutil.parser, logging
#
# Future State:
# Consider asyncio, aiofiles, pandas for future inputs if this needs to be 
#   web-based, use large inputs, or both
# Consider charset-normalizer if inputs need to be converted to UTF-8 from
#   unknown

import sys, re, csv, datetime, dateutil.tz, dateutil.parser, ftfy

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])

    except getopt.GetoptError:
        print('bureauofnormalcy.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('bureauofnormalcy.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

def get_seconds(duration_str):
    if re.search( "\d{2}:\d{2}:\d{2}(\.\d+|\b)" , duration_str ):
        hh, mm, sec = duration_str.split(':')
        return int(hh) * 3600 + int(mm) * 60 + int(sec)
    else:
        raise ValueError('Expected data in HH:MM:SS.MS, received: ' +
            duration_str)

# This could probably be a function combined with the Timestamp block
normal_date = datetime.datetime.combine(datetime.datetime.now(),
    datetime.time(0, tzinfo=dateutil.tz.gettz("America/Los_Angeles")))
normal_tz = dateutil.tz.gettz("America/New_York")

# Open & read the input - would prefer to do this as a stream for larger sets
with open(inputfile, newline='',encoding='utf-8') as csvfile:
    oddity = csv.DictReader(csvfile)
    oddFields = oddity.keys()
    with open(outputfile, mode='x',encoding='utf-8',errors='strict') as \
        normalcsvfile:

# Explicitly pulling along "unsafely assumed" fields
        normality = csv.DictWriter(normalcsvfile,fieldnames=oddFields)
        normality.writeheader()
        for csvrow in oddity:

# Convert & "fix" UTF-8
            oddTimestamp = fix_text(csvrow['Timestamp'])
            oddFooDuration = fix_text(csvrow['FooDuration'])
            oddBarDuration = fix_text(csvrow['BarDuration'])

# From here, invalid formatting by UTF should send an error
# Convert to Eastern, assume Pacific
            try:
                normalTimestamp = dateutil.parse(oddTimestamp,
                    default=normal_date).astimezone(normal_tz)
            except ParserError as errorvalue:
                sys.stderr.write( "Error parsing Timestamp:" +
                    str(errorvalue))
                continue

# Unicode validation only, preserve quotes
            normalAddress = fix_text(csvrow['Address'])

# Pad from beginning with 0s
            try:
                normalZIP = int(("00000" + fix_text(csvrow['ZIP']))[-5:])
            except ValueError as errorvalue:
                sys.stderr.write( "Wrong value type for ZIP code:" +
                    str(errorvalue))
                continue
            except ParserError as errorvalue:
                sys.stderr.write( "Error parsing ZIP code after UTF " +
                    "normalization:" + str(errorvalue))
                continue

# To Uppercase (beware CJK characters)
            try:
                normalFullName = fix_text(csvrow['FullName']).upper()
            except TypeError as errorvalue:
                sys.stderr.write( "Wrong value for FullName (expected " +
                    "String): " + str(errorvalue))
                continue

# HH:MM:SS.MS to TotalSeconds
            try:
                normalFooDuration = get_seconds(oddFooDuration)
                normalBarDuration = get_seconds(oddBarDuration)
            except UnicodeError as errorvalue:
                sys.stderr.write( "Error decoding Duration from UTF-8:" +
                    str(errorvalue))
            except ValueError as errorvalue:
                sys.stderr.write( "Error parsing Duration:" + str(errorvalue))

# Sum of FooDuration and BarDuration
            normalTotalDuration = normalFooDuration + normalBarDuration

# Unmodified BUT invalid UTF-8 characters to be replaced with Unicode
#   Replacement Character
            normalNotes = csvrow['Notes'].decode("utf-8", "replace")

# Construct output line from normalized known fields and all unknown fields
            normalRow = {}
            for key in oddity.keys():
                if (key.lower() == "timestamp"):
                    normalRow[key] = normalTimestamp
                elif (key.lower() == "address"):
                    normalRow[key] = normalAddress
                elif (key.lower() == "zip"):
                    normalRow[key] = normalZIP
                elif (key.lower() == "fullname"):
                    normalRow[key] = normalFullName
                elif (key.lower() == "fooduration"):
                    normalRow[key] = normalFooDuration
                elif (key.lower() == "barduration"):
                    normalRow[key] = normalBarDuration
                elif (key.lower() == "totalduration"):
                    normalRow[key] = normalTotalDuration
                elif (key.lower() == "notes"):
                    normalRow[key] = normalNotes
                else:
                        normalRow[key] = oddity[key]
# For use when 3.10+ python is easier to use/install
#                match key:
#                    case "Timestamp":
#                        normalRow[key] = normalTimestamp
#                    case "Address":
#                        normalRow[key] = normalAddress
#                    case "ZIP":
#                        normalRow[key] = normalZIP
#                    case "FullName":
#                        normalRow[key] = normalFullName
#                    case "FooDuration":
#                        normalRow[key] = normalFooDuration
#                    case "BarDuration":
#                        normalRow[key] = normalBarDuration
#                    case "TotalDuration":
#                        normalRow[key] = normalTotalDuration
#                    case "Notes":
#                        normalRow[key] = normalNotes
#                    case _:
#                        normalRow[key] = oddity[key]

# Time to actually write
            normality.writeRow(normalRow)
