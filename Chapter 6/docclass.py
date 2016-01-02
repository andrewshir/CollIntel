# coding: utf-8
__author__ = 'Andrew'
import re
import math
import nltk.corpus
from nltk import SnowballStemmer

stopwords=frozenset(word for word in nltk.corpus.stopwords.words("russian"))
stemmer = SnowballStemmer('russian')
engChars = [ord(char) for char in u"cCyoOBaAKpPeE"]
rusChars = [ord(char) for char in u"сСуоОВаАКрРеЕ"]
eng_rusTranslateTable = dict(zip(engChars, rusChars))
rus_engTranslateTable = dict(zip(rusChars, engChars))

def getwords(doc):
    splitter = re.compile('\\W*')
    # split the words by non-alpha numeric
    words = [s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]

    # return the unique set of words only
    return dict((w, 1) for w in words)

def correctWord (w):
    """ Corrects word by replacing characters with written similarly depending on which language the word.
        Fraudsters use this technique to avoid detection by anti-fraud algorithms."""

    if len(re.findall(ur"[а-я]",w))>len(re.findall(ur"[a-z]",w)):
        return w.translate(eng_rusTranslateTable)
    else:
        return w.translate(rus_engTranslateTable)

def getwords_avito(text, stemmRequired = True, correctWordRequired = True):
    """ Splits the text into words, discards stop words and applies stemmer.
    Parameters
    ----------
    text : str - initial string
    stemmRequired : bool - flag whether stemming required
    correctWordRequired : bool - flag whether correction of words required
    """

    cleanText = re.sub(u'[^a-zа-я0-9]', ' ', text.lower())
    if correctWordRequired:
        words = [correctWord(w) if not stemmRequired or re.search("[0-9a-z]", w) else stemmer.stem(correctWord(w)) for w in cleanText.split() if len(w)>1 and w not in stopwords]
    else:
        words = [w if not stemmRequired or re.search("[0-9a-z]", w) else stemmer.stem(w) for w in cleanText.split() if len(w)>1 and w not in stopwords]

    return dict((w, 1) for w in words)

def sampletrain(cl):
    cl.train('Nobody owns the water.','good')
    cl.train('the quick rabbit jumps fences','good')
    cl.train('the quick brown fox jumps','good')
    cl.train('buy pharmaceuticals now','bad')
    cl.train('make quick money at the online casino','bad')

class classifier:
    def __init__(self, getfeatures, filename=None):
        # Counts of feature/category combinations
        self.fc={}
        # Counts of documents in each category
        self.cc={}
        self.getfeatures=getfeatures

    # Increase the count of a feature/category pair
    def incf(self,f,cat):
        self.fc.setdefault(f,{})
        self.fc[f].setdefault(cat,0)
        self.fc[f][cat]+=1

    # Increase the count of a category
    def incc(self,cat):
        self.cc.setdefault(cat,0)
        self.cc[cat]+=1

    # The number of times a feature has appeared in a category
    def fcount(self,f,cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    # The number of items in a category
    def catcount(self,cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    # The total number of items
    def totalcount(self):
        return sum(self.cc.values())

    # The list of all categories
    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features=self.getfeatures(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f,cat)

        # Increment the count for this category
        self.incc(cat)

    def fprob(self,f,cat):
        if self.catcount(cat)==0: return 0
        # The total number of times this feature appeared in this
        # category divided by the total number of items in this category
        return self.fcount(f,cat)/self.catcount(cat)

    def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
        # Calculate current probability
        basicprob=prf(f,cat)

        # Count the number of times this feature has appeared in
        # all categories
        totals=sum([self.fcount(f,c) for c in self.categories()])
        # Calculate the weighted average
        bp=((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp

    def get_top_features(self, top=10):
        freq = {}
        for f in self.fc.keys():
            for cat in self.categories():
                freq.setdefault(cat, {})
                if cat in self.fc[f]:
                    freq[cat][f] = (f, self.fc[f][cat])
        result = {}
        for cat in self.categories():
            result[cat] = sorted(freq[cat].values(), reverse=True, key=lambda (f,x):x)[:top]
        return result

class naivebayes(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self,getfeatures)
        self.thresholds = {}

    def setthreshold(self,cat,t):
        self.thresholds[cat]=t

    def getthreshold(self,cat):
        if cat not in self.thresholds: return 1.0
        return self.thresholds[cat]

    def docprob(self,item,cat):
        features=self.getfeatures(item)
        # Multiply the probabilities of all the features together
        p=1
        for f in features:
            p *= self.weightedprob(f,cat, self.fprob)
        return p

    def prob(self,item,cat):
        catprob=self.catcount(cat)/self.totalcount()
        docprob=self.docprob(item,cat)
        return docprob*catprob

    def classify(self, item, default=None, target_cat=None):
        probs={}
        # Find the category with the highest probability
        max=0.0
        for cat in self.categories( ):
            probs[cat]=self.prob(item,cat)
            if probs[cat]>=max:
                max=probs[cat]
                best=cat

        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat==best: continue
            if probs[cat]*self.getthreshold(best) > probs[best]: return default
        return best, max if best == target_cat else -max


class fisherclassifier(classifier):
    def __init__(self, getfeatures):
        classifier.__init__(self,getfeatures)
        self.minimums={}

    def cprob(self,f,cat):
        # The frequency of this feature in this category
        clf=self.fprob(f,cat)
        if clf==0: return 0

        # The frequency of this feature in all the categories
        freqsum=sum([self.fprob(f,c) for c in self.categories()])
        # The probability is the frequency in this category divided by
        # the overall frequency
        p=clf/(freqsum)
        return p

    def fisherprob(self,item,cat):
        # Multiply all the probabilities together
        p=1
        features=self.getfeatures(item)
        for f in features:
            p*=(self.weightedprob(f,cat,self.cprob))

        if p == 0.0:
            return 0.0

        # Take the natural log and multiply by -2
        fscore=-2*math.log(p)

        # Use the inverse chi2 function to get a probability
        return self.invchi2(fscore,len(features)*2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m / i
            sum += term
        return min(sum, 1.0)

    def setminimum(self,cat,min):
        self.minimums[cat]=min

    def getminimum(self,cat):
        if cat not in self.minimums: return 0
        return self.minimums[cat]

    def classify(self,item,default=None, target_cat=None):
        # Loop through looking for the best result
        best=default
        max=0.0
        for c in self.categories():
            p=self.fisherprob(item,c)
            # Make sure it exceeds its minimum
            if p>self.getminimum(c) and p>max:
                best=c
                max=p

        return best, max if target_cat == best else -max

# cl = fisherclassifier(getwords)
# sampletrain(cl)
# print cl.classify('quick rabbit', default='unknown')
# print cl.classify('quick money', default='unknown')
# print cl.classify('water', default='unknown')