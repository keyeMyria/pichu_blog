# -*- coding: UTF-8 -*-
from pichublog.models import *
from zlogin.models import User
from django import forms
from django.core.exceptions import ValidationError
from siteutil.DataConvert import str2int
import logging
logger = logging.getLogger('userlog_file')
# def mc_validator(value):
# 	if self.required and not value:
# 		raise ValidationError(self.error_messages['required'], code='required')
# 		for val in value:
# 			if not User.objects.exists(id=str2int(val)):
# 				raise ValidationError(
# 				#self.error_messages['invalid_choice'],
# 				"errrrrrrrrrrrrrro",
# 					code='invalid_choice',
# 					params={'value': val},
# 				)

# def mc_validate(self, value):
# 	raise ValidationError("Test")
# 	if self.required and not value:
# 		raise ValidationError(self.error_messages['required'], code='required')
# 		for val in value:
# 			if not User.objects.exists(id=str2int(val)):
# 				raise ValidationError("Invalid User.")
# 				# raise ValidationError(
# 				# #self.error_messages['invalid_choice'],
# 				# "errrrrrrrrrrrrrro",
# 				# 	code='invalid_choice',
# 				# 	params={'value': val},
# 				# )

# def mc_clean(self,value):
# 	value = self.to_python(value)
# 	self.mc_validate(value)
# 	return value

class UserMultiChoiceField(forms.MultipleChoiceField):
	def validate(self,value):
		if self.required and not value:
			raise ValidationError(self.error_messages['required'], code='required')
			for val in value:
				if not User.objects.exists(id=str2int(val)):
					raise ValidationError(u"用户不存在！")

class BlogCategotyForm(forms.ModelForm):
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
		fields = ['private','passwdlck','passwd','readgrp','readuin','readuex','freecomment','commentgrp','commentuin','commentuex']
		#fields = ['private','passwdlck','passwd','freecomment']
		# field_classes = {
		# 	"readuin":UserMultiChoiceField,
		# 	"readuex":UserMultiChoiceField,
		# 	"commentuin":UserMultiChoiceField,
		# 	"commentuex":UserMultiChoiceField,
		# }
		widgets = {
			"private":forms.CheckboxInput(attrs={'class':'form-control'}),
			"passwdlck":forms.CheckboxInput(attrs={'class':'form-control'}),
			"passwd":forms.TextInput(attrs={'class':'form-control',"placeholder":"请输入访问密码"}),
			"readgrp":forms.TextInput(),
			"readuin":forms.TextInput(),
			"readuex":forms.TextInput(),
			"commentgrp":forms.TextInput(),
			"commentuin":forms.TextInput(),
			"commentuex":forms.TextInput(),
			"readgrp":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
			"readuin":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
			"readuex":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
			"freecomment":forms.CheckboxInput(attrs={'class':'form-control'}),
			"commentgrp":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
			"commentuin":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
			"commentuex":forms.SelectMultiple(attrs={'class':'form-control','size':'10'}),
		}

	def __init__(self,*args,**kwargs):
		super(PostPermForm,self).__init__(*args,**kwargs)
		self.fields['private'].label=u'设为私密文章'
		self.fields['passwdlck'].label=u'使用密码保护'
		self.fields['passwd'].label=u'访问密码'
		self.fields['passwd'].required=False
		self.fields['readgrp'].label=u'允许访问的用户组'
		self.fields['readgrp'].required=False
		self.fields['readuin'].label=u'额外允许访问的用户'
		self.fields['readuin'].required=False
		if 'instance' in kwargs.keys():
			logger.debug(repr(kwargs['instance'].readuin.all()))
			self.fields['readuin'].queryset=kwargs['instance'].readuin.all()
		else:
			self.fields['readuin'].queryset=User.objects.none()
		self.fields['readuex'].label=u'额外不允许访问的用户'
		self.fields['readuex'].required=False
		if 'instance' in kwargs.keys():
			logger.debug(repr(kwargs['instance'].readuin.all()))
			self.fields['readuex'].queryset=kwargs['instance'].readuex.all()
		else:
			self.fields['readuex'].queryset=User.objects.none()
		self.fields['freecomment'].label=u'允许任何人评论'
		self.fields['commentgrp'].label=u'允许评论的用户组'
		self.fields['commentgrp'].required=False
		self.fields['commentuin'].label=u'额外允许评论的用户'
		self.fields['commentuin'].required=False
		if 'instance' in kwargs.keys():
			logger.debug(repr(kwargs['instance'].readuin.all()))
			self.fields['commentuin'].queryset=kwargs['instance'].commentuin.all()
		else:
			self.fields['commentuin'].queryset=User.objects.none()
		self.fields['commentuex'].label=u'额外不允许评论的用户'
		self.fields['commentuex'].required=False
		if 'instance' in kwargs.keys():
			logger.debug(repr(kwargs['instance'].readuin.all()))
			self.fields['commentuex'].queryset=kwargs['instance'].commentuex.all()
		else:
			self.fields['commentuex'].queryset=User.objects.none()
