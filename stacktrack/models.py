from django.db import models
from datetime import datetime
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User


class Ingot(models.Model):
	name = models.CharField(max_length=80)
	description = models.TextField(default='')
	mintage = models.CharField(max_length=20, default='Unspecified')
	year = models.SmallIntegerField(null=True)
	silverartcollector_item_number = models.CharField(
		max_length=20,
		null=True
	)
	date_posted = models.DateTimeField(
		default=timezone.now,
	)

	SILVER =	'Ag'
	GOLD =		'Au'
	PLATINUM =	'Pt'
	PALLADIUM =	'Pd'
	RHODIUM =	'Rh'
	COPPER	=	'Cu'
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
	)

	# Foreign fields
	posted_by = models.ForeignKey(User,
		editable=False,
		null=True,
		on_delete=models.SET_NULL,
	)
	fineness = models.ForeignKey('Fineness')
	mass = models.ForeignKey('Mass')
	ingot_type = models.ForeignKey('IngotType')
	manufacturer = models.ForeignKey('Manufacturer', null=True)
	primary_images = models.ForeignKey('PrimaryImage', null=True)

	# Proposed fields
	#images
	#sales

	def __str__(self):
		return '{name} - {mass} {fineness} {pm} {ingot_type}'.format(
			name=self.name,
			mass=self.mass,
			fineness=self.fineness,
			ingot_type=self.ingot_type,
			pm=self.precious_metal,
		)


class Manufacturer(models.Model):
	company_name = models.CharField(max_length=30)

	def __str__(self):
		return self.company_name


class Fineness(models.Model):
	multiplier = models.FloatField(default=1.0)
	friendly_name = models.CharField(max_length=80)

	class Meta:
		verbose_name_plural = 'fineness entries'

	def __str__(self):
		return '{friendly_name}: x{multiplier} multiplier'.format(
			multiplier=self.multiplier,
			friendly_name=self.friendly_name,
		)


ONE_TROY_OZ = 31.1
class Mass(models.Model):
	number = models.FloatField(default=1.0)
	friendly_name = models.CharField(max_length=80)
	unit = models.ForeignKey('UnitOfMass',
		on_delete=models.SET_NULL,
		null=True,
	)

	class Meta:
		verbose_name_plural = "weights"

	def convert_to_ozt(self):
		return self.number*self.unit.ozt_multiplier

	def __str__(self):
		return '{friendly_name} - {unit}'.format(
			friendly_name=self.friendly_name,
			unit=self.unit.abbreviation,
		)


class UnitOfMass(models.Model):
	name = models.CharField(max_length=20)
	abbreviation = models.CharField(max_length=10)
	ozt_multiplier = models.FloatField()

	class Meta:
		verbose_name_plural = 'mass units'

	def __str__(self):
		return '{name} ({abbr}): {ratio} {name} to 1 troy ounce'.format(
			name=self.name,
			ratio=self.ozt_multiplier,
			abbr=self.abbreviation,
		)


class IngotType(models.Model):
	name = models.CharField(max_length=80)

	def __str__(self):
		return self.name


import urllib.parse
class Image(models.Model):
	OBVERSE = True
	REVERSE = False
	SIDE_OF_INGOT = (
		(OBVERSE, "Obverse"),
		(REVERSE, "Reverse"),
	)

	image = CloudinaryField('image')
	is_obverse = models.BooleanField(
		choices=SIDE_OF_INGOT,
		default=OBVERSE,
	)
	ingot = models.ForeignKey('Ingot',
		null=True,
		on_delete=models.SET_NULL
	)
	from_post = models.ForeignKey('SalePost',
		null=True,
		on_delete=models.SET_NULL
	)

	def truncated_url(self):
		url = 'http://example.com/stuff/image.jpg'
		parsed = urllib.parse.urlsplit(url)
		return '{scheme}//{netloc}/.../{filename}'.format(
			scheme=parsed.scheme,
			netloc=parsed.netloc,
			filename=os.path.split(parsed.path)[-1],
		)

	def __str__(self):
		return '{side} image - {ingot} - {truncated_url}'.format(
			side=self.is_obverse,
			ingot=self.ingot.name,
			truncated_url=self.truncated_url(),
		)


class PrimaryImage(models.Model):
	obverse_image = models.ForeignKey('Image',
		related_name='obverse_img',
		null=True,
		on_delete=models.SET_NULL,
	)
	reverse_image = models.ForeignKey('Image',
		related_name='reverse_img',
		null=True,
		on_delete=models.SET_NULL,
	)

	def __str__(self):
		return '{obv} + {rev}'.format(
			obv=self.obverse_image.truncated_url(),
			rev=self.reverse_image.truncated_url()
		)


class StackEntry(models.Model):
	ingot = models.ForeignKey('Ingot',
		null=True,
		on_delete=models.SET_NULL,
	)
	owner = models.ForeignKey(User,
		editable=False,
		null=True,
		on_delete=models.SET_NULL,
	)

	purchase = models.ForeignKey('Transaction',
		related_name='into_stack',
		null=True,
		on_delete=models.SET_NULL,
	)
	bought_for = models.ForeignKey('TransactionAmount',
		related_name='into_stack',
		null=True,
		on_delete=models.SET_NULL,
	)

	sale = models.ForeignKey('Transaction',
		related_name='from_stack',
		null=True,
		on_delete=models.SET_NULL,
	)
	sold_for = models.ForeignKey('TransactionAmount',
		related_name='from_stack',
		null=True,
		on_delete=models.SET_NULL,
	)

	class Meta:
		verbose_name_plural = 'stack entries'

	def __str__(self):
		return '{user} - {price} - {ingot}'.format(
			user=self.owner,
			price=self.bought_for,
			ingot=self.ingot.name,
		)


class Platform(models.Model):
	name = models.CharField(max_length=80)
	homepage = models.URLField(max_length=80, null=True)
	user_url_fmt = models.URLField(null=True)
	post_url_fmt = models.URLField(null=True)
	logo = CloudinaryField('logo', null=True)

	def __str__(self):
		return '{name} - {url}'.format(
			name=self.name,
			url=self.homepage,
		)


class PlatformUser(models.Model):
	stacktrack_user = models.ForeignKey(User,
		null=True,
		on_delete=models.SET_NULL,
	)
	username = models.CharField(max_length=80)
	user_id = models.CharField(max_length=40, null=True)
	platform = models.ForeignKey('Platform',
		null=True,
		on_delete=models.SET_NULL,
	)

	PHANTOM_USER = True
	REGISTERED_USER = False
	PLATFORM_USER_TYPES = (
		(PHANTOM_USER, 'Phantom User'),
		(REGISTERED_USER, 'Registered User'),
	)
	is_phantom = models.BooleanField(
		choices=PLATFORM_USER_TYPES,
		default=PHANTOM_USER
	)

	def __str__(self):
		return '{username}@{platform} ({phantom})'.format(
			username=self.username,
			platform=self.platform.name,
			phantom=self.is_phantom,
		)


class SalePost(models.Model):
	title = models.CharField(max_length=300)
	description = models.TextField(default='')
	platform = models.ForeignKey('Platform',
		null=True,
		on_delete=models.SET_NULL,
	)
	seller = models.ForeignKey('PlatformUser',
		null=True,
		on_delete=models.SET_NULL,
	)
	ebay_post_attributes = models.ForeignKey('EbayPostAttributes',
		null=True,
		on_delete=models.SET_NULL,
	)
	date_listed = models.DateTimeField(default=timezone.now)
	access_id = models.CharField(max_length=20)

	def __str__(self):
		return 'Sale@{platform} - {title} - from {seller} - {date}'.format(
			platform=self.platform.name,
			title=self.title,
			seller=self.seller.username,
			date=self.date_listed,
		)


class EbayPostAttributes(models.Model):
	post_id = models.BigIntegerField()

	class Meta:
		verbose_name_plural = 'ebay post attributes'

	def __str__(self):
		return str(self.post_id)


class Transaction(models.Model):
	total_price = models.ForeignKey('TransactionAmount',
		null=True,
		on_delete=models.SET_NULL,
	)
	shipping = models.ForeignKey('Shipping',
		null=True,
		on_delete=models.SET_NULL,
	)
	# rewards/discount = ...
	timestamp = models.DateTimeField(default=timezone.now)
	from_post = models.ForeignKey('SalePost',
		null=True,
		on_delete=models.SET_NULL,
	)

	def __str__(self):
		return '{price} + {shipping} S/H'.format(
			price=self.total_price,
			shipping=self.shipping.price,
		)


class TransactionAmount(models.Model):
	amount = models.DecimalField(
		max_digits=20,
		decimal_places=10,
	)
	currency = models.ForeignKey('Currency',
		null=True,
		on_delete=models.SET_NULL,
	)
	original_currency_amount = models.ForeignKey('TransactionAmount',
		null=True,
		on_delete=models.SET_NULL,
	)

	def __str__(self):
		return '{symbol}{amount}'.format(
			symbol=self.currency.symbol,
			amount=self.amount,
		)


class Currency(models.Model):
	name = models.CharField(max_length=30)
	abbreviation = models.CharField(max_length=5)
	symbol = models.CharField(max_length=1)
	country = models.CharField(max_length=30)

	class Meta:
		verbose_name_plural = 'currencies'

	def __str__(self):
		return '{name} ({sym}, {abbr}, {country})'.format(
			name=self.name,
			abbr=self.abbreviation,
			sym=self.symbol,
			country=self.country,
		)


class Shipping(models.Model):
	shipping_company = models.ForeignKey('ShippingCompany',
		null=True,
		on_delete=models.SET_NULL,
	)
	price = models.ForeignKey('TransactionAmount',
		null=True,
		on_delete=models.SET_NULL,
	)
	tracking = models.CharField(max_length=30, default='N/A')

	class Meta:
		verbose_name_plural = 'shipping orders'

	def __str__(self):
		return '{tracking} - {company}'.format(
			tracking=self.tracking,
			company=self.shipping_company.company_name,
		)


class ShippingCompany(models.Model):
	company_name = models.CharField(max_length=30)
	url = models.URLField()
	tracking_url_fmt = models.URLField()
	# country?

	class Meta:
		verbose_name_plural = 'shipping companies'

	def __str__(self):
		return self.company_name


class ShippingStatus(models.Model):
	timestamp = models.DateTimeField()
	location = models.CharField(max_length=80)
	note = models.CharField(max_length=160, default='')
	shipping = models.ForeignKey('Shipping',
		null=True,
		on_delete=models.SET_NULL,
	)

	class Meta:
		verbose_name_plural = 'shipping status updates'

	def __str__(self):
		return '{location} on {timestamp}'.format(
			location=self.location,
			timestamp=self.timestamp,
		)

"""
class Trade(models.Model):
	initiator = models.ForeignKey('PlatformUser')
	respondent = models.ForeignKey('PlatformUser')
	timestamp = models.DateTimeField(default=datetime.now)
	from_post = ...


class TradeItem(models.Model):
	associated_trade = models.ForeignKey('Trade')
	from_stack = models.ForeignKey('StackEntry')
"""

