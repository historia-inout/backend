from django.db import models
from django.utils import timezone

# Create your models here.
class imageDB(models.Model):
	keywords = models.TextField()
	dateTime = models.DateTimeField(default=timezone.now())
	# username = models.CharField(max_length=48)
	title = models.CharField(max_length=128)
	sourceUrl = models.TextField()
	imageUrl = models.TextField()
	icon = models.TextField()
	label = models.CharField(max_length=128)

	def __str__(self):
		return self.title

class textDB(models.Model):
	summary = models.TextField()
	summaryText = models.TextField()
	icon = models.TextField()
	title = models.CharField(max_length=128)
	sourceUrl = models.TextField()
	dateTime = models.DateTimeField(default=timezone.now())

	def __str__(self):
		return self.title