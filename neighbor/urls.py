from django.conf.urls import patterns, url, include

from . import views

account_urls = patterns('',
    url(r'^$', views.manage_account, name='manage_account'),
    url(r'^add-property/$', views.AccountNewPropertyFormView.as_view(), name='add-property'),
    url(r'^payments/$', views.payments, name='payments'),
    url(r'^ajax-community-data/$', views.AjaxCommunityDataView.as_view(), name='ajax-community-data'),
    url(r'^ajax-release-property/$', views.AjaxReleasePropertyView.as_view()),
    url(r'^ajax-update-property/$', views.AjaxUpdatePropertyView.as_view()),
    url(r'^ajax-payment/$', views.ajax_payments),
    url(r'^ajax-payment-success/$', views.ajax_payments_success),
    url(r'^ajax-manage-account/$', views.ajax_manage_account),
    url(r'^ajax-manage-account-success/$', views.ajax_manage_account_success),
    url(r'^ajax-cancel-item/(?P<key>[a-zA-Z0-9_]+)/$', views.ajax_cancel_item),
    url(r'^ajax-cancel-item-success/$', views.ajax_cancel_item_success),
)

urlpatterns = patterns('',
    url(r'^account/', include(account_urls, namespace='neighbor', app_name='neighbor')),
    url(r'^login/', views.neighbor_login, name='login'),
    url(r'^logout/', views.neighbor_logout, name='logout'),
    url(r'^register/add-property/$', views.NewPropertyFormView.as_view(), name='add-property'),
    url(r'^register/', views.register, name='register'),
    url(r'^choose-account-type/', views.ChooseAccountTypeFormView.as_view(), name='choose-account-type'),
    url(r'^forgot-password/$', views.forgot_password, name='forgot-password'),
    url(r'^reset-password/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', views.reset_password_confirm, name='reset-password-confirm'),
    url(r'^reset-password-complete/$', views.reset_password_complete, name='reset-password-complete'),
    url(r'^success/', views.success, name='success'),
)