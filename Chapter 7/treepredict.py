from PIL import Image,ImageDraw

my_data = [
    ['slashdot', 'USA', 'yes', 18, 'None'],
    ['google', 'France', 'yes', 23, 'Premium'],
    ['digg', 'USA', 'yes', 24, 'Basic'],
    ['kiwitobes', 'France', 'yes', 23, 'Basic'],
    ['google', 'UK', 'no', 21, 'Premium'],
    ['(direct)', 'New Zealand', 'no', 12, 'None'],
    ['(direct)', 'UK', 'no', 21, 'Basic'],
    ['google', 'USA', 'no', 24, 'Premium'],
    ['slashdot', 'France', 'yes', 19, 'None'],
    ['digg', 'USA', 'no', 18, 'None'],
    ['google', 'UK', 'no', 18, 'None'],
    ['kiwitobes', 'UK', 'no', 19, 'None'],
    ['digg', 'New Zealand', 'yes', 12, 'Basic'],
    ['slashdot', 'UK', 'no', 21, 'None'],
    ['google', 'UK', 'yes', 18, 'Basic'],
    ['kiwitobes', 'France', 'yes', 19, 'Basic']]


class decisionnde(object):
    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


def divideset(rows, column, value):
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    set_t = [row for row in rows if split_function(row)]
    set_f = [row for row in rows if not split_function(row)]
    return set_t, set_f


def uniquecounts(rows):
    result = {}
    for row in rows:
        r = row[len(row)-1]
        result.setdefault(r, 0)
        result[r] += 1
    return result



def gini_impurity(rows):
    """Probability that  a randomly placed element will be in the wrong category"""
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0.0

    for k1 in counts:
        p1 = float(counts[k1]) / total
        for k2 in counts:
            if k1 == k2: continue
            p2 = float(counts[k1]) / total
            imp += p1 * p2
    return imp


def entropy(rows):
    from math import log
    counts = uniquecounts(rows)
    total = len(rows)
    log2p = lambda x: log(x)/log(2)
    ent = 0.0

    for k in counts:
        p = float(counts[k]) / total
        ent = ent - p*log2p(p)
    return ent


def buildtree(rows, scoref=entropy):
    if len(rows) == 0: return decisionnde()
    current_score = scoref(rows)

    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1

    for col in xrange(column_count):
        column_values = set()
        for row in rows:
            column_values.add(row[col])

        for value in column_values:
            (set_t, set_f) = divideset(rows, col, value)

            p = float(len(set_t))/len(rows)
            gain = current_score - p*scoref(set_t)-(1-p)*scoref(set_f)
            if gain > best_gain and len(set_t) > 0 and len(set_f) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set_t, set_f)

    if best_gain > 0:
        print "Split %f to gain %f" % (current_score, best_gain)
        true_branch = buildtree(best_sets[0])
        false_branch = buildtree(best_sets[1])
        return decisionnde(col=best_criteria[0], value=best_criteria[1], tb=true_branch, fb=false_branch)
    else:
        return decisionnde(results=uniquecounts(rows))


def printtree(tree,indent=''):
    # Is this a leaf node?
    if tree.results!=None:
        print str(tree.results)
    else:
        # Print the criteria
        print str(tree.col)+':'+str(tree.value)+'? '
        # Print the branches
        print indent+'T->',
        printtree(tree.tb,indent+' ')
        print indent+'F->',
        printtree(tree.fb,indent+' ')

def getwidth(tree):
    if tree.tb==None and tree.fb==None: return 1
    return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):
    if tree.tb==None and tree.fb==None: return 0
    return max(getdepth(tree.tb),getdepth(tree.fb))+1


def drawtree(tree,jpeg='tree.jpg'):
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120
    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')


def drawnode(draw,tree,x,y):
    if tree.results==None:
        # Get the width of each branch
        w1=getwidth(tree.fb)*100
        w2=getwidth(tree.tb)*100
        # Determine the total space required by this node
        left=x-(w1+w2)/2
        right=x+(w1+w2)/2
        # Draw the condition string
        draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))
        # Draw links to the branches
        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
        # Draw the branch nodes
        drawnode(draw,tree.fb,left+w1/2,y+100)
        drawnode(draw,tree.tb,right-w2/2,y+100)
    else:
        txt=' \n'.join(['%s:%d'%v for v in tree.results.items( )])
        draw.text((x-20,y),txt,(0,0,0))

def classify(observation,tree):
    if tree.results != None:
        return tree.results
    else:
        v = observation[tree.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v >= tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        else:
            if v == tree.value:
                branch = tree.tb
            else:
                branch = tree.fb
        return classify(observation, branch)


def prune(tree,mingain):
    # If the branches aren't leaves, then prune them
    if tree.tb.results==None:
        prune(tree.tb,mingain)
    if tree.fb.results==None:
        prune(tree.fb,mingain)

    # If both the subbranches are now leaves, see if they
    # should merged
    if tree.tb.results!=None and tree.fb.results!=None:
        # Build a combined dataset
        tb,fb=[],[]
        for v,c in tree.tb.results.items( ):
            tb += [[v]]*c
        for v,c in tree.fb.results.items( ):
            fb += [[v]]*c
        # Test the reduction in entropy
        delta = entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)

        if delta < mingain:
            # Merge the branches
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb+fb)

# print gini_impurity(my_data)
# print entropy(my_data)
#
# tl, fl = divideset(my_data, 2, 'yes')
#
# print gini_impurity(tl)
# print gini_impurity(fl)
# print entropy(tl)
# print entropy(fl)

tree = buildtree(my_data)
# printtree(tree)
# drawtree(tree, jpeg='c:\\temp\\treeview.jpg')
# print classify(['(direct)','USA','yes',5],tree)

prune(tree,0.1)
printtree(tree)

prune(tree, 1)
printtree(tree)

