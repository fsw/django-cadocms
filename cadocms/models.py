from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey, TreeManyToManyField
from django.utils.translation import ugettext_lazy as _

from .fields import ExtraFieldsDefinition, ExtraFieldsValues, HTMLField

from .widgets import ExtraFieldsValuesWidget
from django.contrib.auth.models import User
from haystack import indexes
from django.conf import settings
from django.db.models.signals import class_prepared
from django.forms.models import model_to_dict
#from django.core.mail import send_mail
from datetime import datetime, timedelta     
from cadocms.email import StandardEmail

from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
import caching.base

import reversion
from reversion.models import Version

from django.core.exceptions import ValidationError
from django.contrib.admin.models import LogEntry, CHANGE


MODERATION_STATUS = {
    'NEW' : 0,
    'MODIFIED' : 1,
    'OK' : 2,
    'REJECTED' : 3
}
                       
MODERATION_STATUSES = (
    (MODERATION_STATUS['NEW'], 'New'),
    (MODERATION_STATUS['MODIFIED'], 'Modified'),
    (MODERATION_STATUS['OK'], 'OK'),
    (MODERATION_STATUS['REJECTED'], 'Rejected'),
)

MODERATION_STATUSES_CODES = {
    MODERATION_STATUS['NEW'] : 'new',
    MODERATION_STATUS['MODIFIED'] : 'modified',
    MODERATION_STATUS['OK'] : 'ok',
    MODERATION_STATUS['REJECTED'] : 'rejected',
}

MODERATION_REASONS = (
    (0, 'Other'),
)
    
class ModerationReason(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    email_body = models.TextField(_('Email Body'), blank=True)
        
    def __unicode__(self):
        return u"%s" % (self.name)
    
class Moderated(models.Model):
    
    moderation_status = models.IntegerField(_('Moderation Status'), choices=MODERATION_STATUSES, db_index=True, default=MODERATION_STATUS['NEW'], blank=True)
    moderation_reason = models.ForeignKey(ModerationReason, related_name='moderation_reason', null=True, blank=True)
    moderation_user = models.ForeignKey(User, related_name='moderation_user', null=True, blank=True)
    moderation_comment = models.TextField(_('Moderator Comment'), blank=True)
    moderation_last_ok_revision = models.ForeignKey(Version, blank=True, null=True)
                                 
    created     = models.DateTimeField(editable=False, default=datetime.now)
    modified    = models.DateTimeField(editable=False, default=datetime.now)
    
    owner = models.ForeignKey(User, related_name='owner', null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def moderation_status_code(self):
        return MODERATION_STATUSES_CODES[self.moderation_status]
    
    def on_moderate_accept(self):
        if self.owner:
            StandardEmail(template = "email/moderate_accept.haml", 
                      subject = '[' + settings.CADO_NAME + '] ' + str(self) + ' has been accepted by moderation', 
                      from_email = settings.SPAM_EMAIL, 
                      to_email = [self.owner.email], 
                      variables = {'item': self, 'owner': self.owner}).send()
        
    def on_moderate_reject(self, reason):
        if self.owner:
            StandardEmail(template = "email/moderate_reject.haml", 
                      subject = '[' + settings.CADO_NAME + '] ' + str(self) + ' has been rejected by moderation', 
                      from_email = settings.SPAM_EMAIL, 
                      to_email = [self.owner.email], 
                      variables = {'item': self, 'owner': self.owner, 'reason':reason}).send()

    def moderate_accept(self, user):
        self.on_moderate_accept()
        self.moderation_status = MODERATION_STATUS['OK']
        self.moderation_user = user
        self.moderation_last_ok_revision = reversion.get_for_object(self)[0]
        super(Moderated, self).save()
        content_type = ContentType.objects.get_for_model(self) #get(app_label="unravelling", model="item")
        LogEntry.objects.log_action(user.id, content_type.id, self.id, unicode(self), CHANGE, "MODERATION ACCEPT")

    def moderate_reject(self, user, reason):
        self.on_moderate_reject(reason)
        self.moderation_status = MODERATION_STATUS['REJECTED']
        self.moderation_user = user
        self.moderation_reason = reason
        super(Moderated, self).save()
        content_type = ContentType.objects.get_for_model(self) #get(app_label="unravelling", model="item")
        LogEntry.objects.log_action(user.id, content_type.id, self.id, unicode(self), CHANGE, "MODERATION REJECT (%s)" % reason)

    def show_diff(self):
        ret = []
        #print self, self.moderation_status, MODERATION_STATUS['NEW']
        
        versions = [ ]
        
        #print 'XXX'
        if (self.moderation_last_ok_revision):
            #print self.moderation_last_ok_revision, 'ID'
            versions.append(self.moderation_last_ok_revision);
            
        if reversion.get_for_object(self).count():
            versions.append(reversion.get_for_object(self)[0])
        
        
        #print 'YYY'
        tmp_ret = {}
        
        try:
            for version in versions:
                for key,value in version.field_dict.items():
                    if key not in self.diff_ignored_fields():
                        tmp_ret[key] = tmp_ret.get(key,[])
                        tmp_ret[key].append(value)
        except:
            pass
            
        for field in self.__class__._meta.fields:
            if field.name in tmp_ret:
                if len(tmp_ret[field.name]) < 2 or unicode(tmp_ret[field.name][0]) != unicode(tmp_ret[field.name][1]):
                    if any(tmp_ret[field.name]):
                        if isinstance(field, models.ForeignKey):
                            tmp_ret[field.name] = [(unicode(field.rel.to.objects.get(id=int(id)))) for id in tmp_ret[field.name]]
                        if isinstance(field, models.ImageField):
                            tmp_ret[field.name] = [mark_safe(
                                                             '<a class="fancybox" href="%s%s"><img src="%s%s" height="100" width="100"/></a>' % (settings.MEDIA_URL, path, settings.MEDIA_URL, path) if path else 'NONE' 
                                                             ) for path in tmp_ret[field.name]]

                        ret.append((field.verbose_name, tmp_ret[field.name]))
        for field in self.__class__._meta.many_to_many:
            if field.name in tmp_ret:
                tmp_ret[field.name] = [[(unicode(field.rel.to.objects.get(id=int(id)))) for id in lll] for lll in tmp_ret[field.name]]
                ret.append((field.verbose_name, tmp_ret[field.name]))
                
        #print 'XXX', ret
        return ret
        #model_to_dict(self, fields=[field.name for field in self._meta.fields])
        #model_to_dict(self, fields=[field.name for field in self._meta.fields])
    
    @staticmethod
    def diff_ignored_fields():
        return ['moderation_status', 'moderation_reason', 
                'moderation_user', 'moderation_comment', 
                'moderation_last_ok_revision',
                'created', 'modified']
    
    def save(self, *args, **kwargs):
        
        self.modified = datetime.now()
        
        if self.pk is None:
            self.moderation_status = MODERATION_STATUS['NEW']
            self.created = datetime.today()
        """
        else:
            original = self.__class__._default_manager.get(pk=self.pk)
        
        
        if (self.moderation_status != MODERATION_STATUS['NEW']):
            #print self.__class__._meta.get_all_field_names()
            #print self.__class__._meta.fields
            #print 'IGNORING FIELDS:', self.diff_ignored_fields()
            for field in self.__class__._meta.fields + self.__class__._meta.many_to_many: #self.__class__._meta.get_all_field_names():
                if field.name not in self.diff_ignored_fields():
                    #field_class = self.__class__._meta.get_field(field)
                    original_data = getattr(original, field.name)
                    new_data = getattr(self, field.name)
                    if isinstance(field, models.ManyToManyField):
                        #pass
                        #TODO
                        #print 'KASZANA'
                        list1 = original_data.values_list('id', flat=True).order_by('id')
                        list2 = new_data.values_list('id', flat=True).order_by('id')
                        #print list1
                        #print list2
                        #print set(list1) == set(list2)
                    elif unicode(original_data) != unicode(new_data):
                        #print 'DIFF on ', field.name, original_data, new_data  
                        self.moderation_status = MODERATION_STATUS['MODIFIED']
                        #print 'MODIFIED ' + field
                        #print original_data
                        #print new_data
        
        """
        print 'SAVE', self, self.moderation_status, 'XXX'
        ret = super(Moderated, self).save(*args, **kwargs)
        
        return ret

def pre_revision_commit(**kwargs):
    #print 'PRE', kwargs
    for idx, instance in enumerate(kwargs['instances']):
        if isinstance(instance, Moderated):
            if instance.moderation_status == MODERATION_STATUS['NEW']:
                pass
            elif instance.moderation_status == MODERATION_STATUS['MODIFIED']:
                pass
            elif instance.moderation_status == MODERATION_STATUS['OK']:
                instance.moderation_status = MODERATION_STATUS['MODIFIED']
                instance.save()
            elif instance.moderation_status == MODERATION_STATUS['REJECTED']:
                instance.moderation_status = MODERATION_STATUS['MODIFIED']
                instance.save()
                            
            #print 'VERSION', version.field_dict
            #print 'VERSIONS', version_list.count()
            #print 'VERSION_LIST', version_list
            #print 'POST COMMIT', instance
            

reversion.pre_revision_commit.connect(pre_revision_commit)
  

class Translatable(models.Model):
    translatable_fields = ()
    class Meta:
        abstract = True
    
class StaticPage(caching.base.CachingMixin, models.Model): #, Translatable):
    
    url = models.CharField(_('URL'), max_length=200, db_index=True)
    title = models.CharField(_('Title'), max_length=256)
    content = HTMLField('Content')
    #template = models.CharField(max_length=512, choices=settings.STATICPAGE_TEMPLATES, blank=False)
    seo_title = models.CharField(max_length=512, blank=True)
    seo_keywords = models.CharField(max_length=512, blank=True)
    seo_description = models.TextField('seo_description', blank=True)
    translatable_fields = ('title', 'content', 'seo_title', 'seo_keywords', 'seo_description',)

    objects = caching.base.CachingManager()
    
    class Meta:
        verbose_name = _('static page')
        verbose_name_plural = _('static pages')
        ordering = ('url',)
        abstract = True
        
    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        return self.url

class Chunk(caching.base.CachingMixin, models.Model):#, Translatable):
    key = models.CharField(max_length=256)
    body = HTMLField(blank=True, null=True)
    translatable_fields = ('body',)

    objects = caching.base.CachingManager()
    
    def __unicode__(self):
        return self.key    
    class Meta:
        abstract = True
    
    
class Setting(caching.base.CachingMixin, models.Model):
    
    key = models.CharField(_('Key'), max_length=200, db_index=True)
    value = models.TextField(_('Value'), blank=True)
    description = models.TextField('description', blank=True)
    
    objects = caching.base.CachingManager()

    def __unicode__(self):
        return u"%s = %s" % (self.key, self.value)

    
class Sluggable(models.Model):
    slug = models.SlugField(unique=True, blank=True, max_length=255)#, editable=False)
    
    def _get_queryset_for_slug(self):
        """
        Returns a queryset that will be filtered on to check for conflicting
        slugs. This can be overridden for more advanced implementations.
        """
        return self.__class__._default_manager
    
    def _generate_slug(self):
        """
        Generate a unique slug for this model.
        """
        # Create the keyword arguments for a new queryset based on the values
        # of this model's "unique_together" fields when they include the "slug"
        # field.
        combinations = filter(lambda x: 'slug' in x, self._meta.unique_together)
        if combinations:
            fields = set(reduce(lambda accumulated, update: accumulated + update, combinations))
            fields.remove('slug')
            filter_kwargs = dict(map(lambda x: (x, self.__getattribute__(x)), fields))
        else:
            filter_kwargs = {}
        
            
        queryset = self._get_queryset_for_slug().filter(**filter_kwargs)
        
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
            
        base_slug = self._generate_base_slug()
        
        try:
            slug = base_slug
            queryset.get(slug=slug)
            
            # If no ObjectDoesNotExist exception is thrown, a model with the 
            # current slug already exists. We need to create a new unique slug
            # until we can find one that is truly unique.
            i = 1
            while True:
                slug = '%s-%s' % (base_slug, i)
                queryset.get(slug=slug)
                i = i + 1
            
        except ObjectDoesNotExist:
            # If the object does not exist, there are no naming conflicts and
            # the current value of the "slug" variable is safe to use.
            pass
        
        return slug
    
    def _generate_base_slug(self):
        """
        Generate the base slug for this model.
        
        If you'd like to use something other than this model's __unicode__
        representation to generate the base slug, override this method in your
        model class to return a slugified string.
        """
        return slugify(u'%s' % self)
    
    def full_clean(self, *args, **kwargs):
        #print 'CHUJ'
        if self.slug is None or self.slug == '':
            self.slug = self._generate_slug()
        
        return super(Sluggable, self).full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        #print 'CHUJ'
        if self.slug is None or self.slug == '':
            self.slug = self._generate_slug()
        
        return super(Sluggable, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True
      

class Tree(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    order = models.FloatField(default=0)
    class Meta:
        abstract = True
        ordering = ['order', 'name']
    class MPTTMeta:
        order_insertion_by=['order']

class RootedTree(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', default=0)
    order = models.FloatField(default=0)
    class Meta:
        abstract = True
        ordering = ['order', 'name']
    class MPTTMeta:
        order_insertion_by=['order']
        
    def clean(self):
        super(RootedTree, self).clean()
        from django.core.exceptions import ValidationError
        if not self.parent_id and not (self.level == 0 and self.tree_id == 1):
            #print self.parent_id, self.level, self.tree_id
            raise ValidationError("Can't create new item here")

"""
loosly based on https://github.com/thornomad/django-hitcount
"""

class HitCounter(models.Model):
    key         = models.SlugField(unique=True, blank=True, max_length=255)
    value       = models.PositiveIntegerField(default=0)
    
class Hit(models.Model):
    counter         = models.ForeignKey(HitCounter, editable=False)
    created         = models.DateTimeField(editable=False, default=datetime.now)
    ip              = models.CharField(max_length=40, editable=False)
    session         = models.CharField(max_length=40, editable=False)
    user_agent      = models.CharField(max_length=255, editable=False)
    user            = models.ForeignKey(User,null=True, editable=False)
    
    class Meta:
        index_together = [
            ["counter", "ip", "created"],
        ]

 
def hits_get(key):
    try:
        counter = HitCounter.objects.get(key=key)
        return counter.value
    except HitCounter.DoesNotExist:
        return 0

# if request is passed key will increment only if it is unique
def hits_inc(key, request = None, interval = 'day'):
    
    
    counter, created_created = HitCounter.objects.get_or_create(key=key)
    
    if request is not None:
        BotNames = ['Googlebot','Slurp','Twiceler','msnbot','KaloogaBot','YodaoBot','"Baiduspider','googlebot','Speedy Spider','DotBot']
        user_agent = request.META.get('HTTP_USER_AGENT',None)
        for botname in BotNames:
            if botname in user_agent:
                #this is a bot
                return False;
    
    
    if request is None:
        hit_created = True;
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        try:
            now = datetime.now() - timedelta(1,0)
            hit = Hit.objects.get(counter = counter, ip = ip, created__gt = now)
            hit_created = False;
        except Hit.DoesNotExist:
            hit = Hit(counter = counter, 
                      ip = ip, 
                      session = request.session.session_key if request.session.session_key else '',
                      user_agent = request.META.get('HTTP_USER_AGENT'),
                      user = request.user if request.user.is_authenticated() else None
                      )
            hit.save()
            hit_created = True;
        
        
    print 'HIT', hit, hit_created
    
    if hit_created:
        counter.value = counter.value + 1
        counter.save()
        
    return hit_created


class MyDateField(models.DateField):
    #def formfield(self, **kwargs):
    #    #//defaults.update(kwargs)
    #    print defaults
    #    return super(MyDateField, self).formfield(**kwargs)
    
    def formfield(self, **kwargs):
        return super(MyDateField, self).formfield(input_formats = ("%d/%m/%Y",), **kwargs)

class MyTimeField(models.TimeField):
    def formfield(self, **kwargs):
        return super(MyTimeField, self).formfield(input_formats = ("%I:%M %p",), **kwargs)

class MyDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        #kwargs.setdefault('input_formats', ("%d.%m.%Y",))
        super(MyDateTimeField, self).__init__(*args, **kwargs)
        
        
from django import forms
from django.forms import widgets 
from django.utils.datastructures import MultiValueDict, MergeDict 

class TextCheckboxSelectMultiple(widgets.SelectMultiple):

    def render(self, name, value, **kwargs):
        #print 'RENDER', value
        if isinstance(value, basestring):
            value = value.split(",")
        return super(TextCheckboxSelectMultiple, self).render(name, value, **kwargs)
    
    def value_from_datadict(self, data, files, name):
        #print 'VVV', data, name
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

class TextMultiField(forms.TypedMultipleChoiceField):
    
    widget = TextCheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        #self.coerce = kwargs.pop('coerce', lambda val: val)
        super(TextMultiField, self).__init__(*args, **kwargs)
        self.empty_value = None
        
    def to_python(self, value):
        #print 'VAVAVA0', value
        return super(TextMultiField, self).to_python(value)

    def clean(self, value):
        #print 'VAVAVA1', value
        val = super(TextMultiField, self).clean(value)
        return ",".join(val)
    
    def validate(self, value):
        #print 'VAVAVA2', value
        return super(TextMultiField, self).validate(value)
        

class MyTextMultiField(models.CharField):
    
    def __init__(self, *args, **kwargs):
        super(MyTextMultiField, self).__init__(*args, **kwargs)
        self.empty_label='ASDASD'
        self.default=''
        #print 'INIT'
    
    def formfield(self, **kwargs):
        #print self.empty_label
        #print 'KWARGS', kwargs
        return super(MyTextMultiField, self).formfield(choices_form_class = TextMultiField, **kwargs)

class ExtraFieldsProvider(models.Model):

    extra_fields = ExtraFieldsDefinition(null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def get_extra_fields(self):
        #print 'LOL'
        all_cats = self.get_ancestors(include_self=True)
        #ret = {}
        ret = []
        for cat in all_cats:
            try:
                #print 'WHOLE', cat.extra_fields
                if type(cat.extra_fields) is list:
                    loop = cat.extra_fields
                else:
                    loop = cat.extra_fields.items()
                for key, field in loop:
                    if not field:
                        #ret.pop(key, None)
                        ret = [(k, v) for k, v in ret if k != key]
                    else:
                        #print key, field
                        className = field.get('class', 'CharField')
                        args = field.get('kwargs', {}).copy()
                        
                        if className == 'DateField': 
                            methodToCall = MyDateField
                        elif className == 'TimeField': 
                            methodToCall = MyTimeField
                        elif className == 'DateTimeField':
                            methodToCall = MyDateTimeField
                        elif className == 'TextMultiField':
                            methodToCall = MyTextMultiField
                        else:
                            methodToCall = getattr(models, className, models.CharField)
                        
                        #different default values    
                        if className == 'CharField':
                            args.setdefault('max_length', 64)
                        else:
                            pass
                         
                        if ('choices' in args) and (type(args['choices']) is dict):
                            new_options = []
                            for k, v in args['choices'].items():
                                new_options.append((k,v))
                            args['choices'] = new_options
                            
                        if ('choices' in args) and (isinstance(args['choices'], list)):
                            new_options = []
                            for v in args['choices']:
                                if isinstance(v, basestring):
                                    new_options.append((v,v))
                                else:
                                    new_options.append(v)
                            args['choices'] = new_options
                        
                        #print 'XXX EXTRA:', className, args
                        
                        f = methodToCall(**args)
                        
                        #print 'ZZZ EXTRA:', f
        
                        solr_key = key
                        h_field = indexes.index_field_from_django_field(f)
                        if h_field == indexes.CharField:
                            solr_key = '%s_s' % key
                        elif h_field == indexes.DateTimeField:
                            solr_key = '%s_dt' % key
                        elif h_field == indexes.BooleanField:
                            solr_key = '%s_b' % key
                        elif h_field == indexes.MultiValueField:
                            solr_key = '%s_ms' % key
                        elif h_field == indexes.FloatField:
                            solr_key = '%s_f' % key
                        elif h_field == indexes.IntegerField:
                            solr_key = '%s_i' % key
                        else:
                            raise Exception('unknown type')
                        
                        if className == 'TextMultiField':
                            solr_key = '%s_ms' % key

                        #ret[key] = {'field' : f, 'solr_key' : solr_key}
                        #TODO option to override fields in child categories here!
                        ret.append((key, {'field' : f, 'solr_key' : solr_key, 'params' : field.get('params', {}).copy()}))
                        
            except Exception, err:
                print err
        #print 'RETTT', ret
        return ret
    
import time
    
class ExtraFieldsUser(models.Model):
    
    PROVIDER_FIELD = 'category'
    EXTRA_PARENT = ''
    extra = ExtraFieldsValues(null=True, blank=True, help_text='Extra fields depends on category you select', 
                              provider_field = PROVIDER_FIELD, extra_parent = EXTRA_PARENT)
                              #model_name = _meta.app_label + '.' + _meta.object_name)
    definitions_cache = dict()
    
    class Meta:
        abstract = True
    
    def clean(self):
        #raise ValidationError({'extra' : 'test'})
        return super(ExtraFieldsUser, self).clean();
    
    @staticmethod
    def clear_cache():
        ExtraFieldsUser.definitions_cache = dict()

    def get_provided_extra_fields_by_provider_id(self, provider_field_value):
        # TODO: late static binding ?
        if int(provider_field_value) not in ExtraFieldsUser.definitions_cache:
            
            path_bits = self.PROVIDER_FIELD.split('.')
            #current_class = self
            #for bit in path_bits:
            #    current_class = current_class._meta.get_field(bit).rel.to
            #return current_class.objects.get(id=provider_field_value).get_extra_fields()
            
            field_class = self._meta.get_field(path_bits.pop(0))
            current = field_class.rel.to.objects.get(id=provider_field_value)
            for bit in path_bits:
                if current is not None:
                    current = getattr(current, bit)
            
            if current is None:
                ExtraFieldsUser.definitions_cache[int(provider_field_value)] = {}
            else:
                ExtraFieldsUser.definitions_cache[int(provider_field_value)] = current.get_extra_fields()
        
        return ExtraFieldsUser.definitions_cache[int(provider_field_value)]
    
    def get_provided_extra_fields(self):
        path_bits = self.PROVIDER_FIELD.split('.')
        #print self
        try:
            provider_id = getattr(self, path_bits.pop(0) + '_id', 0)
        except:
            provider_id = None
            
        if provider_id is None:
            return {}
        else:
            return self.get_provided_extra_fields_by_provider_id(provider_id)
        """
        current = self
        for bit in path_bits:
            if hasattr(current, bit):
                current = getattr(current, bit)
            else:
                current = None
        if current is None:
            return {}
        return current.get_extra_fields()
        """        
    
    def __init__(self, *args, **kwargs):
        
        super(ExtraFieldsUser, self).__init__(*args, **kwargs)
        
        #print self.id, time.time()
        """
        parent_path_bits = self.EXTRA_PARENT.split('.')
        current = self
        for bit in parent_path_bits:
            if bit:
                parrent = getattr(current, bit)
                self.extra = dict(parrent.extra.items() + self.extra.items())
                current = parrent
        """
        #print 'EXTRA = ' + self.__class__._meta.app_label + '.' + self.__class__._meta.object_name
        self._meta.get_field('extra').set_model_and_provider(self.PROVIDER_FIELD, self.__class__._meta.app_label + '.' + self.__class__._meta.object_name); 
        self.extra_fields = {}
        
        self.extra_definition = self.get_provided_extra_fields()
        #print self.__class__.__name__, 'DEFINITION', self.extra_definition, self.extra;
        #print 'VALUES', self.extra;
        #print self.extra_definition
        for key, field in self.extra_definition:
            #print 'BBBBB', field['field'].formfield()
            try:
                #import ipdb; ipdb.set_trace() 
                #print 'JJJJJJJ', field['field'].formfield()
                self.extra_fields[key] = field['field'].formfield().to_python(self.extra[key])
                #print 'set'
                if not self.extra_fields[key] :
                    self.extra_fields[key] = getattr(self, self.EXTRA_PARENT).extra_fields[key]
            except Exception as e:
                #print 'EEE1', e
                try:
                    #print 'GGGGGGGGGGGG', getattr(self, self.EXTRA_PARENT).extra_fields[key]
                    self.extra_fields[key] = getattr(self, self.EXTRA_PARENT).extra_fields[key]
                except Exception as e:
                    #print 'EEE2', e
                    self.extra_fields[key] = field['field'].get_default();
                    #print 'default'
            #print key, self.extra.get(key, None), self.extra_fields[key], type(self.extra_fields[key])
        #print self.extra_fields
        #print self.extra_fields, 'FIELDS'
