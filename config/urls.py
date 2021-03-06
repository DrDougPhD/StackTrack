from django.conf.urls import include
from django.conf.urls import url

from django.contrib import admin
admin.autodiscover()

import stacktrack.views

# Examples:
# url(r'^$', 'config.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
	url(r'^$', stacktrack.views.index, name='index'),
	url(r'^db', stacktrack.views.db, name='db'),
	url(r'^admin/', include(admin.site.urls)),
]
