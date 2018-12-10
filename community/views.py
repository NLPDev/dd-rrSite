import json, datetime, pytz
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.datastructures import MultiValueDictKeyError

from community.models import Community, Document
from neighbor.models import CalendarEvent, EventPhoto
from neighbor.views import neighbor_login
from utility import set_detail_context, send_admin_notification
from community.forms import CalendarEventForm, CalendarEventPhotoForm
from page_content.models import ModalSuccess


@login_required
def index(request, path):
    community = get_object_or_404(Community, slug=path)
    request.session['community'] = community.id

    return neighbor_login(request)


@login_required
def calendar(request):

    # Get upcoming events, closest occurring first.
    calendar = request.user.neighbor.community.calendar
    events = CalendarEvent.objects.filter(calendar=calendar, is_approved=True, is_cancelled=False, start_date__gte=datetime.date.today).order_by('start_date')[:10]

    context = {'events': events}
    set_detail_context(request, context)

    return render(request, 'community/calendar.html', context)


def calendar_update(request):
    if request.POST:
        calendar = request.session['community']
        calendar = Community.objects.get(id=calendar).calendar
        year = request.POST['year']
        month = request.POST['month']

        events = calendar.get_month(month=month, year=year)

        events_json = []
        for event in events:
            events_json.append({'title': event.title, 'start': event.start_date, 'end': event.end_date,
                                'first_name': event.first_name, 'last_name': event.last_name,
                                'phone': event.phone, 'email': event.email, 'location': event.location,
                                'description': event.description})

        # return events_json. Use start/end date.day to populate left side calendar with event visual
        return JsonResponse(events_json, encoder=DjangoJSONEncoder)


@login_required
def ajax_add_calendar_event(request):

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

        event_form = CalendarEventForm(data=formatted_data, files=request.FILES)

        # validate the photos
        photo_i = 0
        more_photos = True
        photo_forms = []
        while more_photos and photo_i < 100:
            try:
                if photo_i == 0:
                    name = 'photo'
                else:
                    name = 'photo' + str(photo_i + 1)

                photo_forms.append(CalendarEventPhotoForm(data={}, files={'photo': request.FILES[name]}))
                if not photo_forms[photo_i].is_valid():
                    json_data = {'success': False, 'errors': json.dumps({'photo':photo_forms[photo_i].errors}), 'datepicker_refill': formatted_data['datepicker_value'], 'form': render_to_string('community/ajax_add_calendar_event.html', {'calendar_event_form': event_form, 'event_photo_form': photo_forms[photo_i]})}
                    return HttpResponse(json.dumps(json_data), content_type='application/json')

                photo_i += 1
            except MultiValueDictKeyError:
                more_photos = False

        # validate the primary form
        if event_form.is_valid():

            event_instance = event_form.save(commit=False)
            event_instance.neighbor = request.user.neighbor
            event_instance.save()

            if len(photo_forms) > 0:
                for photo_form in photo_forms:
                    eventphoto_instance = photo_form.save(commit=False)
                    eventphoto_instance.event = event_instance
                    try:
                        eventphoto_instance.save()
                    except Exception as e:
                        # if we have a file permission error, it will show up here
                        print e

            send_admin_notification('Calendar Event Submission', {
                'message': 'A new calendar event has been submitted for approval to ' + str(request.user.neighbor.community),
                'url': request.build_absolute_uri(reverse("admin:neighbor_calendarevent_change", args=(event_instance.id,)))
            })

            json_data = { 'success': True }
        else:
            json_data = {'success': False, 'errors': json.dumps(event_form.errors), 'datepicker_refill': formatted_data['datepicker_value'], 'form': render_to_string('community/ajax_add_calendar_event.html', {'calendar_event_form': event_form})}

    else:
        event_form = CalendarEventForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'phone': request.user.neighbor.phone, 'email': request.user.email})
        json_data = {'form': render_to_string('community/ajax_add_calendar_event.html', {'calendar_event_form': event_form})}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_calendar_event_success(request):

    # get the most recent event added by this user
    event = CalendarEvent.objects.filter(neighbor=request.user.neighbor).order_by('-pk')[0]

    success_content = ModalSuccess.get_content('calendar_event', 'Your event has been received', 'Your calendar event has been submitted for review. It will appear after approval.')

    json_data = {'content': render_to_string('community/ajax_calendar_event_success.html', {'event': event, 'success_content': success_content}),
                    'title': 'SUCCESS!',
                    'title_position': 'center',
                    'button': 'Continue',
                    'button_position': 'center',
                    'text_position': 'center',
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_calendar_items(request, date=None):

    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')

    if date_obj.date() == datetime.date.today():
        date_formatted_long = 'Today'
    else:
        date_formatted_long = date_obj.strftime('%B %Y')

    # lookup all reservations for this day
    calendar = request.user.neighbor.community.calendar
    items = calendar.get_day(date_obj.year, date_obj.month, date_obj.day)

    context = {'date': date_obj, 'items': items, 'date_formatted_long': date_formatted_long}

    return HttpResponse(render_to_string('community/ajax_calendar_items.html', context))


@login_required
def ajax_calendar_days(request):

    dates = []
    site_tz = pytz.timezone(settings.TIME_ZONE)
    try:
        items = request.user.neighbor.community.calendar.events
    except:
        items = []

    for item in items:
        # this takes our dates stored as UTC and converts them to local dates
        corrected_time = item.start_date.astimezone(site_tz).replace(tzinfo=None)

        if not corrected_time.strftime("%Y-%m-%d") in dates:
            dates.append(corrected_time.strftime("%Y-%m-%d"))

    return HttpResponse(json.dumps(dates), content_type='application/json')

def event_details(request, event_id):

    try:
        event = CalendarEvent.objects.get(pk=event_id)
    except CalendarEvent.DoesNotExist:
        raise Http404

    photos = event.get_photoset()

    context = {'event': event, 'photos': photos}
    set_detail_context(request, context)

    return render(request, 'community/event_details.html', context)

def resources(request):

    context = {}
    set_detail_context(request, context)

    return render(request, 'community/resources.html', context)

def documents(request):

    documents = Document.objects.filter(community=request.user.neighbor.community).order_by('title')

    context = {'documents': documents}
    set_detail_context(request, context)

    return render(request, 'community/documents.html', context)

@staff_member_required
def admin_edit(request, community_id):

    community = get_object_or_404(Community, id=community_id)
    # simply change the admin's community to the requested one, then show them the homepage for that community
    request.user.neighbor.community = community
    request.user.neighbor.save()

    return redirect(reverse('home'))