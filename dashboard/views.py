from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User

from dashboard.forms import QueueForm
from community.models import Community


def superuser_su(request):
    # Let it be known that I know just enough security to know that I don't like this feature, but not enough to know
    # why, or if I am completely wrong. Without further ado:

    if request.POST:
        # Get user id so we know who is who
        history = [request.user.pk]

        # Check and see if we are still hijacked into a user account. If so, just add it to the beginning of the list.
        # Newly hijacked accounts should always be last.
        if request.session.get('history'):
            history = request.session['history'] + history

        # Check for user permissions. Only SUPERUSERS can hijack.
        if not request.user.is_superuser:
            raise PermissionDenied

        # Time for the actual hijack. We need to get the targeted user, a backend to handle auth,
        # then login, update the session, and redirect.
        user = User.objects.get(id=request.POST['user_id'])

        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, user)

        request.session['must_be_true_to_yourself'] = False
        request.session['history'] = history
        request.session.modified = True

        return HttpResponseRedirect(reverse('neighbor:manage_account'))

    # Logout on anything besides post. We iterate back through the list logging back in until
    # we get back to our original admin, then redirect to the admin page.
    if not request.session.get('history'):
        raise PermissionDenied

    history = request.session['history']
    if len(history):
        user_pk = history.pop()
        user = User.objects.get(id=user_pk)
        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(request, user)
    if len(history):
        request.session['history'] = history
        request.session['must_be_true_to_yourself'] = False
    else:
        try:
            del request.session['history']
            del request.session['must_be_true_to_yourself']
        except KeyError:
            pass

    request.session.modified = True
    return HttpResponseRedirect(reverse('dashboard'))


@staff_member_required
def dashboard(request):

    # Check if POST, validate form if so
    if request.POST:
        pending_form = QueueForm(data=request.POST)

        if pending_form.is_valid():
            if 'deny' in request.POST:
                pending_form.save(action='deny')

            else:
                pending_form.save(action='save')

            context = {'pending_form': QueueForm()}
            return HttpResponseRedirect(reverse('dashboard'))

        else:
            pass

    else:
        # No post data, load clean form and return response
        pending_form = QueueForm()

    active_users = User.objects.filter(is_active=True)

    community_list = Community.objects.all()

    context = {'pending_form': pending_form, 'users': active_users or None, 'community_list': community_list or None}

    return render(request, 'dashboard/queue.html', context)
