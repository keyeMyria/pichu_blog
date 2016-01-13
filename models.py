from django.db import models
from zlogin.models import User,UserGroup

class KVConf(models.Model):
	key = models.CharField(max_length=64,unique=True,db_index=True)
	value = models.TextField()

class BlogCategoty(models.Model):
	engname = models.CharField(max_length=64,db_index=True)
	title = models.CharField(max_length=64)

# Create your models here.
class BlogPost(models.Model):
	title = models.CharField(max_length=128)
	category = models.ManyToManyField(BlogCategoty,null=True)
	author = models.ForeignKey(User,related_name="pichublog_post_set")
	crttime = models.DateTimeField(auto_now_add=True)
	pubtime = models.DateTimeField(auto_now_add=True,auto_now=True)
	markdown = models.TextField()
	rendered = models.TextField()
	hidden = models.BooleanField(default=False)
	private = models.BooleanField(default=True)
	passwdlck = models.BooleanField(default=True)
	passwd = models.CharField(max_length=128)
	readgrp = models.ManyToManyField(UserGroup,blank=True,null=True,related_name="pichublog_readgrp")
	readuin = models.ManyToManyField(User,blank=True,null=True,related_name="pichublog_readuin")
	readuex = models.ManyToManyField(User,blank=True,null=True,related_name="pichublog_readuex")
	freecomment = models.BooleanField(default=True)
	commentgrp = models.ManyToManyField(UserGroup,blank=True,null=True,related_name="pichublog_commentgrp")
	commentuin = models.ManyToManyField(User,blank=True,null=True,related_name="pichublog_commentuin")
	commentuex = models.ManyToManyField(User,blank=True,null=True,related_name="pichublog_commentuex")

class BlogComment(models.Model):
	cmid      = models.BigIntegerField(primary_key=True)
	reviewed  = models.BooleanField(default=False)
	post      = models.ForeignKey(BlogPost)
	time      = models.DateTimeField(auto_now_add=True,auto_now=True)
	anonymou  = models.BooleanField(default=True)
	stoken    = models.CharField(max_length=36,db_index=True)
	mail      = models.CharField(max_length=255,blank=True,null=True)
	website   = models.CharField(max_length=255,blank=True,null=True)
	fromuser = models.CharField(max_length=64)
	title     = models.CharField(max_length=255)
	content   = models.TextField()

class LeaveMsg(models.Model):
	cmid      = models.BigIntegerField(primary_key=True)
	reviewed  = models.BooleanField(default=False)
	time      = models.DateTimeField(auto_now_add=True,auto_now=True)
	anonymou  = models.BooleanField(default=True)
	stoken    = models.CharField(max_length=36,db_index=True)
	mail      = models.CharField(max_length=255,blank=True,null=True)
	website   = models.CharField(max_length=255,blank=True,null=True)
	fromuser = models.CharField(max_length=64)
	title     = models.CharField(max_length=255)
	content   = models.TextField()