"""
TODO

* Interface with various websites
	* ebay (public)
	* ebay (account)
	* Paypal
	* reddit (public)
	* reddit (account)
	* Google Wallet
	* Bank / credit card statements
		* PDF?
		* QuickBooks / portable format
"""

import csv
import pprint
import urllib.parse
from datetime import datetime
import os
from collections import defaultdict
import logging
logger = logging.getLogger('batch')

DATA_DIRECTORY = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    'data',
)) 
csv_filename = os.path.join(
    DATA_DIRECTORY,
    'ag_tx.csv'
)


def main():
	with open(csv_filename) as csv_file:
		records = csv.DictReader(csv_file)
		pprint.pprint(records.fieldnames)
		print('-'*80)
		processed = process(records)
	return processed

from django.contrib.auth.models import User
from .models import Ingot
from .models import Manufacturer
from .models import Fineness
from .models import Mass
from .models import UnitOfMass
from .models import IngotType
from .models import Image
from .models import PrimaryImage
from .models import StackEntry
from .models import Platform
from .models import PlatformUser
from .models import SalePost
from .models import Transaction
from .models import TransactionAmount
from .models import Currency
from .models import Shipping
from .models import ShippingCompany
from .models import ShippingStatus

def process(csvrecords):
	us_dollar = Currency(
		name='US Dollar',
		abbreviation='USD',
		symbol='$',
		country='United States',
	)
	us_dollar.save()
	#us_dollar = ('US Dollar', 'USD', '$', 'United States')
	admin = User.objects.all()[0]

	records = [dict(r) for r in csvrecords]
	process_platforms(records)
	process_shipping(records, us_dollar)
	process_masses(records)
	process_ingots(records, admin)
	process_posts(records, us_dollar)
	process_stack_entries(records, admin, us_dollar)
	return records


def process_stack_entries(records, owner, us_dollar):
	stack_entries = []
	for r in records:
		tx = TransactionAmount(
			amount=float(r['Bought for']),
			currency=us_dollar,
		)
		tx.save()
		stack_entry = StackEntry(**{
			'ingot': r['ingot'],
			'owner': owner,
			'purchase': r['transaction'],
			'bought_for': tx,
			'sale': None,
			'sold_for': None,
		})
		stack_entry.save()

		stack_entries.append(stack_entry)
		print('-'*10 + '|~ Stack Entry ~|' + '-'*10)
		pprint.pprint(stack_entry)

	return stack_entries


def process_posts(records, us_dollar):
	# sale posts
	transactions = {}
	sale_posts = {}
	for r in records:
		url = r['Purchase message thread']
		if not url:
			unique_id = cleaned_url = r['Item']
			url = 'N/A'

		else:
			domain_name, homepage = extract_website_info(url)
			parsed_url = urllib.parse.urlparse(url)

			stripped_queries = lambda x: '{scheme}://{netloc}{path}'.format(
				scheme=x.scheme,
				netloc=x.netloc,
				path=x.path
			)
			url_cleaners = {
				'jmbullion': lambda x: x,
				'ebay': stripped_queries,
				'reddit': stripped_queries,
				'apmex': stripped_queries,
				'providentmetals': stripped_queries,
				'qualitysilverbullion': stripped_queries,
				'paypal': lambda x: x,
			}
			cleaned_url = url_cleaners[domain_name](parsed_url)

			before_last_forward_slash = lambda x: x.path.split('/')[-2]
			last_entry_in_path = lambda x: os.path.basename(x.path)
			first_query_parameter = lambda x: urllib.parse.parse_qsl(x.query)[0][1]
			last_query_parameter = lambda x: urllib.parse.parse_qsl(x.query)[-1][1]
			def paypal_id_extractor(x):
				if x.query:
					return last_query_parameter(x)
				else:
					return os.path.basename(x.path).split('=')[-1]

			def reddit_id_extractor(x):
				if 'message' in x.path:
					return last_entry_in_path(x)

				else:
					return before_last_forward_slash(x)

			extractors = defaultdict(lambda x: x)
			extractors.update({
				'ebay': last_entry_in_path,
				'jmbullion': before_last_forward_slash,
				'providentmetals': before_last_forward_slash,
				'reddit': reddit_id_extractor,
				'qualitysilverbullion': last_entry_in_path,
				'apmex': last_entry_in_path,
				'jmbullion': first_query_parameter,
				'paypal': paypal_id_extractor,
			})
			unique_id  = extractors[domain_name](parsed_url)

		# cleaned_url = ...
		#print('{0}:\t{1}'.format(domain_name, unique_id))
		#print('\t\t\t\t{}'.format(cleaned_url))

		if unique_id in sale_posts:
			sale_post = sale_posts[unique_id]

		else:
			sale_post = SalePost(**{
				'title': cleaned_url,
				'description': url,
				'platform': r['platform'],
				'seller': r['seller'],
				# ebay_post_attributes: ...,
				# 'date_listed': '',
				'access_id': unique_id,
			})
			sale_post.save()
			sale_posts[unique_id] = sale_post

		r['sale_post'] = sale_post

		# Transactions associated with sale post
		ingot_bought_for = float(r['Bought for'])
		if unique_id in transactions:
			tx = transactions[unique_id]

			# Update total price by including this item's price
			tx['total_price'] += ingot_bought_for

		else:
			timestamp_str = r['Buy date']
			if timestamp_str:
				timestamp = datetime.strptime(
					timestamp_str,
					'%m/%d/%Y',
				)
			else:
				timestamp = datetime(year=2015, month=1, day=1)

			tx = {
				'total_price': ingot_bought_for,
				'shipping': r['tracking'],
				'timestamp': timestamp,
				'from_post': sale_post,
			}
			transactions[unique_id] = tx

		r['transaction'] = tx
		r['tx_id'] = unique_id

	print('-'*10 + '|~ Sale posts ~|' + '-'*10)
	pprint.pprint(sale_posts)
	print('-'*10 + '|~ Transactions ~|' + '-'*10)
	saved_txs = {}
	for t in transactions:
		tx_amount = TransactionAmount(
			amount=transactions[t]['total_price'],
			currency=us_dollar,
		)
		tx_amount.save()
		transactions[t]['total_price'] = tx_amount
		transaction = Transaction(**transactions[t])
		transaction.save()
		saved_txs[t] = transaction

	for r in records:
		r['transaction'] = saved_txs[r['tx_id']]

	pprint.pprint(transactions)


def process_ingots(records, admin):
	three_nines_fine = Fineness(**{
		'multiplier': 1.0,
		'friendly_name': '.999 fine (three nines)',
	})  #Fineness(friendly_name='.999 fine (three nines)')
	three_nines_fine.save()
	bar = IngotType(name='bar')
	_round = IngotType(name='round')
	coin = IngotType(name='coin')
	ingot = IngotType(name='ingot')
	default = IngotType(name='not specified')
	ingot_types = {
		'bar': bar,
		'round': _round,
		'coin': coin,
		'ingot': ingot,
		'default': default,
	}
	for i in ingot_types:
		ingot_types[i].save()

	silver = Ingot.SILVER

	# Process ingots
	ingots = {}
	for r in records:
		ingot_name = r['Item']

		# detect ingot type from name
		ingot_type = default
		stop = False
		for ingot_word in ingot_types:
			for word in ingot_name.split():
				if ingot_word in word.lower():
					ingot_type = ingot_types[ingot_word]
					stop = True
					break

			if stop:
				break

		if ingot_name in ingots:
			ingot = ingots[ingot_name]

		else:
			ingot = Ingot(**{
				'name': ingot_name,
				'description': '',
				# mintage: ,
				# year: ,
				# silverartcollector_item_number: ,
				'date_posted': datetime.now(),
				'precious_metal': silver,
				'posted_by': admin,
				'fineness': three_nines_fine,
				'mass': r['mass'],
				'ingot_type': ingot_type,
				# manufacturer: ,
				# primary_images: ,
			})
			ingot.save()
			ingots[ingot_name] = ingot

		r['ingot'] = ingot

	print('-'*10 + '|~ Ingots ~|' + '-'*10)
	pprint.pprint(ingots)


def process_masses(records):
	# Process masses
	gram_to_ozt = UnitOfMass(**{
		'name': 'gram', 'abbreviation': 'g', 'ozt_multiplier': 0.03215
	})
	gram_to_ozt.save()
	ozt_to_ozt = UnitOfMass(**{
		'name': 'troy ounce', 'abbreviation': 'ozt', 'ozt_multiplier': 1.0
	})
	ozt_to_ozt.save()
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
				weight = Mass(**{
					'number': float(g),
					'friendly_name': '{} grams'.format(g),
					'unit': gram_to_ozt,
				})
			else:
				troy_ounces = float(ozt)
				if troy_ounces >= 1:
					friendly_name_number = troy_ounces
				else:
					fraction = int(1/troy_ounces)
					friendly_name_number = '1/{}'.format(fraction)

				weight = Mass(**{	
					'number': float(ozt),
					'friendly_name': '{} ozt'.format(friendly_name_number),
					'unit': ozt_to_ozt,
				})

			weight.save()
			registered_weights[ozt] = weight

		r['mass'] = weight

	print('-'*10 + '|~ Mass ~|' + '-'*10)
	print('Units of mass: {}'.format(pprint.pformat(units_of_mass)))
	print('-'*40)
	pprint.pprint(registered_weights)


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
			shipping_tx = TransactionAmount(**{
				'amount': shipping_cost,
				'currency': us_dollar,
			})
			shipping_tx.save()
			shipping_costs[shipping_cost] = shipping_tx

		r['shipping_cost'] = shipping_tx


		# Shipping company
		tracking = r['Purchase tracking']
		if tracking:
			domain_name, homepage = extract_website_info(tracking)
			#print('{domain_name}:\t{homepage}'.format(**locals()))

		else:
			domain_name, homepage = ('Not specified', 'N/A')

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
			s = ShippingCompany(**{
				'company_name': domain_name,
				'url': homepage,
			})
			s.save()
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
			#print(tracking_num)

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
			t = Shipping(**{
				'shipping_company': s,
				'price': shipping_tx,
				'tracking': tracking_num,
			})
			t.save()
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
			'paypal': lambda x: 'Paypal',
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
			p = Platform(**{
				'name': platform_name,
				'homepage': homepage,
			})
			p.save()
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
			u = PlatformUser(**{
				'username': username,
				'platform': p,
			})
			u.save()
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

