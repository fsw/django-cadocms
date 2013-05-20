'''
This is loosly based on Derek Schaefer's django-json-field:
https://github.com/derek-schaefer/django-json-field
'''

from .forms import JSONFormField, ExtraFieldsValuesFormField
from django.forms import fields

from django.db import models
from django.utils import simplejson as json
from django.core import exceptions
from django.utils.timezone import is_aware
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from django import forms
from django.utils.text import capfirst

from cadolib.widgets import ExtraFieldsValuesWidget

import re
import decimal
import datetime
try:
    from dateutil import parser as date_parser
except ImportError:
    raise ImproperlyConfigured('The "dateutil" library is required and was not found.')

try:
    JSON_DECODE_ERROR = json.JSONDecodeError # simplejson
except AttributeError:
    JSON_DECODE_ERROR = ValueError # other

TIME_RE = re.compile(r'^\d{2}:\d{2}:\d{2}')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}(?!T)')
DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T')

class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(JSONEncoder, self).default(o)

class JSONDecoder(json.JSONDecoder):
    """ Recursive JSON to Python deserialization. """

    _recursable_types = [str, unicode, list, dict]

    def _is_recursive(self, obj):
        return type(obj) in JSONDecoder._recursable_types

    def decode(self, obj, *args, **kwargs):
        if not kwargs.get('recurse', False):
            obj = super(JSONDecoder, self).decode(obj, *args, **kwargs)
        if isinstance(obj, list):
            for i in xrange(len(obj)):
                item = obj[i]
                if self._is_recursive(item):
                    obj[i] = self.decode(item, recurse=True)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if self._is_recursive(value):
                    obj[key] = self.decode(value, recurse=True)
        elif isinstance(obj, basestring):
            if TIME_RE.match(obj):
                try:
                    return date_parser.parse(obj).time()
                except ValueError:
                    pass
            if DATE_RE.match(obj):
                try:
                    return date_parser.parse(obj).date()
                except ValueError:
                    pass
            if DATETIME_RE.match(obj):
                try:
                    return date_parser.parse(obj)
                except ValueError:
                    pass
        return obj

class Creator(object):
    """
    Taken from django.db.models.fields.subclassing.
    """

    _state_key = '_json_field_state'

    def __init__(self, field, lazy):
        self.field = field
        self.lazy = lazy

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')

        if self.lazy:
            state = getattr(obj, self._state_key, None)
            if state is None:
                state = {}
                setattr(obj, self._state_key, state)

            if state.get(self.field.name, False):
                return obj.__dict__[self.field.name]

            value = self.field.to_python(obj.__dict__[self.field.name])
            obj.__dict__[self.field.name] = value
            state[self.field.name] = True
        else:
            value = obj.__dict__[self.field.name]

        return value

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value if self.lazy else self.field.to_python(value)

class JSONField(models.TextField):
    """ Stores and loads valid JSON objects. """

    description = 'JSON object'

    def __init__(self, *args, **kwargs):
        self.default_error_messages = {
            'invalid': _(u'Enter a valid JSON object')
        }
        self._db_type = kwargs.pop('db_type', None)
        self.evaluate_formfield = kwargs.pop('evaluate_formfield', False)

        self.lazy = kwargs.pop('lazy', True)
        encoder = kwargs.pop('encoder', JSONEncoder)
        decoder = kwargs.pop('decoder', JSONDecoder)
        encoder_kwargs = kwargs.pop('encoder_kwargs', {})
        decoder_kwargs = kwargs.pop('decoder_kwargs', {})
        if not encoder_kwargs and encoder:
            encoder_kwargs.update({'cls':encoder})
        if not decoder_kwargs and decoder:
            decoder_kwargs.update({'cls':decoder, 'parse_float':decimal.Decimal})
        self.encoder_kwargs = encoder_kwargs
        self.decoder_kwargs = decoder_kwargs

        kwargs['default'] = kwargs.get('default', 'null')
        kwargs['help_text'] = kwargs.get('help_text', self.default_error_messages['invalid'])

        super(JSONField, self).__init__(*args, **kwargs)

    def post_decode(self, dict):
        return dict
    
    def pre_encode(self, dict):
        return dict
    
    def db_type(self, *args, **kwargs):
        if self._db_type:
            return self._db_type
        return super(JSONField, self).db_type(*args, **kwargs)

    def to_python(self, value):
        if value is None: # allow blank objects
            return None
        if isinstance(value, basestring):
            try:
                value = self.post_decode(json.loads(value, **self.decoder_kwargs))
            except JSON_DECODE_ERROR:
                pass
        return value

    def get_db_prep_value(self, value, *args, **kwargs):
        if self.null and value is None and not kwargs.get('force'):
            return None
        return json.dumps(self.pre_encode(value), **self.encoder_kwargs)

    def value_to_string(self, obj):
        return self.get_db_prep_value(self._get_val_from_obj(obj))

    def value_from_object(self, obj):
        return json.dumps(self.pre_encode(super(JSONField, self).value_from_object(obj)), indent=4 * ' ', **self.encoder_kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': kwargs.get('form_class', JSONFormField),
            'evaluate': self.evaluate_formfield,
            'encoder_kwargs': self.encoder_kwargs,
            'decoder_kwargs': self.decoder_kwargs,
        }
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name):
        super(JSONField, self).contribute_to_class(cls, name)

        def get_json(model_instance):
            return self.get_db_prep_value(getattr(model_instance, self.attname, None), force=True)
        setattr(cls, 'get_%s_json' % self.name, get_json)

        def set_json(model_instance, value):
            return setattr(model_instance, self.attname, self.to_python(value))
        setattr(cls, 'set_%s_json' % self.name, set_json)

        setattr(cls, name, Creator(self, lazy=self.lazy)) # deferred deserialization

try:
    # add support for South migrations
    from south.modelsinspector import add_introspection_rules
    rules = [
        (
            (JSONField,),
            [],
            {
                'db_type': ['_db_type', {'default': None}]
            }
        )
    ]
    add_introspection_rules(rules, ['^cadoshop\.fields\.JSONField'])
except ImportError:
    pass

        
class ExtraFieldsDefinition(JSONField):
    pass
    
class ExtraFieldsValues(JSONField):
    
    provider_field = 'unknown'
    model_name = 'Unknown'
    
    def __init__(self, *args, **kwargs):
        super(ExtraFieldsValues, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        #print "INIT FORM FIELD FORM %s %s" % (self.provider_field, self.model_name)
        kwargs['form_class'] = ExtraFieldsValuesFormField
        kwargs['widget'] = ExtraFieldsValuesWidget(model_name = self.model_name, provider_field = self.provider_field)
        return super(ExtraFieldsValues, self).formfield(**kwargs)
    """
    def formfield(self, **kwargs):
        defaults = {
            'form_class': kwargs.get('form_class', JSONFormField),
            'evaluate': self.evaluate_formfield,
            'encoder_kwargs': self.encoder_kwargs,
            'decoder_kwargs': self.decoder_kwargs,
        }
        defaults.update(kwargs)
        return super(JSONField, self).formfield(**defaults)
    """

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^cadolib\.fields\.ExtraFieldsDefinition"])
add_introspection_rules([], ["^cadolib\.fields\.ExtraFieldsValues"])

class HTMLField(models.TextField):
    
    widget = forms.Textarea(attrs={'class':'special'})
    
    """
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(HTMLField, self).formfield(**defaults)
        """


