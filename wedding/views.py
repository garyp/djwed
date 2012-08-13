# Create your views here.

from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect,Http404, HttpResponseForbidden
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from djwed.wedding.models import *
from djwed.wedding import guest_filter
from djwed.wedding.mailing_labels import LabelMaker, LabelSpecBasic
from djwed.wedding.auth import user_to_invitee
from djwed.wedding.utils import SVG2PDF
from djwed.wedding.spreadsheet import SpreadSheet
from djwed.settings import DEBUG, SEND_EMAIL
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Min
from django.contrib.auth import login
from django import forms
from django.forms.models import BaseModelFormSet,BaseModelFormSet,ModelForm,modelformset_factory
from django.core.mail import send_mail, mail_managers
from photologue.models import *

users_with_rsvp_view_perms = (u'invitee9__',  # a user you want to give additional permissions to
                       )

# Set to False to prevent guests from making RSVP changes
allow_rsvp_changes = True

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['type','text']

class InviteeProfileForm(ModelForm):
    class Meta:
        model = Invitee
        fields = ('full_address',)

class AddGuestForm(ModelForm):
    class Meta:
        model = Guest
        fields = ('first_name','last_name','nickname',
                  'email','home_phone','cell_phone')

GuestProfileFormSet = modelformset_factory(Guest,
                                           fields=('first_name','last_name','nickname',
                                                   'email','home_phone','cell_phone'),
                                           extra=0)

def pagesnippet(request, key, template='pagesnippet.html', login_required=False):
    if login_required and not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
    try:
        o = PageSnippet.objects.get(key=key)
    except PageSnippet.DoesNotExist:
        raise Http404
    # Snippets should have a more general "auth required" attribute
    if key == 'MA/lodging-codes' and not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
    return render_to_response(template, {'pagesnippet': o},
                              context_instance=RequestContext(request))


#class PrelimRSVPForm(ModelForm):
#    class Meta:
#        model = RSVP
#        fields = ('status',)

class ModelChoiceFieldLong(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.long_desc

class FinalRSVPForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(FinalRSVPForm, self).__init__(*args, **kwargs)
        self.fields['status'].queryset = RSVPOption.objects.all().order_by('-likelihood')
        self.fields['food_selection'].queryset = FoodOption.objects.filter(venue=self.instance.venue)

    status = ModelChoiceFieldLong([],
            empty_label="-- Please indicate whether you will be attending --",
            widget=forms.Select(attrs={
                'onchange':'rsvpHideIfNotAttendingSelect(this);'
                })
            )

    bus_selection = forms.ChoiceField(RSVP.bus_choice_long_names, required=False)
    food_selection = ModelChoiceFieldLong([], required=False,
            empty_label="--- Please choose from a dinner selection below ---"
            )
    class Meta:
        model = RSVP
        fields = ('status','food_selection','bus_selection')

class GuestRSVPs:
    """ Temporary for use in templates.  Somewhat of a hack. """
    def __init__(self, guest):
        self.guest = guest
        self.MA = None
        self.CA = None

    def add_rsvp(self, rsvp, form):
        if rsvp.venue.site == u'CA':
            self.CA = form
        elif rsvp.venue.site == u'MA':
            self.MA = form
        else:
            raise ValidationError('Invalid Venue Error')
        

@login_required
def rsvp(request):
    if request.user.is_staff: return HttpResponseRedirect('/accounts/login/')        
    inv = user_to_invitee(request.user)
    inv.mark_visited()
    cform = CommentForm(initial={'type':'general'})
    if request.method == 'POST':
        if not allow_rsvp_changes:
            if SEND_EMAIL:
                mail_managers('RSVP attempt from '+inv.full_name(),"")
            return HttpResponseRedirect('/rsvp/locked/')
        guest_rsvps = []
        all_rsvp_forms = []
        valid = True
        for g in inv.ordered_guests().all():
            rsvps = g.get_or_create_rsvps()
            gr = GuestRSVPs(g)
            guest_rsvps.append(gr)
            for r in rsvps:
                rf = FinalRSVPForm(request.POST, instance=r, prefix=str(r.pk))
                gr.add_rsvp(r, rf)
                all_rsvp_forms.append(rf)
                if not rf.is_valid():
                    valid = False
        if valid:
            summary = []
            for rf in all_rsvp_forms:
                r = rf.save(commit=False)
                # Clear preliminary RSVP flag
                r.prelim = False

                # If not attending, unset meals and bus
                if not r.yes_or_maybe():
                    r.food_selection = None
                    r.bus_selection = None
                r.last_update_source = u'web'
                if r.guest.invitee != inv:
                    raise HttpResponseForbidden("Invalid invitee for RSVP/guest!")
                summary.append(unicode(r))
                r.save()
            inv.mark_updated()
            #print summary
            if SEND_EMAIL:
                mail_managers('RSVP from '+inv.full_name(),
                              'New status: \n%s\n\n'%("\n".join(summary),))
            else:
                print ('RSVP from '+inv.full_name(),
                       'New status: \n%s\n\n'%("\n".join(summary),))
            return HttpResponseRedirect('/thankyou/') 
    else:
        # This could perhaps be better handled with a formset...
        guest_rsvps = []
        for g in inv.ordered_guests().all():
            rsvps = g.get_or_create_rsvps()
            gr = GuestRSVPs(g)
            guest_rsvps.append(gr)
            for r in rsvps:
                rf = FinalRSVPForm(instance=r, prefix=str(r.pk))
                gr.add_rsvp(r, rf)
    return render_to_response('rsvp.html', {
        'comment_form': cform,        
        'invitee': inv,
        'guest_rsvps': guest_rsvps,
        'comments': Comment.objects.filter(invitee=inv),
        'allow_rsvp_changes': allow_rsvp_changes,
        'user': request.user        
    })



@login_required
def thankyou(request):
    inv = user_to_invitee(request.user)
    return render_to_response('thanks.html', {
        'invitee': inv,
        'user': request.user 
    })


@login_required
def comment(request, ctype=u"general"):
    if request.user.is_staff: return HttpResponseRedirect('/accounts/login/')        
    if not ctype in [x[0] for x in Comment.COMMENT_TYPES]:
        ctype = u"general"
    inv = user_to_invitee(request.user)
    inv.mark_visited()
    if request.method == 'POST': 
        cform = CommentForm(request.POST) 
        if cform.is_valid():
            c = cform.save(commit=False)
            c.invitee = inv
            c.save()
            inv.mark_updated()
            if SEND_EMAIL:
                mail_managers('Wedding comment from '+inv.full_name(),
                              'Comment type: %s\nComment:\n\n%s\n'%(c.type, c.text))
            else:
                print 'Wedding comment from '+inv.full_name()
            return HttpResponseRedirect('/thankyou/') 
    else:
        cform = CommentForm(initial={'type': ctype})
    return render_to_response('comment.html', {
        'comment_form': cform,
        'invitee': inv,
        'comments': Comment.objects.filter(invitee=inv),
        'user': request.user 
    })


@login_required
def profile(request):
    if request.user.is_staff: return HttpResponseRedirect('/accounts/login/')        
    inv = user_to_invitee(request.user)
    inv.mark_visited()
    if request.method == 'POST': 
        # Form has been submitted
        guest_formset = GuestProfileFormSet(request.POST, queryset=Guest.objects.filter(invitee=inv))
        inv_form = InviteeProfileForm(request.POST, instance=inv)
        if inv_form.is_valid() and guest_formset.is_valid():
            inv2 = inv_form.save(commit=False)
            guests = guest_formset.save(commit=False)
            if inv != inv2:
                raise HttpResponseForbidden("Invalid invitee!")
            for g in guests:
                if g.invitee != inv:
                    raise HttpResponseForbidden("Invalid invitee for guest!")
                g.save()
            inv2.save()
            inv.mark_updated()
            if SEND_EMAIL:
                mail_managers('Profile update from '+inv.full_name(),
                              'This invitee has updated their profile.\nhttp://wedding.example.org/admin/wedding/invitee/%s/'%(str(inv.id,)))
            else:
                print 'Profile update from '+inv.full_name()
            return HttpResponseRedirect('/thankyou/') 
    else:
        guest_formset = GuestProfileFormSet(queryset=Guest.objects.filter(invitee=inv))
        inv_form = InviteeProfileForm(instance=inv)
    return render_to_response('profile.html', {
        'guest_formset': guest_formset,
        'invitee': inv,
        'inv_form': inv_form,
        'user': request.user 
    })


@login_required
def rsvp_addguest(request):
    if request.user.is_staff: return HttpResponseRedirect('/accounts/login/')        
    inv = user_to_invitee(request.user)
    # grab the name before the addition of the new guest
    inv_full_name = inv.full_name()
    if request.method == 'POST':
        if not allow_rsvp_changes:
            if SEND_EMAIL:
                mail_managers('RSVP guest addition attempt from '+inv.full_name(),"")
            return HttpResponseRedirect('/rsvp/locked/')        
        form = AddGuestForm(request.POST) 
        if form.is_valid():
            g = form.save(commit=False)
            g.invitee = inv
            g.role = "added_by_invitee"
            g.order = inv.guest_set.count() + 1            
            g.save()
            inv.mark_updated()
            if SEND_EMAIL:
                mail_managers('Guest addition from '+inv_full_name,
                              u'This invitee has added a guest: %s\nhttp://wedding.example.org/admin/wedding/invitee/%s/'%(unicode(g.full_name()), str(inv.id)))
            return HttpResponseRedirect('/thankyou/') 
    else:
        form = AddGuestForm()
    return render_to_response('rsvp_addguest.html', {
        'form': form,
        'invitee': inv,
        'user': request.user,
        'allow_rsvp_changes': allow_rsvp_changes,
    })





class PhotoGalleryUploadForm(ModelForm):

    def __init__(self, invitee, *args, **kwargs):
        super(PhotoGalleryUploadForm, self).__init__(*args, **kwargs)
        #print invitee
        self.fields['photographer'].queryset = Guest.objects.filter(invitee=invitee)

    photographer = forms.ModelChoiceField(queryset=Guest.objects.all())

    #bus_selection = forms.ChoiceField(RSVP.bus_choice_long_names, required=False)
    #food_selection = FoodChoiceField([], required=False,
    #                                 empty_label = "--- Please choose from a dinner selection below ---")

    class Meta:
        model = GalleryUpload
        fields = ('zip_file','title','photographer')

@login_required
def photo_gallery_upload(request):
    if request.user.is_staff: return HttpResponseRedirect('/accounts/login/?next=/photos/')
    inv = user_to_invitee(request.user)
    if request.method == 'POST':
        form = PhotoGalleryUploadForm(inv, request.POST, request.FILES)
        #print form.is_valid()
        #print form
        #print request.FILES
        #print form.errors
        if form.is_valid():
            guestid = int(request.POST['photographer'])
            photographer = Guest.objects.get(id=guestid)
            if photographer.invitee != inv:
                raise HttpResponseForbidden("Invalid invitee for Photographer/guest!")
            g = form.save(commit=False)
            gname = u'Photos from %s: %s'%(photographer.full_name(), g.title)
            slugname = slugify(u'%s: %s'%(photographer.full_name(), g.title))[:49]
            try:
                gal = Gallery.objects.get(title_slug=slugname)
                #print "GOT: "+repr(gal)
            except Gallery.DoesNotExist:
                #print "MEEP"                
                gal = Gallery(title=gname, title_slug=slugname)
                #print u"MADE: %s / %s"%(repr(gal), unicode(gal.title_slug))
                gal.save()
            #print "HERE"
            g.gallery = gal
            g.title = gname
            #g.description = u'%s'%(inv.full_name(),g.title)
            g.tags = u'from:invitee:%d from:guest:%d'%(inv.id,photographer.id)
            g.save()
            albumurl = "/photologue/gallery/%s"%(str(gal.title_slug))
            if SEND_EMAIL:
                mail_managers('Photo gallery upload from '+inv.full_name(),
                              u'This invitee has uploaded photos from an album %s to:\n   http://wedding.example.org/%s'%(gal.title, albumurl))
            return HttpResponseRedirect(albumurl)
    else:
        form = PhotoGalleryUploadForm(invitee=inv)
    return render_to_response('photo_upload.html', {
        'form': form,
        'invitee': inv,
        'user': request.user,
    })





@login_required
def tools_report(request, filter=None, template=None):
    if request.user.is_staff or request.user.username in users_with_rsvp_view_perms:
        pass
    else:
        return HttpResponseRedirect('/admin/login/?next=/tools/')        
    inv = Invitee.objects.all().order_by('last_updated','last_visited').reverse()
    if filter=='std':
        inv = guest_filter.savedate_invitees()
    return render_to_response(template, {
        'invitees': inv,
        'filter': filter,
        'venues': Venue.objects.all(),
        'guests': Guest.objects.all(),
        'rsvps': RSVP.objects.all(),
        'user': request.user },
        context_instance=RequestContext(request))


@login_required
def tools_export(request, filter="all-invitees", rowset="invitee", columns=None):
    if not request.user.is_staff: return HttpResponseRedirect('/admin/')        

    venue_ma = Venue.objects.get(site="MA")
    venue_ca = Venue.objects.get(site="CA")
    ss = SpreadSheet(filter+"-"+rowset)
    if rowset == "invitees":
        if filter=='std':
            inv = guest_filter.savedate_invitees()
        else:
            inv = guest_filter.all_invitees()
        ss.add_column("invite_code", 40)
        ss.add_column("full_name", 120)
        ss.add_column("country", 15)       
        ss.add_column("state", 15)       
        ss.add_column("association", 40)       
        ss.add_column("side", 15)       
        ss.add_column("full_address", 120)       
        ss.add_column("ma_ev", 15)       
        ss.add_column("ca_ev", 15)       
        for x in inv:
            ma_ev = 0
            ca_ev = 0
            for g in x.guest_set.all():
                ma_ev += g.venue_likelihood(venue_ma)
                ca_ev += g.venue_likelihood(venue_ca)
            row = [x.invite_code,
                   x.full_name(),
                   x.country,
                   x.state,
                   x.association,
                   x.side,
                   x.full_address,
                   ma_ev,
                   ca_ev]
            ss.add_row(row)

    elif rowset == "guests":
        guests = guest_filter.all_guests()
        ss.add_column("invitee_id", 10)
        ss.add_column("full_name", 80)
        ss.add_column("last_name", 40)
        ss.add_column("first_name", 30)
        ss.add_column("nickname", 30)
        ss.add_column("email", 70)       
        ss.add_column("country", 15)       
        ss.add_column("state", 15)       
        ss.add_column("association", 40)       
        ss.add_column("side", 15)       
        ss.add_column("home_phone", 50)       
        ss.add_column("cell_phone", 50)
        ss.add_column("ma_ev", 15)       
        ss.add_column("ca_ev", 15)       
        for g in guests:
            row = [g.invitee.id,
                   g.full_name(),
                   g.last_name,
                   g.first_name,
                   g.nickname,
                   g.email,
                   g.invitee.country,
                   g.invitee.state,
                   g.invitee.association,
                   g.invitee.side,
                   g.home_phone,
                   g.cell_phone,
                   g.venue_likelihood(venue_ma),
                   g.venue_likelihood(venue_ca)
                   ]
            ss.add_row(row)

    elif rowset == "bus":
        ss.add_column("direction", 30)
        ss.add_column("there", 20)
        ss.add_column("back", 20)
        ss.add_column("full_name", 80)
        ss.add_column("cell_phone", 50)
        ss.add_column("last_name", 40)
        ss.add_column("first_name", 30)
        ss.add_column("nickname", 30)
        ss.add_column("email", 70)       
        ss.add_column("home_phone", 50)       
        for r in RSVP.objects.filter(venue="MA", status__in=RSVPOption.objects.yes()).order_by("bus_selection","guest__last_name"):
            if not r.bus_selection or r.bus_selection == "none": continue
            #print "%s,%s,%s,%s"%(r.guest.full_name(),r.bus_selection,r.guest.cell_phone,r.guest.home_phone)	        for g in guests
            direction=r.bus_selection
            if direction == "from":
                direction = "return only"
            row = [direction,
                   "","",
                   r.guest.full_name(),
                   r.guest.cell_phone,
                   r.guest.last_name,
                   r.guest.first_name,
                   r.guest.nickname,
                   r.guest.email,
                   r.guest.home_phone,
                   ]
            ss.add_row(row)
        
    elif rowset == "gifts":
        inv = Invitee.objects.annotate(Min('gift__received')).filter(gift__isnull=False).order_by('gift__received__min')
        ss.add_column("invite_code", 40)
        ss.add_column("full_name_address", 120)
        ss.add_column("received", 40)       
        ss.add_column("gift description", 200)       
        ss.add_column("notes", 100)       
        ss.add_column("assignment", 40)       
        ss.add_column("status", 40)       
        ss.add_column("thank_you_sent", 40)       
        ss.add_column("registry", 40)       
        ss.add_column("association", 40)       
        ss.add_column("side", 15)       
        ss.add_column("country", 15)       
        ss.add_column("state", 15)       
        for x in inv:
            for g in x.gift_set.order_by('received'):
                row = [x.invite_code,
                       x.full_name()+"\n"+x.full_address,
                       str(g.received),
                       g.description,
                       g.notes,
                       g.assignment,
                       g.status,
                       str(g.thank_you_sent) if g.thank_you_sent else "",
                       g.registry,
                       x.association,
                       x.side,
                       x.country,
                       x.state]
                #print row
                ss.add_row(row)
       
    else:
        raise Http404("Invalid row set")
    
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=export-%s-%s.xls'%(rowset,filter,)
    response.write(ss.finalize())
    return response




class VenueStatusReport:
    def __init__(self, vr, status):
        self.vr = vr
        self.status = status

    def short_name(self):
        if self.status:
            return self.status.short_desc
        else:
            return 'No Information'

    def rsvps(self):
        if self.any_response():
            return self.vr.venue.rsvp_set.filter(status=self.status)
        else:
            return Guest.objects.exclude(rsvp__venue=self.vr.venue)

    def any_response(self):
        return self.status is not None

    def current_ev(self):
        if self.any_response():
            return sum(rsvp.guest.venue_likelihood(self.vr.venue)
                       for rsvp in self.rsvps())
        else:
            return self.initial_ev()

    def initial_ev(self):
        if self.any_response():
            return sum(rsvp.guest.original_venue_ev(self.vr.venue)
                       for rsvp in self.rsvps())
        else:
            return sum(inote.venue_ev(self.vr.venue)
                       for inote in
                       InviteeNotes.objects.exclude(invitee__guest__rsvp__venue=self.vr.venue))
        
        
class VenueReport:
    def __init__(self, site):
        self.venue = Venue.objects.get(site=site)
        self.report_by_status = [VenueStatusReport(self, None),]
        for sv in RSVPOption.objects.all().order_by('likelihood'):
            self.report_by_status.append(VenueStatusReport(self, sv))
        self.no_information = []
        for inote in InviteeNotes.objects.exclude(invitee__guest__rsvp__venue=self.venue, invitee__guest__rsvp__status__isnull=False):
            self.no_information.append({'invitee': inote.invitee.full_name(),
                                        'ev': inote.venue_ev(self.venue) })
        self.viewed_but_blank = []
        self.vbb_found = {}
        for inote in InviteeNotes.objects.filter(invitee__guest__rsvp__venue=self.venue,
                                                 invitee__guest__rsvp__status=None):
            if not self.vbb_found.has_key(inote.invitee):
                self.viewed_but_blank.append({'invitee': inote.invitee.full_name(),
                                              'ev': inote.venue_ev(self.venue) })
                self.vbb_found[inote.invitee] = 1

    def current_estimate(self):
        return sum(g.venue_likelihood(self.venue) for g in Guest.objects.all())
    def initial_estimate(self):
        return sum(inote.venue_ev(self.venue)
                   for inote in InviteeNotes.objects.all())

    def food_report(self):
        food_counts = []
        food_selected = {}
        for r in self.venue.rsvp_set.filter(status__in=RSVPOption.objects.yes()):
            food = "unknown"
            if r.food_selection:
                food = r.food_selection.short_desc
            if not food_selected.has_key(food): food_selected[food] = []
            food_selected[food].append(r.guest)
        for food in sorted(food_selected.keys()):
            food_counts.append({'name': food, 'count': len(food_selected[food])})
        return {'counts': food_counts, 'selected': food_selected }

    def bus_report(self):
        bus_counts = []
        bus_selected = {}
        for r in self.venue.rsvp_set.filter(status__in=RSVPOption.objects.yes()):
            bus = "unknown"
            if r.bus_selection:
                bus = r.bus_selection
            if not bus_selected.has_key(bus): bus_selected[bus] = []
            bus_selected[bus].append(r.guest)
        for bus in sorted(bus_selected.keys()):
            bus_counts.append({'name': bus, 'count': len(bus_selected[bus])})
        return {'counts': bus_counts, 'selected': bus_selected }

    def tables_report(self):
        tables = []
        tindex = {}
        for t in Table.objects.filter(venue=self.venue).order_by("number"):
            ti = { 'name': t.name, 'number': t.number, 'rsvps': [], 'foodcounts': {} }
            tindex[t] = ti
            tables.append(ti)
            #print ti
        for r in self.venue.rsvp_set.filter(status__in=RSVPOption.objects.yes()).order_by("food_selection","guest__last_name"):
            if r.table_assign:
                ti = tindex[r.table_assign]
                ti['rsvps'].append(r)
                food = r.food_selection.food_name()
                if not food: food = "undecided"
                if ti['foodcounts'].has_key(food):
                    ti['foodcounts'][food] += 1
                else:
                    ti['foodcounts'][food] = 1        
        for ti in tables:
            f = ""
            for k in sorted(ti['foodcounts'].keys()):
                f += "%s: %s<br/>"%(k,ti['foodcounts'][k])
            ti['food'] = f

        return tables


@login_required
def tools_guest_count(request, filter=None, template=None, venue_site=None):
    if request.user.is_staff or request.user.username in users_with_rsvp_view_perms:
        pass
    else:
        return HttpResponseRedirect('/admin/')        

    venues = []
    if venue_site:
        venues = [VenueReport(venue_site),]
    else:
        venues = [VenueReport(v.site) for v in Venue.objects.all()]

    return render_to_response(template, {
        'invitees': Invitee.objects.all().order_by('last_updated','last_visited').reverse(),
        'venue_reports': venues,
        'guests': Guest.objects.all(),
        'rsvps': RSVP.objects.all(),
        'user': request.user },
        context_instance=RequestContext(request))

@login_required
def make_labels(request, filter=None):
    if not request.user.is_staff: return HttpResponseRedirect('/admin/')
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=mailing-labels.pdf'
    labels = LabelMaker(LabelSpecBasic)
    inv_set = guest_filter.all_invitees()
    if filter == 'std':
        inv_set = guest_filter.savedate_invitees()
    for inv in inv_set:
        if inv.full_address:
            text = inv.full_name_couple()+u'\n'+inv.full_address
            labels.add_label(text)
    response.write(labels.finish())
    return response


@login_required
def make_svg(request, filter=None, n_up=4, template=None, venue_site=None, format="ps", orient="portrait"):
    if not request.user.is_staff: return HttpResponseRedirect('/admin/')
    if not filter: filter="all"

    if format == "pdf":
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=results-%s.pdf'%(filter,)
        svg2pdf = SVG2PDF(pdf_mode=True, orient=orient)
    else:
        response = HttpResponse(mimetype='application/postscript')
        response['Content-Disposition'] = 'attachment; filename=results-%s.ps'%(filter,)
        svg2pdf = SVG2PDF(orient=orient)

    inv_set = guest_filter.all_invitees()
    if filter == 'std':
        inv_set = guest_filter.savedate_invitees()
    elif filter == 'non-ru':
        inv_set = guest_filter.non_ru_invitees()
    elif filter == 'ru':
        inv_set = guest_filter.ru_invitees()
    elif filter == 'test':
        inv_set = guest_filter.test_invitees()
    elif filter == 'rsvp_yes':
        rsvps = RSVP.objects.filter(venue=venue_site, status__in=RSVPOption.objects.yes()).order_by('guest__last_name','guest__first_name')
        inv_set = []
        for r in rsvps:
            inv_set.append(r)

    for spos in range(0,len(inv_set),n_up):
    #for spos in range(0,10,n_up):
        inv_group = [None,]
        for invitee in inv_set[spos:spos+4]:
            inv_group.append(invitee)        
        svg2pdf.add_svg(loader.render_to_string(template, { 'inv': inv_group, }))
    response.write(svg2pdf.finish())
    return response


