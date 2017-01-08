from django.contrib import admin

from .models import Fineness


@admin.register(Fineness)
class FinenessAdmin(admin.ModelAdmin):
	pass


