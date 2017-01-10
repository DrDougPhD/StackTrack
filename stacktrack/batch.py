import csv
from pprint import pprint
import urllib.parse


csv_filename = 'ag_tx.csv'


def main():
	with open(csv_filename) as csv_file:
		records = csv.DictReader(csv_file)
		pprint(records.fieldnames)
		print('-'*80)
		process(records)

GRAMS = ('gram', 'g', 0.0321543408)
TROY_OUNCE = ('troy ounce', 'ozt', 1.0)
MASS_CONVERSION = {
 '0.05': ('1/20 ozt', 0.05, TROY_OUNCE),
 '0.16': ('5 grams', 5.0, GRAMS),
 '0.466': ('14.5 grams', 14.5, GRAMS),
 '0.5': ('1/2 ozt', 1.0, TROY_OUNCE),
 '0.623': ('19.4 grams', 19.4, GRAMS),
 '0.643': ('20 grams', 20.0, GRAMS),
 '0.836': ('26 grams', 26.0, GRAMS),
 '0.877': ('27.3 grams', 27.3, GRAMS),
 '1': ('1 ozt', 1.0, TROY_OUNCE),
 '10': ('10 ozt', 10.0, TROY_OUNCE),
 '2': ('2 ozt', 2.0, TROY_OUNCE),
 '2.5': ('2.5 ozt', 2.5, TROY_OUNCE),
 '3': ('3 ozt', 3.0, TROY_OUNCE),
 '5': ('5 ozt', 5.0, TROY_OUNCE)
}
mass_entries = set()
for mass in MASS_CONVERSION:
	from_conversion = MASS_CONVERSION[mass]
	mass_entries.add(from_conversion[:2])

def process(csvrecords):
	"""
	admin = User.objects.all()[0]
	fineness = Fineness(friendly_name='.999 fine (three nines)')
	fineness.save()
	ingot_types = {
		'bar': IngotType(name='bar'),
		'round': IngotType(name='round'),
		'coin': IngotType(name='coin'),
	}
	for ingot_name in ingot_types:
		ingot_types[ingot_name].save()

	us_dollar = Currency(
		name='US Dollar',
		abbreviation='USD',
		symbol='$',
		country='United States',
	)
	us_dollar.save()
	"""
	records = [dict(r) for r in csvrecords]

	# Platform
	def extract_platform_info(url):
		parsed_url = urllib.parse.urlparse(url)
		domain_name = parsed_url.netloc.split('.')[-2]
		homepage = '{scheme}://{netloc}/'.format(
			scheme=parsed_url.scheme,
			netloc=parsed_url.netloc,
		)
		return domain_name, homepage

	# Platform user
	def extract_platform_user(url, platform_name):
		import os
		def basename_url_extractor(url):
			parsed_url = urllib.parse.urlparse(url)
			return os.path.basename(parsed_url.path)

		extractors = {
			'ebay': basename_url_extractor,
			'reddit': basename_url_extractor,
			'N/A': lambda x: x or 'Not specified',
			'apmex': lambda x: 'APMEX',
			'jmbullion': lambda x: 'JM Bullion',
			'providentmetals': lambda x: 'Provident Metals',
			'qualitysilverbullion': lambda x: 'QSB: Quality Silver Bullion',
		}
		username = extractors[platform_name](url)
		print('{username}:\t {platform_name}'.format(**locals()))
		return username

	def extract_platform(r):
		# Extract platform from sale URL
		url = r['Purchase message thread']
		if not url:
			url = r['Purchased from']

		if not url or not url.startswith('http'):
			domain_name = 'N/A'
			homepage = None

		else:
			domain_name, homepage = extract_platform_info(url)

		# Extract username
		url = r['Purchased from']
		if not url:
			username = 'Not specified'

		else:
			username = extract_platform_user(url, domain_name)

		return domain_name, homepage, username

	platforms = {}
	users = {}
	for record in records:
		platform_name, homepage, username = extract_platform(record)
		if platform_name in platforms:
			p = platforms[platform_name]

		else:
			"""
			p = Platform(
				name=platform_name,
				homepage=homepage,
				#user_url_fmt=,
				#post_url_fmt=,
				#logo=,
			)
			p.save()
			"""
			p = (platform_name, homepage)
			platforms[platform_name] = p

		record['platform'] = p

		if username in users:
			u = users[username]

		else:
			"""
			user = PlatformUser(
				username='',
				platform=record['platform'],
			)
			user.save()

			u = PlatformUser
			"""
			u = (username, p)
			users[username] = u

		record['seller'] = u

		"""
		if record[] in platforms:
			platform_key = ... # extract domain from sale url
			p = platforms[platform_key]

		else:
		
		record['platform'] = p
		"""

	print('-'*10 + '|~ USERS ~|' + '-'*10)
	pprint(users)
	print('-'*10 + '|~ PLATFORMS ~|' + '-'*10)
	pprint(platforms)

	"""
	# Platform users
	for record in records:
		platform = ...
		user = PlatformUser(
			username='',
			platform=record['platform'],
		)
		user.save()
		record['seller'] = user

	if True:
		price = TransactionAmount(
			amount=,
			currency=us_dollar,
		)
		price.save()

		stack_entry = StackEntry(
			ingot=ingot,
			owner=admin,
			purchase=tx,
			bought_for=price,
		)

	ingots = set()
	registered_weights = set()
	for r in records:
		mass_entry = registered_weights.add(r['Size (ozt)'])
		ingots.add(r['Item'])

	pprint(ingots)
	pprint(registered_weights)
	"""

	# Create mass entries
	"""
	for m in registered_weights:
		mass_unit = UnitOfMass(name='', abbreviation='', ozt_multiplier='')
		mass = Mass(number='', friendly_name='', unit='')
	"""


if __name__ == '__main__':
	main()

"""
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
		default=datetime.now,
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
	posted_by = models.ForeignKey(User, editable=False)
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
	unit = models.ForeignKey('UnitOfMass')

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
	ingot = models.ForeignKey('Ingot', null=True)
	from_post = models.ForeignKey('SalePost', null=True)

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
	)
	reverse_image = models.ForeignKey('Image',
		related_name='reverse_img',
	)

	def __str__(self):
		return '{obv} + {rev}'.format(
			obv=self.obverse_image.truncated_url(),
			rev=self.reverse_image.truncated_url()
		)


class StackEntry(models.Model):
	ingot = models.ForeignKey('Ingot')
	owner = models.ForeignKey(User, editable=False)

	purchase = models.ForeignKey('Transaction',
		related_name='into_stack',
	)
	bought_for = models.ForeignKey('TransactionAmount',
		related_name='into_stack',
	)

	sale = models.ForeignKey('Transaction',
		related_name='from_stack',
		null=True,
	)
	sold_for = models.ForeignKey('TransactionAmount',
		related_name='from_stack',
		null=True,
	)

	class Meta:
		verbose_name_plural = 'stack entries'

	def __str__(self):
		return '{user} - {price} - {ingot}'.format(
			user=self.owner,
			price=self.bought_for,
			ingot=self.ingot.name,
		)


class TransactionAmount(models.Model):
	amount = models.DecimalField(
		max_digits=20,
		decimal_places=10,
	)
	currency = models.ForeignKey('Currency')
	original_currency_amount = models.ForeignKey('TransactionAmount',
		null=True,
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


class PlatformUser(models.Model):
	stacktrack_user = models.ForeignKey(User, null=True)
	username = models.CharField(max_length=80)
	user_id = models.CharField(max_length=40, null=True)
	platform = models.ForeignKey('Platform')

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
			phantom=self.phantom,
		)


class Platform(models.Model):
	name = models.CharField(max_length=80)
	homepage = models.URLField(max_length=80, null=True)
	user_url_fmt = models.URLField(null=True)
	post_url_fmt = models.URLField(null=True)
	logo = CloudinaryField('image', null=True)

	def __str__(self):
		return '{name} - {url}'.format(
			name=self.name,
			url=self.homepage,
		)


class SalePost(models.Model):
	title = models.CharField(max_length=300)
	description = models.TextField(default='')
	platform = models.ForeignKey('Platform')
	seller = models.ForeignKey('PlatformUser')
	ebay_post_attributes = models.ForeignKey('EbayPostAttributes',
		null=True
	)
	date_listed = models.DateTimeField(default=datetime.now)

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
	total_price = models.ForeignKey('TransactionAmount')
	shipping = models.ForeignKey('Shipping')
	# rewards/discount = ...
	timestamp = models.DateTimeField(default=datetime.now)
	from_post = models.ForeignKey('SalePost', null=True)

	def __str__(self):
		return '{price} + {shipping} S/H'.format(
			price=self.total_price,
			shipping=self.shipping.price,
		)


class Shipping(models.Model):
	shipping_company = models.ForeignKey('ShippingCompany')
	price = models.ForeignKey('TransactionAmount')
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
	shipping = models.ForeignKey('Shipping')

	class Meta:
		verbose_name_plural = 'shipping status updates'

	def __str__(self):
		return '{location} on {timestamp}'.format(
			location=self.location,
			timestamp=self.timestamp,
		)
"""
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

