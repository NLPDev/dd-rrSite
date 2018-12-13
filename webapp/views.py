import logging
from django.shortcuts import render_to_response
from django.template import RequestContext
from utility import set_detail_context
from django.contrib.auth.decorators import login_required
from page_content.models import Billboard, MiniBillboard
from announcement.models import Announcement

@login_required
def view_home(request):
    community = request.user.neighbor.community

    try:
        billboards = Billboard.get_published_objects(community)
    except Exception, e:
        logging.error(e)
        billboards = None

    try:
        mini_billboards = MiniBillboard.get_published_objects(community)
    except Exception, e:
        logging.error(e)
        mini_billboards = None

    try:
        announcements = Announcement.get_published_objects(community)
    except Exception, e:
        logging.error(e)
        announcements = None

    context = {
        'billboards': billboards,
        'mini_billboards': mini_billboards,
        'announcements': announcements
    }
    set_detail_context(request, context)

    template = 'home.html'

    return render_to_response(
        template, context, context_instance=RequestContext(request)
    )