import requests
import re
import urllib
import urllib.error
import urllib.request
from urllib.parse import urlparse, quote
import posixpath
import re
from bs4 import BeautifulSoup
import datetime

class FilterURL(object):
    def __init__(self, urls=[], max_length = 128, confine=None, exclude=[]):
        self.urls = urls

        self.max_len = max_length           # Max length of link
        self.confine_prefix = confine       # Limit search to this prefix
        self.exclude_prefixes = exclude     # URL prefixes NOT to visit

        # To remove image, video, rss link
        self.ignore_exts = { '.png', '.jpg', '.jpeg', '.gif', '.mp3', '.mp4', '.rss', '.pdf', '.css', '.js', '.zip', '.gz'}

        # To check if a string is url
        self.regex = re.compile(
                        r'^(?:http|ftp)s?://' # http:// or https://
                        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                        r'localhost|' #localhost...
                        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                        r'(?::\d+)?' # optional port
                        r'(?:/?|[/?]\S+)$', re.IGNORECASE)


    # Check if a string is url
    def is_url(self, url):
        return re.match(self.regex, url) is not None


    # Check if a url is image, video, rss, pdf
    def is_in_ignore_exts(self, url):
        if posixpath.splitext(urlparse(url).path)[1] in self.ignore_exts:
            return True
        
        return False


    # Reduce URLs into some canonical form before visiting
    # http://abc.com/test.html\#hehe --> http://abc.com/test.html
    def url_condense(self, url):
        if url is None:
            return None

        base, frag = urllib.parse.urldefrag(url)
        return base


    # Remove all queries in url
    def clean_url_query(self, url):
        if url is None:
            return None

        obj = urlparse(url)
        return '%s://%s%s' % (obj.scheme, obj.netloc, obj.path)   


    # Normalize url (if url has unicode)
    def url_encode(self, url):
        if url is None:
            return None

        return quote(url, safe="%/:=&?~#+!$,;'@()*[]") 
    
    # Pass if the URL has len <= 128
    def len_too_long(self, url):
        return len(url) > self.max_len


    # Pass if the URL has the correct prefix, or none is specified
    def prefix_ok(self, url):
        return (self.confine_prefix is None or
                    url.startswith(self.confine_prefix))


    # Pass if the URL does not match any exclude patterns
    def exclude_ok(self, url):
        prefixes_ok = [not url.startswith(p) for  p in self.exclude_prefixes]

        return all(prefixes_ok)


    # Get urls is ok
    def get_okurls(self):
        urls_ok = set()

        # Traverse each url to normalize and check
        for url in self.urls:
            # Is urls
            if self.is_url(url) is False:
                continue

            # Is image, video, rss
            if self.is_in_ignore_exts(url) is True:
                continue

            # Check len
            if self.len_too_long(url):
                continue

            # Check prefix
            if self.prefix_ok(url) is False:
                continue

            if self.exclude_ok(url) is False:
                continue

            # Clean url
            tmp = self.clean_url_query(url)
            tmp = self.url_condense(tmp)
            tmp = self.url_encode(tmp)

            # Everything ok --> add to urls_ok
            urls_ok.add(tmp)

        return list(urls_ok)
    

def get_all_links(urls=['https://e.vnexpress.net/news/news', 'https://e.vnexpress.net/news/business', 'https://e.vnexpress.net/news/travel', 'https://e.vnexpress.net/news/life', 'https://e.vnexpress.net/news/sports', 'https://e.vnexpress.net/news/world']):
    '''
    Get all links from seek urls
    
    Args:
        urls (str): The seek urls

    Returns:
        links (list): A list of all links
    '''

    links = {}

    for seek in urls:
        # Send a GET request to the URL and get the response
        response = requests.get(seek)

        # Parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        cate_urls = []

        # Get links from page
        tags = soup('a')
        for tag in tags:
            url = tag.get('href')
            if url is not None and url.startswith('https://e.vnexpress.net/news/'):
                if url not in cate_urls:
                    cate_urls.append(url)
        
        cate_urls = FilterURL(cate_urls).get_okurls()
        links[seek.split('/')[-1]] = cate_urls

    return links


def get_content(url, category='news'):
    '''
    Get the content of the url
    The response from the URL is parsed into a dictionary containing the extracted information

    Args:
        url (str): The url to get the content from

    Returns:
        info (dict): A dictionary containing: title, date, text, author, and url
    '''

    # Send a GET request to the URL and get the response
    response = requests.get(url)

    # Parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    info = {
        'url': url,
        'is_valid': False
    }

    try:
        # Find the title of the page
        title = soup.find('h1', {'class': 'title_post'}).text

        # Find the date
        author_and_date = soup.find('div', {'class': 'author'}).text
        author = author_and_date.split('&nbsp')[0].replace('By ', '')
        date = author_and_date.split('&nbsp')[1].split('|')[0].strip()
        date = datetime.datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')

        # Find the text
        description = soup.find('span', {'class': 'lead_post_detail row'}).text
        paras = soup.find_all('p', {'class': 'Normal'})
        text = description.strip() + '\n\n' + '\n\n'.join([p.text.strip() for p in paras])

        # Create a dictionary to store the extracted information
        info = {
            'title': title.strip(),
            'date': date,
            'text': text.strip(),
            'author': author.strip(),
            'category': category,
            'url': url,
            'is_valid': True
        }
    except:
        pass

    return info