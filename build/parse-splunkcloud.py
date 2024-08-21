import requests
import smtplib
import re
from bs4 import BeautifulSoup
import csv

def getversions():

    url = 'https://docs.splunk.com/Documentation/SplunkCloud/latest/ReleaseNotes'
    website = requests.get(url)
    results = BeautifulSoup(website.content, 'html.parser')
    select = results.find_all('select', id="version-select")
    
    versions = select[0].contents
    dbxversions = []

    for t in versions:
        try: 
            matches = re.search('value=\"(\d\.\d+\.\d{4})\"', str(t))
            dbxversions.append(matches.group(1))
        except:
            print("not valid: " + str(len(t)))


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
    website = requests.get(URL)
    results = BeautifulSoup(website.content, 'html.parser')

    try: 
        selectcontent = results.find_all('div', {"class": "mw-parser-output"})
        #print(str(selectcontent[0]))

        resultstable = BeautifulSoup(str(selectcontent[0]), 'html.parser')
        selecttable = results.find_all('table')

        resolved = []
        for table in selecttable:
            if "Date filed" in table.text:
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