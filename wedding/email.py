# Create your views here.

from django.conf import settings
from django.template import Context, loader
from djwed.wedding.models import *
from datetime import datetime
from django.core.mail import send_mail, mail_managers, EmailMessage, EmailMultiAlternatives
import logging
import smtplib

logger = logging.getLogger(__name__)

def email_generic(template, subject, recipients, template_data=None, send=False,
                  html_template=None, attach_file=None):
    """ Sends email to recipient email addresses based on a template. """
    if template_data is None:
        template_data = {}
    body = loader.render_to_string(template, template_data)
    from_email = '%s <%s>' % settings.FROM_EMAIL
    email = EmailMultiAlternatives(subject, body, from_email, recipients, bcc=())
    if html_template:
        html_body = loader.render_to_string(html_template, template_data)
        email.attach_alternative(html_body, "text/html")
    if attach_file:
        email.attach_file(attach_file)
    try:
        if send:
            logger.info("Sending to %s"%(str(recipients,)))
            email.send()
            return email
        else:
            logger.info("Would have sent to %s"%(str(recipients,)))
            return email
    except smtplib.SMTPException, e:
        logger.error("Problem sending email to %s: %s"%(str(recipients),str(e)))

def email_guest(template, subject, guest, send=False, html_template=None, attach_file=None):
    """ Sends email to a guest based on a template. """
    if not guest.email:
        logger.warning("No email address for "+str(guest))
        return
    return email_generic(template, subject, [guest.email], { 'guest': guest }, send,
                         html_template, attach_file)

def email_invitee(template, subject, invitee, send=False, html_template=None, attach_file=None):
    """ Sends email to an invitee based on a template. """
    recipients = []
    for g in invitee.guest_set.all():
        if g.email and g.email not in recipients:
            recipients.append(g.email)
    if not recipients:
        logger.warning("No email addresses for guests of "+str(invitee))
        return
    return email_generic(template, subject, recipients, { 'invitee': invitee }, send,
                         html_template, attach_file)

def select_invitees(recipient):
    if recipient is None:
        recipient = settings.FROM_EMAIL[1]
    invitees = []    
    #if test_to == "us":
    #    invitees = Invitee.objects.filter(invite_code="555-555")
    #elif test_to == "parents":
    #    invitees = Invitee.objects.filter(invite_code="555-555")
    if recipient == "all":
        invitees = Invitee.objects.all()
    elif recipient == "unresponded":
        for inv in Invitee.objects.all():
            if (inv.rsvp_any_unresponded() or inv.rsvp_missing_food_selection()) and inv.country != u'RU':
                invitees.append(Invitee.objects.filter(guest__email=recipient))
    elif isinstance(recipient, basestring):
        invitees = Invitee.objects.filter(guest__email=recipient)
    else:
        try:
            for r in recipient:
                if isinstance(r, Invitee):
                    invitees.append(r)
                else:
                    invitees.append(Invitee.objects.filter(guest__email=r))
        except TypeError: # recipient was not a sequence
            pass

    return invitees


def email_all_invitees(template, subject, send=False):
    return [ email_invitee(template, subject, inv, send=send)
             for inv in Invitee.objects.all() ]


def email_save_the_date(send=False, recipient=None):
    return email_with_template(send,
                               select_invitees(recipient),
                               template_prefix="email_save_the_date",
                               subject=("""Save the Date for %s's Wedding!"""
                                        % settings.WEDDING_NAMES)
                               )


def email_website_update_1(send=False, recipient=None):
    invitees = select_invitees(recipient)
    return email_with_template(send, invitees, template_prefix="email_website_update",
                               subject="""Updates on Our upcoming wedding and receptions""")

def email_invite_code(guest):
    return email_guest("email_invite_code.txt",
                       "Your invite code for %s's wedding website" % settings.WEDDING_NAMES,
                       guest,
                       send=settings.SEND_EMAIL,
                       html_template="email_invite_code.html",
                       )

def email_with_template(send=False, invitees=None, template_prefix="",
                        subject="Updates for our upcoming wedding and receptions"):
    if invitees is None: return
    sent = []
    for inv in invitees:
        print inv
        email = email_invitee(template_prefix+".txt",
                              subject,
                              inv,
                              send=send,
                              html_template=template_prefix+".html",
                              #attach_file="media/save-the-date.png"
                              )
        sent.append((inv, email))
    return sent

