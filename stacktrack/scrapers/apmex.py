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
logger = logging.getLogger(__appname__)


PRODUCT_URL_FMT = 'http://www.apmex.com/product/{i}/'
SEARCH_MAX = 120000
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

	except requests.exceptions.HTTPError as e:
		logger.exception('End of the line at product #{}'.format(SEARCH_MAX))

	else:
		pass

	finally:
		pass


import requests
from lxml import html
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
	title = product_container.xpath('div[1]/div/div[2]/div/h1')[0]
	assert title.get('class') == 'product-title',\
		'Title item does not have product-title class'

	# Product images
	image_element = product_container.xpath('//*[@id="additional-images-carousel"]/div/div')[0]
	assert len(image_element.xpath('a')) > 0, 'There are no images in expected location'
	
	# Product description
	product_description = product_container.xpath('div[1]/div/div[3]')[0]
	assert product_description.xpath('//*[@id="productdetails-nav"]')[0].text == 'Product Details',\
		'Product description header is not named "Product Details"'

	# Product specification
	product_spec = product_container.xpath('div[2]/div[3]/div')[0]
	assert product_spec.xpath('h2/text()')[0].strip() == 'Product  Specifications',\
		'Product spec header is not named as expected'

	product_spec_rows = product_container.xpath('/html/body/main/div[1]/div[2]/div[3]/div/div[1]/div')
	assert len(product_spec_rows) == 10,\
		'There are not exactly 10 entries in the product spec'

	expected_product_spec_row_names = ['Product ID:', 'Year:', 'Grade:', 'Grade Service:', 'Denomination:', 'Mint Mark:', 'Metal Content:', 'Purity:', 'Manufacturer:', 'Diameter:']
	for (row, expected_name) in zip(product_spec_rows, expected_product_spec_row_names):
		assert row[0].text == expected_name, 'Product spec row "{0}" did not match expected name "{1}"'.format(row[0].text, expected_name)
		


def download_product_page(product_id):
	logger.info('Download product #{}'.format(product_id))
	r = requests.get(PRODUCT_URL_FMT.format(i=product_id))

	# If page not found, raise an exception and stop processing.
	r.raise_for_status()

	page = html.fromstring(r.text)

	global ASSUMPTIONS_TESTED
	if not ASSUMPTIONS_TESTED:
		test_parsing_assumptions(page)
		ASSUMPTIONS_TESTED = True

	return


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
