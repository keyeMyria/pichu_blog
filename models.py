from django.db import models
from zlogin.models import User,UserGroup

class CrossDbForeignKey(models.ForeignKey):
    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(models.ForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        # Here is the trick, get db relating to fk, not to root model
        using = router.db_for_read(self.rel.to, instance=model_instance)

        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})

class CrossDbManyToManyField(models.ManyToManyField):
    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(models.ManyToManyField, self).validate(value, model_instance)
        if value is None:
            return

        # Here is the trick, get db relating to fk, not to root model
        using = router.db_for_read(self.rel.to, instance=model_instance)

        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(self.error_messages['invalid'] % {
                'model': self.rel.to._meta.verbose_name, 'pk': value})

class KVConf(models.Model):
	key = models.CharField(max_length=64,unique=True,db_index=True)
	value = models.TextField()

class BlogCategoty(models.Model):
	engname = models.CharField(unique=True,max_length=64,db_index=True)
	title = models.CharField(max_length=64)
	order = models.IntegerField()
	topli = models.CharField(max_length=64,blank=True,null=True)

	def __unicode__(self):
		return self.title

	def __repr__(self):
		return self.engname

# Create your models here.
class BlogPost(models.Model):
	class Meta:
		ordering = ["-pubtime"]

	title = models.CharField(max_length=128)
	category = models.ManyToManyField(BlogCategoty,null=True)
	author = models.ForeignKey(User,related_name="pichublog_post_set")
	crttime = models.DateTimeField(auto_now_add=True)
	pubtime = models.DateTimeField(auto_now_add=True,auto_now=True)
	markdown = models.TextField()
	rendered = models.BooleanField(default=False)
	html = models.TextField()
	hidden = models.BooleanField(default=True)
	private = models.BooleanField(default=False)
	passwdlck = models.BooleanField(default=False)
	passwd = models.CharField(max_length=128)
	readgrp = models.ManyToManyField('zlogin.UserGroup',blank=True,null=True,related_name="pichublog_readgrp")
	readuin = models.ManyToManyField('zlogin.User',blank=True,null=True,related_name="pichublog_readuin")
	readuex = models.ManyToManyField('zlogin.User',blank=True,null=True,related_name="pichublog_readuex")
	freecomment = models.BooleanField(default=True)
	commentgrp = models.ManyToManyField('zlogin.UserGroup',blank=True,null=True,related_name="pichublog_commentgrp")
	commentuin = models.ManyToManyField('zlogin.User',blank=True,null=True,related_name="pichublog_commentuin")
	commentuex = models.ManyToManyField('zlogin.User',blank=True,null=True,related_name="pichublog_commentuex")

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
	content   = models.TextField()