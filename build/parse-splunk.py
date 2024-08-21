import requests
import smtplib
import re
from bs4 import BeautifulSoup
import csv
 
def get_versions():

    url = 'https://docs.splunk.com/Documentation/Splunk/latest/ReleaseNotes/Knownissues'
    website = requests.get(url)
    results = BeautifulSoup(website.content, 'html.parser')
    select = results.find_all('select', id="version-select")
    
    versions = select[0].contents
    dbxversions = []

    for t in versions:
        try: 
            matches = re.search('value=\"(\d\.\d\.\d+)\"', str(t))
            dbxversions.append(matches.group(1))
        except:
            print("not valid: " + str(t))


    return dbxversions

def filter_versions(versions):
    
    outversions = []
    for version in versions:
        if re.search("^[789]",version):
        #if re.search("^8\.2",version):
            outversions.append(version)
    
    print(outversions)
    return outversions

versions = [
    #'8.2.0',
    '8.2.1'
]

versions = get_versions()
versions = filter_versions(versions)

resolvedissues = {}
for version in versions:
    URL = 'https://docs.splunk.com/Documentation/Splunk/'+version+'/ReleaseNotes/Fixedissues'
    print("parsing " + str(URL))
    website = requests.get(URL)
    results = BeautifulSoup(website.content, 'html.parser')

    selectcontent = results.find_all('div', {"class": "mw-parser-output"})
    #print(str(selectcontent[0]))

    resultstable = BeautifulSoup(str(selectcontent[0]), 'html.parser')
    selectcategories = results.find_all('span', {"class": "mw-headline"})

    resolved = []

    
    for category in selectcategories:
        if category.text not in "Fixed issues":
            #print(category.text)
            next = category.next_element
            next = next.next_element
            next = next.next_element
          #  next = next.next_element # table

            for row in next.findAll('tr'):
                    columns = row.findAll('td')
                    #print(columns)
                    if len(columns) > 0:
                        n = 0
                        outrow = {}
                        for column in columns:
                            outrow['url'] = URL
                            outrow['category'] = category.text
                            if n==0:
                                outrow['resolved'] = column.text
                            if n==1:
                                outrow['issuenr'] = column.text
                            if n==2:
                                outrow['description'] = column.text
                            n = n + 1
                        resolved.append(outrow)
        if len(resolved) > 0:
            resolvedissues[version] = resolved

outfile = "fixedissues-splunk.csv"

with open(outfile, "w") as filenew:

    fieldnames = ["url","version","category","resolveddate","spl","description"]
    writer = csv.DictWriter(filenew, fieldnames=fieldnames)
    writer.writeheader()
    
    for version, values in resolvedissues.items():
        #print("version: " + str(version))
        for value in values:
            #print("value: " + str(value))
            writer.writerow({'url': value['url'],'version': version, 'category': value['category'], \
                'resolveddate': value['resolved'], 'spl': value['issuenr'], \
                'description': value['description']})
