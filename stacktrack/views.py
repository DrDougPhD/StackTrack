from django.shortcuts import render
from django.http import HttpResponse

from .models import Fineness

# Create your views here.
def index(request):
	# return HttpResponse('Hello from Python!')
	return render(request, 'index.html')
	# r = requests.get('http://httpbin.org/status/418')
	# print(r.text)
	# return HttpResponse('<pre>' + r.text + '</pre>')


def db(request):

	three_nines = Fineness(multiplier=1.0, friendly_name='.999 fine')
	three_nines.save()

	finenesses = Fineness.objects.all()

	return render(request, 'db.html', {'finenesses': finenesses})


def batch(request):

	return HttpResponse('Hello!') #render(request, 'stack.html', locals())

