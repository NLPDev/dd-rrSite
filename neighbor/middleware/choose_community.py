"""
Neighbor Middleware.

This simply enforces that all neighbors/users are assigned to a community.
If they do not have a community, they are forced to choose one.
"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from neighbor.models import Neighbor
from neighbor.forms import ChooseCommunityForm

class NeighborMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):

        # if user is not logged in, or trying to logout, let them through.
        if request.path == '/logout/' or request.user.id is None:
            return None

        # ensure that the user has a neighbor account.
        # admins can change their neighborhood, but they still need an associated neighbor account for this to work
        try:
            neighbor = request.user.neighbor
        except Neighbor.DoesNotExist:
            # create the neighbor account
            neighbor = Neighbor()
            neighbor.user = request.user
            neighbor.save()

        # show community selection form if the neighbor doesn't have a community
        # if request.user.neighbor.community is None:
        if (
                request.method == 'GET'
                and not request.is_ajax()
                and request.user.is_authenticated()
                and not request.user.neighbor.community_id
                and request.resolver_match.url_name != 'add-property'
        ):
            return HttpResponseRedirect(reverse('add-property'))

            # if request.method == "POST":
            #     choose_community_form = ChooseCommunityForm(data=request.POST)

            #     if choose_community_form.is_valid():
            #         # save community to neighbor instance
            #         request.user.neighbor.community = choose_community_form.cleaned_data['community']
            #         request.user.neighbor.position = choose_community_form.cleaned_data['position']
            #         request.user.neighbor.save()

            #         return HttpResponseRedirect(reverse('success') + '?event=register')
            # else:
            #     choose_community_form = ChooseCommunityForm()

            # context = {'choose_community_form': choose_community_form}

            # return render(request, 'registration/choose-community.html', context)

        return None