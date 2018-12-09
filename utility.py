import logging
from django.contrib.sites.models import Site
from django.conf import settings
from datetime import date, time, datetime, timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from navigation.models import PrimaryNavigation, TopperNavigation
from page_content.models import Logo, Footer, WebPage
from neighbor.models import Neighbor


def set_detail_context(request, a_context):
    # CHECK FOR ADMIN USER
    active_user = None
    try:
        if request.user.is_authenticated():
            active_user = request.user

    except Exception, e:
        print e

    a_context['active_user'] = active_user

    # NAV LINKS
    desktop_links = PrimaryNavigation.get_published_objects()[0:5]
    a_context['desktop_links'] = desktop_links

    topper_links = TopperNavigation.get_published_objects()
    a_context['topper_links'] = topper_links

    nav_links = PrimaryNavigation.get_published_objects()
    a_context['nav_links'] = nav_links

    try:
        # GET CURRENT SITE
        current_site = Site.objects.get_current()
    except Exception, e:
        logging.error(e)
        current_site = None

    if current_site:
        try:
            # GET LOGO FOR CURRENT SITE
            logo = Logo.objects.get(site=current_site)
        except Exception, e:
            logging.error(e)
            logo = None
        try:
            # GET FOOTER FOR CURRENT SITE
            footer = Footer.objects.get(site=current_site)
        except Exception, e:
            logging.error(e)
            footer = None
    else:
        logo = None
        footer = None

    a_context['logo'] = logo
    a_context['footer'] = footer

    if 'page' not in a_context:
        # look for an existing system page, or create one
        page_label = request.resolver_match.url_name
        try:
            page = WebPage.objects.filter(
                slug=page_label,
                community=request.user.neighbor.community,
                is_published=True
            )[:1].get()
        except WebPage.DoesNotExist:
            page = WebPage.objects.create(
                slug=page_label,
                community=request.user.neighbor.community,
                image_cover='/media/uploads/cover_images/grass_cover.jpg',
                label=page_label.replace('_', ' ').title(),
                is_published=True
            )
        except Neighbor.DoesNotExist:
            logging.error(
                "Loading page without a community for user %s" % request.user.username
            )
            page = None

        a_context['page'] = page


# ATTN: this is used by multiple forms
#  if a different fidelity is required, consider adding it as a parameter
def get_time_choices():
    times = []
    times.append(['', '---------'])

    time_step = time.min
    while (time_step > time.min or len(times) < 2) and len(times) < 300:
        times.append([time_step, time_step.strftime('%I:%M %p').lstrip('0')])
        dt = datetime.combine(date.today(), time_step) + timedelta(hours=1)
        time_step = dt.time()

    return times

# usage:
# send_admin_notification('Violation Report', {
#     'message': 'A new violation has been reported for ' + str(request.user.neighbor.community),
#     'url': request.build_absolute_uri(reverse("admin:violation_violationevent_change", args=(violation_instance.id,)))
# })
def send_admin_notification(subject, email_context):

    if settings.DISABLE_ADMIN_NOTIFICATION:
        return True

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.EMAILTO,]
    text_content = render_to_string("email/admin_notification_string.html", email_context)
    html_content = render_to_string("email/admin_notification_html.html", email_context)
    msg = EmailMultiAlternatives('Real Clear Communities - ' + subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    return msg.send()