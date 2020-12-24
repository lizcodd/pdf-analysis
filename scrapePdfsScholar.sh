#!/bin/bash
# scrapePdfsScholar.sh

# Print help message and exit if wrong parameters
if [ $# -lt 2  ] || ! [[ $2 =~ ^[0-9]+$ ]]
then
	echo "Usage:   ./scrapePdfsScholar.sh keywords PAGES_TO_SCRAPE"
        echo "Example: ./scrapePdfsScholar.sh lions,tigers,bears 10"
        exit 1
fi

# First arg has keywords to search on Google Scholar, replace commas with +
keywords=${1//,/+}

# Max pages of search results to scrape
MAX_PAGES=$2

# Loop through Google Scholar results pages
function scrape {
	for ((i=0;i<MAX_PAGES;i++))
	do
		# Build new url for each page of query results
		url="https://scholar.google.com/scholar?start="$((i * 10))"&q=filetype:pdf+"${keywords}"&hl=en&as_sdt=0,22"
		# Download all available pdfs using wget2
		wget2 -e robots=off --random-wait --continue --timestamping -H -U "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0" -r -l 1 -nd -A pdf --filter-mime-type=application/pdf "$url"
		sleep $((1 + RANDOM % 10))  # Wait somewhere between 1 and 10 seconds - could wait longer, might help
	done
}

# DOES NOT WORK (eventually script will get blocked by Google)
# scrape 1>scrapePdfsScholar.log 2>scrapePdfsScholar.err
