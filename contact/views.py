import datetime
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from contact.forms import ContactForm
from contact.models import ContactLead
from utility import set_detail_context


def view_contact(request, page=None):
    message = False

    if request.method == 'POST':
        contact_form = ContactForm(data=request.POST)

        if contact_form.is_valid():
            cleaned_data = contact_form.cleaned_data

            lead = ContactLead()
            lead.first_name = request.user.first_name
            lead.last_name = request.user.last_name
            lead.email = cleaned_data['email']
            lead.phone = cleaned_data['phone']
            lead.preferred_method = cleaned_data['preferred_method']
            lead.message = cleaned_data['message']
            lead.date = datetime.datetime.now()
            lead.neighbor = request.user.neighbor
            lead.community = request.user.neighbor.community
            lead.save()

            # SEND EMAIL
            email_context = {'contactLead': lead}

            subject, from_email, to_email = 'New Contact Lead', settings.DEFAULT_FROM_EMAIL, [settings.ONLINE_CONTACT_EMAIL]
            text_content = render_to_string("email/contact/new_contact_lead_string.html", email_context)
            html_content = render_to_string("email/contact/new_contact_lead_html.html", email_context)
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            message = True

    else:
        contact_form = ContactForm(initial={'email': request.user.email, 'phone': request.user.neighbor.phone})

    context = {'contact_form': contact_form, 'message': message}
    if page:
        context['page'] = page
    set_detail_context(request, context)

    return render_to_response('contact/contact.html', context, context_instance=RequestContext(request))