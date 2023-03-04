import ptrFinance

# Used to make requests to an HTML webpage so that we can get the information back
import requests
# Used to import the module allowing us to make HTML requests to webpages
from requests_html import HTMLSession
# Import module for web scraping
from bs4 import BeautifulSoup

# Function Used for Strings
    # Parameters are the stock name and the string array containg the titles of the articles
def stringCheckFunc(stockName, keyWordsArr = [], stringArr = []):
    # Array contains the titles of the stock that the user has selected
    articleTitles = [x for x in ptrFinance.returnMostRecentArticles(stockName) if x != ""]

    # Array used to contain the articles that meet the requirements
    returnArticles = []

    # First for loop used to iterate over the article title array
    for x in articleTitles:
        # For loop used to iterate and check if the keywords in the array are inside of the title
        for keywords in keyWordsArr:
            if keywords in x:
                returnArticles.append(articleTitles.index(x))

    # Contains the links to all of the articles for the specified stock
    links = ptrFinance.returnWebArticles(stockName)

    # Arrays used to contain the article headlines and links to articles respectively
    returnTitles = []
    returnLinks = []

    # For loop used to append all of the articles that meet the speicifed restrictions
    for x in returnArticles:
        returnTitles.append(articleTitles[x])
        returnLinks.append(links[x])

    return returnTitles, returnLinks

# Function used to read websites, and see if they match criteria
    # keyWordsArr - The parameter is used contain the keywords the user specifies
    # articleLinkArr - The parameter contains the links to the articles that the user chooses
def websiteSearch(keyWordsArr, articleLinkArr):
    for x in articleLinkArr:
        session = HTMLSession()
        requests = session.get(x).text

        soup = BeautifulSoup(requests, "html5lib")

        print(x)
        # Used to find all the paragraphs in the website, to check if the keywords are mentioned in them or not
        result = soup.findAll("p")
