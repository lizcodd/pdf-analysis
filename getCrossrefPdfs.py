#!/bin/python3
# getCrossrefPdfs.py

import os
import sys
import re
from time import sleep
import urllib.request
from urllib.error import HTTPError
import json

def printUsage():
    """Prints a usage message"""

    print("Usage: python3 getCrossrefPdfs.py <query_string> <output_dir> <MAX_RESULTS>")
    print("e.g. To download a max of 100 articles with the words lions and/or tigers and output pdfs in current dir:")
    print("python3 getCrossrefPdfs.py lions,tigers . 100")

def downloadPdf(link, filename, output_dir):
    """Try to download pdf from a link, save it with the given filename

    Parameters
    ----------
    link : str
        The URL from which to try and download a pdf
    filename : str
        A filename for the downloaded pdf

    Raises
    ------
    Exception
        There was a problem opening the URL or the link was not actually a pdf
    """

    filepath = output_dir+"/"+filename
    if os.path.isfile(filepath):
        return # already done, don't re-download

    # Request file and check if it is a pdf before saving
    try:
        r = urllib.request.urlopen(link)
        if r.info().get_content_type() == "application/pdf":
            with open(filepath, 'wb') as f:
                f.write(r.read())
        else:
            raise Exception("Link did not resolve to pdf"+"\n")
    # Either the link was not a pdf or we ran into some other download error,
    # forbidden, needs authentication, etc... will handle it in main
    except Exception:
        raise

    sleep(1)  # don't spam, limit requests to 1/second

def downloadPdfLink(doi):
    """Download article data from doi.org as recommended by Crossref.org

    Parameters
    ----------
    doi : string
        The DOI to lookup on dx.doi.org

    Returns
    -------
    str
        The pdf link returned in the response header by dx.doi.org
    """

    opener = urllib.request.build_opener()
    opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]
    doi_link = 'http://dx.doi.org/'+doi
    r = opener.open(doi_link)
    r_link = (r.info()['Link'])

    # Extract pdf link if present (use regex to find the link that comes
    # directly before the first application/pdf)
    pdf_match = re.search('(?: <)(http[^>]*)(?=>; version=\"vor\"; type=\"application\/pdf\")', r_link)
    if pdf_match:
        return(pdf_match.groups()[0])

    # If no specific pdf link is present, try the link that is given
    other_match = re.search('(?: <)(http[^>]*)(?=>; version=\"vor\"; rel=\"item\")', r_link)
    if other_match:
        return(other_match.groups()[0])

    # Return original link as last resort - could possibly redirect to a pdf
    return(doi_link)

def downloadPdfsFromDois(dois, output_dir):
    """Automatically download as many pdfs as possible from a list of DOIs and
    record the unsuccessful attempts in humanNeeded.txt so that a human can
    navigate and manually download the rest from individual publishers.

    Parameters
    ----------
    dois : list of strings
        The DOIs to lookup on dx.doi.org and download from their DOI pdf links
    """

    human_needed = []
    downloads_remaining = 50

    for doi in dois:
        # Get link to article pdf
        try:
            link = downloadPdfLink(doi)
        except Exception as e:
            with open('getCrossrefPdfs.err', 'a') as log:
                log.write("Couldn't retrieve pdf link for " + doi + "\n")
                log.write(str(e))
            continue

        # Replace / with _ to make nice filename from DOI
        filename = re.sub('\/', '_', doi)+".pdf"

        if downloads_remaining == 0:
            sleep(3600)  # limit downloads to 50/hour (Springer policy)
            downloads_remaining = 50

        # Try to download pdf from link - if link fails, write to a txt file
        try:
            downloadPdf(link, filename, output_dir)
            downloads_remaining -= 1
        except Exception as e:
            with open('getCrossrefPdfs.err', 'a') as log:
                log.write("Encountered error while downloading "+link+"\n")
                log.write(str(e))
            human_needed.append(doi+","+link+"\n")

    # Write txt file with failed links to investigate manually if desired
    with open('humanNeeded.txt', 'w') as f:
        f.writelines(human_needed)

def main():
    # Check for correct arguments, then initialize and call main
    if (len(sys.argv) != 4) or not sys.argv[3].isdigit():
        printUsage()
        sys.exit(1)

    query = re.sub(',', '+', sys.argv[1])  # prepare query string for url
    output_dir = sys.argv[2]
    max_results = sys.argv[3]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    url = "https://api.crossref.org/types/journal-article/works?query="+query+"&rows="+max_results
    raw_json = urllib.request.urlopen(url).read()
    obj = json.loads(raw_json)
    articles = obj['message']['items']
    dois = [article['DOI'] for article in articles]

    downloadPdfsFromDois(dois, output_dir)

if __name__ == "__main__":
    main()
