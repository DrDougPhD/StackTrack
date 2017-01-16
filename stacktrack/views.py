from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import Fineness
from .models import StackEntry
from .models import Ingot

# Create your views here.
def index(request):
	# return HttpResponse('Hello from Python!')
	return render(request, 'index.html')
	# r = requests.get('http://httpbin.org/status/418')
	# print(r.text)
	# return HttpResponse('<pre>' + r.text + '</pre>')


def dashboard(request):
	user = User.objects.all()[0]
	stack_entries = StackEntry.objects.filter(owner=user)\
		.order_by('-purchase__timestamp')

	# calculate aggregate attributes
	purchases = 0
	sales = 0
	profits = 0
	weight = 0
	qty = 0
	for entry in stack_entries:
		purchase_price = entry.bought_for.amount
		purchases += purchase_price
		if not entry.sale:
			weight += entry.ingot.mass.convert_to_ozt()
			qty += 1

		else:
			# this ingot was sold
			sale_price = entry.sold_for.amount
			sales += sale_price
			profits += (sale_price - purchase_price)

	cost_per_ozt = float(purchases - sales)/float(weight)

	return render(request, 'stack.html', {
		'page_title': 'Dashboard',
		'stack_entries': stack_entries,
		'cost_per_ozt': cost_per_ozt,
		'weight': weight,
		'qty': qty,
		'purchases': purchases,
		'sales': sales,
		'profits': profits,
	})
	#return render(request, 'dashboard.html')


from .forms import StackAdditionForm
def stack_addition(request, catalog_id):
	ingot = Ingot.objects.get(id=catalog_id)
	print(request)
	print(request.META)
	"""
	if 'application/json' in request.META['CONTENT_TYPE']:
		print('='*80)
		print('Receiving JSON!')
		print(pprint.pformat(request.body)) 
	"""

	if request.method == 'POST':
		form = StackAdditionForm(request.POST)
		print(request.POST)
		if form.is_valid():
			print('='*80)
			print(pprint.pformat(form.cleaned_data))
			print('Sale post: ' + form.cleaned_data['sale_post'])
			print('Purchase price: $' + form.cleaned_data['purchase_price'])
			print('Shipping price: $' + form.cleaned_data['shipping_price'])
			print('Tracking: ' + form.cleaned_data['tracking_num'])
			print('Purchase date: ' + str(form.cleaned_data['purchase_date']))

			return HttpResponse('Success!')

	else: # GET
		form = StackAdditionForm()

	return render(request, 'stack_addition.html', {
		'page_title': 'Stack Addition | {ingot_name}'.format(ingot_name=ingot.name),
		'ingot': ingot,
		'form': form,
	})


import json
def stack_addition_json(request):
	print('Content Type: {}'.format(request.content_type))
	print('Method: {}'.format(request.method))
	print('Body: {}'.format(request.body))
	print('Is AJAX?: {}'.format(request.is_ajax()))
	if request.method == 'POST':
		name = request.POST.get('name')
		return HttpResponse(json.dumps({'name': name}), content_type="application/json")

	else:
		return render(request, 'json.html', { 'data': 'blah' })


def catalog(request):
	ingots = Ingot.objects.all().order_by('-date_posted')
	data = {
		'page_title': 'Catalog',
		'catalog': ingots,
	}
	return render(request, 'catalog.html', data)


from .batch import main
def batch(request):
	processed = main()
	import pprint
	processd_pretty = pprint.pformat(processed)
	return render(request, 'batch.html', { 'data': processd_pretty })

