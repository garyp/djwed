
from djwed.wedding.models import *


def savedate_invitees():
    """People to send save-the-dates to.  Excludes people in Russia."""
    return Invitee.objects.all().exclude(country='RU').order_by('-inviteenotes__batch','-country','state','invite_code')

def non_ru_invitees():
    """Excludes people in Russia."""
    return Invitee.objects.all().exclude(country='RU').order_by('-inviteenotes__batch','-country','state','invite_code')

def ru_invitees():
    """Includes only people in Russia."""
    return Invitee.objects.all().filter(country='RU').order_by('-inviteenotes__batch','-country','state','invite_code')

def all_invitees():
    return Invitee.objects.all().order_by('-inviteenotes__batch','-country','state','invite_code')

def all_guests():
    return Guest.objects.all().order_by('last_name','first_name')

def yes_invitees(venue="MA"):
    invitees = []
    for r in RSVP.objects.filter(status="y",venue=venue):
        if r.guest.invitee not in invitees:
            invitees.append(r.guest.invitee)
    return invitees


def test_invitees():
    """A small set of sample invitees."""
    return Invitee.objects.all().filter(state='WI').order_by('-inviteenotes__batch','-country','state','invite_code')

def response_needed_invitees():
    invitees = []
    for inv in Invitee.objects.all():
        if (inv.rsvp_any_unresponded() or inv.rsvp_missing_food_selection()):
            invitees.append(inv)
    return invitees


