import ptrFinance

# Used to make requests to an HTML webpage so that we can get the information back
import requests
# Used to import the module allowing us to make HTML requests to webpages
from requests_html import HTMLSession
# Import module for web scraping
from bs4 import BeautifulSoup

# Function Used to find the articles that contain the keywords in their titles, returning the titles with the links - O(n^2)
    # Parameters are the stock name and the string array containg the titles of the articles
def stringCheckFunc(stockName, keyWordsArr = []):
    # Array contains the titles of the stock that the user has selected
    articleTitles = [x for x in ptrFinance.returnMostRecentArticles(stockName) if x != ""]

    # Contains the links to all of the articles for the specified stock
    links = ptrFinance.returnWebArticles(stockName)

    # Dictionary used to contain the articles and their links that meet the requirements
    returnArticles = {}

    # First for loop used to iterate over the article title array
    for x in articleTitles:
        # For loop used to iterate and check if the keywords in the array are inside of the title
        for keywords in keyWordsArr:
            if keywords.lower() in x.lower():
                returnArticles[x] = links[articleTitles.index(x)]

    # The return statement will return the dictionary containig the titles of the website and their links
    return returnArticles

# Function used to read websites, and see if they match criteria
    # keyWordsArr - The parameter is used contain the keywords the user specifies
def websiteSearch(stockName, keyWordsArr):
    # Dictionary used to store the article with its returned values
    articleDictionary = {}

    # Variable contains a dictionary with the title of the articles for the specified stock, and their respecitve links
    namesOfArticles = ptrFinance.returnArticleAndLink(stockName)

    for x in namesOfArticles.values():
        # Dicationary used to store the sentances of the website that match the keywords
        keywordDic = {}

        session = HTMLSession()
        requests = session.get(x).text

        soup = BeautifulSoup(requests, "html5lib")

        # Used to find all the paragraphs in the website, to check if the keywords are mentioned in them or not
        result = soup.findAll("p")
        # The result variable contains the text of the paragraphs
        result = [paragraphs.text for paragraphs in result]
        # For loop used to check if the keywords are in the website's paragraphs
        for keywords in keyWordsArr:
            for paragraphs in result:
                if keywords in paragraphs:
                    # Adding the new keyword into the dictionary
                    keywordDic[keywords] = []
                    # If the paragraph contains the keyword that we're looking for, then we add it to its respective dictionary key
                    keywordDic[keywords].append(paragraphs)

        # If-Else block used to remove all articles that don't have the keywords specified.
        if len(keywordDic) == 0:
            continue
        else:
            articleDictionary[list(namesOfArticles.keys())[list(namesOfArticles.values()).index(x)]] = keywordDic

    # Return dictionary with keywords
    return articleDictionary
