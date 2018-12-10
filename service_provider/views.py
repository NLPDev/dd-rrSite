import json, math
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from service_provider.models import ServiceProvider, ServiceType
from django.contrib.auth.decorators import login_required
from utility import set_detail_context, send_admin_notification
from service_provider.forms import ServiceProviderForm
from page_content.models import ModalSuccess


def service_providers(request):

	# we want to show half the service providers in the left column, and half in the right column.
	# if uneven, the right column should contain more
	services = ServiceProvider.objects.filter(community=request.user.neighbor.community, is_approved=True).order_by('type', 'sort_order', 'title')
	num_services = services.count()
	mid_point = math.floor(num_services/2)

	left_services = services[0:mid_point]
	right_services = services[mid_point:]

	context = {'left_services': left_services, 'right_services': right_services}
	set_detail_context(request, context)

	return render(request, 'service_provider/service_providers.html', context)


@login_required
def ajax_add_provider(request):

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
		form = ServiceProviderForm(data=formatted_data)
		if form.is_valid():

			instance = form.save(commit=False)
			instance.neighbor = request.user.neighbor
			instance.community = request.user.neighbor.community
			instance.save()

			send_admin_notification('Service Provider Submission', {
                'message': 'A new service provider has been submitted for approval to ' + str(request.user.neighbor.community),
                'url': request.build_absolute_uri(reverse("admin:service_provider_serviceprovider_change", args=(instance.id,)))
            })

			json_data = { 'success': True }
		else:
			form.fields['type'].queryset = ServiceType.objects.filter(community=request.user.neighbor.community)

			json_data = {'success': False, 
			             'errors': json.dumps(form.errors),
						 'form': render_to_string('service_provider/ajax_add_provider.html', {'form': form})
			}

	else:
		form = ServiceProviderForm()
		form.fields['type'].queryset = ServiceType.objects.filter(community=request.user.neighbor.community)
		json_data = {'form': render_to_string('service_provider/ajax_add_provider.html', {'form': form})}

	return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_add_provider_success(request):

	success_content = ModalSuccess.get_content('service_provider', 'Your service has been received', 'Your service has been submitted for review. It will appear after approval.')

	json_data = {'content': render_to_string('service_provider/ajax_add_provider_success.html', {'success_content': success_content}),
	                'title': 'SUCCESS!',
	                'title_position': 'center',
	                'button': 'Continue',
	                'button_position': 'center',
					'text_position': 'center',
	}

	return HttpResponse(json.dumps(json_data), content_type='application/json')
