# -*- coding: UTF-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response,RequestContext
#from django_hosts.resolvers import reverse
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Max as DbMax
from siteutil.DataConvert import str2int,CheckPOST,str2long,BigIntUniqueID,CacheConfGet
from siteutil.CommonPaginator import SelfPaginator
from zlogin.common.JsonResponse import JsonResponse
from zlogin.decorators import login_detect,login_required,PermNeed
from zlogin import zlauth
from zlogin.zlauth import GetUser,PermCheck
from zlogin.captcha_app import CheckCaptcha,OutsiteCaptchaURL
from pichublog.models import *
from pichublog.forms import *
cache = get_cache("pichublog")
import traceback

@login_detect()
def Home(request):
	mpid = CacheConfGet(cache,'HomePagePost',default=0)
	mpo = None
	try:
		mpo = BlogPost.objects.get(id=str2int(mpid))
		hp = True
	except:
		hp = False
	if hp:
		if not mpo.rendered:
			hp = False
	kwargs = {"request":request,"hp":hp,"mpo":mpo}
	return render_to_response('home/home.html',kwargs,RequestContext(request))

def LeaveMsgPage(request):
	kwargs = {"request":request,'OutsiteCaptchaURL':OutsiteCaptchaURL(request),
			  "LeaveMsgReviewSwitch":CacheConfGet(cache,'LeaveMsgReviewSwitch',default=True)}
	return render_to_response('home/leave.msg.html',kwargs,RequestContext(request))

def AjaxShowLeaveMsg(request):
	thisuser = GetUser(request)
	owner = PermCheck(request.auth,'pichublog','Admin')
	if owner:
		cmt = LeaveMsg.objects.all().order_by('-time')
	else:
		cmt = LeaveMsg.objects.filter(reviewed=True).order_by('-time')
	lPage = SelfPaginator(request,cmt,20)
	kwvars = {
		'request':request,
		'owner':owner,
		'lPage':lPage,
		'AjaxPaginatorID':'cmt',
	}
	return render_to_response('home/ajax.leavemsg.html',kwvars,RequestContext(request))

def LeaveMsgAdd(request):
	if request.method == "POST":
		if request.auth.islogin:
			chkpr=CheckPOST(['content'],request.POST.keys())
			if not chkpr == "" :
				return JsonResponse({"code":400,"msg":"Error Args."})
		else:
			chkpr=CheckPOST(['content','nick','website','mail','title'],request.POST.keys())
			if not chkpr == "" :
				return JsonResponse({"code":400,"msg":"Error Args."})
		if request.auth.islogin:
			content = request.POST.get('content')
			title = request.POST.get('title')
			stk = request.auth.cookie.get('zl2_token')
			LeaveMsg.objects.create(cmid=BigIntUniqueID(),title=title,anonymou=False,stoken=stk,fromuser=request.auth.user,content=content,reviewed=True)
			return HttpResponseRedirect(reverse('pichublog_msgboard'))
		else:
			capt = request.POST.get('captcha')
			if not CheckCaptcha(request,capt):
				messages.error(request,u"<b>验证码错误</b>")
				return HttpResponseRedirect(reverse('pichublog_msgboard'))
			content = request.POST.get('content')
			nick = request.POST.get('nick')
			mail = request.POST.get('mail')
			web = request.POST.get('website')
			title = request.POST.get('title')
			stk = request.auth.cookie.get('zl2_token')
			rws = not CacheConfGet(cache,'LeaveMsgReviewSwitch',default=True)
			LeaveMsg.objects.create(cmid=BigIntUniqueID(),title=title,anonymou=True,stoken=stk,fromuser=nick,mail=mail,website=web,content=content,reviewed=rws)
			return HttpResponseRedirect(reverse('pichublog_msgboard'))
	else:
		return HttpResponse("405 Method Not Allowed")

@PermNeed('pichublog','Admin')
def SysConf(request):
	kwvars = {
		"request":request,
	}
	return render_to_response('home/sysconf.home.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def SysVarConf(request):
	kwvars = {
		"request":request,
	}
	return render_to_response('home/sysconf.var.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def SysVarConfAjaxGet(request):
	defaultconf = [
		("LeaveMsgReviewSwitch","访客在留言板的留言要求审核再显示",True,"bool"),
		("CommentsReviewSwitch","访客对文章的评论要求审核再显示",True,"bool"),
		("HomePagePost","首页内容来源文章ID","","str"),
		("MainTopList","总分类置顶列表（填文章ID，多项之间英文逗号隔开）","","str"),
	]
	conf = []
	for i in defaultconf:
		conf.append((i[0],i[1],CacheConfGet(cache,i[0],default=i[2]),i[3]))
	kwvars = {
		"request":request,
		"conf":conf
	}
	return render_to_response('home/sysconf.var.ajax.list.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def SysVarConfAjaxEdit(request):
	if request.method == "POST":
		chkpr=CheckPOST(['key','value'],request.POST.keys())
		if not chkpr == "" :
			return JsonResponse({"code":"400","errmsg":"Invalid Args."})
		cache.set(request.POST['key'],request.POST['value'])
		return JsonResponse({"code":"200"})
	else:
		return JsonResponse({"code":"400","errmsg":"Invalid Args."})

@PermNeed('pichublog','Admin')
def SysVarConfAjaxToggle(request):
	if request.method == "POST":
		chkpr=CheckPOST(['key'],request.POST.keys())
		if not chkpr == "" :
			return JsonResponse({"code":"400","errmsg":"Invalid Args."})
		c = cache.get(request.POST['key'])
		if c == True:
			cache.set(request.POST['key'],False)
		elif c == False:
			cache.set(request.POST['key'],True)
		else:
			return JsonResponse({"code":"505","errmsg":"Not Boolean Field"})
		return JsonResponse({"code":"200"})
	else:
		return JsonResponse({"code":"400","errmsg":"Invalid Args."})

@PermNeed('pichublog','Admin')
def CategoryList(request):
	kwvars = {
		"request":request,
	}
	return render_to_response('home/sysconf.category.list.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def AjaxCategoryList(request):
	cto = BlogCategoty.objects.all().order_by('order')
	kwvars = {
		"request":request,
		"cto":cto,
	}
	return render_to_response('home/sysconf.catlist.ajax.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def CategoryAdd(request):
	if request.method == "POST":
		form = BlogCategotyForm(request.POST)
		if form.is_valid():
			co = form.save(commit=False)
			maxorder = BlogCategoty.objects.all().aggregate(order_max=DbMax('order'))['order_max']
			if maxorder == None:
				maxorder = 0
			co.order = maxorder+1
			co.save()
			form.save_m2m()
			return HttpResponseRedirect(reverse('pichublog_catlist'))
	else:
		form = BlogCategotyForm()
	kwvars = {
		"request":request,
		'form':form,
		"addmode":True,
	}
	return render_to_response('home/sysconf.category.edit.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def CategoryEdit(request,ID):
	try:
		bco = BlogCategoty.objects.get(id=ID)
	except BlogCategoty.DoesNotExist:
		messages.error(request,u"<b>编辑分类失败</b><br /><b>详细信息：</b>找不到ID为%s的分类！"%ID)
		return HttpResponseRedirect(reverse('pichublog_catlist'))
	if request.method == "POST":
		form = BlogCategotyForm(request.POST,instance=bco)
		if form.is_valid():
			co = form.save(commit=False)
			co.order = BlogCategoty.objects.all().aggregate(order_max=DbMax('order'))['order_max']
			co.save()
			form.save_m2m()
			return HttpResponseRedirect(reverse('pichublog_catlist'))
	else:
		form = BlogCategotyForm(instance=bco)
	kwvars = {
		"request":request,
		'form':form,
		"addmode":False,
	}
	return render_to_response('home/sysconf.category.edit.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Admin')
def CategoryDel(request,ID):
	try:
		bco = BlogCategoty.objects.get(id=ID).delete()
	except BlogCategoty.DoesNotExist:
		messages.error(request,u"<b>删除分类失败</b><br /><b>详细信息：</b>找不到ID为%s的分类！"%ID)
	return HttpResponseRedirect(reverse('pichublog_catlist'))

@PermNeed('pichublog','Admin')
def AjaxCategoryMoveOrder(request):
	chkpr = CheckPOST(['dct','mvid'],request.GET.keys())
	if not chkpr == "" :
		return JsonResponse({"code":400,"msg":"Error Args."})
	dct = request.GET.get('dct')
	mvid = request.GET.get('mvid')
	try:
		curo = BlogCategoty.objects.get(id=mvid)
	except BlogCategoty.DoesNotExist:
		return JsonResponse({"code":404,"msg":"object Not Found."})
	if dct == "up":
		neo = curo.order - 1
	elif dct == "dn":
		neo = curo.order + 1
	try:
		nexto = BlogCategoty.objects.get(order=neo)
	except BlogCategoty.DoesNotExist:
		return JsonResponse({"code":300,"msg":"Attached Limit."})
	except BlogCategoty.MultipleObjectsReturned:
		return JsonResponse({"code":500,"isec":"500@AjaxChpOcMv$100","msg":"Internal Server Error, Please Contact With Website Master or Admin."})
	o1=nexto.order
	o2=curo.order
	nexto.order=o2
	curo.order=o1
	nexto.save()
	curo.save()
	return JsonResponse({"code":200,"msg":"OK."})