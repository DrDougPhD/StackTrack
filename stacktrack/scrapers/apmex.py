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
import os
import logging
import requests
from lxml import html
from lxml import etree
import json
import time
import urllib.parse
logger = logging.getLogger(__appname__)


PRODUCT_URL_FMT = 'http://www.apmex.com/product/{i}/'
SEARCH_MAX = 120000

TITLE_XPATH = '/html/body/main/div[1]/div[1]/div/div[2]/div/h1'
IMAGES_XPATH = '//*[@id="additional-images-carousel"]/div/div/a'
DESCRIPTION_XPATH = '//*[@id="productdetails"]/div[1]'
SPEC_XPATH = '//div[@class="product-specifications"]/div'

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FILES_DIR = os.path.join(CURRENT_DIR, 'archive')
os.makedirs(ARCHIVE_FILES_DIR, exist_ok=True)
IMAGES_DIR = os.path.join(CURRENT_DIR, 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)

DELAY = 2

def main(args):
	for i in range(1, SEARCH_MAX):
		try:
			webpage, local_cache = download_product_page(i)
			product_info = extract_product_info(webpage)
			save(product_info, i)
			download_images(product_info, i)
			logger.info('{0}:\t {1}'.format(i, product_info['title']))
			time.sleep(DELAY)

		except requests.exceptions.HTTPError as e:
			logger.exception('End of the line at product #{}'.format(SEARCH_MAX))
			log_product_id_error(i)
			break

		else:
			log_product_id_success(i)

	logger.info('Done')


def log_product_id_error(pid):
	with open('errors.txt', 'a') as f:
		f.write('{}\n'.format(pid))


def log_product_id_success(pid):
	with open('successes.txt', 'a') as f:
		f.write('{}\n'.format(pid))


def download_images(product_info, pid):
	for img_url in product_info['images']:
		url = urllib.parse.urlparse(img_url)
		filename = os.path.basename(url.path)
		download_to = os.path.join(IMAGES_DIR, filename)
		if os.path.isfile(download_to):
			continue

		logger.debug('\t\t{}'.format(filename))

		response = requests.get(img_url, stream=True)
		downloaded_file = open(download_to, 'wb')
		for chunk in response.iter_content(chunk_size=4096):
			if chunk:
				downloaded_file.write(chunk)


def save(product_info, pid):
	json_file_path = os.path.join(ARCHIVE_FILES_DIR, '{}.json'.format(pid))
	with open(json_file_path, 'w') as f:
		json.dump(product_info, f)

	logger.debug('\tProduct info json saved to {}'.format(json_file_path))


def download_product_page(product_id):
	local_cache_file_path = get_archive_file_path(product_id)
	if os.path.isfile(local_cache_file_path):
		logger.debug('\tAlready archived at {}'.format(local_cache_file_path))
		with gzip.open(local_cache_file_path, 'rb') as f:
			content = f.read()

		return content.decode(), local_cache_file_path

	else:
		logger.debug('\tRetrieving from website')
		r = requests.get(PRODUCT_URL_FMT.format(i=product_id))

		# If page not found, raise an exception and stop processing.
		r.raise_for_status()

		archived_file_path = archive(r.content, product_id)
		return r.text, archived_file_path


import gzip
def archive(raw_html, product_id):
	archive_file = get_archive_file_path(product_id)
	with gzip.open(archive_file, 'wb') as f:
		f.write(raw_html)

	logger.debug('\tArchived to {}'.format(archive_file))
	return archive_file


def get_archive_file_path(pid):
	return os.path.join(ARCHIVE_FILES_DIR, '{}.html.gz'.format(pid))


def extract_product_info(raw_html):
	page = html.fromstring(raw_html)

	global ASSUMPTIONS_TESTED
	if not ASSUMPTIONS_TESTED:
		test_parsing_assumptions(page)
		ASSUMPTIONS_TESTED = True

	bullion, breadcrumbs = get_bullion(page)
	product_info = dict(
		title = get_title(page),
		bullion = bullion,
		breadcrumbs = breadcrumbs,
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
	return breadcrumb_bullion_item['item']['name'], breadcrumbs


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


def get_description(page):
	description_element = page.xpath(DESCRIPTION_XPATH)[0]
	description_raw_html = etree.tostring(description_element).decode().strip()
	return description_raw_html


def get_spec(page):
	spec_table_elements = page.xpath(SPEC_XPATH)
	spec = {}
	for row in spec_table_elements:
		key = row[0].text.strip()
		if not key:
			# sometimes there's a pdf in the spec table. just ignore it.
			continue

		val = row[1].text.strip()
		spec[key] = val

	return spec


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
	product_spec = product_container.xpath('//div[@class="product-specs"]')[0]
	assert product_spec.xpath('h2/text()')[0].strip() == 'Product  Specifications',\
		'Product spec header is not named as expected'

	product_spec_rows = product_container.xpath(SPEC_XPATH)
	assert len(product_spec_rows) >0,\
		'There are no specs in the table!'


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
		'%(message)s'
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
		default=False, help='verbose output')

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
