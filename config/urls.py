from django.conf.urls import include
from django.conf.urls import url

from django.contrib import admin
admin.autodiscover()

import stacktrack.views

# Examples:
# url(r'^$', 'config.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

# stack/dashboard/
# stack/silver/
# stack/gold/
# stack/platinum/
# stack/palladium/
# stack/archive/
# stack/add/
urlpatterns = [
	url(r'^$', stacktrack.views.index, name='index'),
	url(r'^dashboard', stacktrack.views.dashboard, name='dashboard'),
	url(r'^catalog', stacktrack.views.catalog, name='catalog'),
	url(r'^batch', stacktrack.views.batch, name='batch'),
	url(r'^stack/add/([0-9]+)/$', stacktrack.views.stack_addition, name='stack-add'),
	url(r'^admin/', include(admin.site.urls)),
]
