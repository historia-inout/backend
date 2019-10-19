from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Close sumy imports

from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, urljoin

# Closing scraper imports

from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from .scraper import Scraper
from .models import textDB, imageDB
# Create your views here.
def home(request):
	return render(request, 'app/home.html')

def scrape(request):
	if request.method == 'POST':
		y = json.loads(request.body)
		url = y.get("url", None)
		print(url)

		imageSourceUrls = imageDB.objects.values_list('sourceUrl', flat=True)
		imageSourceUrls = list(imageSourceUrls)

		textSourceUrls = textDB.objects.values_list('sourceUrl', flat=True)
		textSourceUrls = list(textSourceUrls)

		if url not in textSourceUrls or url not in imageSourceUrls:
			LANGUAGE = "english"
			SENTENCES_COUNT = 10

			parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
			stemmer = Stemmer(LANGUAGE)

			summarizer = Summarizer(stemmer)
			summarizer.stop_words = get_stop_words(LANGUAGE)

			summary = ''
			
			for sentence in summarizer(parser.document, SENTENCES_COUNT):
				summary = summary + str(sentence)

			x = urlopen(url)
			codebase = BeautifulSoup(x, 'html.parser')
			title = codebase.title.string
			iconLink = codebase.find("link", rel="shortcut icon")

			tempIconUrl = urljoin(url, iconLink.get('href'))
			print(tempIconUrl)

			textDB.objects.create(summary=summary, dateTime=timezone.now(), sourceUrl=url, title=title, icon=tempIconUrl)

			scraper = Scraper()
			scraper.scrape(url)
		else:
			textDB.objects.filter(sourceUrl=url).delete()
			imageDB.objects.filter(sourceUrl=url).delete()
			LANGUAGE = "english"
			SENTENCES_COUNT = 10

			parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
			stemmer = Stemmer(LANGUAGE)

			summarizer = Summarizer(stemmer)
			summarizer.stop_words = get_stop_words(LANGUAGE)

			summary = ''
			
			for sentence in summarizer(parser.document, SENTENCES_COUNT):
				summary = summary + str(sentence)

			x = urlopen(url)
			codebase = BeautifulSoup(x, 'html.parser')
			title = codebase.title.string
			iconLink = codebase.find("link", rel="shortcut icon")

			print(iconLink)

			textDB.objects.create(summary=summary, dateTime=timezone.now(), sourceUrl=url, title=title)

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
				"summary": temp.summary
			}
		else:
			data = {
				"sourceUrl": temp.sourceUrl,
				"imageUrl": temp.imageUrl,
				"dateTime": temp.dateTime,
				"summary": temp.keywords
			}

		return JsonResponse(data, safe=False)

def query(request):
	if request.method == 'POST':
		y = json.loads(request.body)
		query = y.get('query', None)
		
		imgRecords = imageDB.objects.values_list('keywords', flat=True)
		imgRecords = list(imgRecords)

		summaryRecords = textDB.objects.values_list('summary', flat=True)
		summaryRecords = list(summaryRecords)

		result = {}

		for i in imgRecords:
			if query.lower() in i.lower():
				temp = imageDB.objects.get(keywords=i)
				sourceUrl = temp.sourceUrl
				data = {
					"imageUrl": temp.imageUrl,
					"summary": temp.keywords
				}

				if sourceUrl not in result.keys():
					result[sourceUrl] = {
						"collection": []
					}
					result[sourceUrl]["collection"].append(data)
				else:
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)

		for i in summaryRecords:
			if query.lower() in i.lower():
				temp = textDB.objects.get(summary=i)
				sourceUrl = temp.sourceUrl
				data = {
					"summary": temp.summary
				}

				if sourceUrl not in result.keys():
					result[sourceUrl] = {
						"collection": []
					}
					result[sourceUrl]["collection"].append(data)
				else:
					result[sourceUrl]["icon"] = temp.icon
					result[sourceUrl]["title"] = temp.title
					result[sourceUrl]["collection"].append(data)

		jsonDataResult = {
			"data": result
		}
		return JsonResponse(result, safe=False)

	else:
		print(request.body)
		print("Idiota")
		return HttpResponse("Noob")
