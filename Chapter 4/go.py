__author__ = 'Andrew'
import searchengine
import nn

# crawler = searchengine.crawler('searchindex.db')
# # crawler.createindextables()
# # crawler.crawl(['https://en.wikipedia.org/wiki/List_of_programming_languages'], 2, 50)
# print crawler.con.execute('select count(*) from wordlocation where urlid<>1').fetchone()
# crawler.close()

# e=searchengine.searcher('searchindex.db')
# print e.query('procedural language')
# e.calculatepagerank()
# e.close()

mynet=nn.searchnet('nn.db')
# mynet.maketables()
wWorld,wRiver,wBank = 101, 102, 103
uWorldBank,uRiver,uEarth = 201, 202, 203
# mynet.generatehiddennode([wWorld,wBank],[uWorldBank,uRiver,uEarth])
# for c in mynet.con.execute('select * from wordhidden'): print c
# for c in mynet.con.execute('select * from hiddenurl'): print c
mynet.trainquery([wWorld,wBank], [uWorldBank,uRiver,uEarth], uWorldBank)
print mynet.getresult([wWorld,wBank],[uWorldBank,uRiver,uEarth])
mynet.close()
