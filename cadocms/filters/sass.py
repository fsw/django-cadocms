import re,os
from compressor.filters import CompilerFilter
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from django.contrib.staticfiles import finders

class SassFilter(CompilerFilter):
    
    def __init__(self, content, attrs, *args, **kwargs):
        self.attrs = attrs
        super(SassFilter, self).__init__(content, command='sass --scss', *args, **kwargs)
    
    def replace_images(self, csspath, content):
        #print "REPLACING IMAGES FOR " + csspath
        image_pattern = "url\((.*?)\)"
        images = re.findall(image_pattern, content)
        for file in images:
            path = file.replace("'", "").replace("\"", "")
            if path.startswith('/'):
                new_path = path[1:]
            else:
                new_path = csspath.replace(os.path.basename(csspath), '') + path
            new_path = settings.STATIC_URL + os.path.normpath(new_path)
            #print csspath, new_path
            content = content.replace("url(%s)" % file, "url(%s)" % new_path); 

        return content
    
    def replace_imports(self, parentpath, content, stack):
        #TODO: limit stac, check circular imports
        content = self.replace_images(parentpath, content)
        import_pattern = "@import \"(.*?)\";"
        imports = re.findall(import_pattern, content)
        for file in imports:
            if file.startswith('/'):
                filepath = file[1:]
            else:
                filepath = parentpath.replace(os.path.basename(parentpath), '') + file
            if finders.find(filepath):
                #print 'IMPORTING ', file, '  path= ', finders.find(filepath, True);
                #print "@import \"%s\";" % file
                content = content.replace("@import \"%s\";" % file, 
                          self.replace_imports(filepath, open(finders.find(filepath), 'r').read(), stack))
        return content
    
    def input(self, **kwargs):
        print self.content, self.filename, self.infile
        staticpath = self.attrs.get('href').replace(settings.STATIC_URL, '')
        self.content = self.replace_imports(staticpath, self.content, [])
        #print self.content
        return super(SassFilter, self).input(**kwargs)