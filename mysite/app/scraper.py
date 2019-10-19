from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, urljoin
import json
from google.cloud import vision
from .models import imageDB
from django.utils import timezone

class Scraper:

	def detect_web_uri(self, uri):
		client = vision.ImageAnnotatorClient()
		image = vision.types.Image()
		image.source.image_uri = uri

		keywordsGenerated = []

		response = client.web_detection(image=image)
		annotations = response.web_detection

		if annotations.best_guess_labels:
			for label in annotations.best_guess_labels:
				bestGuessLabel = label.label

		if annotations.web_entities:
			for entity in annotations.web_entities:
				keyword = entity.description
				keywordsGenerated.append(keyword)

		return keywordsGenerated, bestGuessLabel

	def scrape(self, url):
		x = urlopen(url)
		codebase = BeautifulSoup(x, 'html.parser')
		images = codebase.findAll("img")
		imageUrls = []
		for i in images:
			relativeUrl = i.get("src")
			if (not relativeUrl):
				relativeUrl = i.get("data-src")
			if "http" in relativeUrl:
				imageUrls.append(relativeUrl)
			else:
				tempUrl = urljoin(url, relativeUrl)
				imageUrls.append(tempUrl)

		for i in imageUrls:
			keywords, label = self.detect_web_uri(i)
			x = ''
			for j in keywords:
				x = x + j + ", "
			imageDB.objects.create(keywords=x, dateTime=timezone.now(), sourceUrl=url, imageUrl=i, label=label)