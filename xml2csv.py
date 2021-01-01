#!/usr/bin/python3
# xml2csv.py

import os
import sys
from bs4 import BeautifulSoup
import csv
from glob import glob
import re
from langdetect import detect


def printUsage():
    """Prints usage message"""

    print("Usage: python3 xml2csv.py <input_path> <output_path> [output_filename]")
    print("e.g. To parse xmls in papers and output summary.csv in the current dir:")
    print("python3 xml2csv.py papers .")


def getTextOrNA(elt):
    """Return the text in an element if possible

    Parameters
    ----------
    elt : bs4.element.Tag
        A BeautifulSoup tag element to extract text from

    Returns
    -------
    str
        The text within the given element or "NA" if the element is non-existant
        or contains an empty string
    """

    if elt and elt.getText():
        return elt.getText().strip()
    else:
        return "NA"


def getLanguage(elt):
    """Detect the language of the text in an element if possible

    Parameters
    ----------
    elt : bs4.element.Tag
        A BeautifulSoup tag that contains the text to check language

    Returns
    -------
    str
        The detected language as a 2 letter code, or "NA" if element is
        non-existant or contains an empty string
    """

    if elt and elt.getText():
        return detect(elt.getText())
    else:
        return "NA"

def getKeywordsOrNA(keywords):
    """Turn keywords into comma-separated string if possible

    Parameters
    ----------
    keywords : bs4.element.Tag
        The keywords tag that BeautifulSoup extracted from the xml

    Returns
    -------
    str
        All keywords separated by commas, or "NA" if element is
        non-existant or contains an empty string
    """

    if not keywords:
        return "NA"
    keywordsText = keywords.getText()
    keywordsText = keywordsText.strip().replace('\n', ',')
    if keywordsText:
        return keywordsText
    else:
        return "NA"

def paperID(filename):
    """Make a guaranteed-to-exist unique ID for the xml file being processed

    Parameters
    ----------
    filename : str
        The name (only name, not path) of the xml file

    Returns
    -------
    str
        A unique ID for the file (just filename with no .xml or .tei extensions)
    """

    id = re.sub('\.xml$', '', filename)  # remove .xml extensions
    id = re.sub('\.tei$', '', id)  # remove any remaining .tei extensions
    return id

def parseXml(filename):
    """Extracts some useful info (DOI, article title, etc) from xml file

    Parameters
    ----------
    filename : str
        The path of the xml file to be processed

    Returns
    -------
    list
        A list containing the info that was extracted from the xml:
        DOI, title, publication date, keywords, abstract, language of article
    """

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

def main():
    # Check for correct usage and initialize paths and filename
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        printUsage()
        sys.exit()

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    out_filename = "summary.csv"  # default output filename

    if len(sys.argv) == 4:
        out_filename = sys.argv[3]  # use specified output filename

    if not os.path.exists(in_dir):  # cannot proceed if input path is wrong
        print(in_dir+" is not a valid path")
        printUsage()
        sys.exit(2)

    if not os.path.exists(out_dir):  # make output dir if doesn't already exist
        os.makedirs(out_dir)

    infiles = glob(in_dir+"/*.xml")
    outfile = open(out_dir+"/"+out_filename, 'w', encoding="UTF-8")
    writer = csv.writer(outfile)

    # Write csv header row
    columns = ['ID', 'DOI', 'Title', 'Date', 'Keywords', 'Abstract', 'Language']
    writer.writerow(columns)

    # For each xml file, parse info and write a row in the csv file
    for filename in infiles:
        record = parseXml(filename)
        writer.writerow(record)

    outfile.close()

if __name__ == "__main__":
    main()
