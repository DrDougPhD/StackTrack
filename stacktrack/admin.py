from django.contrib import admin

from .models import Ingot
from .models import Fineness
from .models import Mass
from .models import IngotType


@admin.register(Ingot)
class IngotAdmin(admin.ModelAdmin):
	pass

@admin.register(Fineness)
class FinenessAdmin(admin.ModelAdmin):
	pass

@admin.register(Mass)
class MassAdmin(admin.ModelAdmin):
	pass

@admin.register(IngotType)
class IngotTypeAdmin(admin.ModelAdmin):
	pass

