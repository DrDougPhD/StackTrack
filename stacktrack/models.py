from django.db import models


class Ingot(models.Model):
	name = models.CharField(max_length=80, null=False)
	description = models.TextField(default='')

	SILVER = 'Ag'
	GOLD = 'Au'
	PLATINUM = 'Pt'
	PALLADIUM = 'Pd'
	RHODIUM = 'Rh'
	COPPER = 'Cu'
	PRECIOUS_METALS = (
		(SILVER, 'Silver'),
		(GOLD, 'Gold'),
		(PLATINUM, 'Platinum'),
		(PALLADIUM, 'Palladium'),
		(RHODIUM, 'Rhodium'),
		(COPPER, 'Copper'),
	)
	precious_metal = models.CharField(
		max_length=2,
		choices=PRECIOUS_METALS,
		default=SILVER,
		null=False
	)

	# Foreign fields
	fineness = models.ForeignKey('Fineness', null=False)
	mass = models.ForeignKey('Mass', null=False)
	ingot_type = models.ForeignKey('IngotType', null=False)

	# Proposed fields
	# manufacturer = ...
	# mintage = ...
	# year = ...

	#primary_obverse_img
	#primary_reverse_img
	#images
	#sales


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


ONE_TROY_OZ = 31.1
class Mass(models.Model):
	grams = models.FloatField(default=ONE_TROY_OZ, null=False)
	friendly_name = models.CharField(max_length=80, null=False)

	class Meta:
		verbose_name_plural = "weights"

	def __str__(self):
		return '{friendly_name}: {grams} grams'.format(
			friendly_name=self.friendly_name,
			grams=self.grams,
		)


class IngotType(models.Model):
	name = models.CharField(max_length=10, null=False)
	plural = models.CharField(max_length=10, null=False)

	def __str__(self):
		return self.name

