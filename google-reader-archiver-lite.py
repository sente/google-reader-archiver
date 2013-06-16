# encoding: utf-8
import json
import sys
import os
import getpass
import requests
import tablib
from libgreader import GoogleReader, ClientAuthMethod, Feed

def login():

    try:
        username, password = open('auth.txt').read().strip().split('\n')
    except:
        username = raw_input('username? ')
        password = getpass.getpass('password? ')
        open('auth.txt','w').write("{0}\n{1}\n".format(username,password))

    auth = ClientAuthMethod(username, password)
    reader = GoogleReader(auth)
    reader.buildSubscriptionList()
    return reader

def redundantly_save_meta_feed_data(reader):

    ds = tablib.Dataset(headers=['title','feedUrl','siteUrl','fetchUrl'])
    for i,f in enumerate(reader.getFeeds()):
        ds.append(map(str,(f.title,f.feedUrl,f.siteUrl,f.fetchUrl)))
    open('feeds.html','w').write(ds.html)
    open('feeds.json','w').write(ds.json)
    open('feeds.yaml','w').write(ds.yaml)
    open('feeds.csv','w').write(ds.csv)
    sys.stderr.write('created feeds.html\n')
    sys.stderr.write('created feeds.json\n')
    sys.stderr.write('created feeds.yaml\n')
    sys.stderr.write('created feeds.csv\n')


def get_feed_entries(google_feed_url, max_items=5000):
    """
    returns the items for a given Google Reader FetchUrl...
    """
    c = ''
    url = google_feed_url + '?n=1000&c='

    items = []
    while (len(items) < max_items):
        sys.stderr.write('fetching ' + url + c + '...\n')
        data = json.loads(requests.get(url + c).content)
        items.extend(data['items'])
        c = data.get('continuation', None)
        if not c:
            return items

    sys.stderr.write('fetched %d items\n' % len(items[0:max_items]))
    return items[0:max_items]




if __name__ == '__main__':
    #reader = login()
    #redundantly_save_meta_feed_data()

    # fetch 2000 items from google's cache of the feed: www.reddit.com/new/.rss
    items = get_feed_entries('https://www.google.com/reader/api/0/stream/contents/feed/http%3A//www.reddit.com/new/.rss%3Fsort%3Dnew',
            max_items=2000)

    # and now print them!
    print json.dumps(items,indent=2)







