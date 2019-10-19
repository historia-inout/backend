from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Close sumy imports

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
		LANGUAGE = "english"
		SENTENCES_COUNT = 10

		parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
		stemmer = Stemmer(LANGUAGE)

		summarizer = Summarizer(stemmer)
		summarizer.stop_words = get_stop_words(LANGUAGE)

		summary = ''
		
		for sentence in summarizer(parser.document, SENTENCES_COUNT):
			summary = summary + str(sentence)

		textDB.objects.create(summary=summary, dateTime=timezone.now(), sourceUrl=url)

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
		imgRecordsList = list(imgRecords)
		imgRecordsDatabase = {}
		for i in imgRecords:
			x = imageDB.objects.get(keywords=i)
			objectID = x.id
			imgRecordsDatabase[objectID] = i

		result = []
		for key in imgRecordsDatabase:
			# print(imgRecordsDatabase[key])
			if str(query) in str(imgRecordsDatabase[key]):
				temp = imageDB.objects.get(id=key)
				summary = temp.keywords
				sourceUrl = temp.sourceUrl
				imageUrl = temp.imageUrl
				data = {
					"id": key,
					"summary": summary,
					"sourceUrl": sourceUrl,
					"imageUrl": imageUrl
				}
				# print(data)
				result.append(data)

		textRecords = textDB.objects.values_list('summary', flat=True)
		textRecordsList = list(textRecords)
		textRecordsDatabase = {}

		for i in textRecords:
			x = textDB.objects.get(summary=i)
			objectID = x.id
			textRecordsDatabase[objectID] = i

		for key in textRecordsDatabase:
			if query in textRecordsDatabase[key]:
				data = {}
				temp = textDB.objects.get(id=key)
				summary = temp.summary
				sourceUrl = temp.sourceUrl
				data = {
					"id": key,
					"summary": summary,
					"sourceUrl": sourceUrl,
				}
				result.append(data)

		return JsonResponse(result, safe=False)