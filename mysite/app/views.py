from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from .scraper import Scraper
# Create your views here.
def home(request):
	return render(request, 'app/home.html')

def scrape(request):
	if request.method == 'POST':
		y = json.loads(request.body)
		url = y.get("url", None)
		print(url)
		scraper = Scraper()
		scraper.scrape(url)
		return HttpResponse("Successful")