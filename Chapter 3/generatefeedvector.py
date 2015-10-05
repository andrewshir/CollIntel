__author__ = 'Andrew'

import feedparser
import re
import path

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
    # Parse the feed
    d=feedparser.parse(url)
    wc={}

    # Loop over all the entries
    for e in d.entries:
        if 'summary' in e: summary=e.summary
        else: summary=e.description

        # Extract a list of words
        words=getwords(e.title+' '+summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word]+=1
    return [(d.feed.title, wc)]

def getwordcounts_by_post(url):
    # Parse the feed
    d=feedparser.parse(url)

    result = []
    # Loop over all the entries
    for e in d.entries:
        wc={}
        if 'summary' in e: summary=e.summary
        else: summary=e.description

        # Extract a list of words
        words=getwords(summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word]+=1
        title = u'%s [%s]' % (e.title, d.feed.title)
        result.append((title, wc))
    return result


def getwords(html):
    # Remove all the HTML tags
    txt=re.compile(r'<[^>]+>').sub('',html)
    # Split words by all non-alpha characters
    words=re.compile(r'[^A-Z^a-z]+').split(txt)
    # Convert to lowercase
    return [word.lower( ) for word in words if word!='']

apcount={}
wordcounts={}
blogcount = 0
for feedurl in file(path.feed_path):
    try:
        items=getwordcounts(feedurl)
        #items=getwordcounts_by_post(feedurl)
    except:
        continue
    blogcount += len(items)
    for title,wc in items:
        wordcounts[title]=wc
        for word,count in wc.items( ):
            apcount.setdefault(word,0)
            if count>1:
                apcount[word]+=1

wordlist=[]
for w,bc in apcount.items( ):
    frac=float(bc)/blogcount
    if frac>0.1 and frac<0.5: wordlist.append(w)

with open(path.data_path,'w') as out:
    out.write('Blog')
    for word in wordlist:
        out.write('\t%s' % word)
    out.write('\n')

    for blog,wc in wordcounts.items( ):
        out.write(blog.encode('utf8'))
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')