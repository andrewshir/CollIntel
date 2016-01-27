import httplib
import ebay
from xml.dom.minidom import parse, parseString, Node
from ebaypredict2 import getItem


devKey = ebay.devKey
appKey = ebay.appKey
certKey = ebay.certKey
userToken = ebay.userToken
serverUrl = 'svcs.ebay.com'
endpoint = 'services/search/FindingService/v1'


def getHeaders():
    headers = {"X-EBAY-SOA-REQUEST-DATA-FORMAT": "XML",
               "X-EBAY-SOA-RESPONSE-DATA-FORMAT": "XML",
               "X-EBAY-SOA-SECURITY-APPNAME": appKey,
               "Content-Type": "text/xml"}
    return headers


def sendRequest(operation, xmlparameters):
    connection = httplib.HTTPConnection(serverUrl)
    url = endpoint + '?' + 'OPERATION-NAME=' + operation

    connection.request("POST", url, xmlparameters, getHeaders())
    response = connection.getresponse()
    if response.status != 200:
        print "Error sending request:" + response.reason
    else:
        data = response.read()
        connection.close()
    return data


def getSingleValue(node,tag):
    nl = node.getElementsByTagName(tag)
    if len(nl) > 0:
        tagNode = nl[0]
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    return '-1'


def doSearch(query, categoryID=None):
    xml = '<?xml version="1.0" encoding="UTF-8"?>' +\
        '<findItemsAdvancedRequest xmlns="http://www.ebay.com/marketplace/search/v1/services">' +\
        '<outputSelector>AspectHistogram</outputSelector>' +\
        '<itemFilter>' +\
        '<name>Condition</name><value>New</value>' +\
        '</itemFilter>'
    if categoryID is not None:
        xml += '<categoryId>' + str(categoryID) +'</categoryId>'
    xml += '<keywords>'+ query +'</keywords>' +\
        '</findItemsAdvancedRequest>'

    data = sendRequest('findItemsAdvanced', xml)
    response = parseString(data)
    itemNodes = response.getElementsByTagName('item')
    results = []
    for item in itemNodes:
        ritem = {}
        ritem['itemId'] = getSingleValue(item, 'itemId')
        ritem['title'] = getSingleValue(item, 'title')

        listingInfo = item.getElementsByTagName('listingInfo')
        if len(listingInfo) > 0:
            ritem['endTime'] = getSingleValue(listingInfo[0], 'endTime')

        sellingStatus = item.getElementsByTagName('sellingStatus')
        if len(sellingStatus) > 0:
            ritem['price'] = getSingleValue(sellingStatus[0], 'currentPrice')
            ritem['bids'] = getSingleValue(sellingStatus[0], 'bidCount')

        sellerInfo = item.getElementsByTagName('sellerInfo')
        if len(sellerInfo) > 0:
            ritem['seller'] = getSingleValue(sellerInfo[0], 'sellerUserName')
            ritem['feedback'] = getSingleValue(sellerInfo[0], 'feedbackScore')

        attributes = []
        for att in item.getElementsByTagName('attribute'):
            attName = getSingleValue(att, 'name')
            attValue = getSingleValue(att, 'value')
            attributes[attName] = attValue
        ritem['attributes'] = attributes

        results.append(ritem)
    return results


def take_first_number(s):
    str_result = ''
    for c in s:
        if c.isdigit():
            str_result += c
        else:
            break

    if str_result == '':
        return 0
    else:
        return int(str_result)

def makeLaptopDataset():
    searchResults = doSearch('laptop', categoryID=177)
    result = []
    for r in searchResults:
        item = getItem(r['itemId'])

        if item is None:
            continue

        att = item['attributes']
        try:
            data = (float(take_first_number(att['Memory'])), float(take_first_number(att['Hard Drive Capacity'])),
                    float(take_first_number(att['Screen Size'])),
                    float(item['feedback']))
            print data
            entry = {'input': data, 'result': float(item['price'])}
            result.append(entry)
        except:
            print item['title']+' failed'
    return result


# print doSearch('laptop', categoryID=177)[15]
data = makeLaptopDataset()
print data

