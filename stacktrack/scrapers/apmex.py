#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	python SCRIPT.py [-h,--help] [-v,--verbose]


DESCRIPTION

	Download catalog information from APMEX.


ARGUMENTS

	-h, --help		show this help message and exit
	-v, --verbose		verbose output


STEPS

	Download a product page.
	Archive original HTML file.
	Extract values from product page.
	Download images.

NOTES

	Image filename formats: 
		http://www.images-apmex.com/images/Catalog Images/Products/{i}_Slab.jpg?v=20160819024312&width=900&height=900
		http://www.images-apmex.com/images/Catalog%20Images/Products/{i}_Obv.jpg?v=20130602094622&width=75&height=75
		http://www.images-apmex.com/images/Catalog%20Images/Products/{i}_Rev.jpg?v=20130602094622&width=75&height=75
		sometimes the obv/Obv is capitalized
	Product page url format:
		http://www.apmex.com/product/{i}/
	Bullion type of item is not listed in spec, but can be deduced from breadcrumb.

AUTHOR

	Doug McGeehan <djmvfb@mst.edu>


LICENSE

	Specify this script's / package's license.

"""

__appname__ = "stacktrack.scrapers.apmex"
__author__  = "Doug McGeehan <djmvfb@mst.edu>"
__version__ = "0.0pre0"
__license__ = "License"


import argparse
from datetime import datetime
import sys
import logging
import requests
from lxml import html
import json
logger = logging.getLogger(__appname__)


PRODUCT_URL_FMT = 'http://www.apmex.com/product/{i}/'
SEARCH_MAX = 120000

TITLE_XPATH = '/html/body/main/div[1]/div[1]/div/div[2]/div/h1'
IMAGES_XPATH = '//*[@id="additional-images-carousel"]/div/div/a'
DESCRIPTION_XPATH = '//*[@id="productdetails"]/div[1]'
SPEC_XPATH = '/html/body/main/div[1]/div[2]/div[3]/div/div[1]/div'


def main(args):
	starting_index = 116000

	try:
		"""
		for i in range(SEARCH_MAX):
			webpage = download_product_page(i)
			if page_not_found(webpage):
				break

			archive(webpage)
			product_info = extract_product_info(webpage)
			save(product_info)
			download_images(i, product_info)
		"""
		webpage = download_product_page(starting_index)
		product_info = extract_product_info(webpage)
		from pprint import pprint
		pprint(product_info)

	except requests.exceptions.HTTPError as e:
		logger.exception('End of the line at product #{}'.format(SEARCH_MAX))

	else:
		pass

	finally:
		pass


ASSUMPTIONS_TESTED = False
def test_parsing_assumptions(page):
	# Page contains a "page-container" div with "http://schema.org/Product" itemtype.
	containers = page.xpath('/html/body/main/div[1]')
	assert len(containers) >= 1,\
		'No expected div class for entire product info'

	product_container = containers[0]
	assert product_container.get('itemtype') == 'http://schema.org/Product',\
		'First page-container is not of type http://schema.org/Product'

	# The product title exists
	title = product_container.xpath(TITLE_XPATH)[0]
	assert title.get('class') == 'product-title',\
		'Title item does not have product-title class'

	# Product images
	images_element = product_container.xpath(IMAGES_XPATH)
	assert len(images_element) > 0, 'There are no images in expected location'
	
	# Product description
	assert page.xpath('//*[@id="productdetails-nav"]')[0].text == 'Product Details',\
		'Product description header is not named "Product Details"'

	# Product specification
	product_spec = product_container.xpath('div[2]/div[3]/div')[0]
	assert product_spec.xpath('h2/text()')[0].strip() == 'Product  Specifications',\
		'Product spec header is not named as expected'

	product_spec_rows = product_container.xpath(SPEC_XPATH)
	assert len(product_spec_rows) == 10,\
		'There are not exactly 10 entries in the product spec'

	expected_product_spec_row_names = [
		'Product ID:', 'Year:', 'Grade:', 'Grade Service:', 'Denomination:',
		'Mint Mark:', 'Metal Content:', 'Purity:', 'Manufacturer:', 'Diameter:'
	]
	for (row, expected_name) in zip(product_spec_rows, expected_product_spec_row_names):
		assert row[0].text == expected_name, 'Product spec row "{0}" did not match expected name "{1}"'.format(row[0].text, expected_name)
		


def download_product_page(product_id):
	logger.info('Download product #{}'.format(product_id))
	r = requests.get(PRODUCT_URL_FMT.format(i=product_id))

	# If page not found, raise an exception and stop processing.
	r.raise_for_status()

	return r.text


def extract_product_info(raw_html):
	page = html.fromstring(raw_html)

	global ASSUMPTIONS_TESTED
	if not ASSUMPTIONS_TESTED:
		test_parsing_assumptions(page)
		ASSUMPTIONS_TESTED = True

	product_info = dict(
		bullion = get_bullion(page),
		title = get_title(page),
		images = get_image_urls(page),
		description = get_description(page),
		spec = get_spec(page),
	)
	return product_info


def get_bullion(page):
	breadcrumb_xpath = '/html/body/main/div[1]/div[1]/div/script'
	breadcrumbs_json = page.xpath(breadcrumb_xpath)[0].text
	breadcrumbs = json.loads(breadcrumbs_json)
	breadcrumb_itemlist = breadcrumbs['itemListElement']
	breadcrumb_bullion_item = breadcrumb_itemlist[1]
	return breadcrumb_bullion_item['item']['name']


def get_title(page):
	raw_title = page.xpath(TITLE_XPATH)[0].text
	stripped_title = raw_title.strip()
	return stripped_title


def get_image_urls(page):
	# NOTE: Some pages have video, some images are named "slab", some "rev" images are actually logos.
	image_elements = page.xpath(IMAGES_XPATH)

	urls = []
	for single_image in image_elements:
		if single_image.get('class') == 'video':
			continue

		raw_url = single_image.get('href')

		# strip parameters from URL
		final_url = raw_url.split('?')[0]
		urls.append(final_url)

	return urls


from lxml import etree
def get_description(page):
	description_element = page.xpath(DESCRIPTION_XPATH)[0]
	description_raw_html = etree.tostring(description_element).decode().strip()
	return description_raw_html

def get_spec(page):
	spec_table_elements = page.xpath(SPEC_XPATH)
	spec = {}
	for row in spec_table_elements:
		key = row[0].text.strip()
		val = row[1].text.strip()
		spec[key] = val

	return spec


def setup_logger(args):
	logger.setLevel(logging.DEBUG)
	# create file handler which logs even debug messages
	# todo: place them in a log directory, or add the time to the log's
	# filename, or append to pre-existing log
	fh = logging.FileHandler(__appname__ + ".log")
	fh.setLevel(logging.DEBUG)
	# create console handler with a higher log level
	ch = logging.StreamHandler()

	if args.verbose:
		ch.setLevel(logging.DEBUG)
	else:
		ch.setLevel(logging.INFO)

	# create formatter and add it to the handlers
	fh.setFormatter(logging.Formatter(
		'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	))
	ch.setFormatter(logging.Formatter(
		'%(levelname)s - %(message)s'
	))
	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

	
def get_arguments():
	parser = argparse.ArgumentParser(
		description="Description printed to command-line if -h is called."
	)
	# during development, I set default to False so I don't have to keep
	# calling this with -v
	parser.add_argument('-v', '--verbose', action='store_true',
		default=True, help='verbose output')

	return parser.parse_args()


if __name__ == '__main__':
	try:
		start_time = datetime.now()

		args = get_arguments()
		setup_logger(args)
		logger.debug(start_time)

		main(args)

		finish_time = datetime.now()
		logger.debug(finish_time)
		logger.debug('Execution time: {time}'.format(
			time=(finish_time - start_time)
		))
		logger.debug("#"*20 + " END EXECUTION " + "#"*20)

		sys.exit(0)

	except KeyboardInterrupt as e: # Ctrl-C
		raise e

	except SystemExit as e: # sys.exit()
		raise e

	except Exception as e:
		logger.exception("Something happened and I don't know what to do D:")
		sys.exit(1)
