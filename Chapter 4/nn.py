__author__ = 'Andrew'
from math import tanh
from sqlite3 import dbapi2 as sqlite

def dtanh(y):
    return 1.0-y*y

class searchnet:
    def __init__(self,dbname, layer_count=3):
        self.con=sqlite.connect(dbname)
        self.layer_count = layer_count

    def __del__(self):
        self.con.close()

    def close(self):
        self.dbcommit()
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def maketables(self):
        self.con.execute('create table hiddennode(create_key, layer)')
        self.con.execute('create table wordhidden(fromid,toid,strength)')
        self.con.execute('create table hiddenedge(fromid,toid,strength)')
        self.con.commit( )

    def getstrength(self,fromid,toid,layer):
        if layer==0: table='wordhidden'
        else: table='hiddenedge'
        res=self.con.execute('select strength from %s where fromid=%d and toid=%d' %
                             (table,fromid,toid)).fetchone()
        if res==None:
            if layer==0: return -0.2
            else: return 0
        return res[0]

    def setstrength(self,fromid,toid,layer,strength):
        if layer==0: table='wordhidden'
        else: table='hiddenedge'
        res=self.con.execute('select rowid from %s where fromid=%d and toid=%d' %
            (table,fromid,toid)).fetchone( )
        if res==None:
            self.con.execute('insert into %s (fromid,toid,strength) values (%d,%d,%f)' %
                (table,fromid,toid,strength))
        else:
            rowid=res[0]
            self.con.execute('update %s set strength=%f where rowid=%d' %
                (table,strength,rowid))

    def generatehiddennode(self,wordids,urls, layer):
        if len(wordids)>3: return None
        if layer == 0 or layer >= self.layer_count-1: return None
        # Check if we already created a node for this set of words
        createkey='_'.join(sorted([str(wi) for wi in wordids])) + '_l' + str(layer)
        res=self.con.execute(
            "select rowid from hiddennode where create_key='%s'" % createkey).fetchone()
        # If not, create it
        if res==None:
            cur=self.con.execute(
                "insert into hiddennode (create_key, layer) values ('%s', %d)" % (createkey, layer))
            hiddenid=cur.lastrowid
            # Put in some default weights
            if layer == 1:
                for wordid in wordids:
                    self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
            if layer == self.layer_count-2:
                for urlid in urls:
                    self.setstrength(hiddenid,urlid,layer,0.1)
            self.dbcommit()

    def getallhiddenids(self):
        result=[]
        cur=self.con.execute('select rowid, layer from hiddennode')
        for row in cur: result.append((row[0], row[1]))
        return result

    def setupnetwork(self, wordids, urlids):
        # value lists
        self.wordids=wordids
        self.hiddenids=self.getallhiddenids()
        self.urlids=urlids
        self.nodes = []
        self.nodes.extend([(wordid, 0) for wordid in self.wordids])
        self.nodes.extend(self.hiddenids)
        self.nodes.extend([(urlid, self.layer_count-1) for urlid in self.urlids])
        self.nodes_dict = {}
        for i in range(len(self.nodes)):
            self.nodes_dict[self.nodes[i][0]] = i

        # node outputs
        self.an = [1.0]*len(self.nodes)
        self.w = [[None for x in self.nodes] for y in self.nodes]
        lfrom = [t[0] for t in self.nodes if t[1] == 0]
        for layer in range(self.layer_count-1):
            lto = [t[0] for t in self.nodes if t[1] == layer+1]
            for fromid in lfrom:
                for toid in lto:
                    self.w[self.nodes_dict[fromid]][self.nodes_dict[toid]] \
                        = self.getstrength(fromid, toid, layer)
            lfrom = lto

    def print_network(self):
        print "input layer"
        for wordid in self.wordids:
            print wordid,
        print
        cur=self.con.execute('select fromid, toid, strength from wordhidden')
        for row in cur: print row[0], row[1], row[2]
        print


        for layer in range(1, self.layer_count-1):
            print "%d layer" % layer
            cur=self.con.execute('select rowid from hiddennode where layer=%d' % layer)
            nodes = [row[0] for row in cur]
            for node in nodes: print node,
            print
            cur=self.con.execute('select b.fromid, b.toid, b.strength from hiddennode a join hiddenedge b on a.rowid=b.fromid where a.layer=%d' % layer)
            for row in cur: print row[0], row[1], row[2]
            print

        print "output layer"
        for urlid in self.urlids:
            print urlid,
        print

    def feedforward(self):
        # the only inputs are the query words
        for wordid in self.wordids:
            self.an[self.nodes_dict[wordid]] = 1.0

        # hidden activations
        for layer in range(self.layer_count-1):
            for toid in [t[0] for t in self.nodes if t[1]==layer+1]:
                sum = 0.0
                for fromid in [t[0] for t in self.nodes if t[1]==layer]:
                    sum += self.an[self.nodes_dict[fromid]] \
                                * self.w[self.nodes_dict[fromid]][self.nodes_dict[toid]]
                self.an[self.nodes_dict[toid]] = tanh(sum)

        return [self.an[self.nodes_dict[t[0]]] for t in self.nodes if t[1] == self.layer_count-1]

    def getresult(self,wordids,urlids):
        self.setupnetwork(wordids,urlids)
        return self.feedforward()

    def backPropagate(self, targets, N=0.5):
        # calculate errors for output
        output_deltas = {}
        for k, urlid in enumerate(self.urlids) :
            error = targets[k]-self.an[self.nodes_dict[urlid]]
            output_deltas[urlid] = dtanh(self.an[self.nodes_dict[urlid]]) * error
        tonodes = [node[0] for node in self.nodes if node[1] == self.layer_count-1 ] # self.urlids

        for layer in range(self.layer_count-2, -1, -1):
            fromnodes = [node[0] for node in self.nodes if node[1] == layer ]
            new_output_deltas = {}
            for fromnodeid in fromnodes:
                error = 0.0
                for tonodeid in tonodes:
                    error += output_deltas[tonodeid]*self.w[self.nodes_dict[fromnodeid]][self.nodes_dict[tonodeid]]
                    change = output_deltas[tonodeid]*self.an[self.nodes_dict[fromnodeid]]
                    self.w[self.nodes_dict[fromnodeid]][self.nodes_dict[tonodeid]] += N*change
                new_output_deltas[fromnodeid] = dtanh(self.an[self.nodes_dict[fromnodeid]]) * error
            output_deltas = new_output_deltas
            tonodes = fromnodes


        # # calculate errors for output
        # output_deltas = [0.0] * len(self.urlids)
        # for k in range(len(self.urlids)):
        #     error = targets[k]-self.ao[k]
        #     output_deltas[k] = dtanh(self.ao[k]) * error
        #
        # # calculate errors for hidden layer
        # hidden_deltas = [0.0] * len(self.hiddenids)
        # for j in range(len(self.hiddenids)):
        #     error = 0.0
        #     for k in range(len(self.urlids)):
        #         error = error + output_deltas[k]*self.wo[j][k]
        #     hidden_deltas[j] = dtanh(self.ah[j]) * error
        #
        # # update output weights
        # for j in range(len(self.hiddenids)):
        #     for k in range(len(self.urlids)):
        #         change = output_deltas[k]*self.ah[j]
        #         self.wo[j][k] = self.wo[j][k] + N*change
        #
        #
        # # update input weights
        # for i in range(len(self.wordids)):
        #     for j in range(len(self.hiddenids)):
        #         change = hidden_deltas[j]*self.ai[i]
        #         self.wi[i][j] = self.wi[i][j] + N*change

    def trainquery(self,wordids,urlids,selectedurl):
        # generate a hidden node if necessary
        for layer in range(1, self.layer_count-1):
            self.generatehiddennode(wordids, urlids, layer)
        self.setupnetwork(wordids,urlids)
        self.feedforward()
        targets = [0.0]*len(urlids)
        targets[urlids.index(selectedurl)]=1.0
        error = self.backPropagate(targets)
        self.updatedatabase()

    def updatedatabase(self):
        for layer in range(0, self.layer_count-1):
            for toid in [t[0] for t in self.nodes if t[1]==layer+1]:
                for fromid in [t[0] for t in self.nodes if t[1]==layer]:
                    self.setstrength(fromid,
                                     toid,
                                     layer,
                                     self.w[self.nodes_dict[fromid]][self.nodes_dict[toid]])
        self.dbcommit()