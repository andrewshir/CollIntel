from random import random,randint
import math
import optimization

def wineprice(rating,age):
    peak_age=rating-50
    # Calculate price based on rating
    price=rating/2
    if age>peak_age:
        # Past its peak, goes bad in 5 years
        price=price*(5-(age-peak_age))
    else:
        # Increases to 5x original value as it
        # approaches its peak
        price=price*(5*((age+1)/peak_age))
    if price<0: price=0
    return price


def wineset1():
    rows = []
    for i in range(300):
        # Create a random age and rating
        rating = random()*50+50
        age = random()*50
        # Get reference price
        price = wineprice(rating, age)
        # Add some noise
        price *= (random()*0.4+0.8)
        # Add to the dataset
        rows.append({'input': (rating, age), 'result':price})
    return rows


def wineset2():
    rows = []
    for i in range(300):
        # Create a random age and rating
        rating = random()*50+50
        age = random()*50
        aisle=float(randint(1,20))
        bottlesize=[375.0,750.0,1500.0,3000.0][randint(0,3)]
        # Get reference price
        price = wineprice(rating, age)
        price*=(bottlesize/750)
        # Add some noise
        price *= (random()*0.4+0.8)
        # Add to the dataset
        rows.append({'input' : (rating, age, aisle, bottlesize), 'result':price})
    return rows


def wineset3():
    rows = wineset1()
    for row in rows:
        if random() < 0.5:
            # Wine was bought at a discount store
            row['result'] *= 0.6
    return rows


def euclidean(v1, v2):
    sum = 0.0
    for i in xrange(len(v1)):
        sum += (v1[i] - v2[i]) ** 2
    return math.sqrt(sum)


def getdistances(data, vec1):
    distancelist = []
    for i in range(len(data)):
        vec2 = data[i]['input']
        distancelist.append((euclidean(vec1, vec2), i))
    distancelist.sort()
    return distancelist


def knnestimate(data, vec1, k=3):
    dlist=getdistances(data, vec1)
    avg = 0.0

    for i in xrange(k):
        idx = dlist[i][1]
        avg += data[idx]['result']

    avg = avg/k
    return avg


def inverseweight(dist, num=1.0, const=0.1):
    return num/(dist+const)


def subtractweight(dist, const=1.0):
    if dist > const:
        return 0
    else:
        return const-dist


def gaussian(dist, sigma=10.0):
    return math.e**(-dist**2/(2*sigma**2))


def weightknn(data, vec1, k=3, weightf=gaussian):
    dlist=getdistances(data, vec1)
    avg = 0.0
    totalweight = 0.0

    for i in xrange(k):
        dist = dlist[i][0]
        idx = dlist[i][1]
        weight = weightf(dist)
        avg += weight*data[idx]['result']
        totalweight += weight

    avg = avg/totalweight
    return avg


def dividedata(data,test=0.05):
    trainset = []
    testset = []
    for row in data:
        if random() < test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset, testset


def testalgorithm(algf, trainset, testset):
    error = 0.0
    for row in testset:
        guess = algf(trainset, row['input'])
        error += (row['result']-guess)**2
    return error/len(testset)


def crossvalidate(algf, data, trials=100, test=0.05):
    error = 0.0
    for i in range(trials):
        trainset, testset = dividedata(data, test)
        error += testalgorithm(algf, trainset, testset)
    return error/trials


def rescale(data, scale):
    scaleddata = []
    for row in data:
        scaled = [scale[i]*row['input'][i] for i in range(len(scale))]
        scaleddata.append({'input': scaled, 'result': row['result']})
    return scaleddata

def createcostfunction(algf, data):
    def costf(scale):
        sdata=rescale(data, scale)
        return crossvalidate(algf, sdata, trials=10)
    return costf

# data = wineset1()
# print data[0]
# print data[1]
# print wineprice(95.0, 3.0)


def knn1(d, v):
    return knnestimate(d, v, k=1)


def knn3(d, v):
    return knnestimate(d, v, k=3)

# data = wineset2()
#
# scales = [1, 1, 1, 1]
# print scales
# sdata = rescale(data, scales)
# print crossvalidate(knn3, sdata)
# print crossvalidate(knn3, sdata)
# print
#
# scales = [8, 1, 18, 16]
# print scales
# sdata = rescale(data, scales)
# print crossvalidate(knn3, sdata)
# print crossvalidate(knn3, sdata)
# print
#
#
# costf = createcostfunction(knnestimate, data)
# weightdomain = [20] * 4
# scales, value = optimization.simulated_annealing_optimization(weightdomain, costf)
# print scales
# sdata = rescale(data, scales)
# print crossvalidate(knn3, sdata)
# print crossvalidate(knn3, sdata)
# print

