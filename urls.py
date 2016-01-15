from django.conf.urls import patterns, include, url

urlpatterns = patterns('pichublog.views',
	url(r'^$', 'home.Home', name='pichublog_home'),
	url(r'^pichu/sysconf/$', 'home.SysConf', name='pichublog_sysconf'),
	url(r'^pichu/sysconf/var/$', 'home.SysVarConf', name='pichublog_sysvarconf'),
	url(r'^pichu/sysconf/var/ajax/get/$', 'home.SysVarConfAjaxGet', name='pichublog_sysvarajaxget'),
	url(r'^pichu/sysconf/var/ajax/edit/$', 'home.SysVarConfAjaxEdit', name='pichublog_sysvarajaxedit'),
	url(r'^pichu/sysconf/var/ajax/toggle/$', 'home.SysVarConfAjaxToggle', name='pichublog_sysvarajaxtoggle'),
	url(r'^msgboard/$', 'home.LeaveMsgPage', name='pichublog_msgboard'),
	url(r'^msgboard/ajax/show/$', 'home.AjaxShowLeaveMsg', name='pichublog_lmshow'),
	url(r'^msgboard/add/$', 'home.LeaveMsgAdd', name='pichublog_lmadd'),
)