from django.conf.urls import patterns, include, url

urlpatterns = patterns('pichublog.views',
	url(r'^$', 'home.Home', name='pichublog_home'),
	url(r'^msgboard/$', 'home.LeaveMsgPage', name='pichublog_msgboard'),
	url(r'^msgboard/ajax/show/$', 'home.AjaxShowLeaveMsg', name='pichublog_lmshow'),
	url(r'^msgboard/add/$', 'home.LeaveMsgAdd', name='pichublog_lmadd'),
)