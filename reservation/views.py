import json, datetime
from decimal import Decimal
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from page_content.models import ModalSuccess
from reservation.models import ReserveBlock, ReservableServices
from reservation.forms import ReservationForm, RelatedServicesForm, ReservationPaymentsForm, get_available_times, \
    SelectWithDisabled
from neighbor.models import Transactions
from django.contrib.auth.decorators import login_required
from utility import set_detail_context


@login_required
def reserve_service(request):
    reserveForm = ReservationForm()
    community = request.user.neighbor.community
    services = community.reservableservices_set.all()

    if request.POST:
        new_block = ReserveBlock()
        reserveForm = ReservationForm(request.POST, instance=new_block)

        if reserveForm.is_valid():
            reserveForm.save()

    context = {'reserveForm': reserveForm, 'community': community, 'services': services, 'neighbor': request.user.neighbor}

    return render(request, 'reservation/reserve.html', context)


@login_required
def common_areas(request):

    reservable_services = ReservableServices.objects.filter(community=request.user.neighbor.community).order_by('title')



    context = {'common_areas': reservable_services}
    set_detail_context(request, context)

    return render(request, 'reservation/common_areas.html', context)

@login_required
def ajax_reservation_payment(request):

    if 'service_id' in request.session:
        if len(request.session['service_id']) > 0:
            # Get total amount for each service. Append block id's to a list to mark_paid when payment is accepted.
            amount = Decimal('0.00')
            block_list = []
            for service, block in request.session['service_id']:
                service = ReservableServices.objects.get(id=service)
                amount += service.fee

                block_list.append(ReserveBlock.objects.get(id=block))

        else:
            # Skip this step as nothing has a fee associated with it.

            try:
                del request.session['reservation_total']
            except KeyError:
                pass

            json_data = { 'skip_step': True }
            return HttpResponse(json.dumps(json_data), content_type='application/json')

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

        payments_form = ReservationPaymentsForm(data=formatted_data)

        if payments_form.is_valid():
            cleaned_data = payments_form.cleaned_data

            # Transactions model actually handles the payment process, this code is for
            # instantiating needed variables.
            currency = 'usd'
            metadata = {'email': request.user.email}
            description = 'Reservation made by ' + str(request.user.neighbor)

            # Set up card info from form.
            # Reminder: Add form field for selecting saved card(s). If none are picked, go ahead with entered card info.
            card = {'name': cleaned_data['name_on_card'], 'number': cleaned_data['card_number'],
                    'exp_month': cleaned_data['exp_date'].month, 'exp_year': cleaned_data['exp_date'].year,
                    'cvc': cleaned_data['security_code']
            }

            # Stripe uses cents instead of dollars. Convert so stripe knows what we mean.
            stripe_amount = int(amount * 100)

            # Create a new transaction instance, and set up needed variables.
            transaction = Transactions()
            transaction.wallet = request.user.neighbor.wallet
            transaction.title = description
            transaction.transaction_type = 'R'
            transaction.amount = amount

            # Transactions have stripe functions. This means that Transaction instances needs to
            # know certain things, like the amount, (currency is not needed as we will always use USD.), card info, etc.
            # metadata is used for easier tracking (by email), instead of by stripe_id, as an email is always going to be
            # more memorable than randomly generated strings.
            # description and statement_descriptor show up on the receipt and neighbor bank provided transaction history,
            # respectively. Make sure these are always relevant to the site/type of payment.
            keys = request.user.neighbor.community.keys
            response = transaction.stripe(amount=stripe_amount, currency=currency, card=card, metadata=metadata, description=description, keys=keys)

            # always save the declined transaction so that we have record of it
            transaction.save()

            # Response returns with either True meaning that the payment was successful, in which case, go ahead and do
            # further processing. If it returns with anything else, it will be the stripe provided error message. Return
            # this using the new django 1.7 Form.add_error() method, which can be done completely outside of the form.
            # Like here, for instance.
            if response != True:
                payments_form.add_error('card_number', response)
                json_data = {'success': False, 'errors': json.dumps(payments_form.errors), 'form': render_to_string('reservation/ajax_payment.html', {'payments_form': payments_form, 'amount': amount})}
            else:
                # After the transaction is saved, a bunch of stripe metadata is saved to the transaction as well. Specifically,
                # we want to check and see if stripe reported the transaction as 'paid' or not. We handle any errors in the save
                # function of the txcn instance.
                if transaction.stripe_paid:
                    for payment in block_list:
                        payment.mark_paid(transaction)

                    try:
                        del request.session['service_id']
                    except KeyError:
                        pass

                    # used for display purposes only
                    request.session['reservation_total'] = str(amount)

                    json_data = { 'success': True }
                else:
                    payments_form.add_error('card_number', 'Transaction not paid.')
                    json_data = {'success': False, 'errors': json.dumps(payments_form.errors), 'form': render_to_string('reservation/ajax_payment.html', {'payments_form': payments_form, 'amount': amount})}

            # =====================================================================

        else:
            json_data = {'success': False, 'errors': json.dumps(payments_form.errors), 'form': render_to_string('reservation/ajax_payment.html', {'payments_form': payments_form})}

    else:
        payments_form = ReservationPaymentsForm()
        json_data = {'form': render_to_string('reservation/ajax_payment.html', {'payments_form': payments_form, 'amount': amount})}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_related_services(request, common_area_id=None):

    assert common_area_id is not None

    try:
        service = ReservableServices.objects.get(pk=common_area_id)
    except ReservableServices.DoesNotExist:
        raise Http404

    # if they previously chose a related service, but closed the modal before completing,
    # then we need to clear out the session data
    try:
        del request.session['reservation_related_services']
    except KeyError:
        pass

    if service.related_service.all():

        if request.method == 'POST' and 'form_data' in request.POST:

            # try to load the submitted form data
            try:
                form_data = json.loads(request.POST['form_data'])
                # format the form data
                formatted_data = {}
                formatted_data['related_service_choices'] = []
                for row in form_data:
                    if row['name'] == 'related_service_choices':
                        formatted_data['related_service_choices'].append(row['value'])
                    else:
                        formatted_data[row['name']] = row['value']
            except:
                json_data = {'success': False, 'errors': 'Form data could not be read.', 'form': ''}
                return HttpResponse(json.dumps(json_data), content_type='application/json')

            # validate the form
            related_services_form = RelatedServicesForm(base_service=service, data=formatted_data)
            if related_services_form.is_valid():
                # save related services they'd also like to reserve to the session. this is a list of ReservableServices primary keys
                request.session['reservation_related_services'] = formatted_data['related_service_choices']
                json_data = { 'success': True }
            else:
                json_data = {'success': False, 'errors': json.dumps(related_services_form.errors), 'form': render_to_string('reservation/ajax_related_services.html', {'related_services_form': related_services_form})}

        else:
            related_services_form = RelatedServicesForm(base_service=service)
            json_data = {'form': render_to_string('reservation/ajax_related_services.html', {'related_services_form': related_services_form})}
    else:
        json_data = {'skip_step':True}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_reservation_form(request, common_area_id=None):

    assert common_area_id is not None

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
        reservation_form = ReservationForm(request=request, reservable_service=common_area_id, data=formatted_data)
        if reservation_form.is_valid():
            # Cleaned data to get start and end times.
            cleaned_data = reservation_form.cleaned_data

            # session tracked service ids for payment step.
            request.session['service_id'] = []
            # session tracked service ids for success message.
            request.session['reserved_services_ids'] = []

            # potentially saving multiple blocks
            for service_id in reservation_form.services:
                service = ReservableServices.objects.get(pk=service_id)

                reservation_instance = ReserveBlock()
                reservation_instance.neighbor = request.user.neighbor
                reservation_instance.service = service
                reservation_instance.start_time = cleaned_data['start_time']
                reservation_instance.end_time = cleaned_data['end_time']
                reservation_instance.save()
                request.session['reserved_services_ids'].append(reservation_instance.id)

                # Check if the service has an associated fee. If so, assign service id and block id to session key.
                if service.fee > Decimal('0.00'):
                    request.session['service_id'].append((service.id, reservation_instance.id))

                else:
                    # Mark Reservation as paid so it shows up in the calendar view.
                    reservation_instance.is_paid = True
                    reservation_instance.save()

            try:
                del request.session['reservation_related_services']
            except:
                pass

            json_data = { 'success': True }
        else:
            json_data = {'success': False, 'errors': json.dumps(reservation_form.errors), 'datepicker_refill': formatted_data['datepicker_value'], 'form': render_to_string('reservation/ajax_reservation.html', {'reservation_form': reservation_form})}

    else:
        reservation_form = ReservationForm(request=request, reservable_service=common_area_id)
        json_data = {'form': render_to_string('reservation/ajax_reservation.html', {'reservation_form': reservation_form})}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_reservation_success(request):

    # get all reservation events just completed this user
    events = []
    try:
        for service_id in request.session['reserved_services_ids']:
            events.append(ReserveBlock.objects.get(pk=service_id))
    except:
        events.append(ReserveBlock.objects.filter(neighbor=request.user.neighbor).order_by('-pk')[0])

    # transaction = Transactions.objects.filter(wallet=request.user.neighbor.wallet).order_by('-pk')[0]
    transaction = {}
    try:
        transaction['amount'] = str(request.session['reservation_total'])
    except:
        transaction = False

    success_content = ModalSuccess.get_content('reservation', 'Your reservation has been made', 'Your common area reservation has been secured.')

    json_data = {'content': render_to_string('reservation/ajax_reservation_success.html', {'events': events, 'transaction': transaction, 'success_content': success_content}),
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
    items = ReserveBlock.objects.filter(neighbor__community = request.user.neighbor.community, start_time__gte = date_obj.date(), start_time__lt = date_obj.date() + datetime.timedelta(days=1), is_paid=True, is_cancelled=False).order_by('service', 'start_time')

    context = {'date': date_obj, 'items': items, 'date_formatted_long': date_formatted_long}

    return HttpResponse(render_to_string('reservation/ajax_calendar_items.html', context))


@login_required
def ajax_calendar_days(request):

    dates = []
    try:
        items = ReserveBlock.objects.filter(neighbor__community = request.user.neighbor.community, is_paid=True, is_cancelled=False).datetimes('start_time', 'day')
    except:
        items = []

    for item in items:
        if not item.date().strftime("%Y-%m-%d") in dates:
            dates.append(item.date().strftime("%Y-%m-%d"))

    return HttpResponse(json.dumps(dates), content_type='application/json')


@login_required
def ajax_datepicker_times(request):

    select_html = ''

    if request.method == 'POST' and len(request.body) > 0:

        # try to load the submitted data
        try:
            args = json.loads(request.body)
        except:
            json_data = {'success': False, 'errors': 'Datepicker data could not be read.', 'form': ''}
            return HttpResponse(json.dumps(json_data), content_type='application/json')

        # get available times list for the given arguments
        services_list = args['services'][:-1].split(",")
        times = get_available_times(services_list, args['field'], args['date'])

        # translate the time list into a select html element
        widget = SelectWithDisabled()
        select_html = widget.render(args['field'], '', attrs=None, choices=times)

    return HttpResponse(json.dumps({'select_html':select_html}), content_type='application/json')