__author__ = 'Andrew'
import searchengine

# crawler = searchengine.crawler('searchindex.db')
# # crawler.createindextables()
# # crawler.crawl(['https://en.wikipedia.org/wiki/List_of_programming_languages'], 2, 50)
# print crawler.con.execute('select count(*) from wordlocation where urlid<>1').fetchone()
# crawler.close()

e=searchengine.searcher('searchindex.db')
print e.query('procedural language')
# e.calculatepagerank()
e.close()