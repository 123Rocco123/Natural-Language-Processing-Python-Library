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

# Function used for "sentence segmentation"
    # AKA Splitting the sentances
def sentenceSegmentation(inputText):
    # Used to split up the inputted text into seperate sentances
    seperatedText = inputText.split(".")
    # Used to remove empty string from the returned array
    seperatedText = [x for x in seperatedText if x != ""]
    return seperatedText

# Function used to change the words into their most basic form of the word
def lemmazation(wordsArray):
    # Used to contain the lemmanized words with thein non lemmanized versions
    returnArray = {}

    for word in wordsArray:
        try:
            session = HTMLSession()
            requests = session.get("https://dictionary.cambridge.org/dictionary/english/{word}".format(word = word)).text
            soup = BeautifulSoup(requests, "html5lib")

            #print(word)

            # Used in case of a stock name
            try:
                if soup.find("div", {"class" : "def ddef_d db"}).find("span", {"class" : "x-h dx-h"}) != None:
                    returnArray[word] = soup.find("div", {"class" : "def ddef_d db"}).find("span", {"class" : "x-h dx-h"}).text
            except:
                pass
                #print("test")
        except:
            continue

    return returnArray

# Function has the goal of identifying the main verb of a sentence
def findMainVerb(textArray):
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    # Function used to scrape information from the main page
    driver = webdriver.Chrome(options = chrome_options)
    # Used to contain the verbs that are in the input text
    verbs = []

    for words in textArray:
        driver.get("https://www.google.com/search?q=is+{word}+a+verb".format(word = words))

        try:
            if driver.find_element(By.CSS_SELECTOR, "[class*='YrbPuc']").text == "verb":
                verbs.append(driver.find_element(By.CSS_SELECTOR, "[class*='YrbPuc']").text == "verb")
        except:
            continue

    # The two different returns are which of the elements are verbs in the string
        # The second one returning the dominant verb
    return verbs, verbs[0]

# Function used to find the subject of the sentance
def findSubject(wordsArray, filteredWords, positionOfRoot):
    for x in wordsArray:
        if wordsArray.index(x) < positionOfRoot and x in filteredWords:
            return x

# Function is used to return if the sentance is positive or negative
def sentimentDetermination(wordsArray):
    score = 0

    for x in wordsArray:
        for letters in x:
            score += ord(letters)

    scoreAndClassificationDF = pd.DataFrame(columns = ["Score", "Positive", "Negative", "Neutral"])

    # Open function used to read the training data
    with open("{currentDir}/ptrNaturalLanguage/training.csv".format(currentDir = os.getcwd()), "r") as sentimentDeterminationTraining:
        reader = csv.reader(sentimentDeterminationTraining)
        next(reader)

        for x in reader:
            score = 0
            for word in x[0].split(" "):
                for letter in word:
                    score += ord(letter)

            # Appends the new row to the DataFrame
            scoreAndClassificationDF = scoreAndClassificationDF.append({"Score" : score,
                                                                        "Positive" : x[1],
                                                                        "Negative" : x[2],
                                                                        "Neutral" : x[3]
                                                                        },

                                                                        ignore_index = True)

    x = scoreAndClassificationDF[["Score"]]
    y = scoreAndClassificationDF[["Positive", "Neutral","Negative"]]

    # Used to contain our test and train data
    x_train, x_test, y_train, y_test = train_test_split(x,y,train_size=0.8, test_size=0.2)

    # StandardScaler used to normalize the data
    scaler = StandardScaler()
    scaler.fit(x_train)

    x_train = scaler.transform(x_train)
    x_test = scaler.transform(x_test)

    # Used to contain the algorithm for determining the nearest neighbor
    classifier = KNeighborsClassifier(n_neighbors = 5)
    classifier.fit(x_train, y_train)

    #print(classifier.predict([[score]]))

# Function used to check that no numbers are in the string / word
def checkIfNumInString(string):
    return any(char.isdigit() for char in string)

# Function used for tokenization
    # AKA splitting the sentances into words
def tokenization(inputText):
    stopWords = pd.read_csv("{currentDir}/ptrNaturalLanguage/stopWords.csv".format(currentDir = os.getcwd()))
    stopWords = list(stopWords["Stop Words"])

    for x in sentenceSegmentation(inputText):
        # Used to split up the inputted text into seperate words
        words = x.split(" ")
        # Used to remove empty string from the returned array
            # We also make sure that there is no percentage in the word
            # As well as making sure that we remove any and all strings that contain numbers as they can't feasibly have sentiment
        words = [x for x in words if x != "" and "%" not in x and checkIfNumInString(x) == False]
        # Used to contain the words that passed the stopWords for loop
        filteredWords = []
        filteredWordsType = []

        # Used to move all of the words that we currently have in the array to their most basic form
        lemmaOfWords = lemmazation(words)

        for lemma in lemmaOfWords:
            words[words.index(lemma)] = lemmaOfWords[lemma]

        # Used to classify the words
        for wordsToSearch in words:
            # Condition is used to make sure that we get rid of the "stopWords"
            if wordsToSearch.lower() in stopWords:
                continue
            else:
                # Used in case there is some issue with connecting to the dictionary for any reason
                try:
                    # Used to check for the word on the dictionary
                    session = HTMLSession()
                    requests = session.get("https://dictionary.cambridge.org/dictionary/english/{searchedWord}".format(searchedWord = wordsToSearch)).text
                    soup = BeautifulSoup(requests, "html5lib")

                    try:
                        filteredWords.append(wordsToSearch)
                        filteredWordsType.append(soup.find("span", {"class" : "pos dpos"}).text)
                    except:
                        pass

                    del session
                    del requests
                    del soup

                except:
                    continue

        return filteredWords

        # Variables used to contain the root of the sentance and the verbs
        #verbs, root = findMainVerb(words)
        # Variable used to contain the subject of the sentance
        #subject = findSubject(words, filteredWords, words.index(root))

        # Pass in the training data to the function for classification of the sentence sentiment
        #sentimentDetermination(filteredWords)

#tokenization("Tesla stock is overvalued")

"""
# Pass the data into the training csv
with open("{currentDir}/ptrNaturalLanguage/training.csv".format(currentDir = os.getcwd()), "a") as fileToAppendTo:
    writer = csv.writer(fileToAppendTo)

    # For loop used to iterate over the parameter containing the dataframe
        # This will make it so that we write the user specified data to the training csv
    for x in range(len(data)):
        writer.writerow[list(data.iloc[x])]
"""

# Function used to clear the training model CSV file
    # This makes it so that it can then be re-used later for different NPL issues
def clearTraining():
    # Used to open the file and set it to its header values only
        # It does this by using the "w+" write mode, truncating the file (bringing it to length 0)
    with open("{currentDir}/ptrNaturalLanguage/training.csv".format(currentDir = os.getcwd()), "w+") as resetFile:
        writer = csv.writer(resetFile)

        writer.writerow(['sentance','positive','negative','neutral'])

# Function used to train the model
    # dataFrame parameter is used to contain the CSV file with the string and the "supervised" column
def train(dataFrame):
    # Dictionary used to contain the word with its frequency and overall score
    wordAndScore = {}

    # Used to iterate over the
    for x in dataFrame.index:
        print(dataFrame["sentance"][x])
        for words in tokenization(dataFrame["sentance"][x]):
            try:
                if dataFrame["positive"][x] == 1:
                    newArray = [wordAndScore[words][0] + 1, wordAndScore[words][1] + 0.1]

                    wordAndScore[words] = newArray

                elif dataFrame["negative"][x] == 1:
                    newArray = [wordAndScore[words][0] + 1, wordAndScore[words][1] - 0.1]

                    wordAndScore[words] = newArray

                else:
                    newArray = [wordAndScore[words][0] + 1, wordAndScore[words][1]]

                    wordAndScore[words] = newArray

            except:
                wordAndScore[words] = [1, 0.5]

    print(wordAndScore)

train(pd.read_csv("C:/Users/dodob/OneDrive/Desktop/GitHubFiles/Natural-Language-Processing-Python-Library/ptrNaturalLanguage/training.csv", encoding = "latin-1"))
