from django.db import models

# Create your models here.
class Greeting(models.Model):
	when = models.DateTimeField('date created', auto_now_add=True)


class Fineness(models.Model):
	multiplier = models.FloatField(null=False, default=1.0)
	friendly_name = models.CharField(max_length=80, null=False)

	class Meta:
		verbose_name_plural = 'finenesses'

	def __str__(self):
		return '{friendly_name}: x{multiplier} multiplier'.format(
			multiplier=self.multiplier,
			friendly_name=self.friendly_name,
		)
