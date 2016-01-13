from django.conf.urls import patterns, include, url

urlpatterns = patterns('mainapp.views',
	url(r'^$', 'home.Home', name='pichublog_home'),
)