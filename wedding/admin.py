from django import forms
from djwed.wedding.models import *
from django.contrib import admin



class InviteeNotesInline(admin.TabularInline):
    model = InviteeNotes
    extra = 0

class RSVPInline(admin.TabularInline):
    model = RSVP
    extra = 2

class GuestInline(admin.StackedInline):
    model = Guest
    extra = 1
    inlines = [RSVPInline,]

class FoodOptionInline(admin.StackedInline):
    model = FoodOption
    extra = 3
    
#class CommentInline(admin.StackedInline):
#    model = Comment
#    fk_name = "comment"
    
class InviteeAdmin(admin.ModelAdmin):
    #fieldsets = [
    #    (None,               {'fields': ['question']}),
    #    ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    #]
    inlines = [GuestInline,InviteeNotesInline]
    list_display = ('full_name', 'full_name_override', 'full_address', 'state','country')
    list_editable = ('full_name_override',)
    list_filter = ['side', 'association','country','state']
    search_fields = ['full_name_override','invite_code','guest__first_name', 'guest__last_name', 'guest__nickname']
    #date_hierarchy = 'pub_date'

class LongFoodChoiceField(forms.ModelChoiceField):
    #widget = forms.widgets.RadioSelect()
    def label_from_instance(self, obj):
        return obj.long_desc


class GuestAdmin(admin.ModelAdmin):
    inlines = [RSVPInline,]
    list_display = ('full_name', 'first_name', 'nickname', 'last_name', 'email', 'home_phone', 'cell_phone')
    list_filter = ['role']
    search_fields = ['first_name', 'last_name']
    list_editable = ('first_name', 'last_name', 'email',  'home_phone', 'cell_phone')


class RSVPAdminForm(forms.ModelForm):
    class Meta:   model = RSVP

    def clean(self, *args, **kwargs):
        sret = super(RSVPAdminForm, self).clean(*args,**kwargs)
        if self.cleaned_data['food_selection'] and self.cleaned_data['food_selection'].venue != self.cleaned_data['venue']:
            raise ValidationError('Food selected from another venue')
        if self.cleaned_data['venue'].site != u'MA' and self.cleaned_data['bus_selection']:
            raise ValidationError('Bus selection for a site with no bus')
        rsvp_filter = RSVP.objects.filter(venue = self.cleaned_data['venue'],
                                          guest = self.cleaned_data['guest'])
        if rsvp_filter.count()>1 or (rsvp_filter.count() == 1
                                     and rsvp_filter.all()[0] != self.instance):
            raise ValidationError('Only one RSVP allowed per person')            
        return sret

    
class RSVPAdmin(admin.ModelAdmin):
    #inlines = [GuestInline,]
    #food_selection = LongFoodChoiceField([], required=False, empty_label = "--- Please choose from a dinner selection below ---")    
    list_display = (
            'guest_site',
            'venue',
            'status',
            'food_selection',
            'bus_selection',
            'last_updated',
            'prelim',
            'guest_invitee',
            'last_update_source',
            'guest',
            'table_assign',
            )
    search_fields = [
            'guest__first_name',
            'guest__last_name',
            'guest__invitee__guest__last_name',
            'guest__invitee__invite_code',
            ]
    list_editable = (
            'status',
            'food_selection',
            'bus_selection',
            'prelim',
            'last_update_source',
            'table_assign'
            )
    form = RSVPAdminForm
    list_filter = ('venue','status')

    def guest_site(self,rsvp):
        return u"%s (%s)"%(rsvp.guest.full_name(), unicode(rsvp.venue.site))
    guest_site.short_description = "Guest (Site)"

    def guest_invitee(self,rsvp):
        return rsvp.guest.invitee
    guest_invitee.short_description = "Invitee"

    def guest_invitee_association(self,rsvp):
        return rsvp.guest.invitee.association
    guest_invitee_association.short_description = "Association"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "guest":
            kwargs["queryset"] = Guest.objects.all().order_by('last_name','first_name')
            return db_field.formfield(**kwargs)
        return super(RSVPAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class InviteeNotesAdmin(admin.ModelAdmin):
    search_fields = ['invitee__guest__first_name',
                     'invitee__guest__last_name','invitee__guest__nickname']
    list_display = [ 'invitee',
                     'likely_site',
                     'ma_likelihood',
                     'ca_likelihood',
                     'or_likelihood',
                     'invitee_rsvp_count',
                     'adults',
                     'children',
                     'invitee_country',
                     ]
    list_editable = ['ma_likelihood',
                     'ca_likelihood',
                    ]

    def invitee_rsvp_count(self,inote):
        return str(inote.invitee.rsvp_yes_counts())
    invitee_rsvp_count.short_description = "RSVP Yes"

    def invitee_country(self,inote):
        return str(inote.invitee.country)
    invitee_country.short_description = "Country"



class CommentAdmin(admin.ModelAdmin):
    list_filter = ['type']
    search_fields = ['invitee__guest__first_name','text',
                     'invitee__guest__last_name','invitee__guest__nickname']
    list_display = ['id','invitee','type','last_updated','text']

class VenueAdmin(admin.ModelAdmin):
    inlines = [FoodOptionInline,]

class PageSnippetAdmin(admin.ModelAdmin):
    list_display = ['key','title','last_updated']


class GiftAdmin(admin.ModelAdmin):
    search_fields = ['source__guest__first_name','notes','description','source__guest__last_name',
                     'source__guest__nickname','notes','description']
    list_filter = ['status','registry','assignment','registry']
    list_display = ['source','received','description','notes',
                    'assignment','registry','status','thank_you_sent']
    list_editable = ('status', 'registry', 'assignment','thank_you_sent') # 'description')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "source" and request.META['REQUEST_METHOD'] != 'POST':
            kwargs["queryset"] = Invitee.objects.all().order_by('guest__last_name','guest__first_name')
            return db_field.formfield(**kwargs)
        return super(GiftAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TableAdmin(admin.ModelAdmin):
    search_fields = ['rsvp__guest__first_name','name','number','notes',
                     'rsvp__guest__last_name','invitee__guest__nickname']
    list_display = ['number','name','venue','table_count','table_guests','notes','position']
    list_editable = ('name','notes')
    list_filter = ['venue',]

    def table_count(self,table):
        return str(table.rsvp_set.count())
    table_count.short_description = "# people"

    def table_guests(self,table):
        guests = []
        for r in table.rsvp_set.all():
            guests.append(unicode(r.guest))
        guests.sort()
        return u" , \n".join(guests)
    table_count.short_description = "guests"


admin.site.register(Invitee, InviteeAdmin)

admin.site.register(InviteeNotes, InviteeNotesAdmin)

admin.site.register(Guest, GuestAdmin)

admin.site.register(Venue, VenueAdmin)

admin.site.register(PageSnippet, PageSnippetAdmin)

admin.site.register(RSVP, RSVPAdmin)

admin.site.register(Comment, CommentAdmin)

admin.site.register(Gift, GiftAdmin)

admin.site.register(Table, TableAdmin)

