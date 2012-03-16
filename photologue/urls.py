from django.conf import settings
from django.conf.urls.defaults import *
from models import *
from django.views.generic import date_based, list_detail
from django.contrib.auth.decorators import login_required

# Number of random images from the gallery to display.
SAMPLE_SIZE = ":%s" % getattr(settings, 'GALLERY_SAMPLE_SIZE', 8)

# galleries
gallery_args = {'date_field': 'date_added', 'allow_empty': True, 'queryset': Gallery.objects.filter(is_public=True), 'extra_context':{'sample_size':SAMPLE_SIZE}}
urlpatterns = patterns('django.views.generic.date_based',
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(date_based.object_detail), {'date_field': 'date_added', 'slug_field': 'title_slug', 'queryset': Gallery.objects.filter(is_public=True), 'extra_context':{'sample_size':SAMPLE_SIZE}}, name='pl-gallery-detail'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', login_required(date_based.archive_day), gallery_args, name='pl-gallery-archive-day'),
    url(r'^gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', login_required(date_based.archive_month), gallery_args, name='pl-gallery-archive-month'),
    url(r'^gallery/(?P<year>\d{4})/$', login_required(date_based.archive_year), gallery_args, name='pl-gallery-archive-year'),
    url(r'^gallery/?$', login_required(date_based.archive_index), gallery_args, name='pl-gallery-archive'),
)
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^gallery/(?P<slug>[\-\d\w]+)/$', login_required(list_detail.object_detail), {'slug_field': 'title_slug', 'queryset': Gallery.objects.filter(is_public=True), 'extra_context':{'sample_size':SAMPLE_SIZE}}, name='pl-gallery'),
    url(r'^gallery/page/(?P<page>[0-9]+)/$', login_required(list_detail.object_list), {'queryset': Gallery.objects.filter(is_public=True), 'allow_empty': True, 'paginate_by': 8, 'extra_context':{'sample_size':SAMPLE_SIZE}}, name='pl-gallery-list'),
)

# photographs
photo_args = {'date_field': 'date_added', 'allow_empty': True, 'queryset': Photo.objects.filter(is_public=True)}
urlpatterns += patterns('django.views.generic.date_based',
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$', login_required(date_based.object_detail), {'date_field': 'date_added', 'slug_field': 'title_slug', 'queryset': Photo.objects.filter(is_public=True)}, name='pl-photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', login_required(date_based.archive_day), photo_args, name='pl-photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', login_required(date_based.archive_month), photo_args, name='pl-photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$', login_required(date_based.archive_year), photo_args, name='pl-photo-archive-year'),
    url(r'^photo/$', login_required(date_based.archive_index), photo_args, name='pl-photo-archive'),
)
urlpatterns += patterns('django.views.generic.list_detail',
    url(r'^photo/(?P<slug>[\-\d\w]+)/$', login_required(list_detail.object_detail), {'slug_field': 'title_slug', 'queryset': Photo.objects.filter(is_public=True)}, name='pl-photo'),
    url(r'^photo/page/(?P<page>[0-9]+)/$', login_required(list_detail.object_list), {'queryset': Photo.objects.filter(is_public=True), 'allow_empty': True, 'paginate_by': 20}, name='pl-photo-list'),
)


