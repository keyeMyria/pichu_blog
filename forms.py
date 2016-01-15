# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from pichublog.models import *
from django import forms

class BlogCategotyForm(ModelForm):
	class Meta:
		model = BlogCategoty
		fields = ['engname','title']
		widgets = {
			"engname":forms.TextInput(attrs={'class':'form-control'}),
			"title":forms.TextInput(attrs={'class':'form-control'}),
		}

	def __init__(self,*args,**kwargs):
		super(BlogCategotyForm,self).__init__(*args,**kwargs)
		self.fields['engname'].label=u'英文名'
		self.fields['engname'].error_messages={'required':u'请输入英文名（用于URL）'}
		self.fields['title'].label=u'分类名称'
		self.fields['title'].error_messages={'required':u'请输入分类名称'}