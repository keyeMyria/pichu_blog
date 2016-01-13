from django.conf.urls import patterns, include, url

urlpatterns = patterns('pichublog.views',
	url(r'^$', 'home.Home', name='pichublog_home'),
)