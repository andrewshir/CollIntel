import feedparser
import re
from numpy import *
import numpy as np

feedlist = [
        'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'http://www.nytimes.com/services/xml/rss/nyt/International.xml',
        'http://news.google.com/?output=rss',
        'http://www.foxnews.com/xmlfeed/rss/0,4313,0,00.rss',
        'http://rss.cnn.com/rss/edition.rss',
        'http://rss.cnn.com/rss/edition_world.rss',
        'http://rss.cnn.com/rss/edition_us.rss']


def stripHTML(h):
    p=''
    s=0
    for c in h:
        if c=='<': s=1
        elif c=='>':
            s=0
            p+=' '
        elif s==0: p+=c
    return p


def separatewords(text):
    splitter=re.compile('\\W*')
    return [s.lower() for s in splitter.split(text) if len(s)>3]


def getarticlewords():
    allwords={}
    articlewords=[]
    articletitles=[]
    ec=0
    # Loop over every feed
    for feed in feedlist:
        f=feedparser.parse(feed)
        # Loop over every article
        for e in f.entries:
            # Ignore identical articles
            if e.title in articletitles: continue
            # Extract the words
            txt=e.title.encode('utf8')+stripHTML(e.description.encode('utf8'))
            words=separatewords(txt)
            articlewords.append({})
            articletitles.append(e.title)
            # Increase the counts for this word in allwords and in articlewords
            for word in words:
                allwords.setdefault(word,0)
                allwords[word]+=1
                articlewords[ec].setdefault(word,0)
                articlewords[ec][word]+=1
            ec+=1
    return allwords, articlewords, articletitles

def makematrix(allw, articlew):
    wordvec=[]
    # Only take words that are common but not too common
    for w,c in allw.items():
        if c>3 and c<len(articlew)*0.6:
            wordvec.append(w)

    # Create the word matrix
    l1 = [[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
    return l1, wordvec


def difcost(a,b):
    dif=0
    # Loop over every row and column in the matrix
    for i in range(shape(a)[0]):
        for j in range(shape(a)[1]):
            # Add together the differences
            dif+=pow(a[i,j]-b[i,j],2)
    return dif


def factorize(v, pc=10, iter=50):
    ic = shape(v)[0]
    fc = shape(v)[1]

    # Initialize the weight and feature matrices with random values
    w = array([[random.uniform(0.1, 1) for j in range(pc)] for i in range(ic)])
    h = array([[random.uniform(0.1, 1) for j in range(fc)] for i in range(pc)])

    # Perform operation a maximum of iter times
    for i in range(iter):
        wh = dot(w, h)

        # Calculate the current difference
        cost = difcost(v, wh)
        if i % 10 == 0:
            print cost

        # Terminate if the matrix has been fully factorized
        if cost == 0:
            break

        # Update feature matrix
        hn = dot(transpose(w), v)
        hd = dot(transpose(w), dot(w, h))
        if (hd == 0.0).any(): #len([x for x in hd.ravel() if x == 0.0]) > 0:
            print "Zeros in hd"
        h = array(h) * array(hn) / array(hd)

        # Update weights matrix
        wn = dot(v, transpose(h))
        wd = dot(w, dot(h, transpose(h)))

        if (wd == 0.0).any(): #len([x for x in wd.ravel() if x == 0.0]) > 0:
            print "Zeros in wd"
        w = w * wn / wd # /array(wd)
    return w, h

def showfeatures(w, h, titles, wordvec,out=r'C:/Temp/features.txt'):
    outfile = file(out,'w')
    pc,wc = shape(h)
    toppatterns=[[] for i in range(len(titles))]
    patternnames=[]
    # Loop over all the features
    for i in range(pc):
        slist=[]
        # Create a list of words and their weights
        for j in range(wc):
            slist.append((h[i,j],wordvec[j]))
        # Reverse sort the word list
        slist.sort()
        slist.reverse()

        # Print the first six elements
        n=[s[1] for s in slist[0:6]]
        outfile.write(str(n)+'\n')
        patternnames.append(n)

        # Create a list of articles for this feature
        flist=[]
        for j in range(len(titles)):
            # Add the article with its weight
            flist.append((w[j,i],titles[j]))
            toppatterns[j].append((w[j,i],i,titles[j]))

        # Reverse sort the list
        flist.sort()
        flist.reverse()

        # Show the top 3 articles
        for f in flist[0:3]:
            outfile.write(str(f)+'\n')
        outfile.write('\n')

    outfile.close()
    # Return the pattern names for later use
    return toppatterns, patternnames

allw, artw, artt = getarticlewords()
wordmatrix, wordvec = makematrix(allw, artw)

wordmatrix = array(wordmatrix)
wordvec = array(wordvec)
artt = array(artt)
wordmatrix = wordmatrix[:, np.any(wordmatrix != 0.0, axis=0)]
artt = artt[np.any(wordmatrix != 0.0, axis=1)]
wordmatrix = wordmatrix[np.any(wordmatrix != 0.0, axis=1), :]


weights, feat = factorize(wordmatrix, pc=20, iter=50)
topp, pn = showfeatures(weights, feat, artt, wordvec)

print topp
print pn