import csv
import pprint
import urllib.parse


csv_filename = 'ag_tx.csv'


def main():
	with open(csv_filename) as csv_file:
		records = csv.DictReader(csv_file)
		pprint.pprint(records.fieldnames)
		print('-'*80)
		process(records)


def process(csvrecords):
	"""
	us_dollar = Currency(
		name='US Dollar',
		abbreviation='USD',
		symbol='$',
		country='United States',
	)
	us_dollar.save()
	"""
	us_dollar = ('US Dollar', 'USD', '$', 'United States')
	admin = 'Me' # User.objects.all()[0]
	fineness = '.999 fine (three nines)' #Fineness(friendly_name='.999 fine (three nines)')
	# fineness.save()
	ingot_types = {
		'bar': None, #IngotType(name='bar'),
		'round': None, #IngotType(name='round'),
		'coin': None, #IngotType(name='coin'),
	}
	"""
	for ingot_name in ingot_types:
		ingot_types[ingot_name].save()
	"""

	records = [dict(r) for r in csvrecords]
	process_platforms(records)
	process_shipping(records, us_dollar)
	#process_masses(records)

	# Process masses
	gram_to_ozt = {'name': 'gram', 'abbreviation': 'g', 'ozt_multiplier': 0.03215}
	ozt_to_ozt = {'name': 'troy ounce', 'abbreviation': 'ozt', 'ozt_multiplier': 1.0}
	units_of_mass = {
		'gram': gram_to_ozt,
		'troy ounce': ozt_to_ozt,
	}
	registered_weights = {}
	for r in records:
		ozt = r['Size (ozt)']

		if ozt in registered_weights:
			weight = registered_weights[ozt]

		else:
			g = r['Total unit weight (g)'] or None

			# is this unit in grams or ozt?
			if g:
				weight = {
					'number': float(g),
					'friendly_name': '{} grams'.format(g),
					'unit': gram_to_ozt,
			} 
			else:
				troy_ounces = float(ozt)
				if troy_ounces >= 1:
					friendly_name_number = troy_ounces
				else:
					fraction = int(1/troy_ounces)
					friendly_name_number = '1/{}'.format(fraction)

				weight = {	
					'number': float(ozt),
					'friendly_name': '{} ozt'.format(friendly_name_number),
					'unit': ozt_to_ozt,
				}

			registered_weights[ozt] = weight

		r['mass'] = weight

	print('-'*10 + '|~ Mass ~|' + '-'*10)
	print('Units of mass: {}'.format(pprint.pformat(units_of_mass)))
	print('-'*40)
	pprint.pprint(registered_weights)

	"""
	# Ingot
		fineness # done
		mass
		mass_unit
		ingot_type # done
		image
		primary_image

	# Stack Entry
		ingot # done
		owner # done
		purchase
		bought_for

	# Purchase (Transaction)

	# Purchase Amount (TransactionAmount, single ingot)
		currency # done

	# Platform User
		platform # done

	# Sale Post
		platform # done
		seller # done

	# Total cost of transaction?
		shipping # done
		total_price
		sale_post # above

	"""
	"""
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

	pprint.pprint(ingots)
	pprint.pprint(registered_weights)
	"""

	# Create mass entries
	"""
	for m in registered_weights:
		mass_unit = UnitOfMass(name='', abbreviation='', ozt_multiplier='')
		mass = Mass(number='', friendly_name='', unit='')
	"""


def process_shipping(records, us_dollar):
	shipping_companies = {}
	tracking_numbers = {}
	shipping_costs = {}
	for r in records:
		# Shipping costs
		if r['Actual shipping']:
			shipping_cost_entry = r['Actual shipping']

		elif r['Charged shipping']:
			shipping_cost_entry = r['Charged shipping']

		else:
			shipping_cost_entry = '0.00'

		shipping_cost = float(shipping_cost_entry)

		if shipping_cost in shipping_costs:
			shipping_tx = shipping_costs[shipping_cost]

		else:
			"""
			shipping_tx = TransactionAmount(
				amount=shipping_cost,
				currency=us_dollar,
			)
			shipping_tx.save()
			"""
			shipping_tx = (shipping_cost, us_dollar)
			shipping_costs[shipping_cost] = shipping_tx

		r['shipping_cost'] = shipping_tx


		# Shipping company
		tracking = r['Purchase tracking']
		if tracking:
			domain_name, homepage = extract_website_info(tracking)
			print('{domain_name}:\t{homepage}'.format(**locals()))

		else:
			domain_name, homepage = ('Not specified', None)

		if domain_name in shipping_companies:
			s = shipping_companies[domain_name]

		else:
			"""
			s = ShippingCompany(
				company_name=domain_name,
				url=homepage,
				# tracking_url_fmt=,
			)
			s.save()
			"""
			s = (domain_name, homepage)
			shipping_companies[domain_name] = s

		r['shipping_company'] = s

		# Tracking
		if tracking:
			parsed_url = urllib.parse.urlparse(tracking)
			query_params = urllib.parse.parse_qsl(parsed_url.query)
			assert len(query_params) == 1, (
				'Tracking URL has more than one query'
				' parameters: {}').format(tracking)
			tracking_num = query_params[0][1]
			print(tracking_num)

		else:
			tracking_num = 'None specified'

		if tracking_num in tracking_numbers:
			t = tracking_numbers[tracking_num]

		else:
			"""
			t = Shipping(
				shipping_company=s,
				price=shipping_tx,
				tracking=tracking_num,
			)
			t.save()
			"""
			t = (s, shipping_tx, tracking_num)
			tracking_numbers[tracking_num] = t

		r['tracking'] = t

	print('-'*10 + '|~ Shipping ~|' + '-'*10)
	pprint.pprint(shipping_companies)
	print('-'*10 + '|~ Ship cost ~|' + '-'*10)
	pprint.pprint(shipping_costs)
	print('-'*10 + '|~ Tracking ~|' + '-'*10)
	pprint.pprint(tracking_numbers)


def process_platforms(records):
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
			domain_name, homepage = extract_website_info(url)

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
			u = PlatformUser(
				username=username,
				platform=p,
			)
			u.save()

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
	pprint.pprint(users)
	print('-'*10 + '|~ PLATFORMS ~|' + '-'*10)
	pprint.pprint(platforms)


def extract_website_info(url):
	parsed_url = urllib.parse.urlparse(url)
	domain_name = parsed_url.netloc.split('.')[-2]
	homepage = '{scheme}://{netloc}/'.format(
		scheme=parsed_url.scheme,
		netloc=parsed_url.netloc,
	)
	return domain_name, homepage


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

# Sale Platform Models
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
	tracking_url_fmt = models.URLField(null=True)
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

