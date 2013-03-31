from django.db import models
from django.template.defaultfilters import slugify
from django.core.exceptions import ObjectDoesNotExist
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from django.utils.translation import ugettext_lazy as _

class StaticPage(models.Model):
    
    url = models.CharField(_('URL'), max_length=200, db_index=True)
    title = models.CharField(_('title'), max_length=256)
    content = models.TextField(_('content'), blank=True)
    seo_title = models.CharField(max_length=512, blank=True)
    seo_keywords = models.CharField(max_length=512, blank=True)
    seo_description = models.TextField('seo_description', blank=True)

    class Meta:
        verbose_name = _('static page')
        verbose_name_plural = _('static pages')
        ordering = ('url',)

    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        return self.url
    
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
    order = models.IntegerField(default=0)
    class Meta:
        abstract = True
        ordering = ['order', 'name']
    class MPTTMeta:
        order_insertion_by=['order']
