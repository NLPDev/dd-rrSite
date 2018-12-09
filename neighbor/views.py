from decimal import Decimal
import datetime, json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth import login, logout, REDIRECT_FIELD_NAME
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.http import int_to_base36, base36_to_int
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import FormView, View

from webapp.mixins import LoginRequiredMixin
from announcement.models import Announcement
from neighbor.forms import (LoginForm, RegisterForm, ForgotPasswordForm, ConfirmPasswordResetForm,
                            ManageAccountForm, PaymentsForm, MailingAddressForm, AccountTypeForm,
                            RealPropertyForm)
from neighbor.models import (Neighbor, Transactions, DuePayment, CalendarEvent,
                             RealProperty, NeighborCommunity)
from community.models import Community
from reservation.models import ReserveBlock
from utility import set_detail_context, send_admin_notification
from page_content.models import ModalSuccess
from violation.models import ViolationEvent


def neighbor_login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if redirect_to == '':
        try:
            redirect_to = request.session['redirect_to']
        except KeyError:
            pass
    else:
        request.session['redirect_to'] = redirect_to

    if request.user.id is not None:
        if redirect_to == '':
            redirect_to = reverse('home')
        try:
            del request.session['redirect_to']
        except KeyError:
            pass
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        login_form = LoginForm(data=request.POST, request=request)

        if login_form.is_valid():
            login(request, login_form.get_user())

            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = reverse('home')
            try:
                del request.session['redirect_to']
            except KeyError:
                pass
            return HttpResponseRedirect(redirect_to)
    else:
        login_form = LoginForm()

    context = {'login_form': login_form}

    return render(request, 'registration/login.html', context)


def neighbor_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class ChooseAccountTypeFormView(FormView):
    template_name = 'registration/choose-account-type.html'
    form_class = AccountTypeForm

    def form_valid(self, form):
        return HttpResponseRedirect(
            ''.join((
                reverse('register'), '?account_type=', form.cleaned_data['account_type']
            ))
        )


def register(request):

    if request.user.id is not None:
        return HttpResponseRedirect(reverse('home'))

    if request.method == "POST":
        register_form = RegisterForm(data=request.POST)
        mailing_flag = True
        account_type_title = [
            x[1] for x in Neighbor.ACCOUNT_TYPE_CHOICES
            if x[0] == int(request.POST['account_type'])
        ][0] 

        if request.POST.get('mailing_address_differ') == 'on':
            mailing_form = MailingAddressForm(data=request.POST)
            if not mailing_form.is_valid():
                mailing_flag = Fals
        else:
            mailing_form = MailingAddressForm()

        if register_form.is_valid() and mailing_flag:
            # Make sure this address is unique from anything else in the db.
            # if it's not unique, log this conflict, but allow them to continue with registration
            #alex: address was substituded with billing address, so old check uniqueness doesn't work
            # if not register_form.validate_unique():
            #     send_admin_notification('Address Conflict Detected', {
            #         'message': 'A user has registered an address belonging to another user',
            #         'url': request.build_absolute_uri(reverse("admin:index"))
            #     })

            #alex: community moved to properties
            # # assign user to a community
            # #  1. see if they came in through a community url, ie. rcn.com/my-neighborhood
            # try:
            #     community = Community.objects.get(pk=request.session['community'])
            # except (IndexError, KeyError, Community.DoesNotExist):
            # #  2. see if the address they entered only matches one community, based on zip
            #     try:
            #         communities = Community.objects.filter(zip_code=register_form.cleaned_data['zip_code'])
            #         if communities.count() > 1:
            #             raise Community.DoesNotExist
            #         else:
            #             community = communities[:1].get()
            #     except Community.DoesNotExist:
            # #  3. see if the address they entered only matches one community, based on city/state
            #         try:
            #             communities = Community.objects.filter(city=register_form.cleaned_data['city'],
            #                                                    state=register_form.cleaned_data['state'])
            #             if communities.count() > 1:
            #                 raise Community.DoesNotExist
            #             else:
            #                 community = communities[:1].get()
            #         except Community.DoesNotExist:
            # #  4. allow their community to be blank. they will be forced to choose one on the next page
            #             community = None

            user = register_form.create_user()
            neighbor = register_form.save(commit=False)
            # neighbor.community = community
            neighbor.user = user
            neighbor.save()

            if mailing_form.data:
                mailing_address = mailing_form.save(commit=False)
                mailing_address.neighbor = neighbor
                mailing_address.save()

            # if register_form.cleaned_data['multiple_properties']:
            #     for num in register_form.cleaned_data['extra_property_numbers']:
            #         ExtraProperty.objects.create(neighbor=neighbor, lot_number=num)

            user = authenticate(
                username=user.username,
                password=register_form.cleaned_data['password']
            )
            login(request, user)
            messages.add_message(
                request, messages.INFO,
                'Your account has been created successfully. Add your property to accomplish.',
            )
            return HttpResponseRedirect(reverse('add-property'))
    else:
        if not request.GET.get('account_type'):
            return HttpResponseRedirect(reverse('choose-account-type'))

        register_form = RegisterForm(initial={'account_type': request.GET['account_type']})
        mailing_form = MailingAddressForm()
        account_type_title = [
            x[1] for x in Neighbor.ACCOUNT_TYPE_CHOICES if x[0] == int(request.GET['account_type'])
        ][0] 

    context = RequestContext(request, {
        'register_form': register_form,
        'mailing_form': mailing_form,
        'account_type_title': account_type_title
    })

    return render(request, 'registration/register.html', context_instance=context)


class NewPropertyFormView(LoginRequiredMixin, FormView):
    template_name = 'registration/property_form.html'
    form_class = RealPropertyForm

    def dispatch(self, *args, **kwargs):
        if self.request.user.neighbor.can_add_property:
            return super(NewPropertyFormView, self).dispatch(*args, **kwargs)
        else:
            messages.add_message(
                self.request, messages.ERROR,
                'You can\'t add more properties'
            )
            return HttpResponseRedirect(reverse('neighbor:manage_account'))

    def get_initial(self):
        return {'contact': self.request.user.email}

    def get_form(self, form_class):
        if self.request.method == 'POST':
            community = self.request.POST.get('community')
            lot = self.request.POST.get('lot_number')
            instance = None
            if community and lot:
                instance = RealProperty.objects.filter(
                    community_id=community, lot_number=lot, neighbor__isnull=True,
                ).first()
            return form_class(self.request.POST, instance=instance)
        return form_class(initial=self.get_initial())

    def form_valid(self, form):
        neighbor = self.request.user.neighbor
        real_property = form.save(commit=False)
        real_property.neighbor = neighbor
        real_property.save()
        # create or update relation between user and community
        try:
            relation = NeighborCommunity.objects.get(
                neighbor=neighbor, community=form.cleaned_data['community']
            )
            if form.cleaned_data.get('position') != relation.position:
                relation.update(position=form.cleaned_data.get('position'))
        except NeighborCommunity.DoesNotExist:
            relation = NeighborCommunity()
            relation.community = form.cleaned_data['community']
            relation.neighbor = neighbor
            if form.cleaned_data.get('position'):
                relation.position = form.cleaned_data['position']
            relation.save()
        # add neighbor.community as default user community because of legacy
        if not neighbor.community:
            neighbor.community = form.cleaned_data['community']
            neighbor.position = form.cleaned_data.get('position')
            neighbor.save()
        return HttpResponseRedirect(reverse('neighbor:manage_account'))


class AccountNewPropertyFormView(NewPropertyFormView):
    template_name = 'neighbor/property_form.html'

    def get_context_data(self, **kwargs):
        context = super(AccountNewPropertyFormView, self).get_context_data(**kwargs)
        set_detail_context(self.request, context)
        return context


class AjaxCommunityDataView(View):
    def get(self, request):
        if request.GET.get('id'):
            try:
                community = Community.objects.get( id=request.GET['id'])
                data = model_to_dict(community, fields=('id', 'city', 'state', 'zip_code'))
                data['position'] = request.user.neighbor.position
                return HttpResponse(json.dumps(data))
            except Community.DoesNotExist:
                return HttpResponse('Community does not exist', status=404)
        return HttpResponse('Community id has not been passed', status=400)


class AjaxReleasePropertyView(LoginRequiredMixin, View):
    """this view just removes relation between Neighbor and RealProperty"""
    def post(self, request):
        if request.POST.get("id"):
            try:
                real_property = RealProperty.objects.get(id=request.POST['id'])
                real_property.neighbor = None
                real_property.save()
                user = request.user
                send_admin_notification('User has released his property', {
                    'message': 'user: %s %s, email: %s, community: %s lot_number: %s' % (
                        user.first_name, user.last_name, user.email,
                        real_property.community.name, real_property.lot_number,
                    ),
                    # 'url': request.build_absolute_uri(reverse("admin:index"))
                })
                return HttpResponse(json.dumps({'property': real_property.id}))
            except RealProperty.DoesNotExist:
                return HttpResponse('Property does not exist', status=404)
        return HttpResponse('Real property id has not been passed', status=400)


class AjaxUpdatePropertyView(LoginRequiredMixin, View):
    def post(self, request):
        instance = RealProperty.objects.get(id=request.POST.get('id'))
        FormClass = modelform_factory(RealProperty, fields=('contact',))
        form = FormClass(data=request.POST, instance=instance)
        if form.is_valid():
            real_property = form.save()
            return HttpResponse(json.dumps(model_to_dict(real_property)))
        else:
            print(form.errors)
            return HttpResponse('form invalid', status=400)


def forgot_password(request):
    errors = ''
    if request.method == "POST":
        forgot_form = ForgotPasswordForm(data=request.POST)

        if forgot_form.is_valid():

            # send reset email
            user = User.objects.get(email=forgot_form.cleaned_data['email'])
            token = default_token_generator.make_token(user)
            uid = int_to_base36(user.id)
            reset_url = request.build_absolute_uri(reverse('reset-password-confirm', args=[uid, token]))

            email_context = {'neighbor_email': forgot_form.cleaned_data['email'], 'user': user, 'reset_url': reset_url}

            subject = 'Password Reset'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = list(forgot_form.cleaned_data['email'])
            text_content = render_to_string("email/iforgot_string.html", email_context)
            html_content = render_to_string("email/iforgot_html.html", email_context)
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            success = msg.send()

            if not success:
                forgot_form.add_error(None, 'Internal Server Error: failed to send email.')
            else:
                return HttpResponseRedirect(reverse('success') + '?event=reset-password')
        else:
            errors = forgot_form.errors
    else:
        forgot_form = ForgotPasswordForm()

    context = {'forgot_form': forgot_form, 'errors': errors}

    return render(request, 'registration/forgot.html', context)


def reset_password_confirm(request, uidb36=None, token=None,
                           template_name='registration/reset-password-confirm.html',
                           token_generator=default_token_generator):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None  # checked by URLconf
    # if post_reset_redirect is None:
    # post_reset_redirect = reverse('password_reset_complete')

    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    context_instance = RequestContext(request)

    if token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ConfirmPasswordResetForm(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('reset-password-complete'))
        else:
            form = ConfirmPasswordResetForm(None)
    else:
        # token doesn't match with the provided user
        raise Http404

    context_instance['form'] = form

    return render_to_response(template_name, context_instance=context_instance)


def reset_password_complete(request):
    return render_to_response(
        'registration/reset-password-complete.html', {}, context_instance=RequestContext(request)
    )


def success(request):
    return render(
        request, 'registration/success.html', {'event': request.GET.get('event', False)}
    )


@login_required
def manage_account(request):
    neighbor = request.user.neighbor
    manage_account_form = ManageAccountForm(
        instance=neighbor,
        initial={
            'company': request.user.neighbor.company_name,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
    )

    announcements = neighbor.announcement_set.filter(
        is_cancelled=False,
        event_date__gt=datetime.date.today()
    ).order_by('event_date', '-approved_date').first()

    reservations = neighbor.reserveblock_set.filter(
        is_paid=True,
        is_cancelled=False,
        start_time__gt=datetime.date.today()
    ).order_by('start_time', 'service')[:5] or None

    events = neighbor.calendarevent_set.filter(
        is_approved=True,
        is_cancelled=False,
        start_date__gt=datetime.date.today()
    ).order_by('start_date')[:5] or None

    payments = neighbor.wallet.transaction_history[:5] or None

    context = {
        'manage_account_form': manage_account_form,
        'announcements': announcements,
        'reservations': reservations,
        'events': events,
        'payments': payments,
        'real_properties': neighbor.realproperty_set.all(),
    }
    set_detail_context(request, context)

    return render(request, 'neighbor/manage_account.html', context)


@login_required
def ajax_manage_account(request):

    if request.method == 'POST' and 'form_data' in request.POST:
        # try to load the submitted form data
        try:
            form_data = json.loads(request.POST['form_data'])
            # format the form data
            formatted_data = {}
            for row in form_data:
                formatted_data[row['name']] = row['value']
        except:
            json_data = {
                'success': False,
                'errors': 'Form data could not be read.',
                'form': ''
            }
            return HttpResponse(json.dumps(json_data), content_type='application/json')

        manage_account_form = ManageAccountForm(
            data=formatted_data,
            instance=request.user.neighbor,
            initial={
                'company': request.user.neighbor.company_name,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            }
        )
        if manage_account_form.is_valid():
            user = request.user
            user.first_name = manage_account_form.cleaned_data['first_name']
            user.last_name = manage_account_form.cleaned_data['last_name']
            user.email = manage_account_form.cleaned_data['email']
            user.username = manage_account_form.cleaned_data['email']
            user.save()
            manage_account_form.save()
            json_data = {'success': True}
        else:
            json_data = {
                'success': False,
                'errors': render_to_string(
                    'neighbor/ajax_manage_account_errors.html',
                    {'errors': manage_account_form.errors}
                ),
                'form': ''
            }

    else:
        json_data = {'success': False, 'errors': 'Form data missing.', 'form': ''}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_manage_account_success(request):

    success_content = ModalSuccess.get_content('manage_account', 'Your account has been updated', 'Your account details have been updated successfully.')

    json_data = {'content': render_to_string('neighbor/ajax_manage_account_success.html', {'success_content': success_content}),
                    'title': 'Saved',
                    'title_position': 'center',
                    'button_position': 'center',
                    'text_position': 'center',
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def payments(request):
    payments_form = PaymentsForm(neighbor=request.user.neighbor)
    context = {'payments': payments_form}
    set_detail_context(request, context)
    return render(request, 'neighbor/payments.html', context)


@login_required
def ajax_payments(request):

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

        payments_form = PaymentsForm(data=formatted_data, neighbor=request.user.neighbor)

        if payments_form.is_valid():
            cleaned_data = payments_form.cleaned_data

            # session tracked payment objects for success message
            request.session['violations_ids'] = []
            request.session['dues_ids'] = []
            request.session['payment_total_amount'] = 0

            # This handles stripe payment. Transactions model actually handles the payment process, this code is for
            # instantiating needed variables.
            currency = 'usd'
            metadata = {'email': request.user.email}
            description = 'Payment made by ' + str(request.user.neighbor)

            # Set up card info from form.
            # Reminder: Add form field for selecting saved card(s). If none are picked, go ahead with entered card info.
            card = {'name': cleaned_data['name_on_card'], 'number': cleaned_data['card_number'],
                    'exp_month': cleaned_data['exp_date'].month, 'exp_year': cleaned_data['exp_date'].year,
                    'cvc': cleaned_data['security_code']}

            # Get amounts from each payment object, add up total.
            amount = Decimal('0.00')
            for payment in cleaned_data['violations']:
                amount += payment.amount
                request.session['violations_ids'].append(payment.id)

            for payment in cleaned_data['dues']:
                amount += payment.amount
                request.session['dues_ids'].append(payment.id)

            request.session['payment_total_amount'] = str(amount)
            # Stripe uses cents instead of decimals. Convert so stripe knows what we mean.
            amount = int(amount * 100)

            # Create a new transaction instance, and set up needed variables.
            transaction = Transactions()
            transaction.wallet = request.user.neighbor.wallet
            transaction.title = description
            transaction.transaction_type = 'V'
            transaction.amount = (amount/100)

            # Transactions have stripe functions. This means that Transaction instances needs to
            # know certain things, like the amount, (currency is not needed as we will always use USD.), card info, etc.
            # metadata is used for easier tracking (by email), instead of by stripe_id, as an email is always going to be
            # more memorable than randomly generated strings.
            # description and statement_descriptor show up on the receipt and neighbor bank provided transaction history,
            # respectively. Make sure these are always relevant to the site/type of payment.
            keys = request.user.neighbor.community.keys
            response = transaction.stripe(amount=amount, currency=currency, card=card, metadata=metadata, description=description, keys=keys)

            # Response returns with either True meaning that the payment was successful, in which case, go ahead and do
            # further processing. If it returns with anything else, it will be the stripe provided error message. Return
            # this using the new django 1.7 Form.add_error() method, which can be done completely outside of the form.
            # Like here, for instance.
            if response is not True:
                payments_form.add_error('card_number', response)
                json_data = {'success': False, 'errors': render_to_string('neighbor/ajax_payments_errors.html', {'errors': payments_form.errors}), 'form': ''}

            # After the transaction is saved, a bunch of stripe metadata is saved to the transaction as well. Specifically,
            # we want to check and see if stripe reported the transaction as 'paid' or not. We handle any errors in the save
            # function of the txcn instance.
            if transaction.stripe_paid:
                transaction.save()
                for payment in cleaned_data['violations']:
                    payment.mark_paid(transaction)

                for payment in cleaned_data['dues']:
                    payment.mark_paid(transaction)

                json_data = {'success': True}

            # =====================================================================

        else:
            json_data = {'success': False, 'errors': render_to_string('neighbor/ajax_payments_errors.html', {'errors': payments_form.errors}), 'form': ''}

    else:
        json_data = {'success': False, 'errors': 'Form data missing.', 'form': ''}

    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_payments_success(request):

    # get all payment objects just completed this user
    payment_objects = []

    try:
        for violation_id in request.session['violations_ids']:
            payment_objects.append(ViolationEvent.objects.get(pk=violation_id))
    except:
        pass

    try:
        for dues_id in request.session['dues_ids']:
            payment_objects.append(DuePayment.objects.get(pk=dues_id))
    except:
        pass

    transaction = {}
    try:
        transaction['amount'] = str(request.session['payment_total_amount'])
    except:
        transaction = False

    success_content = ModalSuccess.get_content('payment', 'Your payment has gone through', 'Thank you.')

    json_data = {'content': render_to_string('neighbor/ajax_payments_success.html', {'success_content': success_content, 'transaction': transaction, 'payment_objects': payment_objects}),
                    'title': 'SUCCESS!',
                    'title_position': 'center',
                    'button_position': 'center',
                    'text_position': 'center',
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')



@login_required
def ajax_cancel_item(request, key):

    try:
        key = key.split('_')
        model = key[0]
        id = key[1]
    except:
        json_data = {'success': False, 'errors': 'True', 'form': 'Error: item to cancel unrecognized'}
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
            json_data = {'success': False, 'errors': 'Form data could not be read.', 'form': 'Error: Form data could not be read.'}
            return HttpResponse(json.dumps(json_data), content_type='application/json')

        # confirm that the given item is owned by this user
        obj = False
        if model == 'announcement':
            obj = Announcement.objects.get(pk=id, neighbor=request.user.neighbor)
        elif model == 'reservation':
            obj = ReserveBlock.objects.get(pk=id, neighbor=request.user.neighbor)
        elif model == 'event':
            obj = CalendarEvent.objects.get(pk=id, neighbor=request.user.neighbor)

        if not obj:
            json_data = {'success': False, 'errors': 'Item not found or permission denied', 'form': 'Error: Item not found or permission denied.'}
        else:
            # do removal
            try:
                obj.is_cancelled = True
                obj.save()
                json_data = { 'success': True }
            except:
                json_data = {'success': False, 'errors': 'Error removing item', 'form': 'Error: Internal server error. Item could not be removed.'}

    else:
        json_data = {'form': render_to_string('neighbor/ajax_confirm_cancel_item.html', {'model': model, 'id': id})}


    return HttpResponse(json.dumps(json_data), content_type='application/json')


@login_required
def ajax_cancel_item_success(request):

    success_content = ModalSuccess.get_content('cancel_item', 'Cancelled', 'Cancellation successful.')

    json_data = {'content': render_to_string('neighbor/ajax_cancel_item_success.html', {'success_content': success_content}),
                    'title': 'SUCCESS!',
                    'title_position': 'center',
                    'button_position': 'center',
                    'button': 'Continue',
                    'text_position': 'center',
    }

    return HttpResponse(json.dumps(json_data), content_type='application/json')
