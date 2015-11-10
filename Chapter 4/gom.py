__author__ = 'Andrew'
import nnm

mynet=nnm.searchnet('nnm.db', 4)
mynet.maketables()

wWorld,wRiver,wBank = 101, 102, 103
uWorldBank,uRiver,uEarth = 201, 202, 203
allurls=[uWorldBank,uRiver,uEarth]

# mynet.setupnetwork([wWorld,wBank], allurls)
# mynet.print_network()

# mynet.trainquery([wWorld,wBank], allurls, uWorldBank)
# mynet.print_network()

# print mynet.getresult([wRiver,wBank],allurls)
# print mynet.getresult([wBank],allurls)

max_rate = 5.0

for i in range(30):
    mynet.trainquery([wWorld,wBank],[(uWorldBank, 3/max_rate),(uRiver, 0), (uEarth, 0)])
    mynet.trainquery([wRiver,wBank],[(uWorldBank, 0),(uRiver, 3/max_rate), (uEarth, 0)])
    # mynet.trainquery([wWorld],[(uWorldBank, 0),(uRiver, 0), (uEarth, 3/max_rate)])



mynet.print_network()

print mynet.getresult([wBank],allurls)


mynet.close()

