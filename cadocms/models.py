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
from django.core.mail import send_mail
from datetime import datetime    

import reversion

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
    created     = models.DateTimeField(editable=False, default=datetime.now)
    modified    = models.DateTimeField(editable=False, default=datetime.now)
    
    owner = models.ForeignKey(User, related_name='owner', null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def moderation_status_code(self):
        return MODERATION_STATUSES_CODES[self.moderation_status]
    
    def on_moderate_accept(self):
        send_mail('[' + settings.CADO_NAME + '] ' + str(self) + ' has been accepted by moderation',
                  'Dear ' + str(self.owner) + "!\n\n" + 'Your item has been accepted and is now publicly visible on ' + settings.CADO_NAME,
                  settings.SPAM_EMAIL,
                  [self.owner.email])
        
    def on_moderate_reject(self, reason):
        send_mail('[' + settings.CADO_NAME + '] ' + str(self) + ' has been rejected by moderation',
                  'Dear ' + str(self.owner) + "!\n\n" + reason.email_body,
                  settings.SPAM_EMAIL,
                  [self.owner.email])

    def moderate_accept(self, user):
        self.moderation_status = MODERATION_STATUS['OK']
        self.moderation_user = user
        self.on_moderate_accept()
        super(Moderated, self).save()

    def moderate_reject(self, user, reason):
        self.moderation_status = MODERATION_STATUS['REJECTED']
        self.moderation_user = user
        self.moderation_reason = reason
        self.on_moderate_reject(reason)
        super(Moderated, self).save()

    def show_diff(self):
        if (self.moderation_status == MODERATION_STATUS['NEW']):
            d = model_to_dict(self, fields=[field.name for field in self._meta.fields])
            return dict([(x,[y]) for x,y in d.items()])
        if (self.moderation_status == MODERATION_STATUS['MODIFIED']):
            version_list = reversion.get_for_object(self)
            ret = {}
            for version in version_list[0:2]:
                for key,value in version.field_dict.items():
                    ret[key] = ret.get(key,[])
                    ret[key].append(value)
            return ret
        #model_to_dict(self, fields=[field.name for field in self._meta.fields])
        #model_to_dict(self, fields=[field.name for field in self._meta.fields])
        
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.moderation_status = MODERATION_STATUS['NEW']
            self.created = datetime.today()
        else:
            original = self.__class__._default_manager.get(pk=self.pk)
        
        self.modified = datetime.today()
        
        if (self.moderation_status != MODERATION_STATUS['NEW']):
            print self.__class__._meta.get_all_field_names()
            print self.__class__._meta.fields
            for field in self.__class__._meta.fields + self.__class__._meta.many_to_many: #self.__class__._meta.get_all_field_names():
                if field.name not in ['moderation_status', 'moderation_reason', 'moderation_user', 'moderation_comment', 'created', 'modified']:
                    #field_class = self.__class__._meta.get_field(field)
                    original_data = getattr(original, field.name)
                    new_data = getattr(self, field.name)
                    if isinstance(field, models.ManyToManyField):
                        pass
                        #TODO
                        #print original_data.all()
                        #print new_data.all()
                    elif original_data != new_data:
                        self.moderation_status = MODERATION_STATUS['MODIFIED']
                        #print 'MODIFIED ' + field
                        #print original_data
                        #print new_data
        
        with reversion.create_revision():
            ret = super(Moderated, self).save(*args, **kwargs)
        
        return ret
    

class Translatable(models.Model):
    translatable_fields = ()
    class Meta:
        abstract = True
    
class StaticPage(Translatable):
    
    url = models.CharField(_('URL'), max_length=200, db_index=True)
    title = models.CharField(_('Title'), max_length=256)
    content = HTMLField('Content')
    seo_title = models.CharField(max_length=512, blank=True)
    seo_keywords = models.CharField(max_length=512, blank=True)
    seo_description = models.TextField('seo_description', blank=True)
    translatable_fields = ('title', 'content', 'seo_title', 'seo_keywords', 'seo_description',)

    class Meta:
        verbose_name = _('static page')
        verbose_name_plural = _('static pages')
        ordering = ('url',)
        abstract = True
        
    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        return self.url


class Chunk(Translatable):
    key = models.CharField(max_length=256)
    body = HTMLField(blank=True, null=True)
    translatable_fields = ('body',)

    def __unicode__(self):
        return self.key    
    class Meta:
        abstract = True
    
    
class Setting(models.Model):
    
    key = models.CharField(_('Key'), max_length=200, db_index=True)
    value = models.TextField(_('Value'), blank=True)
    description = models.TextField('description', blank=True)

    def __unicode__(self):
        return u"%s = %s" % (self.key, self.value)

    
class Sluggable(models.Model):
    slug = models.SlugField(unique=True, blank=True)#, editable=False)
    
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
    
    def save(self, *args, **kwargs):
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
    parent = TreeForeignKey('self', null=True, blank=False, related_name='children', default=0)
    order = models.FloatField(default=0)
    class Meta:
        abstract = True
        ordering = ['order', 'name']
    class MPTTMeta:
        order_insertion_by=['order']
        
    def clean(self):
        super(RootedTree, self).clean()
        from django.core.exceptions import ValidationError
        if self.tree_id > 1:
            raise ValidationError("Cant create new category here")
        
class ExtraFieldsProvider(models.Model):

    extra_fields = ExtraFieldsDefinition(null=True, blank=True)
    
    class Meta:
        abstract = True
        
    def get_extra_fields(self):
        all_cats = self.get_ancestors(include_self=True)
        ret = {}
        for cat in all_cats:
            try:
                for key, field in cat.extra_fields.items():
                    if not field:
                        ret.pop(key, None)
                    else:
                        #print key, field
                        methodToCall = getattr(models, field.get('class', 'CharField'), models.CharField)
                        #print methodToCall
                        args = field.get('kwargs', {}).copy()
                        if 'choices' in args:
                            new_options = []
                            for k, v in args['choices'].items():
                                new_options.append((k,v))
                            args['choices'] = new_options
                        f = methodToCall(**args)
                        solr_key = key
                        h_field = indexes.index_field_from_django_field(f)
                        if h_field == indexes.CharField:
                            solr_key = '%s_s' % key
                        elif h_field == indexes.DateTimeField:
                            solr_key = '%s_dt' % key
                        elif h_field == indexes.BooleanField:
                            solr_key = '%s_b' % key
                        elif h_field == indexes.MultiValueField:
                            solr_key = '%s_s' % key
                        elif h_field == indexes.FloatField:
                            solr_key = '%s_f' % key
                        elif h_field == indexes.IntegerField:
                            solr_key = '%s_i' % key
                        else:
                            raise Exception('unknown type')
    
                        ret[key] = {'field' : f, 'solr_key' : solr_key}
                    
            except Exception, err:
                print err
        return ret
    
    
class ExtraFieldsUser(models.Model):
    
    PROVIDER_FIELD = 'category'
    EXTRA_PARENT = ''
    extra = ExtraFieldsValues(null=True, blank=True, help_text='Extra fields depends on category you select', 
                              provider_field = PROVIDER_FIELD)
                              #model_name = _meta.app_label + '.' + _meta.object_name)
    class Meta:
        abstract = True
    
    def get_provided_extra_fields_by_provider_id(self, provider_field_value):
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
            return {}
        return current.get_extra_fields()  
    
    def get_provided_extra_fields(self):
        path_bits = self.PROVIDER_FIELD.split('.')
        current = self
        for bit in path_bits:
            if hasattr(current, bit):
                current = getattr(current, bit)
            else:
                current = None
        if current is None:
            return {}
        return current.get_extra_fields()        
    
    def __init__(self, *args, **kwargs):
        super(ExtraFieldsUser, self).__init__(*args, **kwargs)
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
        for key, field in self.extra_definition.items():
            #print key
            try:
                self.extra_fields[key] = field['field'].to_python(self.extra[key])
                #print 'set'
                if not self.extra_fields[key] and self.EXTRA_PARENT:
                    self.extra_fields[key] = getattr(self, self.EXTRA_PARENT).extra_fields[key]
            except Exception:
                try:
                    #print 'GGGGGGGGGGGG', getattr(self, self.EXTRA_PARENT).extra_fields[key]
                    self.extra_fields[key] = getattr(self, self.EXTRA_PARENT).extra_fields[key]
                except Exception:
                    self.extra_fields[key] = field['field'].get_default();
                    #print 'default'
        
        #print self.extra_fields
        #print self.extra_fields, 'FIELDS'
