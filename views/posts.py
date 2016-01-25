# -*- coding: UTF-8 -*-
from django.http import HttpResponse,HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response,RequestContext
#from django_hosts.resolvers import reverse
from django.core.cache import get_cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from siteutil.DataConvert import str2int,CheckPOST,str2long,BigIntUniqueID,CacheConfGet,MakeSummary
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
	for i in BlogCategoty.objects.all().order_by('order'):
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
	for i in BlogCategoty.objects.all().order_by('order'):
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
	if ctname == "*":
		stcl = CacheConfGet(cache,'MainTopList',default="")
		ltcl = stcl.split(',')
		itcl = map(lambda x:str2int(x), ltcl)
		toplist = BlogPost.objects.filter(id__in=itcl)
	else:
		bpo = bpo.filter(category__engname=ctname)
		try:
			cato = BlogCategoty.objects.get(engname=ctname)
			stcl = cato.topli
			ltcl = stcl.split(',')
			itcl = map(lambda x:str2int(x), ltcl)
			toplist = BlogPost.objects.filter(id__in=itcl)
		except:
			stcl = CacheConfGet(cache,'MainTopList',default="")
			ltcl = stcl.split(',')
			itcl = map(lambda x:str2int(x), ltcl)
			toplist = BlogPost.objects.filter(id__in=itcl)
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
		"TopList":toplist,
		"lPage":lpg,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
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
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if not bpo.rendered:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if bpo.hidden:
		if not bpo.author == thisuser:
			if not PermCheck('pichublog','Admin'):
				kwvars = {
				"request":request,
				"ctlist":BlogCategoty.objects.all().order_by('order'),
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
				"ctlist":BlogCategoty.objects.all().order_by('order'),
				}
				return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if bpo.freecomment:
		pmhc = True
	else:
		pmhc = False
		for hgp in thisuser.group:
			if hgp in bpo.commentgrp:
				if not thisuser in bpo.commentuex:
					pmhc = True
				break
		if not pmhc:
			if thisuser in bpo.commentuin:
				pmhc = True
	kwvars = {
		"request":request,
		"bpo":bpo,
		"bkmode":False,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		"crws":CacheConfGet(cache,'CommentsReviewSwitch',default=True),
		"allowcmt":pmhc,
	}
	return render_to_response('home/post.view.html',kwvars,RequestContext(request))

@PermNeed('pichublog','Writer')
def PostPreview(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if not PermCheck(request.auth,'pichublog','Admin'):
		if not thisuser == bpo.author:
			kwvars = {
			"request":request,
			"ctlist":BlogCategoty.objects.all().order_by('order'),
			}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	kwvars = {
		"request":request,
		"bpo":bpo,
		"bkmode":True,
	}
	return render_to_response('home/post.view.html',kwvars,RequestContext(request))
def PostEdit(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
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
			if request.REQUEST.get("rfm") == "w":
				return HttpResponseRedirect(reverse('pichublog_postwbklist'))
			else:
				return HttpResponseRedirect(reverse('pichublog_postabklist'))
	else:
		form = EditPostForm(instance=bpo)
	kwvars = {
		"request":request,
		'form':form,
		'rfm':request.REQUEST.get("rfm"),
	}
	return render_to_response('home/post.edit.html',kwvars,RequestContext(request))


def PostGrant(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if request.method == "POST":
		form = PostPermForm(request.POST,instance=bpo)
		if form.is_valid():
			form.save()
			if request.REQUEST.get("rfm") == "w":
				return HttpResponseRedirect(reverse('pichublog_postwbklist'))
			else:
				return HttpResponseRedirect(reverse('pichublog_postabklist'))
	else:
		form = PostPermForm(instance=bpo)
	kwvars = {
		"request":request,
		'form':form,
		'rfm':request.REQUEST.get("rfm"),
	}
	return render_to_response('home/post.grant.html',kwvars,RequestContext(request))

def PostHidden(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if not "val" in request.GET.keys():
		return HttpResponse("Err Request Arguments")
	bset = (request.GET['val']=="true")
	bpo.hidden = bset
	bpo.save()
	if request.REQUEST.get("rfm") == "w":
		return HttpResponseRedirect(reverse('pichublog_postwbklist'))
	else:
		return HttpResponseRedirect(reverse('pichublog_postabklist'))

def PostDel(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		"randposts":BlogPost.objects.all().order_by('?')[:5],
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if request.GET.get('veryfycode') == unicode(hash(bpo.title)):
		bpo.delete()
	else:
		messages.error(request,"<b>删除失败：</b>请求参数校验不成功，为了安全起见，该删除请求被服务器拒绝。")
	if request.REQUEST.get("rfm") == "w":
		return HttpResponseRedirect(reverse('pichublog_postwbklist'))
	else:
		return HttpResponseRedirect(reverse('pichublog_postabklist'))

def AjaxShowComments(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	thisuser = GetUser(request)
	owner = PermCheck(request.auth,'pichublog','Admin')
	if not owner:
		if bpo.author == thisuser:
			owner = True
	if owner:
		cmt = BlogComment.objects.filter(post=bpo).order_by('-time')
	else:
		cmt = BlogComment.objects.filter(post=bpo,reviewed=True).order_by('-time')
	lPage = SelfPaginator(request,cmt,20)
	kwvars = {
		'request':request,
		'owner':owner,
		'lPage':lPage,
		'AjaxPaginatorID':'cmt',
	}
	return render_to_response('home/ajax.comment.html',kwvars,RequestContext(request))

def AddComments(request,ID):
	try:
		bpo = BlogPost.objects.get(id=ID)
	except BlogPost.DoesNotExist:
		kwvars = {
		"request":request,
		"ctlist":BlogCategoty.objects.all().order_by('order'),
		}
		return render_to_response('home/post.err.html',kwvars,RequestContext(request))
	if bpo.freecomment:
		pmhc = True
	else:
		pmhc = False
		for hgp in thisuser.group:
			if hgp in bpo.commentgrp:
				if not thisuser in bpo.commentuex:
					pmhc = True
				break
		if not pmhc:
			if thisuser in bpo.commentuin:
				pmhc = True
	if not pmhc:
		messages.error(request,u"<b>作者只允许指定身份的人评论本文，您不在此列。</b>")
		return HttpResponseRedirect(reverse('pichublog_postview',args=(ID,)))
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
			stk = request.auth.cookie.get('zl2_token')
			BlogComment.objects.create(post=bpo,cmid=BigIntUniqueID(),anonymou=False,stoken=stk,fromuser=request.auth.user,content=content,reviewed=True)
			return HttpResponseRedirect(reverse('pichublog_postview',args=(ID,)))
		else:
			capt = request.POST.get('captcha')
			if not CheckCaptcha(request,capt):
				messages.error(request,u"<b>验证码错误</b>")
				return HttpResponseRedirect(reverse('pichublog_postview',args=(ID,)))
			content = request.POST.get('content')
			nick = request.POST.get('nick')
			mail = request.POST.get('mail')
			web = request.POST.get('website')
			stk = request.auth.cookie.get('zl2_token')
			rws = not CacheConfGet(cache,'CommentsReviewSwitch',default=True)
			LeaveMsg.objects.create(post=bpo,cmid=BigIntUniqueID(),anonymou=True,stoken=stk,fromuser=nick,mail=mail,website=web,content=content,reviewed=rws)
			return HttpResponseRedirect(reverse('pichublog_postview',args=(ID,)))
	else:
		return HttpResponse("405 Method Not Allowed")
