from django.contrib import admin


from .models import Ingot
@admin.register(Ingot)
class IngotAdmin(admin.ModelAdmin):
	pass


from .models import Manufacturer
@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
	pass


from .models import Fineness
@admin.register(Fineness)
class FinenessAdmin(admin.ModelAdmin):
	pass


from .models import Mass
@admin.register(Mass)
class MassAdmin(admin.ModelAdmin):
	pass


from .models import UnitOfMass
@admin.register(UnitOfMass)
class UnitOfMassAdmin(admin.ModelAdmin):
	pass


from .models import IngotType
@admin.register(IngotType)
class IngotTypeAdmin(admin.ModelAdmin):
	pass


from .models import Image
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
	pass


from .models import PrimaryImage
@admin.register(PrimaryImage)
class PrimaryImageAdmin(admin.ModelAdmin):
	pass


from .models import StackEntry
@admin.register(StackEntry)
class StackEntryAdmin(admin.ModelAdmin):
	pass


from .models import TransactionAmount
@admin.register(TransactionAmount)
class TransactionAmountAdmin(admin.ModelAdmin):
	pass


from .models import Currency
@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
	pass


from .models import PlatformUser
@admin.register(PlatformUser)
class PlatformUserAdmin(admin.ModelAdmin):
	pass


from .models import Platform
@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
	pass


from .models import SalePost 
@admin.register(SalePost)
class SalePostAdmin(admin.ModelAdmin):
	pass


from .models import EbayPostAttributes
@admin.register(EbayPostAttributes)
class EbayPostAttributesAdmin(admin.ModelAdmin):
	pass


from .models import Shipping
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
	pass


from .models import ShippingCompany
@admin.register(ShippingCompany)
class ShippingCompanyAdmin(admin.ModelAdmin):
	pass


from .models import ShippingStatus
@admin.register(ShippingStatus)
class ShippingStatusAdmin(admin.ModelAdmin):
	pass

"""
from .models import Trade
@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
	pass


from .models import TradeItem
@admin.register(TradeItem)
class TradeItemAdmin(admin.ModelAdmin):
	pass
"""
