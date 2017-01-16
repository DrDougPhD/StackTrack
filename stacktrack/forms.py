from django import forms
from django.forms import formset_factory

ImagesToUploadFormset = formset_factory(forms.ImageField, can_order=True)


class StackAdditionForm(forms.Form):
		uploaded_imgs = ImagesToUploadFormset(
		) # requires pillow
		sale_post = forms.URLField(
			required=False,
			help_text='URL to where you purchased this item'
		)
		purchase_price = forms.FloatField(
			min_value=0.0,
			help_text='How much did you pay for this?'
		)
		shipping_price = forms.FloatField(
			min_value=0.0,
			required=False,
			help_text='How much was shipping?'
		)
		tracking_num = forms.URLField(
			required=False,
			help_text='Specify the tracking number if available'
		)
		purchase_date = forms.DateTimeField(
			help_text='When did you purchase this item?'
		)

		# hidden fields
		ingot = forms.IntegerField()
		user = forms.IntegerField()

