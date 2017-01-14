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
		http://www.images-apmex.com/images/Catalog%20Images/Products/{i}_Obv.jpg?v=20130602094622&width=75&height=75
		http://www.images-apmex.com/images/Catalog%20Images/Products/{i}_Rev.jpg?v=20130602094622&width=75&height=75
	Product page url format:
		http://www.apmex.com/product/{i}/

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
