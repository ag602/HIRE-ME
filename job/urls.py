from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('findjob/', views.findjob, name='findjob'),
    path('findjob/search/', views.search, name='search'),
    path('jobpage/', views.jobpage, name='jobpage'),
    path('jobpage/<int:job_id>', views.jobpage, name='jobpage'),
    path('managejobs/', views.managejobs, name='managejobs'),
    path('notification/', views.notification, name='notification'),
    path('saved_jobs/', views.bookmark, name='bookmark'),
    path('baseprofile/', views.baseprofile),
    path('applied/', views.appliedjobs, name='appliedjobs'),
    path('managecandidates/', views.manage_candidates, name='managecandidates'),
    # By user ID
    # <int:pk> syntax is available only through path function (introduced in Django 2.0), not url:
    url(r'^profile/edit/id/(?P<pk>\d+)$', views.profile_edit, name='profile'),
    url(r'^freelancer/id/(?P<pk>\d+)$', views.seefreelancer, name='seefreelancer'),
    url('profile/', views.profile, name='profilepage'),
    # # By username
    # url(r'^profile/username/(?P<slug>[\w.@+-]+)/$', views.profile, name='profile'),
    path('post/', views.post, name='post'),
    path('post/edit/<int:job_id>', views.post_edit, name='post_edit'),
    url('post/thankyou', views.thank_you_post_job, name='thank_post'),
    url(r'^delete/(?P<id>\d+)/$', views.post_delete, name='delete'),
    url(r'^delete/(?P<id>\d+)/$', views.candidate_delete, name='candidate_delete'),
    path('credits/', views.credits, name='credits'),
    path('orders/', views.orders, name='orders'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('withdraw/successful', views.withdraw_succesful, name='withdraw_successful'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacypolicy/', views.privacypolicy, name='privacypolicy'),
    path('checkout/', views.checkout, name='checkout'),
    # path('checkout/paymentmode', views.checkoutpayment, name='checkoutpayment'),
    path('checkout_confirmation/', views.make_payment, name='make_payment'),
    path('checkout_confirmation/success', views.confirmation, name='confirmation'),
    path('checkout_confirmation/success/<str:test>', views.confirmation, name='confirmation'),
    path('invoice/', views.invoice, name='invoice'),
    path('invoice/<str:invoice_id>', views.invoice, name='invoice'),
    url('accounts/login/', views.logins, name='logins'),
    url('loginpage/', views.loginpage, name='loginpage'),
    url('social_login/', views.sociallogin, name='sociallogin'),
    url('logout/', views.logouts, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/data?$', views.signup_det, name='signup_det'),
    path('password_reset/',
       auth_views.PasswordResetView.as_view(template_name='registration/passwordreset/password_reset_form.html',),
       name='password_reset_form'),
    path('password_reset/done/',
       auth_views.PasswordResetDoneView.as_view(template_name='registration/passwordreset/password_reset_done.html'),
       name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
      template_name='registration/passwordreset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
      template_name='registration/passwordreset/password_reset_complete.html'), name='password_reset_complete'),

   path('chat', views.chat_view, name='chats'),
   path('chat/<int:sender>/<int:receiver>', views.message_view, name='chat'),
   path('api/messages/<int:sender>/<int:receiver>', views.message_list, name='message-detail'),
   path('api/messages', views.message_list, name='message-list'),
   path('api/users/<int:pk>', views.user_list, name='user-detail'),
   path('api/users', views.user_list, name='user-list'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
