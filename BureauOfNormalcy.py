#!/usr/bin/python3

# Title: BureauOfNormalcy.py
# Date Began: 11:12 AM 11/30/2021
# Date Last Updated: 9:49 AM 12/2/2021
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

import sys, argparse, re, csv, datetime, ftfy, logging
from dateutil.tz import gettz
from dateutil.parser import parse

def fix_this(oddData, datatype):
# Convert & "fix" UTF-8
    try:
        fixedData = ftfy.fix_text(oddData)
    except BaseException as errorvalue:
        logging.error("Error normalizing data " + oddData + " - " + errorvalue)
        raise
    if (datatype == "timestamp"):
        normal_date = datetime.datetime.combine(datetime.datetime.now(),
            datetime.time(0, tzinfo=gettz("America/Los_Angeles")))
        normal_tz = gettz("America/New_York")
        try:
            return parse(fixedData, default=normal_date).astimezone(normal_tz)
        except BaseException as errorvalue:
            logging.error( "Error parsing Timestamp: " + str(errorvalue))
            raise
    elif (datatype == "zip"):
        try:
            return int(("00000" + fixedData)[-5:])
        except BaseException as errorvalue:
            logging.error( "Error parsing ZIP code" + fixedData + " :" +
                           str(errorvalue))
            raise
    elif (datatype == "fullname"):
        try:
            return str(fixedData).upper()
        except BaseException as errorvalue:
            logging.error( "Wrong value for FullName " + fixedData +
                           " (expected String): " + str(errorvalue))
            raise
    elif (datatype == "fooduration" or
          datatype == "barduration"):
        try:
            hh, mm, sec = fixedData.split(':')
            return float(hh) * 3600 + float(mm) * 60 + float(sec)
        except BaseException as errorvalue:
            logging.error('Expected data in H:MM:SS.MS, received: ' +
                fixedData + " :" + errorvalue)
            raise
    else:
        return fixedData

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="The input file to be normalized")
parser.add_argument("outputfile", help="The name for the output file to be " +
                                       "written")
parser.add_argument("-l","--loglevel", help="The level of logging to use",
                    default="Debug", choices=["Debug", "Info", "Warning",
                                              "Error", "Critical"])
args = parser.parse_args()
inputfile = args.inputfile
outputfile = args.outputfile
logging.basicConfig(filename="BureauOfLogging.txt",
                    format='%(asctime)s [%(levelname)s]: %(message)s',
                    level=args.loglevel.upper())

# Open & read the input - would prefer to do this as a stream for larger sets
with open(inputfile, mode='r', encoding="utf8", errors="ignore") as csvfile:
    oddity = csv.DictReader(csvfile)
    normalrows = []
    oddFields = oddity.fieldnames
    for csvrow in oddity:
        normalrow = {}
        for key in oddFields:
            try:
                if (key.lower() == "totalduration"):
                    normalrow[key] = (fix_this(csvrow["FooDuration"],
                                    "fooduration") +
                                    fix_this(csvrow["BarDuration"],
                                    "barduration"))
                else:
                    normalrow[key] = fix_this(csvrow[key],key.lower())
            except:
                continue
        normalrows.append(normalrow)

with open(outputfile, mode='w',encoding='utf-8') as normalcsvfile:
    normality = csv.DictWriter(normalcsvfile,fieldnames=oddFields)
    normality.writeheader()
    normality.writerows(normalrows)