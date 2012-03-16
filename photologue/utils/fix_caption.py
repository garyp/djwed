import pyexiv2

from photologue.models import *

# pyexiv2.Image(x.image.file.name)

g = Gallery.objects.get(title_slug=u'cena-bessolo-california-reception-at-spinnaker-2')
g.photos.all()

def get_photo_caption(photo, set=False):
    m = pyexiv2.Image(photo.image.file.name)
    m.readMetadata()
    k = m.iptcKeys()
    if 'Iptc.Application2.Caption' in k:
        caption = m['Iptc.Application2.Caption']
        if caption == 'SONY DSC' or caption[:6] == 'Error:':
            del m
            return        
        print caption
        if set:
            photo.caption = caption
            photo.save()
            print u"set caption"
    del m

