"""
Scrape US obesity datas.
"""
import json
import sys
import urllib

import ffs
from lxml.html import fromstring
import requests
from slugify import slugify

import nonsense_sessions

DATA_DIR = ffs.Path.here()/'../data'


class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

        
class Dataset(object):
    def __init__(self, title, url, description, tags):
        self.title = title
        self.url = url
        self.description = description
        self.tags = tags

    @property
    def as_json(self):
        data = dict(title=self.title, url=self.url, description=self.description, tags=self.tags)
        return json.dumps(data, indent=2)

def _astree(url):
    """
    Helper that returns a URL as a lxml tree
    """
    content = urllib.urlopen(url).read()
    dom = fromstring(content)
    dom.make_links_absolute(url)
    return dom

def health_indicators_dataset(links):
    """
    Scrape the data from the dataset page.
    """
    for dataset in links:
        base_dom = _astree(dataset)
        title = base_dom.cssselect('h1')[0].text_content().strip()
        print '~~~~ Processing {0} Indicator "Warehouse" ~~~~'.format(title)

        description = base_dom.cssselect(
            '#PageContent')[0].text_content().split('\n')
        description = "\n".join([l.strip() for l in description if l.strip()])

        tags = [a.text_content().strip() for a in
                base_dom.cssselect('.TagCloud a span.VariableWidth')]
        url = dataset
        
        resourceslink = base_dom.cssselect(
            '#ctl00_ctl00_ctl00_subNavigation_subNavigation_downloadLink')[0]
        resourceslink = resourceslink.get('href')

        resp = requests.post(
            resourceslink,
            data=nonsense_sessions.healthindicators_dot_gov_session
        )

        ds = Dataset(title, url, description, tags)

        with ffs.Path.temp() as tmp:
            zipfile = tmp/'download.zip'
            zipfile << resp.content
            zipfile = zipfile.as_zip
            extracted = tmp/'extracted'
            extracted.mkdir()
            zipfile.extract(extracted)

            target = DATA_DIR/slugify(title)
            target.mkdir()
            
            for i in extracted.ls():
                dest = target/i[-1]
                moved = i.mv(dest)

        metadata = target/'metadata.json'
        metadata << ds.as_json
    return
        
def health_indicators_warehouse():
    """
    Grab everything from the health indicator warehouse tagged Obesity.
    """
    BASE_URL = 'http://www.healthindicators.gov/Indicators/Search?Query=obesity'
    print '~~~~ Fetching master dataset list from Indicator "Warehouse" ~~~~'
    content = urllib.urlopen(BASE_URL).read()
    base_dom = fromstring(content)
    base_dom.make_links_absolute(BASE_URL)
    links = [a.get('href') for a in base_dom.cssselect('.IndicatorResultsList a') 
             if a.get('href').startswith('http://')]
    health_indicators_dataset(links)
    return

def main():
    health_indicators_warehouse()
    return 0

if __name__ == '__main__':
    sys.exit(main())
