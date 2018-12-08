import json
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse, Http404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from announcement.models import Announcement, Tag
from announcement.forms import AnnouncementForm
from page_content.models import ModalSuccess
from utility import set_detail_context, send_admin_notification


@login_required
def announcements(request):
    announcement_list = Announcement.get_published_objects(request.user.neighbor.community)
    tags = Tag.objects.filter(community=request.user.neighbor.community)

    context = {'announcements': announcement_list, 'tags': tags}
    set_detail_context(request, context)

    return render(request, 'announcement/announcements.html', context)


@login_required
def ajax_add_announcement(request):

    if request.method == 'POST' and 'form_data' in request.POST:

        # try to load the submitted form data
        try:
            form_data = json.loads(request.POST['form_data'])
            # format the form data
            formatted_data = {}
            for row in form_data:
                formatted_data[row['name']] = row['value']
        except:
            json_data = {'success': False, 'errors': 'Form data could not be read.', 'form': ''}
            return HttpResponse(json.dumps(json_data), content_type='application/json')

        # validate the form
        form = AnnouncementForm(data=formatted_data, files=request.FILES)
        if form.is_valid():

            instance = form.save(commit=False)
            instance.neighbor = request.user.neighbor
            instance.community = request.user.neighbor.community
            instance.event_date = form.cleaned_data['event_date']
            instance.save()

            send_admin_notification('Announcement Submission', {
                'message': 'A new announcement has been submitted for approval to ' + str(request.user.neighbor.community),
                'url': request.build_absolute_uri(reverse("admin:announcement_announcement_change", args=(instance.id,)))
            })

            json_data = { 'success': True }
        else:
            json_data = {'success': False, 'errors': json.dumps(form.errors), 'datepicker_refill': formatted_data['datepicker_value'], 'form': render_to_string('announcement/ajax_add_announcement.html', {'form': form})}

    else:
        form = AnnouncementForm()
        json_data = {'form': render_to_string('announcement/ajax_add_announcement.html', {'form': form})}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_announcement_success(request):

    # get the most recent event added by this user
    event = Announcement.objects.filter(neighbor=request.user.neighbor).order_by('-pk')[0]

    success_content = ModalSuccess.get_content('announcement', 'Your announcement has been received', 'Your announcement has been submitted for review. It will appear after approval.')

    json_data = {'content': render_to_string('announcement/ajax_announcement_success.html', {'event': event, 'success_content': success_content}),
                    'title': 'SUCCESS!',
                    'title_position': 'center',
                    'button': 'Continue',
                    'button_position': 'center',
                    'text_position': 'center',
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


def announcement_details(request, announcement_id):

    try:
        announcement = Announcement.objects.get(pk=announcement_id)
    except Announcement.DoesNotExist:
        raise Http404

    tags = Tag.objects.filter(community=request.user.neighbor.community)

    context = {'announcement': announcement, 'tags': tags}
    set_detail_context(request, context)

    return render(request, 'announcement/announcement_details.html', context)
