#!/bin/python3
# getCrossrefPdfs.py

import os
import sys
import re
from time import sleep
import urllib.request
from urllib.error import HTTPError
import json

# Print a helpful message
def printUsage():
    print("Usage: python3 getCrossrefPdfs.py <query_string> <output_dir> <MAX_RESULTS>")
    print("e.g. To download a max of 100 articles with the words lions and/or tigers and output pdfs in current dir:")
    print("python3 getCrossrefPdfs.py lions,tigers . 100")

# Try to download pdfs (often can't determine type from filename)
def downloadPdf(link, filename):
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
            raise Exception("Link did not resolve to pdf")
    # Either the link was not a pdf or we ran into some other download error,
    # forbidden, needs authentication, etc... will handle it in main
    except Exception:
        raise

# Download article data from doi.org as recommended by Crossref.org
def downloadPdfLink(doi):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Accept', 'application/vnd.crossref.unixsd+xml')]
    doi_link = 'http://dx.doi.org/'+doi
    r = opener.open(doi_link)
    r_link = (r.info()['Link'])

    # Extract pdf link if present
    # (Use regex to find the link that comes directly before the first application/pdf)
    pdf_match = re.search('(?: <)(http[^>]*)(?=>; version=\"vor\"; type=\"application\/pdf\")', r_link)
    if pdf_match:
        return(pdf_match.groups()[0])

    # If no specific pdf link is present, try the other link (sometimes it is a pdf)
    other_match = re.search('(?: <)(http[^>]*)(?=>; version=\"vor\"; rel=\"item\")', r_link)
    if other_match:
        return(other_match.groups()[0])

    return(doi_link) # last resort, could possibly redirect to a pdf

def main(query, output_dir, max_results):
    human_needed = []
    downloads_remaining = 50

    url = "https://api.crossref.org/types/journal-article/works?query="+query+"&rows="+max_results
    raw_json = urllib.request.urlopen(url).read()
    obj = json.loads(raw_json)
    articles = obj['message']['items']
    dois = [article['DOI'] for article in articles]

    for doi in dois:
        # Get link to article pdf
        link = downloadPdfLink(doi)

        # Replace / with _ to make nice filename from DOI
        filename = re.sub('\/', '_', doi)+".pdf"

        if downloads_remaining == 0:
            sleep(3600)  # limit downloads to 50/hour (Springer policy)
            downloads_remaining = 50

        # Try to download pdf from link - if link fail, write to a txt file
        try:
            downloadPdf(link, filename)
            downloads_remaining -= 1
        except Exception as e:
            with open('getCrossrefPdfs.err', 'a') as log:
                log.write("Encountered error while downloading "+link+"\n")
                log.write(str(e))
            human_needed.append(link+'\n')

        sleep(1)  # don't spam, limit requests to 1/second

    # Write txt file with failed links to investigate manually if desired
    with open('humanNeeded.txt', 'w') as f:
        f.writelines(human_needed)

    return(0)

if __name__ == "__main__":
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

    main(query, output_dir, max_results)
