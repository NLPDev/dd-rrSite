import logging
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from community.models import Community
from navigation.models import SubPrimaryNavigation
from page_content.models import WebPage
from utility import set_detail_context


def edit_web_page(request, a_slug):
    edit = True
    return view_web_page(request, a_slug, edit)

# path is the community slug
def view_web_page(request, path, a_slug, edit=None):

    community = Community.objects.get(slug=path)

    try:
        # IF WE ARE IN EDIT MODE, WE NEED TO LOOK FOR ALL PAGES
        # REGARDLESS OF IT'S PUBLISHED STATE
        if edit:
            page = WebPage.objects.get(community=community, id=a_slug)

        else:
            page = WebPage.objects.get(community=community, slug=a_slug, is_published=True)

    except:
        raise Http404

    # GET MATCHING LINK
    page_link, sub_link = get_matching_links(a_slug)

    # CHECK TEMPLATE CHOICE
    template_choice = page.template_choice
    template = get_current_template(template_choice)

    if not template:
        raise Http404

    # CHECK FOR ADD-ON
    template_add_on = page.template_addon

    context = {'page': page, 'page_link': page_link, 'sub_link': sub_link, 'template_add_on': template_add_on}
    set_detail_context(request, context)

    return render_to_response(template, context, context_instance=RequestContext(request))


def get_matching_links(a_slug):
    # TRY TO FIND MATCHING SUB LINK
    try:
        sub_links = SubPrimaryNavigation.objects.filter(page__slug=a_slug)
        if len(sub_links) > 0:
            sub_link = sub_links[0]

        else:
            sub_link = None

    except Exception, e:
        print e
        sub_link = None

    # IF SUB LINK, GET SUB LINKS PARENT
    if sub_link:
        page_link = sub_link.parent

    else:
        page_link = None

    return page_link, sub_link


def get_current_template(template_choice):
    if template_choice == '1_col':
        template = 'detail_pages/1_col.html'

    elif template_choice == '1_col_contact':
        template = 'detail_pages/1_col.html'

    elif template_choice == '2_col':
        template = 'detail_pages/2_col.html'

    elif template_choice == 'landing':
        template = 'detail_pages/landing_page.html'

    else:
        template = None

    return template