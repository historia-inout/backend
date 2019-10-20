from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from itertools import chain
# Close sumy imports

from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, urljoin, Request
from urllib.parse import urlparse
# Closing scraper imports

from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from .scraper import Scraper
from .models import textDB, imageDB

from sumy.summarizers.lsa import LsaSummarizer
from selenium import webdriver
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.parsers.plaintext import PlaintextParser

# Create your views here.
def home(request):
	return render(request, 'app/home.html')

def scrape(request):
	if request.method == 'POST':
		
		y = json.loads(request.body)
		url = y.get("url", None)
		print(url)

		driver = webdriver.PhantomJS(executable_path='../phantomjs/bin/phantomjs')
		driver.get(url)
		el=driver.find_element_by_tag_name("body")
		textContent=el.text
		driver.close()

		imageSourceUrls = imageDB.objects.values_list('sourceUrl', flat=True)
		imageSourceUrls = list(imageSourceUrls)

		textSourceUrls = textDB.objects.values_list('sourceUrl', flat=True)
		textSourceUrls = list(textSourceUrls)

		summary = textContent
		if url not in textSourceUrls or url not in imageSourceUrls:
			LANGUAGE = "english"
			SENTENCES_COUNT = 10

			# parser = PlaintextParser.from_string(textContent,Tokenizer("english"))
			# summarizer = LuhnSummarizer()
			# summary = ''

			# for sentence in summarizer(parser.document, SENTENCES_COUNT):
			# 	summary = summary + str(sentence)
			

			# print("Summary ",summary)

			
			parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
			stemmer = Stemmer(LANGUAGE)
			summarizer = Summarizer(stemmer)
			summarizer.stop_words = get_stop_words(LANGUAGE)

			summaryText = ""
			for sentence in summarizer(parser.document, SENTENCES_COUNT):
				summaryText = summaryText + str(sentence)
			
			r = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
			x = urlopen(r)
			codebase = BeautifulSoup(x, 'html.parser')
			title = codebase.title.string
			if not title:
				domain = urlparse(url)
				title = domain.hostname
			print(title)
			iconLink = codebase.find("link", rel="shortcut icon")
			if not iconLink:
				iconLink = ' '
			else:
				iconLink = urljoin(url, iconLink.get('href'))

			textDB.objects.create(summaryText=summaryText, summary=summary, dateTime=timezone.now(), sourceUrl=url, title=title, icon=iconLink)

			scraper = Scraper()
			scraper.scrape(url)
		else:
			textDB.objects.filter(sourceUrl=url).delete()
			imageDB.objects.filter(sourceUrl=url).delete()
			print("DELETED")
			LANGUAGE = "english"
			SENTENCES_COUNT = 10

			parser = PlaintextParser.from_string(textContent,Tokenizer("english"))
			summarizer = LuhnSummarizer()

			summary = ''

			for sentence in summarizer(parser.document, SENTENCES_COUNT):
				summary = summary + str(sentence)

			parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
			stemmer = Stemmer(LANGUAGE)
			summarizer = Summarizer(stemmer)
			summarizer.stop_words = get_stop_words(LANGUAGE)

			summaryText = ""
			for sentence in summarizer(parser.document, SENTENCES_COUNT):
				summaryText = summaryText + str(sentence)

			r = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
			x = urlopen(r)
			codebase = BeautifulSoup(x, 'html.parser')
			title = codebase.title.string
			iconLink = codebase.find("link", rel="shortcut icon")
			if not iconLink:
				iconLink = ' '
			else:
				iconLink = urljoin(url, iconLink.get('href'))

			textDB.objects.create(summaryText=summaryText, summary=summary, dateTime=timezone.now(), sourceUrl=url, title=title, icon=iconLink)

			scraper = Scraper()
			scraper.scrape(url)


		return HttpResponse("Successful")

def queryHistory(request, pk):
	if request.method == 'POST':
		try:
			temp = imageDB.objects.get(pk=pk)
			flag = 1
		except:
			temp = textDB.objects.get(pk=pk)
			flag = 0
		if flag == 0:
			data = {
				"sourceUrl": temp.sourceUrl,
				"dateTime": temp.dateTime,
				"summary": temp.summaryText,
			}
		else:
			data = {
				"sourceUrl": temp.sourceUrl,
				"imageUrl": temp.imageUrl,
				"dateTime": temp.dateTime,
				"summary": temp.keywords
			}

		return JsonResponse(data, safe=False)

def search(queryWord):
	imgRecords = imageDB.objects.values_list('keywords', flat=True)
	imgRecords = list(imgRecords)

	summaryRecords = textDB.objects.values_list('summary', flat=True)
	summaryRecords = list(summaryRecords)

	results = []
	result = {}

	for i in imgRecords:
		if queryWord.lower() in i.lower():
			temps = imageDB.objects.filter(keywords=i)
			for temp in temps:
				sourceUrl = temp.sourceUrl
				data = {
					"imageUrl": temp.imageUrl,
					"summary": temp.keywords
				}

				if sourceUrl not in result.keys():
					result[sourceUrl] = {
						"collection": []
					}
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)
				else:
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)
				results.append(result)

	for i in summaryRecords:
		if queryWord.lower() in i.lower():
			temps = textDB.objects.filter(summary=i)
			for temp in temps:
				sourceUrl = temp.sourceUrl
				data = {
					"summary": temp.summaryText
				}

				if sourceUrl not in result.keys():
					result[sourceUrl] = {
						"collection": []
					}
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)
				else:
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)
				results.append(result)

	return results

def query(request):
	if request.method == 'POST':
		y = json.loads(request.body)
		query = y.get('query', None)

		result = {}
		
		queryList = query.split()

		for i in queryList:
			tempResult = search(i)
			for k in range(len(tempResult)):
				for j in tempResult[k]:
					if j not in result.keys():
						result[j] = {
							"collection": tempResult[k][j]["collection"],
							"icon": tempResult[k][j]["icon"],
							"title": tempResult[k][j]["title"]
						}

		return JsonResponse(result, safe=False)

	else:
		print(request.body)
		print("Idiota")
		return HttpResponse("Noob")

def history(request):
	imageDBResults = imageDB.objects.filter(dateTime__lte=timezone.now()).order_by('-dateTime')
	textDBResults = textDB.objects.filter(dateTime__lte=timezone.now()).order_by('-dateTime')
	imageDBResults = list(imageDBResults)
	textDBResults = list(textDBResults)
	result_list = list(chain(imageDBResults, textDBResults))

	result = {}

	for i in result_list:
		temp = i.sourceUrl
		print(temp)
		if temp not in result.keys():
			try:
				check = i.keywords
			except:
				check = i.summaryText
			result[i.sourceUrl] = {
				"title": i.title,
				"icon": i.icon,
				"summary": check
			}
	print(result)
	return JsonResponse(result, safe=False)

def historyapi(request):
	imageDBResults = imageDB.objects.filter(dateTime__lte=timezone.now()).order_by('-dateTime')
	textDBResults = textDB.objects.filter(dateTime__lte=timezone.now()).order_by('-dateTime')
	imageDBResults = list(imageDBResults)
	textDBResults = list(textDBResults)
	result_list = list(chain(imageDBResults, textDBResults))

	result = {
		"collection": []
	}

	urlsIncluded = []

	for i in result_list:
		temp = i.sourceUrl
		if temp not in urlsIncluded:
			try:
				check = i.keywords
			except:
				check = i.summaryText
			data = {
				"url": temp,
				"title": i.title,
				"icon": i.icon,
				"summary": check
			}
			urlsIncluded.append(temp)
			result["collection"].append(data)

	return JsonResponse(result, safe=False)


