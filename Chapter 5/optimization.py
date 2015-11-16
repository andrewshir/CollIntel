__author__ = 'Andrew'
import time
import sys
import random
import math

working_path = "C:\\Users\\Andrew\\Source\\Repos\\CollIntel\\Chapter 5\\"

people = [('Seymour','LED'),
          ('Franny','AER'),
          ('Zooey','SVX'),
          ('Walt','ROV')]

destination='DME'



def getminutes(t):
    x=time.strptime(t,'%H:%M')
    return x[3]*60+x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name=people[d][0]
        origin=people[d][1]
        out=flights[(origin,destination)][r[d*2]]
        ret=flights[(destination,origin)][r[d*2+1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,
                                                      out[0],out[1],out[2],
                                                      ret[0],ret[1],ret[2])

def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60

    for d in range(len(sol)/2):
        # Get the inbound and outbound flights
        origin=people[d][1]
        outbound=flights[(origin,destination)][int(sol[d*2])]
        returnf=flights[(destination,origin)][int(sol[d*2+1])]

        # Total price is the price of all outbound and return flights
        totalprice+=outbound[2]
        totalprice+=returnf[2]

        # Track the latest arrival and earliest departure
        if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
        if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])

    # Every person must wait at the airport until the latest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait=0
    for d in range(len(sol)/2):
        origin=people[d][1]
        outbound=flights[(origin,destination)][int(sol[d*2])]
        returnf=flights[(destination,origin)][int(sol[d*2+1])]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep

    # Does this solution require an extra day of car rental? That'll be $50!
    if latestarrival>earliestdep: totalprice+=50
    return totalprice+totalwait

def random_optimization(domain, cost, iter=1000):
    best = sys.maxint
    result = None

    for j in xrange(iter):
        s = []
        for i in xrange(len(domain)):
            s.append(random.randint(0, domain[i])-1)

        c = cost(s)
        if c < best:
            best = c
            result = s
    return result, best

def hill_climb_optimization(domain, cost):
    best = sys.maxint
    result = None

    # define random initial solution
    s = []
    for i in xrange(len(domain)):
        s.append(random.randint(0, domain[i])-1)
    best_n = cost(s)

    while best_n < best:
        best = best_n
        result = s
        best_n = sys.maxint
        neighbors = []
        for i in xrange(len(s)):
            if s[i] < domain[i]-1:
                n = []
                n.extend(s)
                n[i] = n[i] + 1
                neighbors.append(n)
            if s[i] > 0:
                n = []
                n.extend(s)
                n[i] = n[i] - 1
                neighbors.append(n)

        for neighbor in neighbors:
            c = cost(neighbor)
            if c < best_n:
                best_n = c
                s = neighbor
    return result, best

def generic_simulated_annealing_optimization(domain, costf):
    best = sys.maxint
    result = None
    for i in xrange(15):
        sol, cost = simulated_annealing_optimization(domain, costf)
        if cost < best:
            result = sol
            best = cost
    return result, best

def simulated_annealing_optimization(domain, costf, T=10000, cooldown=0.95):
    #initial solution
    sol = [random.randint(0, x-1) for x in domain]
    cost = costf(sol)

    while T > 1.0:
        nsol = []
        nsol.extend(sol)
        c = random.randint(0, len(domain)-1)
        if random.random() < 0.5 and sol[c] < domain[c]-1:
            nsol[c] = sol[c] + 1
        elif sol[c] > 0:
            nsol[c] = sol[c] - 1

        ncost = costf(nsol)
        p = pow(math.e, (-ncost-cost)/float(T))

        if random.random() < p or ncost < cost:
            sol = nsol
            cost = ncost

        T *= cooldown
    return sol, cost

def genetic_optimization(domain, costf, popsize=50, elite=0.2, mutprob=0.3, not_changed_cost_count=50):
    def mutate(sol):
        result = []
        result.extend(sol)
        c = random.randint(0, len(domain)-1)
        if random.random() < 0.5 and sol[c] > 0:
            result[c] -= 1
        elif sol[c] < domain[c]-1:
            result[c] += 1
        return result

    def crossover(sol1, sol2):
        result = []
        c = random.randint(1, len(domain)-2)
        result = sol1[0:c] + sol2[c:]
        return result

    def all_the_same(list):
        if len(list) < 2:
            return False
        for el in list:
            if el != list[0]:
                return False
        return True

    # initial population
    pop = []
    for i in xrange(50):
        pop.append([random.randint(0, x-1) for x in domain])

    latest_sol = []

    while not all_the_same(latest_sol):
        # define best solutions
        scored_pop = [(costf(s), s) for s in pop]
        scored_pop.sort(key=lambda tup: tup[0])
        topsol = int(elite*len(scored_pop))

        pop = []
        pop.extend([tup[1] for tup in scored_pop[0:topsol]])
        while len(pop) < popsize:
            if random.random() < mutprob:
                # mutation
                c = random.randint(0, topsol-1)
                pop.append(mutate(pop[c]))
            else:
                # crossover
                c1 = random.randint(0, topsol-1)
                c2 = random.randint(0, topsol-1)

                # to be sure we don't cross the same solution
                while c1 == c2:
                    c1 = random.randint(0, topsol-1)
                    c2 = random.randint(0, topsol-1)

                pop.append(crossover(pop[c1], pop[c2]))

        latest_sol.append(scored_pop[0][0])
        if len(latest_sol) > not_changed_cost_count:
            latest_sol.remove(latest_sol[0])
        print scored_pop[0][0]

    return scored_pop[0][1], scored_pop[0][0]

flights = {}
for line in file(working_path + 'schedule.txt'):
    origin,dest,depart,arrive,price=line.strip().split(',')
    flights.setdefault((origin,dest),[])

    # Add details to the list of possible flights
    flights[(origin,dest)].append((depart,arrive,int(price)))

# s = [1 for x in xrange(8)]
# printschedule(s)
# print schedulecost(s)
domain= [11, 12, 6, 5, 10, 8, 7, 8]
# sol, cost = hill_climb_optimization(domain, schedulecost)
# sol, cost = generic_simulated_annealing_optimization(domain, schedulecost)
sol, cost = genetic_optimization(domain, schedulecost)
print "Cost = " + str(cost)
printschedule(sol)
#35570 - annealing
