# -*- coding: UTF-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response,RequestContext
#from django_hosts.resolvers import reverse
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from siteutil.DataConvert import str2int,CheckPOST,str2long,BigIntUniqueID,CacheConfGet
from siteutil.CommonPaginator import SelfPaginator
from siteutil.CommonFilter import CommonFilter,FilterCondition
from siteutil.htmlutil import renderMarkdownSafety
from zlogin.common.JsonResponse import JsonResponse
from zlogin.decorators import login_detect,login_required,PermNeed
from zlogin import zlauth
from zlogin.zlauth import GetUser,PermCheck
from zlogin.captcha_app import CheckCaptcha,OutsiteCaptchaURL
from pichublog.models import *
from pichublog.forms import *
import time
cache = get_cache("pichublog")

@PermNeed('pichublog','Admin')
def PostABkList(request):
	bpo = BlogPost.objects.all()
	ctids = []
	ctals = []
	for i in BlogCategoty.objects.all():
		ctids.append(i.id)
		ctals.append(i.title)

	fco = FilterCondition()
	fco.addTextContain("t","标题","title")
	fco.addTextContain("au","作者","author__name")
	fco.addDateRange("ct","创建时间","crttime")
	fco.addDateRange("pt","发布时间","pubtime")
	fco.addSingleChoice("hid","隐藏","hidden",[True,False],alias=["真","假"])
	fco.addSingleChoice("prv","私密","private",[True,False],alias=["真","假"])
	fco.addSingleChoice("fc","自由评论","freecomment",[True,False],alias=["真","假"])
	fco.addMultiChoice("cat","分类","category_id",ctids,alias=ctals)

	fList = CommonFilter(request,fco,bpo)
	#分页功能
	lpg = SelfPaginator(request,fList, 20)
	kwvars = {
		"request":request,
		"lPage":lpg,
		'FilterHTML':fco.RenderHTML(request),
		"adminmode":True,
	}
	return render_to_response('home/post.bk.list.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Writer')
def PostWBkList(request):
	bpo = BlogPost.objects.all()
	mList = bpo.filter(author=GetUser(request))
	ctids = []
	ctals = []
	for i in BlogCategoty.objects.all():
		ctids.append(i.id)
		ctals.append(i.title)

	fco = FilterCondition()
	fco.addTextContain("t","标题","title")
	fco.addDateRange("ct","创建时间","crttime")
	fco.addDateRange("pt","发布时间","pubtime")
	fco.addSingleChoice("hid","隐藏","hidden",[True,False],alias=["真","假"])
	fco.addSingleChoice("prv","私密","private",[True,False],alias=["真","假"])
	fco.addSingleChoice("fc","自由评论","freecomment",[True,False],alias=["真","假"])
	fco.addMultiChoice("cat","分类","category_id",ctids,alias=ctals)

	fList = CommonFilter(request,fco,mList)
	#分页功能
	lpg = SelfPaginator(request,fList, 20)
	kwvars = {
		"request":request,
		"lPage":lpg,
		'FilterHTML':fco.RenderHTML(request),
		"adminmode":False,
	}
	return render_to_response('home/post.bk.list.html',kwvars,RequestContext(request))

def PostList(request,ctname):
	bpo = BlogPost.objects.all().filter(rendered=True,hidden=False)
	if not ctname == "*":
		bpo = bpo.filter(category__engname=ctname)
	fco = FilterCondition()
	fco.addTextContain("t","标题","title")
	fco.addTextContain("au","作者用户名","author__name")
	fco.addTextContain("an","作者昵称","author__nick")
	fco.addDateRange("ct","创建时间","crttime")
	fco.addDateRange("pt","发布时间","pubtime")

	fList = CommonFilter(request,fco,bpo)
	#分页功能
	lpg = SelfPaginator(request,fList, 20)
	kwvars = {
		"request":request,
		"ctname":ctname,
		"lPage":lpg,
		"ctlist":BlogCategoty.objects.all(),
		'FilterHTML':fco.RenderHTML(request),
	}
	return render_to_response('home/post.list.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Writer')
def PostAdd(request):
	bpo = BlogPost.objects.create(
		title = time.strftime("[草稿]%Y-%b-%d %H:%M:%S"),
		author = GetUser(request),
		rendered = False,
		hidden = True,
		private = False,
		passwdlck = False,
		freecomment = True,
	)
	return HttpResponseRedirect(reverse('pichublog_postedit',args=(bpo.id,)))

def PostView(request,ID):
	thisuser = GetUser(request)
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if not bpo.rendered:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if bpo.hidden:
		if not bpo.author == thisuser:
			if not PermCheck('pichublog','Admin'):
				kwvars = {
				"request":request,
				"ctlist":BlogCategoty.objects.all(),
				}
				return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if bpo.private:
		if bpo.passwdlck:
			if request.method == POST:
				if not request.POST.get['ppppppppaaaaaassssssssssssswwwwwooorrrrrdddd'] == bpo.password:
					messages.error(request,u"<b>密码错误！</b>")
					return HttpResponseRedirect(reverse('pichublog_postpwdf',args=(bpo.id,)))
			else:
				return HttpResponseRedirect(reverse('pichublog_postpwdf',args=(bpo.id,)))
		else:
			pmh = False
			for hgp in thisuser.group:
				if hgp in bpo.readgrp:
					if not thisuser in bpo.readuex:
						pmh = True
					break
			if not pmh:
				if thisuser in bpo.readuin:
					pmh = True
			if not pmh:
				kwvars = {
				"request":request,
				"ctlist":BlogCategoty.objects.all(),
				}
				return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	kwvars = {
		"request":request,
		"title":bpo.title,
		"content":bpo.html,
		"postid":bpo.id,
		"bkmode":False,
	}
	return render_to_response('home/post.view.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Writer')
def PostPreview(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if not PermCheck('pichublog','Admin'):
		if not thisuser == bpo.author:
			kwvars = {
			"request":request,
			"ctlist":BlogCategoty.objects.all(),
			}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	kwvars = {
		"request":request,
		"title":bpo.title,
		"content":bpo.html,
		"postid":bpo.id,
		"bkmode":True,
	}
	return render_to_response('home/post.view.html',kwvars,RequestContext(request))
def PostEdit(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if request.method == "POST":
		form = EditPostForm(request.POST,instance=bpo)
		if form.is_valid():
			nbp = form.save(commit=False)
			nbp.html = renderMarkdownSafety(nbp.markdown)
			nbp.rendered = True
			nbp.save()
			form.save_m2m()
			return HttpResponseRedirect(reverse('pichublog_postwbklist'))
	else:
		form = EditPostForm(instance=bpo)
	kwvars = {
		"request":request,
		'form':form,
	}
	return render_to_response('home/post.edit.html',kwvars,RequestContext(request))


def PostGrant(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))

def PostHidden(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))

def PostDel(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all(),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))