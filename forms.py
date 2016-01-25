# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from pichublog.models import *
from django import forms

class BlogCategotyForm(ModelForm):
	class Meta:
		model = BlogCategoty
		fields = ['engname','title','topli']
		widgets = {
			"engname":forms.TextInput(attrs={'class':'form-control',"placeholder":"请输入英文名（用于URL，仅能使用大小写字母、数字和下划线）"}),
			"title":forms.TextInput(attrs={'class':'form-control',"placeholder":"请输入分类名称"}),
			"topli":forms.TextInput(attrs={'class':'form-control',"placeholder":"请输入置顶文章ID列表，英文逗号隔开，若没有请留空"}),
		}

	def __init__(self,*args,**kwargs):
		super(BlogCategotyForm,self).__init__(*args,**kwargs)
		self.fields['engname'].label=u'英文名'
		self.fields['engname'].error_messages={'required':u'请输入英文名（用于URL，仅能使用大小写字母、数字和下划线）'}
		self.fields['title'].label=u'分类名称'
		self.fields['title'].error_messages={'required':u'请输入分类名称'}
		self.fields['topli'].label=u'置顶列表'

class EditPostForm(forms.ModelForm):
	class Meta:
		model = BlogPost
		fields = ['title','category','markdown']
		widgets = {
			"title":forms.TextInput(attrs={'class':'form-control',"placeholder":"请输入标题"}),
			"category" : forms.SelectMultiple(attrs={'class':'form-control','size':'10','multiple':'multiple'}),
			"markdown":forms.Textarea(attrs={'class':'form-control',"placeholder":"正文"}),
		}

	def __init__(self,*args,**kwargs):
		super(EditPostForm,self).__init__(*args,**kwargs)
		self.fields['title'].label=u'标题'
		self.fields['title'].required=True
		self.fields['title'].error_messages={'required':u"请输入标题"}
		self.fields['category'].label=u'分类'
		self.fields['markdown'].label=u'正文'
		self.fields['markdown'].required=True
		self.fields['markdown'].error_messages={'required':u"请输入正文"}

class PostPermForm(forms.ModelForm):
	class Meta:
		model = BlogPost
		#fields = ['private','passwdlck','passwd','readgrp','readuin','readuex','freecomment','commentgrp','commentuin','commentuex']
		fields = ['private','passwdlck','passwd','freecomment']
		widgets = {
			"private":forms.CheckboxInput(attrs={'class':'form-control'}),
			"passwdlck":forms.CheckboxInput(attrs={'class':'form-control','placeholder':'（需设为私密文章方可有效）'}),
		}

	def __init__(self,*args,**kwargs):
		super(PostPermForm,self).__init__(*args,**kwargs)
		self.fields['private'].label=u'设为私密文章'
		self.fields['private'].label=u'使用密码保护'
