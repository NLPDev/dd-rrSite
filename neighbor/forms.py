from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User

from helper_classes import ExpiryDateField
from neighbor.models import Neighbor, AddressConflict, MailingAddress, RealProperty
from utility import send_admin_notification
from violation.models import ViolationEvent
from community.models import Community


class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    remember_me = forms.BooleanField(label='Stay signed in', required=False, widget=forms.CheckboxInput(), initial=True)

    def __init__(self, request=None, *args, **kwargs):
        self.cached_user = None
        self.request = request
        kwargs.setdefault('label_suffix', '')
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data

        if len(self._errors) > 0:
            return cleaned_data
        else:
            email = cleaned_data.get('email')
            password = cleaned_data.get('password')

            if email is None or password is None:
                return forms.ValidationError("Please enter an email and password.")
            else:
                self.cached_user = authenticate(username=email.lower(), password=password)

                if self.cached_user is None:
                    if not self._errors.has_key('email'):
                        from django.forms.util import ErrorList
                        self._errors['email'] = ErrorList()
                    self._errors['email'].append(
                        "Please enter a correct email and password. Passwords are case sensitive."
                    )
                elif not self.cached_user.is_active:
                    raise forms.ValidationError("This account is inactive.")

        if not cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)

        return cleaned_data

    def get_user(self):
        return self.cached_user


PHONE_REGEX = r'^([\+]?\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$'
STATE_CHOICES = [('','--')] + Community.STATE_CHOICES_ABBREVIATED


class AccountTypeForm(forms.Form):
    account_type = forms.ChoiceField(
        choices=Neighbor.ACCOUNT_TYPE_CHOICES, widget=forms.RadioSelect
    )


class RegisterForm(forms.ModelForm):

    STATE_CHOICES = STATE_CHOICES

    account_type = forms.ChoiceField(required=True, widget=forms.HiddenInput(), choices=Neighbor.ACCOUNT_TYPE_CHOICES)
    email = forms.EmailField(label="Email Address", required=True, widget=forms.EmailInput())
    company_name = forms.CharField(label="Company Name", required=False)
    # secondary_email = forms.EmailField(label="Secondary Email", required=False, widget=forms.EmailInput())
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput())
    password_verify = forms.CharField(label="Confirm Password", required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(label="First Name", required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="Last Name", required=True, widget=forms.TextInput())
    phone = forms.RegexField(label="Phone Number", required=True, widget=forms.TextInput(), regex=PHONE_REGEX,
                             error_message = ("Invalid phone number. Try removing any dashes or spaces."))
    # secondary_phone = forms.RegexField(label="Secondary Phone", required=False,
    #                                    widget=forms.TextInput(), regex=PHONE_REGEX,
    #                                    error_message = ("Invalid phone number. Try removing any dashes or spaces."))
    lot_number = forms.IntegerField(label="Lot Number", required=False, widget=forms.TextInput())
    billing_address_1 = forms.CharField(label="Billing Address", required=True, widget=forms.TextInput())
    billing_address_2 = forms.CharField(label="Address Line 2", required=False, widget=forms.TextInput())
    billing_city = forms.CharField(label="City", required=True, widget=forms.TextInput())
    billing_state = forms.ChoiceField(label="State", choices=STATE_CHOICES, required=True, widget=forms.Select())
    billing_zip_code = forms.CharField(label="Zip Code", required=True, widget=forms.TextInput())
    # preferred_contact_method = forms.ChoiceField(label="Preferred Method", choices=Neighbor.CONTACT_METHOD_CHOICES,
    #                                              required=True, widget=forms.RadioSelect())
    mailing_address_differ = forms.BooleanField(label="Check if mailing address is different than physical address.",
                                                required=False,)
    # multiple_properties = forms.BooleanField(label="Check if owning multiple properties in subdivision.",
    #                                          required=False)
    # extra_property_numbers = forms.CharField(label="Lot Numbers", required=False, widget=forms.TextInput())

    def __init__(self, request=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(RegisterForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data

        # If there are already errors then no need to go further
        if len(self._errors) > 0:
            return self.cleaned_data

        # Check Passwords
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_verify = cleaned_data.get('password_verify')

        if len(password) < 5:
            self._errors["password"] = self.error_class(["Passwords must be at least 5 characters long."])
            return self.cleaned_data

        if password_verify != password:
            self._errors["password_verify"] = self.error_class(["Password and confirm password did not match."])
            return self.cleaned_data

        if User.objects.filter(username=email.lower()).exists():
            self._errors["email"] = self.error_class(
                ["An account with this email already exist. Please use another one."]
            )
            return self.cleaned_data

        return self.cleaned_data

    def create_user(self):
        try:
            return User.objects.create_user(
                self.cleaned_data['email'].lower(),
                self.cleaned_data['email'].lower(),
                self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
        except Exception:
            raise forms.ValidationError(
                """Sorry for the inconvenience but there was an error creating your user account.
                   Please contact us so we can get this straightened out. Thanks!"""
            )

    def validate_unique(self):
        # If there is an existing street address, create a conflict notification.
        try:
            existing = Neighbor.objects.exclude(pk=self.instance.pk).get(
                address_1=self.cleaned_data['address_1'],
                zip_code=self.cleaned_data['zip_code']
            )
        except Neighbor.DoesNotExist:
            return True
        else:
            conflict = AddressConflict(
                existing_neighbor=existing,
                new_neighbor_first=self.cleaned_data['first_name'],
                new_neighbor_last=self.cleaned_data['last_name'],
                new_neighbor_phone=self.cleaned_data['phone'],
                new_neighbor_email=self.cleaned_data['email'].lower(),
            )
            conflict.save()
            self.add_error(
                'address_1',
                'Someone already has an account at this address. We are reviewing it, and will get back to you shortly.'
            )
        return False

    def clean_extra_property_numbers(self):
        if self.cleaned_data.get('multiple_properties'):
            numbers = self.cleaned_data.get('extra_property_numbers')
            int_numbers = []
            if numbers:
                numbers = numbers.split(',')
                for n in numbers:
                    n = n.strip()
                    if not n:
                        continue
                    try:
                        int_numbers.append(int(n))
                    except ValueError:
                        raise forms.ValidationError("Bad number: %s" % n)
                return int_numbers
            else:
                raise forms.ValidationError("This field is required if option checked")

    class Meta:
        model = Neighbor
        fields = (
            'first_name', 'last_name', 'account_type',
            'password', 'password_verify',
            'phone', 'email', 
            'billing_address_1', 'billing_address_2',
            'billing_city', 'billing_state', 'billing_zip_code',
        )


class MailingAddressForm(forms.ModelForm):
    address_1 = forms.CharField(label="Mailing Address", required=True, widget=forms.TextInput())
    address_2 = forms.CharField(label="Mailing Address line 2", required=False, widget=forms.TextInput())
    city = forms.CharField(label="City", required=True, widget=forms.TextInput())
    state = forms.ChoiceField(label="State", choices=STATE_CHOICES, required=True, widget=forms.Select())
    zip_code = forms.CharField(label="Zip Code", required=True, widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = u'mailing'
        kwargs['label_suffix'] = ''
        super(MailingAddressForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MailingAddress
        fields = ('address_1', 'address_2', 'city', 'state', 'zip_code')


class RealPropertyForm(forms.ModelForm):
    community = forms.ModelChoiceField(label="Community", required=True, queryset=Community.objects.all())
    position = forms.CharField(label="Neighborhood position", required=False, help_text='(If Applicable)')
    lot_number = forms.IntegerField(label="Lot Number", required=True, widget=forms.TextInput())
    address_1 = forms.CharField(label="Address", required=True, widget=forms.TextInput())
    address_2 = forms.CharField(label="Address line 2", required=False, widget=forms.TextInput())
    city = forms.CharField(label="City", required=True, widget=forms.TextInput())
    state = forms.ChoiceField(label="State", choices=STATE_CHOICES, required=True, widget=forms.Select())
    zip_code = forms.CharField(label="Zip Code", required=True, widget=forms.TextInput())
    contact = forms.CharField(label="Contact", required=False)

    class Meta:
        model = RealProperty
        fields = ('community', 'lot_number', 'address_1', 'address_2',
                  'city', 'state', 'zip_code', 'contact')

    def clean(self):
        super(RealPropertyForm, self).clean()
        lot = self.cleaned_data.get('lot_number')
        community = self.cleaned_data.get('community')
        if (
                lot and community and RealProperty.objects.filter(
                    lot_number=lot, community=community, neighbor__isnull=False
                ).exists()
        ):
            self.add_error(
                'lot_number',
                'Sorry, this lot is currently occupied. If you feel an error has been made, please contact RCN.'
            )




class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email Address', widget=forms.EmailInput())

    def __init__(self, request=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()

        email = cleaned_data.get('email')

        users = User.objects

        try:
            users.get(email=email.lower())
        except Exception:
            raise forms.ValidationError('No account with that email exists')

        return cleaned_data


class ConfirmPasswordResetForm(SetPasswordForm):

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if len(password1) < 5:
            raise forms.ValidationError('Passwords must be at least 5 characters long.')

        return password1


class ChooseCommunityForm(forms.Form):
    position = forms.CharField(label="Neighborhood Position", required=False,
                               widget=forms.TextInput(), help_text='(If Applicable)')
    community = forms.ModelChoiceField(label="Your Neighborhood", required=True,
                                       queryset=Community.objects.all(), to_field_name='id')

    def __init__(self, request=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ChooseCommunityForm, self).__init__(*args, **kwargs)


class ManageAccountForm(forms.ModelForm):
    company_name = forms.CharField(label="Company", required=False)
    first_name = forms.CharField(label="First Name", required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="Last Name", required=True, widget=forms.TextInput())
    address_1 = forms.CharField(label="Address Line 1", required=True, widget=forms.TextInput())
    address_2 = forms.CharField(label="Address Line 2", required=False, widget=forms.TextInput())
    city = forms.CharField(label="City", required=False, widget=forms.TextInput())
    state = forms.ChoiceField(label="State", choices=Community.STATE_CHOICES_ABBREVIATED,
                              required=False, widget=forms.Select())
    zip_code = forms.CharField(label="Zip Code", required=False, widget=forms.TextInput())
    phone = forms.RegexField(label="Phone Number", required=True, widget=forms.TextInput(),
                             regex=r'^([\+]?\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
                             error_message = ("Invalid phone number. Try removing any dashes or spaces."))
    email = forms.EmailField(label="Email Address", required=True, widget=forms.EmailInput())
    position = forms.CharField(label="Neighborhood Position", required=False, widget=forms.TextInput())

    def __init__(self, request=None, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ManageAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ManageAccountForm, self).clean()

        # If there are already errors then no need to go further
        if len(self._errors) > 0:
            return cleaned_data

        email = cleaned_data.get('email')

        # only check the email/username if it has changed
        if email != self.instance.user.username:
            if len(User.objects.filter(username=email)) > 0:
                self._errors["email"] = self.error_class([
                    "An account with this email already exist. Please use another one."
                ])
                return cleaned_data

        return cleaned_data

    class Meta:
        model = Neighbor
        fields = ('company_name', 'first_name', 'last_name', 'address_1', 'address_2',
                  'city', 'state', 'zip_code', 'phone', 'email', 'position',)


class PaymentsForm(forms.Form):
    name_on_card = forms.CharField(max_length=200)
    card_number = forms.CharField(max_length=16)
    card_type = forms.ChoiceField(choices=(('V', 'VISA'), ('MC', 'MASTERCARD'), ('AMEX', 'AMERICAN EXPRESS'), ('D', 'DISCOVER')))
    security_code = forms.CharField(max_length=4)
    exp_date = ExpiryDateField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        neighbor = kwargs.pop('neighbor')
        kwargs.setdefault('label_suffix', '')
        super(PaymentsForm, self).__init__(*args, **kwargs)

        self.fields['violations'] = forms.ModelMultipleChoiceField(queryset=neighbor.violationevent_set.filter(is_approved=True, is_paid=False), required=False)
        self.fields['dues'] = forms.ModelMultipleChoiceField(queryset=neighbor.duepayment_set.filter(is_active=True), required=False)