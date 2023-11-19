import ptrFinance

# Used to make requests to an HTML webpage so that we can get the information back
import requests
# Used to import the module allowing us to make HTML requests to webpages
from requests_html import HTMLSession
# Import module for web scraping
from bs4 import BeautifulSoup
# For Training of K-Nearest Neighbor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
# Used to import the sentiment scoreboard for the text analyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# Used for reading Reddit Posts
from selenium import webdriver
from selenium.webdriver.common.by import By
#
from multiprocessing import Pool

import os
import csv
import math
import time
import ptrFinance
import pandas as pd

mainFile = os.path.abspath(os.path.dirname(__file__))

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

# Function used to check for keywords in specified link
def specificWebsiteSearch(link, keyWordsArr):
    # Dictionary used to store the article with its returned values
    articleDictionary = {}

    # Dicationary used to store the sentances of the website that match the keywords
    keywordDic = {}

    session = HTMLSession()
    requests = session.get(link).text

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

    # Return array with keywords
    return keywordDic

# Function used to check for keywords in a string - O(n)
    # "string" parameter is the string that we want searched
    # "keyWordsArr" is the array containing the keywords that the user wants to check for in the string
def stringKeywordFind(string, keyWordsArr):
    # The dictionary is used to contain the keyword with either a true or false statement
        # If its true, then the keyword is inside of the string
    returnDic = {}

    # For loop is used to iterate over the array to check for each keyword in the string
    for x in keyWordsArr:
        if x in string:
            returnDic[x] = True
        else:
            returnDic[x] = False

    return returnDic

# Function used to check if a string is positive or not - O(n)
def positiveOrNegativeString(string, positiveArray, negativeArray):
    # The variables are used to keep track of if the string is positive or not using a basic point system
    positive = 0
    negative = 0

    # For loop is used to iterate over the array to check for each keyword in the string
        # If its in there, then a point is added to the positive variable
    for x in positiveArray:
        if x in string:
            positive += 1

    for x in negativeArray:
        if x in string:
            negative += 1

    # The if else block below is used to check variables above, depending
    if positive > negative:
        return "Positive"
    elif negative > positive:
        return "Negative"
    else:
        return "Neutral"

# Machine Learning Section

# Function used to remove punctuation
def removePunctuation(sentance):
    punctuation = list(pd.read_csv("{currentDir}/punctuation.csv".format(currentDir = mainFile))["symbol"])

    # Replace Comma
    sentance = sentance.replace(",", " ")
    # Replace Quote
    sentance = sentance.replace("\"", " ")

    for x in punctuation:
        if x in sentance:
            sentance = sentance.replace(x, " ")

    return sentance

# Function used to remove numbers
def removeNumbers(sentance):
    filteredSentance = ""

    for x in sentance.split(" "):
        try:
            float(x)
            continue
        except ValueError:
            filteredSentance += x
            filteredSentance += " "

    return filteredSentance

# Function used to get rid of all stop words in the sentance
def ridStopWords(sentance):
    stopWords = list(pd.read_csv("{currentDir}/stopWords.csv".format(currentDir = mainFile))["Stop Words"])
    #
    sentance = removePunctuation(sentance)
    sentance = removeNumbers(sentance)

    filteredSentance = []

    # Iterate over the setnance
    for words in [x for x in sentance.split(" ") if x != ""]:
        if words.lower() not in stopWords:
            filteredSentance.append(words.lower())
        else:
            continue

    return filteredSentance

# Function used to add a score to the words
def determineWordsScore(filteredSentances):
    sentimentDictionary = {}

    for x in filteredSentances:
        # Check if the sentiment is positive
        if x[1] == [1,0,0]:
            for words in x[0]:
                if words in sentimentDictionary:
                    sentimentDictionary[words] += 0.005
                else:
                    sentimentDictionary[words] = 0.505

        # Check if the sentiment is negative
        elif x[1] == [0,1,0]:
            for words in x[0]:
                if words in sentimentDictionary:
                    sentimentDictionary[words] -= 0.005
                else:
                    sentimentDictionary[words] = 0.495

        # Check if the sentiment is neutral
        elif x[1] == [0,0,1]:
            for words in x[0]:
                if words not in sentimentDictionary:
                    sentimentDictionary[words] = 0.5

    return sentimentDictionary

# Function used to check the recorded sentiment of the sentence
def train(dataFrameRow):
    filteredSentances = []

    for x in range(len(dataFrameRow)):
        filteredSentance = ridStopWords(dataFrameRow["sentance"][x])

        filteredSentances.append([filteredSentance, list(dataFrameRow.loc[x, ["positive","negative","neutral"]])])

    saveSentiments(determineWordsScore(filteredSentances))

# Function used to write the sentiment of the words to a CSV file
def saveSentiments(sentimentDictionary):
    with open("{currentDir}/trainedWords.csv".format(currentDir = mainFile), "w", newline = "") as fileToWrite:
        writer = csv.writer(fileToWrite)

        writer.writerow(["word", "sentiment score"])

        for x in sentimentDictionary:
            try:
                writer.writerow([x, sentimentDictionary[x]])
            except:
                continue

#
def checkSentiment(sentance):
    stopWords = list(pd.read_csv("{currentDir}/stopWords.csv".format(currentDir = mainFile))["Stop Words"])
    #
    sentance = removePunctuation(sentance)
    sentance = removeNumbers(sentance)

    filteredSentance = []

    # Iterate over the setnance
    for words in [x for x in sentance.split(" ") if x != ""]:
        if words.lower() not in stopWords:
            filteredSentance.append(words.lower())
        else:
            continue

    del stopWords, sentance

    trainedWordsFilePath = os.path.join(mainFile, 'trainedWords.csv')

    trainedWords = pd.read_csv(trainedWordsFilePath, encoding='latin1')

    sentimentSum = 0

    #
    for x in filteredSentance:
        #
        if x in list(trainedWords["word"]):
            result = trainedWords[trainedWords["word"] == x]

            sentimentSum += (float(result["sentiment score"]))
        #
        else:
            sentimentSum += 0.5

    try:
        sentenceSentiment = sentimentSum / len(filteredSentance)

    except ZeroDivisionError:
        return "Neutral", 0.5

    #print(sentenceSentiment)

    if sentenceSentiment < 0.4:
        return "Negative", sentenceSentiment

    elif sentenceSentiment < 0.45 and sentenceSentiment > 0.4:
        return "Slightly Negative", sentenceSentiment

    elif sentenceSentiment > 0.6:
        return "Positive", sentenceSentiment

    elif sentenceSentiment <= 0.6 and sentenceSentiment > 0.55:
        return "Slightly Positive", sentenceSentiment

    else:
        return "Neutral", sentenceSentiment

#train(pd.read_csv("{currentDir}/ptrNaturalLanguage/training.csv".format(currentDir = os.getcwd()), encoding = "latin-1"))
