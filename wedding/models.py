from django.db import models
from django.core.exceptions import ValidationError,ObjectDoesNotExist
import datetime
from django.contrib.auth.models import User, check_password
from djwed.wedding.settings import *

class PageSnippet(models.Model):
    key = models.CharField(max_length=30, primary_key=True)
    title = models.CharField("Page header/title", max_length=100, blank=True, null=True)
    html = models.TextField("HTML Content")
    last_updated = models.DateTimeField(auto_now=True, null=True)
    def __unicode__(self):
        return u"%s: <h2>%s</h2>\n\n%s"%(self.key, self.title, self.html)

class Venue(models.Model):
    site = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    when_date = models.DateField()    
    url = models.URLField()
    html = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s (%s)"%(self.site,self.name)


class Invitee(models.Model):
    ASSOCIATION_CHOICES = (
        (u'coworker', u'Coworker'),
        (u'family', u'Family'),
        (u'family friend', u'Family friend'),
        (u'former coworker', u'Former coworker'),
        (u'friend', u'Friend'),
        (u'relative', u'Relative'),
        (u'parent', u'Parent'),
        (u'neighbor', u'Neighbor'),
        (u'rabbi', u'Rabbi'),
        (u'vendor', u'Vendor'),
        (u'other', u'Other'),
        (u'self', u'Bride or Groom'))        
    SIDE_CHOICES = (
        (u'A', u'Alyssa'),
        (u'J', u'Both/Joint'),
        (u'B', u'Ben'),
        )    
    full_name_override = models.CharField("Alternate name on invitation", max_length=100, blank=True, null=True)
    invite_code = models.SlugField(max_length=20, unique=True)
    association = models.CharField(max_length=20, choices=ASSOCIATION_CHOICES, blank=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    state = models.CharField(max_length=2, blank=True)
    country = models.CharField(max_length=2)
    full_address = models.TextField()
    private_notes = models.TextField(blank=True, null=True)
    limited_venue = models.ForeignKey(Venue, null=True, blank=True, verbose_name="Strongly preferred venue")  
    last_updated = models.DateTimeField("Last update on site", auto_now=True)
    last_visited = models.DateTimeField("Last site visitation", null=True, blank=True)

    def ordered_guests(self):
        return self.guest_set.order_by("order")

    def shared_last_name(self):
        """ Returns a shared last name or None """
        return reduce(lambda x,y: x if x==y else None,
                      map(lambda x: x.last_name, self.guest_set.all()))

    def mark_visited(self):
        self.last_visited = datetime.datetime.now()
        self.save()

    def mark_updated(self):
        self.last_updated = datetime.datetime.now()
        self.save()

    def full_name(self):
        if self.full_name_override:
            return self.full_name_override
        if self.guest_set.all():
            sln = self.shared_last_name()
            if sln:
                return u' and '.join(map(lambda x: x.first_name, self.ordered_guests()))+u" "+unicode(sln)
            else:
                return u' and '.join(map(lambda x: x.__unicode__(), self.ordered_guests()))
        else:
            return self.invite_code
    full_name.short_description = "Full names of guests"

    def full_name_couple(self):
        """ Returns just the first two full names. """
        if self.full_name_override:
            return self.full_name_override
        if self.guest_set.all():
            sln = self.shared_last_name()
            if sln:
                return u' and '.join(map(lambda x: x.first_name, self.ordered_guests()[:2]))+u" "+unicode(sln)
            else:
                return u' and '.join(map(lambda x: x.__unicode__(), self.ordered_guests()[:2]))
        else:
            return self.invite_code
    full_name_couple.short_description = "Full names of guests"

    def first_names_children(self):
        """ Returns the subsequent names after the first. """
        if self.guest_set.all().count() > 2:
            return u' and '.join(map(lambda x: x.first_name, self.ordered_guests()[2:]))
        else:
            return u""
    full_name_couple.short_description = "Full names of children"

    def first_names(self):
        if self.guest_set.all():
            guests = list(self.ordered_guests())
            if len(guests) == 1:
                return guests[0].first_name
            elif len(guests) == 2:
                return guests[0].first_name+u" and "+guests[1].first_name
            else:
                return u', '.join(map(lambda x: x.first_name, guests[:-1]))+u", and "+guests[-1].first_name
    first_names.short_description = "First names of guests"

    # Attendance summary
    def rsvp_yes_counts(self):
        venue_counts = { 'MA': 0,  'CA': 0 }
        for g in self.guest_set.all():
            for r in g.rsvp_set.all():
                if r.status == u'y':
                    venue_counts[r.venue.site] += 1
        return venue_counts

    def rsvp_any_unresponded(self):
        any = False
        for g in self.guest_set.all():
            if g.rsvp_set.count() == 0:
                any = True
            for r in g.rsvp_set.all():
                if not r.status or r.status == u"m" or r.status == u"-":
                    any = True
        return any        

    def rsvp_yes_text(self):
        vc = self.rsvp_yes_counts()
        ma = vc[u'MA']
        ca = vc[u'CA']
        if not ma and not ca:
            return "You have not yet RSVPed as planning to attend."
        ca_str = ma_str = ""
        if ma > 0:
            ma_str = "<b>%d %s</b> attending in Massachusetts"%(ma, "people" if ma>1 else "person")
        if ca > 0:
            ca_str = "<b>%d %s</b> attending in California"%(ca, "people" if ca>1 else "person")
        return "You are currently RSVPed as %s%s%s."%(ma_str, " and " if ca>0 and ma>0 else "", ca_str)

    def rsvp_missing_food_selection(self):
        missing = False
        for g in self.guest_set.all():
            for r in g.rsvp_set.all():
                if (r.status == u'y' or r.status == u'm') and not r.food_selection:
                    missing = True
        return missing
        
            
    def limited_venue_ma(self):
        return self.limited_venue and self.limited_venue.site == u'MA'
    def limited_venue_ca(self):
        return self.limited_venue and self.limited_venue.site == u'CA'

    def location(self):
        if self.state:
            return u"%s, %s"%(self.state,self.country)
        else:
            return country
    location_property = location

    def user_id(self):
        return username_prefix+unicode(self.id)

    def user(self):
        """ Users are automatically created as needed. """
        try:
             u = User.objects.get(username=self.user_id())
        except User.DoesNotExist:
             u = User(username=self.user_id(), password='*NOT*VALID*FOR*LOGIN*')
             u.save()
        return u

    def __unicode__(self):
        return self.full_name()


class InviteeNotes(models.Model):
    invitee = models.ForeignKey(Invitee)
    likely_site = models.CharField(max_length=50, blank=True, null=True)
    savedate = models.CharField(max_length=1, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)
    adults = models.DecimalField(max_digits=2, decimal_places=1)
    children = models.DecimalField(max_digits=2, decimal_places=1)
    ma_likelihood = models.PositiveIntegerField()
    ca_likelihood = models.PositiveIntegerField()
    def ma_ev(self):
        return (self.ma_likelihood/100.)*float(self.adults)
    def ca_ev(self):
        return (self.ca_likelihood/100.)*float(self.adults)
    def __unicode__(self):
        return u'Notes for '+self.invitee.__unicode__()

    def venue_ev(self, venue):
        if venue.site == "MA":
            return self.ma_ev()
        elif venue.site == "CA":
            return self.ca_ev()
        else:
            raise Exception("No such venue")        

    def normalized_ev(self, venue):
        """ Expected attendance for each guest. """
        return self.venue_ev(venue)/float(self.adults)


class Guest(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    order = models.IntegerField()
    nickname = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    invitee = models.ForeignKey(Invitee)
    role = models.CharField(max_length=20, blank=True)
    home_phone = models.CharField(max_length=50, blank=True, null=True)
    cell_phone = models.CharField(max_length=50, blank=True, null=True)

    def full_name(self):
        if self.nickname:
            return u'%s (%s) %s'%(self.first_name, self.nickname, self.last_name)
        else:
            return u'%s %s'%(self.first_name, self.last_name)
    full_name.short_description = "Full name with nickname"

    def first_last_name(self):
        return u'%s %s'%(self.first_name, self.last_name)
    first_last_name.short_description = "Full name without nickname"

    def invitee_full_name(self):
        return self.invitee.full_name()

    def __unicode__(self):
        return u'%s %s'%(self.first_name, self.last_name)

    def original_venue_ev(self, venue):
        try:
            inotes = self.invitee.inviteenotes_set.get()
            return inotes.normalized_ev(venue)
        except InviteeNotes.DoesNotExist:
            return 0.0

    def venue_likelihood(self, venue):
        rsvps = RSVP.objects.filter(venue=venue, guest=self)
        if len(rsvps) >= 1:
            try:
                return rsvps[0].likelihood()
            except NoRSVPInfo:
                return self.original_venue_ev(venue)
        else:
            return self.original_venue_ev(venue)

    def get_or_create_rsvps(self):
        """ Creates RSVP objects associated with the guest and all venues
        which don't yet have RSVP objects, except in the case of limited_venue.
        Returns a list of the RSVPs (including previously existing ones).
        """
        rsvps = []
        if self.invitee.limited_venue:
            venues = (self.invitee.limited_venue,)
        else:
            venues = Venue.objects.all()
        for v in venues:
            (r,created) = self.rsvp_set.get_or_create(venue=v)
            if created:
                r.prelim = True
                r.status = '-'
                r.save()
            rsvps.append(r)
        return rsvps

class Table(models.Model):
    name = models.CharField(max_length=50)
    number  = models.PositiveIntegerField()
    venue = models.ForeignKey(Venue)
    position = models.CharField(max_length=50,null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return u"%s: %s (%s)"%(self.venue.site, self.number,self.name)

class FoodOption(models.Model):
    short_desc = models.CharField(max_length=10)
    long_desc  = models.CharField(max_length=300)
    venue = models.ForeignKey(Venue)
    def food_name(self):
        return self.short_desc.split(u":")[1]
    def __unicode__(self):
        return self.short_desc

class NoRSVPInfo(Exception): pass

class RSVP(models.Model):
    STATUS_CHOICES = (
        (u'y', u'Yes'),
        (u'n', u'No: Decline'),
        (u'o', u'No: Other Site'),
        (u'm', u'Maybe'),
        (u'v', u'Maybe: Need Visa'),
        )
    status_long_names = (
        (u'-', u'-- Please indicate whether you will be attending --'),
        (u'y', u'Yes: Attending with pleasure'),
        (u'n', u'No: Decline with regret'),
        (u'o', u'No: Will not be attending at this location as the other is more convenient'),
        (u'm', u'Maybe: Undecided at this time'),
        (u'v', u'Maybe: Would love to attend and plan to apply for US travel visa'),
        )

    status_summary_names = {
        u'y': u'Yes',
        u'n': u'No',
        u'v': u'Needs Visa',
        u'm': u'Maybe',
        u'o': u'No (Other)',
        u'-': u'Viewed but Blank',
        u'--': u'No Information',
        }

    BUS_CHOICES = (
        (u'none', u'None requested'),
        (u'both', u'Both directions'),
        (u'to', u'TO Salem'),
        (u'from', u'FROM Salem')
        )        
    bus_choice_long_names = (
        (u'none', u'No shuttle service requested'),
        (u'both', u'Shuttle requested both to and from Salem'),
        (u'to', u'Shuttle requested ONLY TO Salem from Kendall Sq, departing at 4:45 p.m.'),
        (u'from', u'Shuttle requested ONLY FROM Salem to Kendall Sq')
        )        

    SOURCE_CHOICES = (
        (u'web',   u'Online'),
        (u'email', u'Email to us'),
        (u'card',  u'Mailed response card'),
        (u'other', u'Other')
        )        


    unique_together = ("guest","venue")
    guest = models.ForeignKey(Guest)
    venue = models.ForeignKey(Venue)
    prelim = models.BooleanField("Preliminary")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    # Will eventually have food and other choices as well
    food_selection = models.ForeignKey(FoodOption, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_update_source = models.CharField(max_length=8, choices=SOURCE_CHOICES, null=True, blank=True)
    bus_selection = models.CharField(max_length=4, choices=BUS_CHOICES, null=True, blank=True)
    table_assign = models.ForeignKey(Table, null=True, blank=True)

    def __unicode__(self):
        return u"%s: '%s' at %s"%(self.guest,self.status,self.venue)

    def clean(self):
        #print "DEBUG: (%s,%s)"%(str(self.food_selection),str(self.venue))
        #print RSVP.objects.filter(venue=self.venue, guest=self.guest).count()
        if self.food_selection and self.food_selection.venue != self.venue:
            raise ValidationError('Food selected from another venue')
        if self.status in (u'u',u'n'):
            raise ValidationError('Food option selected but not attending')
        if self.bus_selection and self.venue.site != u"MA":
            raise ValidationError('Bus selection for a site with no bus')        
        #try:
        #    rsvp = RSVP.objects.get(venue=self.venue, guest=self.guest)
        #    if rsvp != self:
        #        raise ValidationError('Duplicate RSVP may not exist!')                
        #    if RSVP.objects.filter(venue=self.venue, guest=self.guest).count() > 1:
        #        raise ValidationError('Duplicate RSVP may not exist!')
        #except ObjectDoesNotExist: pass            
        #return super(RSVP, self).clean(self)

    def responded(self):
        return self.status in (u'y',u'm',u'v',u'n',u'o')

    def yes_or_maybe(self):
        return self.status in (u'y',u'm',u'v')

    def likelihood(self):
        if self.status == u'y':
            return 1.0
        elif self.status == u'm':
            return 0.2
        elif self.status == u'o':
            return 0.0
        elif self.status == u'v':
            return 0.4
        elif self.status == u'n':
            return 0.0
        else:
            raise NoRSVPInfo("No RSVP info for guest")

    def food_restrictions(self):
        return self.comment_set.filter(type=u"food")

class Comment(models.Model):
    COMMENT_TYPES = (
        (u'general', u'General Comment'),
        (u'rsvp', u'Attendance Likelihood'),
        (u'food', u'Food Restriction or Allergy'),
        )        
    rsvp = models.ForeignKey(RSVP, null=True)
    invitee = models.ForeignKey(Invitee, null=True)
    type = models.CharField(max_length=10, choices=COMMENT_TYPES)
    text = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.text
    def clean(self):
        if not rsvp and not invitee:
            raise ValidationError('Comment must be associated with a rsvp or invitee')


class Gift(models.Model):
    ASSIGNMENT_CHOICES = (
        (u'A', u'Alyssa'),
        (u'B', u'Ben'),
        (u'J', u'Joint'),
        (u'U', u'Unassigned'),
        )
    STATUS_CHOICES = (
        (u'list', u'Ordered'),
        (u'recv', u'Received'),
        (u'written', u'ThankYou written'),
        (u'sent', u'ThankYou sent'),
        )
    REGISTRY_CHOICES = (
        (u'ws',       u'Williams Sonoma'),
        (u'amazon',   u'Amazon'),
        (u'bbb',      u'Bed, Bath, and Beyond'),
        (u'donation', u'Donation'),
        (u'other',    u'Other'),
        (u'creative', u'Creative gift'),
        (u'cash',     u'Cash'),
        (u'check',    u'Check'),
        (u'multiple', u'Multiple'),
        )    
    source = models.ForeignKey(Invitee)
    received = models.DateField()
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,null=True)
    registry = models.CharField(max_length=20, choices=REGISTRY_CHOICES,null=True)
    assignment = models.CharField(max_length=5, choices=ASSIGNMENT_CHOICES,null=True)
    thank_you_sent = models.DateField(null=True,blank=True)
