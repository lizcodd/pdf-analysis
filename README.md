# pdf-analysis
Some code for downloading and analyzing journal articles using Crossref API, Grobid, etc.

## Step 1: Collect pdfs to analyze

## scrapeScholarPdfs.sh

My first attempt was a script using wget2 to download all pdfs returned by a Google Scholar search query.

Not a good solution. This works but eventually Google will block it. I'm thinking if we want to get the pdfs through Google Scholar we can go through something like scraperapi.com to download all the search result pages, then grab the pdf links and download those automatically.

## getCrossrefPdfs.py

Second attempt was to find pdfs using Crossref.org and then download them from the links provided by dx.doi.org. Crossref provides an API for searching millions of articles across thousands of publishers. Another good thing is that all the articles have DOIs. This script attempts to download pdfs for all the journal articles returned by a Crossref search query (up to 1000, but could alter it to do more).

### Usage:

python3 getCrossrefPdfs.py <query_string> <output_dir> <MAX_RESULTS>")

e.g. to download a max of 100 articles with the words lions and/or tigers and output pdfs in current directory:
python3 getCrossrefPdfs.py lions,tigers . 100")

## Step 2: Process pdfs with Grobid to get xmls

I used Grobid (https://github.com/kermitt2/grobid) and the accompanying python client (https://github.com/kermitt2/grobid_client_python) to turn all pdfs in xml files.

## Step 3: Summarizing data from xmls in a csv

## xml2csv.sh

A script to extract useful information (e.g. doi, title, date, abstract, language) from the xmls and store it is a csv that can then be analyzed.

### Usage:

python3 xml2csv.py <input_path> <output_path> [output_filename]

e.g. to parse xmls in ./papers and output a csv with the default name (summary.csv) in the current directory:
python3 xml2csv.py papers .

## Step 4: Analysis

## CoralAnalysis.ipynb

Just some initial ideas:

1) Find which Acropora species are in each article, rank the species by most commonly studied. Could be expanded to all genera.

2) Find which genes are in each article, rank genes by most commonly studied. A bit problematic because I think sometimes full protein names and official gene names aren't used verbatim. I took my list from Uniprot (https://www.uniprot.org/uniprot/?query=organism%3Aacropora&sort=score). Only used genes listed on Uniprot for Acropora, could be expanded to genes from all genera.

3) Sorting articles: I think the idea of TF-IDF distance is interesting, so I tried nearest-neighbor and K-mean models with turicreate. Doesn't do much on my test datasets but could be interesting if analyzing a lot of articles and/or the article fulltext.
