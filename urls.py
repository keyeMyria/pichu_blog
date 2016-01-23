from django.conf.urls import patterns, include, url

urlpatterns = patterns('pichublog.views',
	url(r'^$', 'home.Home', name='pichublog_home'),

	url(r'^msgboard/$', 'home.LeaveMsgPage', name='pichublog_msgboard'),
	url(r'^msgboard/ajax/show/$', 'home.AjaxShowLeaveMsg', name='pichublog_lmshow'),
	url(r'^msgboard/add/$', 'home.LeaveMsgAdd', name='pichublog_lmadd'),

	url(r'^pichu/sysconf/$', 'home.SysConf', name='pichublog_sysconf'),
	url(r'^pichu/sysconf/var/$', 'home.SysVarConf', name='pichublog_sysvarconf'),
	url(r'^pichu/sysconf/var/ajax/get/$', 'home.SysVarConfAjaxGet', name='pichublog_sysvarajaxget'),
	url(r'^pichu/sysconf/var/ajax/edit/$', 'home.SysVarConfAjaxEdit', name='pichublog_sysvarajaxedit'),
	url(r'^pichu/sysconf/var/ajax/toggle/$', 'home.SysVarConfAjaxToggle', name='pichublog_sysvarajaxtoggle'),
	url(r'^pichu/sysconf/category/$', 'home.CategoryList', name='pichublog_catlist'),
	url(r'^pichu/sysconf/category/add/$', 'home.CategoryAdd', name='pichublog_catadd'),
	url(r'^pichu/sysconf/category/del/(?P<ID>\d+)/$', 'home.CategoryDel', name='pichublog_catdel'),
	url(r'^pichu/sysconf/category/edit/(?P<ID>\d+)/$', 'home.CategoryEdit', name='pichublog_catedit'),

	url(r'^c/(?P<ctname>[0-9a-zA-Z_\*]+)/$', 'posts.PostList', name='pichublog_postlist'),
	url(r'^writer/post/list/$', 'posts.PostWBkList', name='pichublog_postwbklist'),
	url(r'^writer/post/add/$', 'posts.PostAdd', name='pichublog_postadd'),
	url(r'^p/(?P<ID>\d+)/$', 'posts.PostView', name='pichublog_postview'),
	url(r'^pichu/preview/(?P<ID>\d+)/$', 'posts.PostPreview', name='pichublog_postpreview'),
	url(r'^p/(?P<ID>\d+)/edit/$', 'posts.PostEdit', name='pichublog_postedit'),
	url(r'^p/(?P<ID>\d+)/grant/$', 'posts.PostGrant', name='pichublog_postgrant'),
	url(r'^p/(?P<ID>\d+)/hid/$', 'posts.PostHidden', name='pichublog_posthid'),
	url(r'^p/(?P<ID>\d+)/del/$', 'posts.PostDel', name='pichublog_postdel'),
	url(r'^p/(?P<ID>\d+)/comments/ajax/show/$', 'posts.AjaxShowComments', name='pichublog_cmtshow'),
	url(r'^p/(?P<ID>\d+)/comments/add/$', 'posts.AddComments', name='pichublog_cmtadd'),
	url(r'^pichu/post/list/$', 'posts.PostABkList', name='pichublog_postabklist'),
	
)