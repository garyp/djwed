from django.conf.urls.defaults import *
from djwed.wedding.models import Venue,Invitee,Guest,PageSnippet
from django.contrib.auth.decorators import login_required


direct = 'django.views.generic.simple.direct_to_template'

urlpatterns = patterns('',
    (r'^$', 'djwed.wedding.views.pagesnippet', {'key': 'splash'} ),
    (r'^coming-soon/.*$', direct, {'template': 'coming-soon.html'}),                      
    (r'^thankyou/.*$', 'djwed.wedding.views.thankyou'),                      
    (r'^venue/(?P<object_id>[A-Za-z0-9]+)/$', 'django.views.generic.list_detail.object_detail',
                  {'queryset': Venue.objects.all(),
                       }),

    (r'^accounts/login/?$', 'djwed.wedding.auth.rsvp_login' ),
    (r'^accounts/logout/?$', 'djwed.wedding.auth.rsvp_logout' ),
    (r'^[Rr][Ss][vV][pP]/(?P<invite_code>[A-Za-z0-9]+-[A-Za-z0-9]+)/$', 'djwed.wedding.auth.rsvp_login_from_token', { 'target':'rsvp'}),
    (r'^photos/(?P<invite_code>[A-Za-z0-9]+-[A-Za-z0-9]+)/?$', 'djwed.wedding.auth.rsvp_login_from_token', { 'target':'photos'} ),

    (r'^rsvp/$', 'djwed.wedding.views.rsvp' ),
    (r'^(?P<key>(rsvp/locked))/?$', 'djwed.wedding.views.pagesnippet' ),
    (r'^comment/(?P<ctype>[a-z0-9A-Z]+)?/?$', 'djwed.wedding.views.comment' ),
    (r'^rsvp/addguest/$', 'djwed.wedding.views.rsvp_addguest' ),
    (r'^photos/upload/$', 'djwed.wedding.views.photo_gallery_upload' ),
    (r'^profile/$', 'djwed.wedding.views.profile' ),

    (r'^(?P<key>(about-us|gifts|faq|photos))/$', 'djwed.wedding.views.pagesnippet' ),
    (r'^(?P<key>(video/[a-zA-Z0-9-_.]*))/?$', 'djwed.wedding.views.pagesnippet', { 'template': 'pagesnippet-video.html', 'login_required': True } ),
    (r'^venue/(?P<key>([A-Za-z0-9]+)/([A-Za-z0-9-]+))/$', 'djwed.wedding.views.pagesnippet' ),

    # Admin Tools...                       
    (r'^tools/responses/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.tools_report',
                                                       { 'template': 'tools_responses.html' }),
    (r'^tools/$', 'djwed.wedding.views.tools_report', { 'template': 'tools_index.html' }),
    (r'^tools/guest-count/(?P<venue_site>[A-Z]+)?/?$', 'djwed.wedding.views.tools_guest_count', { 'template': 'tools_guest_counts.html' }),
    (r'^tools/food-count/(?P<venue_site>[A-Z]+)?/?$', 'djwed.wedding.views.tools_guest_count', { 'template': 'tools_food_counts.html' }),
    (r'^tools/table-count/(?P<venue_site>[A-Z]+)/?$', 'djwed.wedding.views.tools_guest_count', { 'template': 'tools_table_counts.html' }),

    (r'^tools/mailing-labels/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.make_labels'),

    (r'^tools/invitee-merge/std-insert/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.make_svg',
                          { 'template': 'save-the-date-insert-template.svg', 'n_up': 4 } ),
    (r'^tools/invitee-merge/response-card-insert/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.make_svg',
                          { 'template': 'invite-response-card-template.svg', 'n_up': 2, 'orient': 'landscape' } ),
    (r'^tools/invitee-merge/invitation-envelopes/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.make_svg',
                          { 'template': 'invite-envelope-front.svg', 'n_up': 1, 'orient': 'a8-envelope' } ),
    (r'^tools/invitee-merge/invitee-code-insert/(?P<filter>[a-z0-9A-Z-]*)/?$', 'djwed.wedding.views.make_svg',
                          { 'template': 'invite-invitee-code-insert.svg', 'n_up': 4 } ),
    (r'^tools/rsvp-merge/placecards/(?P<venue_site>[A-Z]+)/$', 'djwed.wedding.views.make_svg',
                          { 'filter': 'rsvp_yes', 'template': 'placecard-template.svg', 'n_up': 4 } ),

    (r'^tools/invitee-list/(?P<filter>[0-9=a-zA-Z-]+)?/?$', 'djwed.wedding.views.tools_report', { 'template': 'tools_invitee_list.html' }),
    (r'^tools/export-(?P<rowset>(invitees|guests|bus|gifts))/(?P<filter>[0-9=a-zA-Z-]+)/?(?P<columns>[0-9=a-zA-Z]*)/?$', 'djwed.wedding.views.tools_export'),

    #(r'^gifts/$', direct, {'template': 'gifts.html'}),
    #(r'^about-us/$', direct, {'template': 'about-us.html'}),

    #(r'^$', 'django.views.generic.list_detail.object_list', info_dict),
    #(r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict),
    #url(r'^(?P<object_id>\d+)/results/$', 'django.views.generic.list_detail.object_detail',
    #    dict(info_dict, template_name='polls/results.html'), 'poll_results'),
    #(r'^(?P<poll_id>\d+)/vote/$', 'mysite.polls.views.vote'),
)

