"""
Scrape US obesity datas.
"""
import sys
import urllib


import ffs
from lxml.html import fromstring

DATA_DIR = ffs.Path.here()/'../data'

class Error(Exception): 
    def __init__(self, msg):
        Exception.__init__(self, '\n\n\n{0}\n\n\n'.format(msg))

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
        print base_dom
        
def health_indicators_warehouse():
    """
    Grab everything from the health indicator warehouse tagged Obesity.
    """
    BASE_URL = 'http://www.healthindicators.gov/Indicators/Search?Query=obesity'
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
