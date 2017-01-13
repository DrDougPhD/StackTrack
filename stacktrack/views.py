from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User

from .models import Fineness
from .models import StackEntry

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
	stack_entries = StackEntry.objects.filter(owner=user).order_by('-purchase_id')
	return render(request, 'stack.html', {
		'stack_entries': stack_entries
	})
	#return render(request, 'dashboard.html')

from .batch import main
def batch(request):
	processed = main()
	import pprint
	processd_pretty = pprint.pformat(processed)
	return render(request, 'batch.html', { 'data': processd_pretty })

