from django.db import models
from django.utils import timezone

# Create your models here.
class imageDB(models.Model):
	keywords = models.TextField()
	dateTime = models.DateTimeField(default=timezone.now())
	# username = models.CharField(max_length=48)
	sourceUrl = models.TextField()
	imageUrl = models.TextField()
	label = models.CharField(max_length=128)

	def __str__(self):
		return self.label

class textDB(models.Model):
	summary = models.TextField()
	sourceUrl = models.TextField()
	dateTime = models.DateTimeField(default=timezone.now())

	def __str__(self):
		return self.id