

import json
import sys
import os
from libgreader import GoogleReader, ClientAuthMethod, Feed

def meta_info(feed):
    """
    returns a formatted JSON string showing the feedUrl, etc...
    """

    obj = {}
    obj['title'] = feed.title
    obj['siteUrl'] = feed.siteUrl
    obj['fetchUrl'] = feed.fetchUrl
    obj['feedUrl'] = feed.feedUrl

    return json.dumps(obj, indent=2)


def login():
    """
        requires an 'auth.txt' to exist in the current directory, this
        file contains two lines, the first line is your username, the
        second line is your password.
    """
    username, password = open('auth.txt').read().strip().split('\n')
    auth = ClientAuthMethod(username, password)
    reader = GoogleReader(auth)
    a = reader.buildSubscriptionList()
    if not a:
        return False
    else:
        return reader

def get_feed_items(reader, feed, loadLimit=1000, maxLimit=3000):
    """
    Retrieve up to <maxLimit> items from the <feed>, do this in chunks of <loadLimit>.
    Google's <loadLimit> limit is 1000
    """
    received = []
    continuation = None

    while len(received) < maxLimit:
        fetch_limit = min((maxLimit - len(received)), loadLimit)
        content = reader.getFeedContent(feed, continuation=continuation, loadLimit=fetch_limit)
        continuation = content.get('continuation')
        if not continuation:
            maxLimit = 0
        items = content.get('items', [])

        sys.stderr.write('received %d items\n' % len(items))
        received.extend(items)

    sys.stderr.write('received %d items in total\n' % len(received))

    return received

def save_feed(reader, feed, directory, loadLimit=1000, maxLimit=5000):
    """
    saves up to <maxLimit> entries of <feed> inside <directory>
    some meta information is saved in <directory>/meta.json
    and the feed items are saved in <directory>/data.json
    """

    if not os.path.isdir(directory):
        os.mkdir(directory)

    items = get_feed_items(reader, feed, loadLimit=loadLimit, maxLimit=maxLimit)

    datafile = os.path.join(directory, 'data.json')
    metafile = os.path.join(directory, 'meta.json')

    with open(metafile, 'w') as mf:
        mf.write(meta_info(feed))
        sys.stderr.write("wrote %s\n" % metafile)

    with open(datafile, 'w') as df:
        df.write(json.dumps(items, indent=2))
        sys.stderr.write("wrote %s (%d items)\n" % (datafile, len(items)))


def save_feeds(reader):
    for i,f in enumerate(reader.getFeeds()):
        print meta_info(f)
        save_feed(reader, f, 'feeds/' + str(i), loadLimit=1000, maxLimit=8000)


if __name__ == '__main__':
    reader = login()
    save_feeds(reader)




