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


def db(request):
	return render(request, 'db.html', {'finenesses': ''})


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
	form = StackAdditionForm()
	return render(request, 'stack_addition.html', {
		'page_title': 'Stack Addition | {ingot_name}'.format(ingot_name=ingot.name),
		'ingot': ingot,
		'form': form,
	})


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

