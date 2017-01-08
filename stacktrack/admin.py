from django.contrib import admin

from .models import Greeting
from .models import Fineness

@admin.register(Greeting)
class GreetingAdmin(admin.ModelAdmin):
	pass


@admin.register(Fineness)
class FinenessAdmin(admin.ModelAdmin):
	pass


