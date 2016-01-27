import httplib
import ebay
from xml.dom.minidom import parse, parseString, Node


devKey = ebay.devKey
appKey = ebay.appKey
certKey = ebay.certKey
userToken = ebay.userToken
serverUrl = 'api.ebay.com'


def getHeaders(apicall,siteID="0",compatabilityLevel = "433"):
    headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
        "X-EBAY-API-DEV-NAME": devKey,
        "X-EBAY-API-APP-NAME": appKey,
        "X-EBAY-API-CERT-NAME": certKey,
        "X-EBAY-API-CALL-NAME": apicall,
        "X-EBAY-API-SITEID": siteID,
        "Content-Type": "text/xml"}
    return headers


def sendRequest(apicall,xmlparameters):
    connection = httplib.HTTPSConnection(serverUrl)
    connection.request("POST", '/ws/api.dll', xmlparameters, getHeaders(apicall))
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


def getItem(itemID):
    xml = "<?xml version='1.0' encoding='utf-8'?>"+\
        "<GetItemRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
        "<RequesterCredentials><eBayAuthToken>" +\
        userToken +\
        "</eBayAuthToken></RequesterCredentials>" + \
        "<ItemID>" + str(itemID) + "</ItemID>"+\
        "<DetailLevel>ItemReturnAttributes</DetailLevel>"+\
        "<IncludeItemSpecifics>true</IncludeItemSpecifics>"+\
        "</GetItemRequest>"

    data = sendRequest('GetItem', xml)
    result = {}
    response = parseString(data)
    result['title'] = getSingleValue(response, 'Title')
    sellingStatusNode = response.getElementsByTagName('SellingStatus')
    if len(sellingStatusNode) == 0:
        return None
    result['price'] = getSingleValue(sellingStatusNode[0], 'CurrentPrice')
    result['bids'] = getSingleValue(sellingStatusNode[0], 'BidCount')
    seller = response.getElementsByTagName('Seller')
    if len(seller) == 0:
        return None
    result['feedback'] = getSingleValue(seller[0], 'FeedbackScore')

    # print data

    attr_root = response.getElementsByTagName('ItemSpecifics')
    if len(attr_root) == 0:
        return None

    attributeSet = attr_root[0].getElementsByTagName('NameValueList')
    attributes = {}
    for att in attributeSet:
        attID=getSingleValue(att, 'Name')
        attValue=getSingleValue(att, 'Value')
        attributes[attID] = attValue

    result['attributes'] = attributes
    return result

