__author__ = 'Andrew'
from math import tanh
from sqlite3 import dbapi2 as sqlite

class searchnet:
    def __init__(self,dbname):
        self.con=sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def close(self):
        self.dbcommit()
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def maketables(self):
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid,toid,strength)')
        self.con.execute('create table hiddenurl(fromid,toid,strength)')
        self.con.commit( )

    def getstrength(self,fromid,toid,layer):
        if layer==0: table='wordhidden'
        else: table='hiddenurl'
        res=self.con.execute('select strength from %s where fromid=%d and toid=%d' %
            (table,fromid,toid)).fetchone()
        if res==None:
            if layer==0: return -0.2
            if layer==1: return 0
        return res[0]

    def setstrength(self,fromid,toid,layer,strength):
        if layer==0: table='wordhidden'
        else: table='hiddenurl'
        res=self.con.execute('select rowid from %s where fromid=%d and toid=%d' %
            (table,fromid,toid)).fetchone( )
        if res==None:
            self.con.execute('insert into %s (fromid,toid,strength) values (%d,%d,%f)' %
                (table,fromid,toid,strength))
        else:
            rowid=res[0]
            self.con.execute('update %s set strength=%f where rowid=%d' %
                (table,strength,rowid))

    def generatehiddennode(self,wordids,urls):
        if len(wordids)>3: return None
        # Check if we already created a node for this set of words
        createkey='_'.join(sorted([str(wi) for wi in wordids]))
        res=self.con.execute(
            "select rowid from hiddennode where create_key='%s'" % createkey).fetchone()
        # If not, create it
        if res==None:
            cur=self.con.execute(
                "insert into hiddennode (create_key) values ('%s')" % createkey)
            hiddenid=cur.lastrowid
            # Put in some default weights
            for wordid in wordids:
                self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid,urlid,1,0.1)
            self.dbcommit()

    def getallhiddenids(self, wordids, urlids):
        l1={}
        for wordid in wordids:
            cur=self.con.execute(
                'select toid from wordhidden where fromid=%d' % wordid)
            for row in cur: l1[row[0]]=1
        for urlid in urlids:
            cur=self.con.execute(
                'select fromid from hiddenurl where toid=%d' % urlid)
            for row in cur: l1[row[0]]=1
        return l1.keys()

    def setupnetwork(self, wordids, urlids):
        # value lists
        self.wordids=wordids
        self.hiddenids=self.getallhiddenids(wordids,urlids)
        self.urlids=urlids

        # node outputs
        self.ai = [1.0]*len(self.wordids)
        self.ah = [1.0]*len(self.hiddenids)
        self.ao = [1.0]*len(self.urlids)

        # create weights matrix
        self.wi = [[self.getstrength(wordid,hiddenid,0)
            for hiddenid in self.hiddenids]
            for wordid in self.wordids]
        self.wo = [[self.getstrength(hiddenid,urlid,1)
            for urlid in self.urlids]
            for hiddenid in self.hiddenids]