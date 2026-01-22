import requests
import smtplib
import re
from bs4 import BeautifulSoup
import csv


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def getversions():

    url = 'https://docs.splunk.com/Documentation/SplunkCloud/latest/ReleaseNotes'
    website = requests.get(url, headers=HEADERS)

    # Extract version patterns (e.g., 9.3.2411) from the page
    # The page now redirects to help.splunk.com and versions are embedded in scripts/links
    all_versions = set(re.findall(r'\d+\.\d+\.\d{4}', website.text))

    # Sort versions in descending order (newest first)
    dbxversions = sorted(all_versions, reverse=True)

    print(f"Found versions: {dbxversions}")
    return dbxversions

versions = [
    #'3.5.0',
    '3.5.1',
    '3.6.0',
    # '3.7.0'
]

versions = getversions()

resolvedissues = {}
for version in versions:
    URL = 'https://docs.splunk.com/Documentation/SplunkCloud/'+version+'/ReleaseNotes/Issues'
    print("parsing " + str(URL))
    website = requests.get(URL, headers=HEADERS)
    results = BeautifulSoup(website.content, 'html.parser')

    try:
        selecttable = results.find_all('table')

        resolved = []
        for table in selecttable:
            # Check for tables with date/issue columns (handle both old and new header formats)
            if "Date filed" in table.text or "Issue number" in table.text:
                # print(table.text)
                for row in table.findAll('tr'):
                    columns = row.findAll('td')
                    if len(columns) > 0:
                        n = 0
                        outrow = {}
                        for column in columns:
                            outrow['url'] = URL
                            if n==0:
                                outrow['resolved'] = column.text
                            if n==1:
                                outrow['issuenr'] = column.text
                            if n==2:
                                outrow['description'] = (column.text).rstrip()
                            
                            n = n + 1
                        resolved.append(outrow)
        if len(resolved) > 0:
            resolvedissues[version] = resolved
    except:
        print("no table found")

outfile = "fixedissues-splunkcloud.csv"

with open(outfile, "w") as filenew:

    fieldnames = ["url","version","category","resolveddate","spl","description"]
    writer = csv.DictWriter(filenew, fieldnames=fieldnames)
    writer.writeheader()
    
    for version, values in resolvedissues.items():
        #print("version: " + str(version))
        for value in values:
            #print("value: " + str(value))
            writer.writerow({'url': value['url'],'version': version, 'category': "dbx", \
                'resolveddate': value['resolved'], 'spl': value['issuenr'], \
                'description': value['description']})