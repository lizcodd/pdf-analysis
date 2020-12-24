#!/usr/bin/python3
# xml2csv.py

import os
import sys
from bs4 import BeautifulSoup
import csv
from glob import glob
import re
from langdetect import detect

# Print usage instructions
def printUsage():
    print("Usage: python3 xml2csv.py <input_path> <output_path> [output_filename]")
    print("e.g. To parse xmls in papers and output summary.csv in the current dir:")
    print("python3 xml2csv.py papers .")

# Handle getting text - return NA for non-existant/empty elements
def getTextOrNA(elt):
    if elt and elt.getText():
        return elt.getText().strip()
    else:
        return "NA"

# Detect the language from the element text - or return NA if non-existant/empty
def getLanguage(elt):
    if elt and elt.getText():
        return detect(elt.getText())
    else:
        return "NA"

# Turn keywords into comma-separated string - or return NA if non-existant/empty
def getKeywordsOrNA(keywords):
    if not keywords:
        return "NA"
    keywordsText = keywords.getText()
    keywordsText = keywordsText.strip().replace('\n', ',')
    if keywordsText:
        return keywordsText
    else:
        return "NA"

# Make a guaranteed-to-exist unique ID for each xml file being processed
# (not all papers will have DOIs if not harvested from Crossref)
def paperID(filename):
    id = re.sub('\.xml$', '', filename)  # remove .xml extensions
    id = re.sub('\.tei$', '', id)  # remove any remaining .tei extensions
    return id

def parseXml(filename):
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f, 'lxml')
    record = []
    record.append(paperID(os.path.basename(filename)))
    record.append(getTextOrNA(soup.find('idno',  type='DOI')))
    record.append(getTextOrNA(soup.title))
    record.append(getTextOrNA(soup.date))
    record.append(getKeywordsOrNA(soup.find('keywords')))
    record.append(getTextOrNA(soup.abstract))
    record.append(getLanguage(soup.abstract))
    return record

### Main ###

# Extract useful info from all xml files in the given directory, write to csv
def main(in_dir, out_dir, out_filename):
    infiles = glob(in_dir+"/*.xml")
    outfile = open(out_dir+"/"+out_filename, 'w', encoding="UTF-8")
    writer = csv.writer(outfile)

    columns = ['ID', 'DOI', 'Title', 'Date', 'Keywords', 'Abstract', 'Language']
    writer.writerow(columns)  # write csv header row

    # For each xml file, parse info and write a row in the csv file
    for filename in infiles:
        record = parseXml(filename)
        writer.writerow(record)

    outfile.close()

if __name__ == "__main__":
    # Check for correct usage and initialize paths and filename
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        printUsage()
        sys.exit()

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    out_filename = "summary.csv"  # default output filename

    if len(sys.argv) == 4:
        out_filename = sys.argv[3]

    if not os.path.exists(in_dir):
        print(in_dir+" is not a valid path")
        printUsage()
        sys.exit(2)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    main(in_dir, out_dir, out_filename)
