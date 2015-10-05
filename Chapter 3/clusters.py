__author__ = 'Andrew'

import path
import random
import math
from math import sqrt
from PIL import Image, ImageDraw


def readfile(filename):
    with open(filename, 'r') as f:
        lines = [line for line in f]

        # First line is the column titles
        colnames = lines[0].strip().split('\t')[1:]
        rownames = []
        data = []

        for line in lines[1:]:
            p = line.strip().split('\t')
            # First column in each row is the rowname
            rownames.append(p[0])
            # The data for this row is the remainder of the row
            data.append([float(x) for x in p[1:]])
        return rownames, colnames, data

############################################################################
#   Distance functions
############################################################################

def pearson(v1, v2):
    # Simple sums
    sum1 = sum(v1)
    sum2 = sum(v2)

    # Sums of the squares
    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])

    # Sum of the products
    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
    if den == 0: return 0
    return 1.0 - num / den


def euclide(v1, v2):
    result = 0
    for i in range(len(v1)):
        result += (v1[i] - v2[i]) ** 2
    return sqrt(result)


def manhatten(v1, v2):
    return sum([math.fabs(v1[i] - v2[i]) for i in range(len(v1))])


class bicluster(object):
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

############################################################################
#   Cluster functions
############################################################################

def hcluster(rows, distance=pearson):
    next_cluster_id = -1
    distances = {}

    clusters = []
    for i in range(len(rows)):
        clusters.append(bicluster(vec=rows[i], id=i))

    while len(clusters) > 1:
        # Find closest clusters
        closestClusters = (0, 1)
        closestDistance = distance(clusters[closestClusters[0]].vec, clusters[closestClusters[1]].vec)

        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                key = ("%s_%s" % (i, j))
                if key not in distances:
                    distances[key] = distance(clusters[i].vec, clusters[j].vec)

                d = distances[key]

                if d < closestDistance:
                    closestClusters = (i, j)
                    closestDistance = d


        # Merge clusters
        mergedvec = [float(clusters[closestClusters[0]].vec[t] + clusters[closestClusters[1]].vec[t]) / 2
                     for t in range(len(clusters[0].vec))]

        newcluster = bicluster(mergedvec, clusters[closestClusters[0]], clusters[closestClusters[1]],
                               closestDistance, next_cluster_id)
        next_cluster_id -= 1

        # Replace two closes clusters with a new one
        for to_delete in [clusters[closestClusters[0]], clusters[closestClusters[1]]]:
            clusters.remove(to_delete)
        clusters.append(newcluster)

    return clusters[0]

def turn_matrix(data):
    rows = []
    for i in range(len(data[0])):
        rows.append([data[j][i] for j in range(len(data))])
    return rows


def kmeans_cluster(rows, distance=pearson, n=4):
    # define range of values
    vrange = [(min([data[j][i] for j in range(len(data))]),
               max([data[j][i] for j in range(len(data))]))
              for i in range(len(data[0]))]

    # set initial centroids
    clusters = [[tup[0] + random.random() * (tup[1] - tup[0])
                 for tup in vrange]
                for k in range(n)]

    members = None

    lastMembers = None

    for iter in range(100):
        #print "Iteration %i" % iter

        # define cluster members
        members = [[] for k in range(n)]
        for i in range(len(rows)):
            row = rows[i]

            nearestCentroid = 0
            nearestD = distance(clusters[nearestCentroid], row)
            for k in range(n):
                d = distance(clusters[k], row)
                if d < nearestD:
                    nearestD = d
                    nearestCentroid = k

            members[nearestCentroid].append(i)

        if members == lastMembers:
            break

        lastMembers = members

        # move centroids
        for k in range(n):
            if len(members[k]) == 0:
                continue

            newcentroid = [sum([rows[i][j] for i in members[k]]) / float(len(members[k])) for j in range(len(rows[0]))]
            clusters[k] = newcentroid

    total_dist = 0
    for i in range(len(members)):
        for member in members[i]:
            total_dist += distance(clusters[i], rows[member])

    return (members, total_dist)

############################################################################
#   Auxiliary functions
############################################################################

def printclust(clust, labels=None, n=0):
    # indent to make a hierarchy layout
    for i in range(n): print ' ',
    if clust.id < 0:
        # negative id means that this is branch
        print '-'
    else:
        # positive id means that this is an endpoint
        if labels == None:
            print clust.id
        else:
            print labels[clust.id]
    # now print the right and left branches
    if clust.left != None: printclust(clust.left, labels=labels, n=n + 1)
    if clust.right != None: printclust(clust.right, labels=labels, n=n + 1)


def getheight(clust):
    # Is this an endpoint? Then the height is just 1
    if clust.left == None and clust.right == None: return 1
    # Otherwise the height is the same of the heights of
    # each branch
    return getheight(clust.left) + getheight(clust.right)


def getdepth(clust):
    # The distance of an endpoint is 0.0
    if clust.left == None and clust.right == None: return 0
    # The distance of a branch is the greater of its two sides
    # plus its own distance
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    # height and width
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)
    # width is fixed, so scale distances accordingly
    scaling = float(w - 150) / depth
    # Create a new image with a white background
    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.line((0, h / 2, 10, h / 2), fill=(255, 0, 0))
    # Draw the first node
    drawnode(draw, clust, 10, (h / 2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust.distance * scaling
        # Vertical line from this cluster to children
        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))
        # Horizontal line to left item
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))
        # Horizontal line to right item
        draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))
        # Call the function to draw the left and right nodes
        drawnode(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
        drawnode(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


############################################################################
#   Code to execute
############################################################################

blognames, words, data = readfile(path.data_path)

# Hierarchical clustering for blogs
#clust=hcluster(data)
# printclust(clust,labels=blognames)
#drawdendrogram(clust,blognames,jpeg=path.img_path)

# words clustering
# data = turn_matrix(data)
# clust=hcluster(data)
# drawdendrogram(clust,words,jpeg=path.img_path)

# K-means clustering
# for i in range(2,11):
#     print "#clusters - " + str(i),
#     avg = []
#     for j in range(5):
#         kclust, total_dist = kmeans_cluster(data, n=i)
#         avg.append(total_dist)
#         print "%d" % total_dist,
#     print "avg - %d" % (sum(avg) / float(len(avg)))

clust_number = 5
kclust, total_dist = kmeans_cluster(data, n=clust_number)
for i in range(clust_number):
    print [blognames[t] for t in kclust[i]]

print
clust_number = 5
kclust, total_dist = kmeans_cluster(data, distance=manhatten, n=clust_number)
for i in range(clust_number):
    print [blognames[t] for t in kclust[i]]
