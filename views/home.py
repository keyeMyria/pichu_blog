# -*- coding: UTF-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response,RequestContext
#from django_hosts.resolvers import reverse
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from siteutil.DataConvert import str2int,CheckPOST,str2long,BigIntUniqueID,KVConfGetText,KVConfGetBool
from siteutil.CommonPaginator import SelfPaginator
from zlogin.common.JsonResponse import JsonResponse
from zlogin.decorators import login_detect,login_required,PermNeed
from zlogin import zlauth
from zlogin.zlauth import GetUser,PermCheck
from zlogin.captcha_app import CheckCaptcha,OutsiteCaptchaURL
from pichublog.models import *

@login_detect()
def Home(request):
	kwargs = {"request":request}
	return render_to_response('home/home.html',kwargs,RequestContext(request))

def LeaveMsgPage(request):
	kwargs = {"request":request,'OutsiteCaptchaURL':OutsiteCaptchaURL(request),
			  "LeaveMsgReviewSwitch":cache.get_or_set('LeaveMsgReviewSwitch',True)}
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
			rws = not cache.get_or_set('LeaveMsgReviewSwitch',True)
			LeaveMsg.objects.create(cmid=BigIntUniqueID(),title=title,anonymou=True,stoken=stk,fromuser=nick,mail=mail,website=web,content=content,reviewed=rws)
			return HttpResponseRedirect(reverse('pichublog_msgboard'))

def ReturnTrue():
	return True

@PermNeed('pichublog','Admin')
def SysConf(request):
	defaultconf = [
		("LeaveMsgReviewSwitch","访客评论要求审核再显示",ReturnTrue,"bool"),
		("HomePagePost","首页内容来源文章ID","","str"),
	]
	conf = []
	map(lambda x:(x[0],x[1],cache.get_or_set(x[0],x[2]),x[3]), defaultconf)
	kwvars = {
		"request":request,
		"conf":conf
	}
	return render_to_response('home/sysconf.html',kwvars,RequestContext(request))