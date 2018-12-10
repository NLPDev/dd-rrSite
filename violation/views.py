from django.core.urlresolvers import reverse
from django.shortcuts import render
import json
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from violation.forms import ViolationForm
from utility import set_detail_context, send_admin_notification
from page_content.models import ModalSuccess
from violation.models import ViolationStep, ViolationFaq, Violation


@login_required
def index(request):

	violation_form = ViolationForm()
	violation_steps = ViolationStep.objects.filter(community=request.user.neighbor.community).order_by('sort_order')
	violation_faqs = ViolationFaq.objects.filter(community=request.user.neighbor.community).order_by('sort_order')

	context = {'violation_form': violation_form, 'violation_steps': violation_steps, 'violation_faqs': violation_faqs}
	set_detail_context(request, context)

	return render(request, 'violation/violations.html', context)


@login_required
def ajax_report(request):

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
		violation_form = ViolationForm(data=formatted_data)
		if violation_form.is_valid():

			violation_instance = violation_form.save(commit=False)
			violation_instance.submitted_by = request.user.neighbor
			if violation_form.cleaned_data['event_start'] == '':
				violation_instance.event_start = None
			if violation_form.cleaned_data['event_end'] == '':
				violation_instance.event_end = None
			violation_instance.save()

			send_admin_notification('Violation Report', {
                'message': 'A new violation has been reported for ' + str(request.user.neighbor.community),
                'url': request.build_absolute_uri(reverse("admin:violation_violationevent_change", args=(violation_instance.id,)))
            })

			json_data = { 'success': True }
		else:
			json_data = {'success': False, 'errors': render_to_string('violation/ajax_report_errors.html', {'errors': violation_form.errors}), 'form': ''}

	else:
		json_data = {'success': False, 'errors': 'Form data missing.', 'form': ''}

	return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_report_success(request):

	success_content = ModalSuccess.get_content('violation', 'Your violation has been reported', 'Your report will be reviewed and acted upon accordingly.')

	json_data = {'content': render_to_string('violation/ajax_report_success.html', {'success_content': success_content}),
	                'title': 'SUCCESS!',
	                'title_position': 'center',
	                'button_position': 'center',
	                'text_position': 'center',
	}

	return HttpResponse(json.dumps(json_data), content_type='application/json')