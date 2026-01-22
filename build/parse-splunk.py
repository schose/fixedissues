import requests
import re
import json
from bs4 import BeautifulSoup
import csv

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_versions_from_dockerhub():
    """Get all MAJOR.MINOR.PATCH versions from Docker Hub splunk/splunk tags"""
    versions = set()
    url = 'https://hub.docker.com/v2/repositories/splunk/splunk/tags?page_size=100'

    while url:
        print(f"Fetching Docker Hub tags...")
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        for tag in data.get('results', []):
            name = tag.get('name', '')
            # Match only MAJOR.MINOR.PATCH format (e.g., 9.4.0, 10.0.2)
            if re.match(r'^\d+\.\d+\.\d+$', name):
                versions.add(name)

        # Get next page URL
        url = data.get('next')

    # Sort versions in descending order
    sorted_versions = sorted(versions, key=lambda v: [int(x) for x in v.split('.')], reverse=True)
    print(f"Found {len(sorted_versions)} versions from Docker Hub")

    return sorted_versions

def filter_versions(versions):
    """Filter to only include versions >= 9"""
    outversions = []
    for version in versions:
        major = int(version.split('.')[0])
        if major >= 7:
            outversions.append(version)

    print(f"Filtered versions: {outversions}")
    return outversions

def build_api_url(version):
    """Build the API URL for a specific version like 9.4.7"""
    # API pattern: https://docs.splunk.com/api.php?action=parse&page=JIRA:SPL-9.4.7-changelog&prop=text&format=json
    return f"https://docs.splunk.com/api.php?action=parse&page=JIRA:SPL-{version}-changelog&prop=text&format=json"

def build_help_url(version):
    """Build the help URL for a specific version like 9.4.5"""
    # Help URL pattern: https://help.splunk.com/en/splunk-enterprise/release-notes-and-updates/release-notes/9.4/fixed-issues/fixed-issues/splunk-enterprise-9.4.5-fixed-issues
    parts = version.split('.')
    major_minor = f"{parts[0]}.{parts[1]}"
    return f"https://help.splunk.com/en/splunk-enterprise/release-notes-and-updates/release-notes/{major_minor}/fixed-issues/fixed-issues/splunk-enterprise-{version}-fixed-issues"

# Get all versions to scrape
all_versions = get_versions_from_dockerhub()
versions = filter_versions(all_versions)

resolvedissues = {}
for version in versions:
    URL = build_api_url(version)
    print(f"parsing {version}")

    try:
        response = requests.get(URL, headers=HEADERS)

        # Skip if page not found
        if response.status_code == 404:
            print(f"  -> 404 not found, skipping")
            continue

        data = response.json()

        # Check if the page exists (API returns 'error' key if not)
        if 'error' in data:
            print(f"  -> page not found, skipping")
            continue

        # Extract HTML content from JSON response
        html_content = data['parse']['text']['*']
        results = BeautifulSoup(html_content, 'html.parser')

        # Find all headline spans with class mw-headline to get categories
        # Each headline is followed by a table, and the id attribute is the category
        resolved = []

        # Find all mw-headline elements
        headlines = results.find_all('span', class_='mw-headline')

        for headline in headlines:
            category = headline.get('id', 'unknown')

            # Find the next table after this headline
            # Navigate up to the parent heading element, then find the next table sibling
            parent = headline.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if parent:
                # Find the next table sibling
                table = parent.find_next_sibling('table')
                if not table:
                    # Sometimes the table might be wrapped in a div
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        table = next_elem.find('table') if next_elem.name != 'table' else next_elem

                if table:
                    for row in table.find_all('tr'):
                        columns = row.find_all('td')
                        if len(columns) >= 3:
                            outrow = {
                                'category': category,
                                'resolved': columns[0].text.strip(),
                                'issuenr': columns[1].text.strip(),
                                'description': columns[2].text.strip()
                            }
                            resolved.append(outrow)

        if len(resolved) > 0:
            resolvedissues[version] = resolved
            print(f"  -> found {len(resolved)} issues")
        else:
            print(f"  -> no issues found")

    except Exception as e:
        print(f"  -> error: {e}")

outfile = "fixedissues-splunk.csv"

with open(outfile, "w") as filenew:
    fieldnames = ["url", "version", "category", "resolveddate", "spl", "description"]
    writer = csv.DictWriter(filenew, fieldnames=fieldnames)
    writer.writeheader()

    for version, values in resolvedissues.items():
        help_url = build_help_url(version)
        for value in values:
            writer.writerow({
                'url': help_url,
                'version': version,
                'category': value.get('category', 'unknown'),
                'resolveddate': value['resolved'],
                'spl': value['issuenr'],
                'description': value['description']
            })

print(f"\nOutput written to {outfile}")
print(f"Total versions with issues: {len(resolvedissues)}")
