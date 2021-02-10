from django.shortcuts import render_to_response
from .forms import *
from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import messages
import request
from django.http import JsonResponse
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.views.generic.detail import DetailView
from django.views.generic import CreateView
from django.template import RequestContext
from notifications.signals import notify
from django.core.mail import send_mail, send_mass_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
# importing uuid
import uuid
import os
# Create your views here.
import re

# Refer paypal developer api for instructions on how to generate client id and secret key -
# https://developer.paypal.com/docs/api/overview/#get-credentials
PAYPAL_SECRET = "EDxFZu110OtKR7D7jPWN2fKYfm1a8APgO-1qQmKUU5rB5tN1PKIqp9VxZS8RnOgva97B5SWwvTINunzr"
PAYPAL_CLIENT_ID = "AYZZeh8LtcExCAzPTE0683MKaDGpRAe6z5yZYGIeaSbhlf9OfUII8-9PXjqNiiYpQuOMc62PeN-eYPNY"
PAYPAL_BUSINESS_ID = "sb-uke47y2386062@business.example.com"

from paypalpayoutssdk.core import PayPalHttpClient, SandboxEnvironment,LiveEnvironment
from paypalpayoutssdk.payouts import PayoutsPostRequest
from paypalhttp import HttpError

# Creating Access Token for Sandbox
client_id = PAYPAL_CLIENT_ID # https://developer.paypal.com/docs/integration/admin/manage-apps/
client_secret = PAYPAL_SECRET # https://developer.paypal.com/docs/integration/admin/manage-apps/
# Creating an environment
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret) # sandbox or live (Use LiveEnvironment in production)
client = PayPalHttpClient(environment)

def home(request):
    return render(request, 'home/index.html')

@login_required()
def credits(request):
    return render(request, 'dashboard/credits.html', {"title": "Credits"})

from django.views.decorators.csrf import csrf_protect
@csrf_protect
def bookmark(request):
    if request.method == 'POST':
        classname = request.POST.get('data1')
        # print(classname)
        jobid = request.POST.get("data2")
        # print(jobid)
        result = classname.find("bookmarked")
        # print(result)
        post = get_object_or_404(Post, id=jobid)
        user = get_object_or_404(User, id=request.user.id)
        c = Bookmark.objects.filter(user=user, job=post)
        if c is not None:
            if result == 14:
                save_info = Bookmark.objects.create(user=user, job=post)
                # print(save_info)
            else:
                Bookmark.objects.get(user=user, job=post).delete()
    bookmarks = Bookmark.objects.filter(user=request.user)
    # for bookmark in bookmarks:
    #     print(bookmark.user.post.values())
    return render(request, 'dashboard/bookmarks.html', {"title": "Bookmarks", "bookmarks":bookmarks})


def manage_candidates(request):
    # print(Profile.objects.all(user=request.user))
    # print(Profile.objects.all())
    created = Post.objects.filter(user=request.user)
    # for i in created:
        # for j in i.applicants.all():
        #     # print(j.user.accepted_user)
    if "completed" in request.POST:
        post_id = request.POST.get('accept')
        freelancer_id = request.POST.get('user')
        # print(freelancer_id)
        post = get_object_or_404(Post, id=post_id)
        user = get_object_or_404(User, id=int(freelancer_id))
        Post.objects.filter(user=request.user, id=post_id).update(is_completed=True)
        notify.send(User.objects.get(email='ak@gmail.com'), recipient=user,
                    verb='Congratulations! You have been marked the Job as completed!')
        notify.send(User.objects.get(email='ak@gmail.com'), recipient=request.user,
                    verb='Congratulations! You have successfully completed the job.')
        success = "You have successfully marked the offer complete!"
        return render(request, 'dashboard/manage_candidates.html', {"dic": success})

    elif "reviews" in request.POST:
        post_id = request.POST.get('accept_review')
        freelancer_id = request.POST.get('user_review')
        review = request.POST.get('review')
        rating = request.POST.get('rating')
        on_budget = request.POST.get('on_budget')
        on_time = request.POST.get('on_time')
        post = get_object_or_404(Post, id=post_id)
        user = get_object_or_404(User, id=int(freelancer_id))
        Accepted.objects.filter(user=user, accept=post).update(review=review, rating=rating, on_budget=on_budget
                                                               ,on_time=on_time)
        success = "You have successfully marked the offer complete!"
        return render(request, 'dashboard/manage_candidates.html', {"dic": success})

    else:
        if request.method == 'POST':
            post_id = request.POST.get('accept')
            freelancer_id = request.POST.get('user')
            # print(freelancer_id)
            terms = request.POST.get('terms')
            #creating particular instances of post and user to save
            post = get_object_or_404(Post, id=post_id)
            user = get_object_or_404(User, id=int(freelancer_id))
            second = Applicant.objects.filter(user=request.user,job=post).update(is_accepted=True)
            Post.objects.filter(user=request.user, id=post_id).update(is_approved=True)
            notify.send(User.objects.get(email='ak@gmail.com'), recipient=user, verb='Congratulations! You have been offered a job for __')
            notify.send(User.objects.get(email='ak@gmail.com'), recipient=request.user,
                        verb='Congratulations! You have accepted the job proposal')
            # For freelancer
            subject = 'HIRE-ME: Job Accepted'
            html_message = render_to_string('email-job-accepted-freelancer.html',)
            plain_message = strip_tags(html_message)
            from_email = 'saiciitvns@gmail.com'
            to = str(user)
            send_mail(
                subject,
                plain_message,
                from_email,
                [to],
                html_message=html_message,
                fail_silently=False,
            )
            success = "You have successfully accepted a Job Form"
            return render(request, 'dashboard/manage_candidates.html', {"dic":success})
    return render(request, 'dashboard/manage_candidates.html', {"title": "Manage Candidates"})

# FUTURE WORK - DELETE CANDIDATE WHO IS ACCEPTED AND APPLIED
def candidate_delete(request, id):
    candidate_to_delete = get_object_or_404(Applicant, pk=id).delete()
    return redirect('managejobs')

def managejobs(request):
    # jobs = Applicant.applicants.filter(user=request.user)
    created_jobs = Post.objects.filter(user=request.user)
    # number = Applicant.applicants.filter(user=request.user)
    return render(request, 'employer/manage_jobs.html', {"title": "Manage Jobs", "created_jobs":created_jobs})

@login_required
def seefreelancer(request,pk):
    users = User.objects.get(pk=pk)
    files = users.profile.profile_file.values()
    c = users.profile.skills.split(',')
    accepteds = Accepted.objects.filter(user=request.user)
    # print(accepteds)
    # print(dict(item.split(',') for item in users.profile.skills))
    return render(request, 'employer/seefreelancerprofile.html',{"users":users,"dic":c,"files":files,"accepteds":accepteds})

def baseprofile(request):
    # jobs = Applicant.objects.filter(user=request.user).count()
    # created_jobs = Post.objects.filter(user=request.user).count()
    # number = Applicant.objects.filter(user=request.user,)
    return render(request, 'dashboard/baseprofile.html', {"title": "Base"})

def notification(request):
    return render(request, 'dashboard/notifications.html', {"title": "Notifications"})

# -----------------------------------------LOGIN AND SIGNUP-----------------------------------------------------#

def loginpage(request):
    c = request.get_full_path
    if request.user.is_authenticated:
        next_url = request.GET.get('next', None)  # if user authenticated catch the next parameter in the url pattern and redirect.
        request.session['next_url'] = next_url
        return HttpResponseRedirect(next_url)
    else:
        next_url = request.GET.get('next', None)  # if user not authenticated catch the next parameter and store in session.
        request.session['next_url'] = next_url
        return render(request, 'registration/pages-login.html', {"title": "Login", 'url_redirect': c})

def logins(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        match = User.objects.filter(email=email)
        if match.exists():
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user.username = user.email
                user = User.objects.filter(email=request.user)
                c = request.session.pop('next_url', None)
                if c is not None:
                    return HttpResponseRedirect(c)
                else:
                    # Redirect to a success page.
                    # cred = Profile.objects.get(user=request.user)
                    # cred.credits = 100
                    # cred.save()
                    return HttpResponseRedirect('/profile/' + 'id/' + str(request.user.id))
            else:
                return render(request, 'registration/pages-login.html', {'title': 'LOGIN',
                                                                            'message': "Password dosen't match. Click on forgot password to reset your password"})

        else:
            return render(request, 'registration/pages-login.html', {'title': 'LOGIN',
                                                                         'message': "User Does not exist. Please create a new account"})
    return render(request, 'registration/pages-login.html', {"title": "Login"})


def logouts(request):
    logout(request)
    # Redirect to a success page.
    return render(request,'home/index.html', {'request': request})

from django.contrib.auth.hashers import make_password

def signup(request):

    if request.method == 'POST':
        form = SignUpFormone(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            request.session['email'] = email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return redirect('signup_det')
        else:
            return render(request, 'registration/pages-register.html',{
                'error': 'Form not valid',
                # 'messages': form.error_messages,
                # 'cleaned_data': form.cleaned_data,
                'form': form,
            })
    else:
        form = SignUpFormone()
    return render(request, 'registration/pages-register.html', {'form': form})

def signup_det(request):
    if request.user.is_authenticated:
        return redirect('sociallogin')
    else:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            # print(form.errors)
            if form.is_valid():
                email = request.session.pop('email', None)
                raw_password = form.cleaned_data.get('password1')
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                raw_pass = make_password(raw_password)
                role = request.POST.get('role')
                # print(role)
                c = User.objects.create(first_name=first_name, last_name=last_name, password=raw_pass, email=email, role=role, username=email)
                user = authenticate(email=email, password=raw_password)
                login(request, user)
                # user = request.user
                # cred = Profile.objects.get(user=request.user)
                # cred.credits = 100
                # cred.save()
                return redirect('/profile/' + 'id/' + str(request.user.id))
            else:
                return render(request, 'registration/pages-register.html',{
                    'error': 'Form not valid',
                    'messages': form.error_messages,
                    'form': form,
                })
        else:
            form = SignUpForm()
    return render(request, 'registration/pages-register-2.html', {'form': form})

from django.db import IntegrityError
@login_required()
def sociallogin(request):
    if request.user.role == None:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            try:
                if form.is_valid():
                    email = request.user
                    raw_password = form.cleaned_data.get('password1')
                    raw_pass = make_password(raw_password)
                    role = request.POST.get('role')
                    username = str(request.user)
                    c = User.objects.create(first_name=request.user.first_name, last_name=request.user.last_name,
                                            password=raw_pass, email=email, role=role, username=username)
                    return redirect('/profile/' + 'id/' + str(request.user.id))
            except IntegrityError:
                print('yo')
                if form.is_valid():
                    email = request.user
                    raw_password = form.cleaned_data.get('password1')
                    raw_pass = make_password(raw_password)
                    role = request.POST.get('role')
                    username = str(request.user)
                    User.objects.filter(email = request.user).update(role=role, password = raw_pass, username=username)
                    user = authenticate(email=email, password=raw_password)
                    login(request, user)
                    return redirect('/profile/' + 'id/' + str(request.user.id))
                else:
                    # print('yo')
                    return redirect('/profile/' + 'id/' + str(request.user.id))

        else:
            form = SignUpForm()
    else:
        return redirect('/profile/' + 'id/' + str(request.user.id))
    return render(request, 'registration/social_login.html', {'form': form})

# -----------------------------------------LOGIN AND SIGNUP END-----------------------------------------------------#


@login_required()
def findjob(request):
    jobs = Post.objects.all()
    paginator = Paginator(jobs, 2) # Show 2 contacts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'findjob/job_list.html', {"title": "Find A Job","jobs":jobs,'page_obj': page_obj})

from django.db.models import Q
def search(request):
    type = request.GET.getlist('type')
    category = request.GET.getlist('category')
    type.extend([5, 6, 7, 8])
    category.extend([5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # print(type, category)
    if type or category:
        jobs = Post.objects.filter(Q(type=type[0]) | Q(type=type[1]) | Q(type=type[2]) | Q(type=type[3]) |
        Q(category=category[0]) | Q(category=category[1]) | Q(category=category[2]) | Q(category=category[3]) |
        Q(category=category[4]) | Q(category=category[5]) | Q(category=category[6]) | Q(category=category[7]) |
        Q(category=category[8]) | Q(category=category[9]))
        return render(request, 'findjob/job_list.html', {"title": "Find A Job", "jobs": jobs, })
    return render(request, 'findjob/job_list.html')

from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.urls import resolve


# class jobpage(CreateView):
#     model = Applicant
#     form_class = Applyjob
#     slug_field = 'job_id'
#     slug_url_kwarg = 'job_id'

def jobpage(request, slug=None, job_id=None):
    posts = Post.objects.get(id=job_id)
    # print(job_id)
    # Skill tags for job post
    try:
        c = posts.tags.split(',')
    except AttributeError:
        c = ""
    # Get job data by using custom filters
    get_post = Post.objects.filter(id=job_id)
    job = get_object_or_404(Post, id=job_id)
    applicant = Applicant.objects.filter(job=job)
    exist = []
    if Applicant.objects.filter(job=job, user=request.user).exists():
        exist.append("yes")
    else:
        exist.append("no")
    # print(exist)
    # POST REQUEST
    if request.method == 'POST':
        form = Applyjob(request.POST, request.FILES, instance=request.user)
        postform = Postjob(request.POST, instance=request.user)
        if form.is_valid() and postform.is_valid():
            email = request.POST.get('email')
            cv = request.POST.get('cv')
            post_id = request.POST.get('job')
            Applicant.objects.create(email=email, cv=cv, user=request.user,job=Post.objects.get(id=post_id))
            #freelancer credits
            cred = User.objects.get(email=request.user)
            cred.credits = cred.credits - 50
            freelancer_credits = cred.credits
            cred.save()
            #admin credits
            cred_admin = User.objects.get(email='ak@gmail.com')
            cred_admin.credits = cred_admin.credits + (freelancer_credits-50)
            admin_credits = cred_admin.credits
            cred_admin.save()
            #employer credits
            # cred_employer_post_obj = Post.objects.get(id=post_id).user
            # cred_employer = User.objects.get(email=cred_employer_post_obj)
            # cred_employer.credits = credits +
            notify.send(User.objects.get(email='ak@gmail.com'), recipient=request.user,
                        verb='Congratulations! You have successfully applied for the job!')

            return render(request, 'findjob/job_page.html', {"applicant":applicant,"dic": 'You have successfully applied for the Job!',"jobs":get_post,"dics":c,"exist":exist},job_id)

    return render(request, 'findjob/job_page.html', {"title": "Job Page","applicant":applicant ,"jobs":get_post, "dics": c,"exist":exist}, job_id)


def contact(request):
    if request.method == 'POST':
        form = Contactform(request.POST)
        # print(form)
        if form.is_valid():
            print('hi')
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            Contact.objects.create(name=name,email=email,subject=subject,message=message)
            return render(request, 'contact.html', {"contact": "Your response has been recorded!"})

    return render(request, 'contact.html', {"title": "Contact Us"})

def privacypolicy(request):
    return render(request, 'privacypolicy.html', {"title": "Privacy Policy"})

# ---------------------------------------ORDERS AND CREDIT MANAGEMENT----------------------------------------------#

def pricing(request):
    return render(request, 'Transactions/pricing_plans.html', {"title": "Pricing"})

@login_required()
def checkout(request):
    all_payments = PaymentRefill.objects.all()
    all_products = Product.objects.all()
    coupons = Coupon.objects.all()
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        list_coupons = []
        for i in coupons:
            list_coupons.append(i.coupon)
            list_coupons.append(i.discount)
        # print(list_coupons)
        if coupon in list_coupons:
            index = list_coupons.index(coupon)
            coupon_dict =  dict(coup=coupon, disc=list_coupons[index+1])
            # print(coupon_dict)
            return render(request, 'Transactions/checkout_page.html',
                          {"title": "Coupon successfully applied!", 'all_products': all_products, "coupons": coupon_dict,"all_payments":all_payments})
        else:
            return render(request, 'Transactions/checkout_page.html',
                          {"title": "Coupon failed!", 'all_products': all_products,"all_payments":all_payments, "message":"No such coupon exists. Please try again with another coupon code." })
    return render(request, 'Transactions/checkout_page.html', {'all_products':all_products, "all_payments":all_payments})

# def checkoutpayment(request):
#
#     return render(request, 'checkout_payment_mode.html', {"title": "Checkout",})

@login_required()
def make_payment(request):
    data = []
    if request.method == 'POST':
        dat = request.POST.get('plan')
        total_price = request.POST.get("total_price")
        coupon_send = request.POST.get("coupon_send")
        # print(coupon_send)
        # print(total_price)
        if dat == "yearly":
            data.append(str(total_price).replace('$',''))
            data.append("Yearly Cost")
        else:
            data.append(str(total_price).replace('$',''))
            data.append("Monthly Cost")

    # creating an instance of
    # uuid object
    test = uuid.uuid4()
    # print(test)
    # Create coupon instance
    coupon = get_object_or_404(Coupon, coupon=coupon_send)
    order_object = Order.objects.create(plan=data[1], total_cost=round(float(int(data[0]))),
                                        user=request.user, invoice_id=test, coupon=coupon)
    paypal_dict = {
        "business": "sb-2hj611803780@business.example.com",
        "amount": str(round(int(float(data[0])))),
        "item_name": data[1],
        "invoice": test,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('confirmation', args=[str(test)])),
        "cancel_return": request.build_absolute_uri(reverse('checkout')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }
    # Create the instance.
    form = ExtPayPalPaymentsForm(initial=paypal_dict)
    dic = {'name':data[1], 'price': str(round(int(float(data[0]))))}
    # print(dic)
    return render(request, 'Transactions/checkout_confirmation.html', {"form": form, 'dic':dic})

@login_required()
def confirmation(request, test=None):
    return render(request, 'Transactions/order_confirmation.html', {"title": "Confirmation", "test":test})


from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from forex_python.converter import CurrencyRates # module imported from django-forex
@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        order = get_object_or_404(Order, invoice_id=ipn.invoice)

        # Add credits equivalent to the amount:
        c = CurrencyRates()
        dollar_to_inr = c.get_rate('USD', 'INR')
        cred = User.objects.get(email=order.user)
        cred.credits = order.total_cost*dollar_to_inr
        cred.save()

        if order.total_cost == ipn.mc_gross:
            # mark the order as paid
            order.is_completed = True
            order.save()


@csrf_exempt
def invoice(request, invoice_id=None):
    orders = Order.objects.get(invoice_id=invoice_id)
    return render(request, 'Transactions/invoice.html', {"title": "Invoice", "order":orders})


@login_required()
def orders(request):
    return render(request, 'Transactions/orders.html', {"title": "Orders"})


import requests
@login_required()
def withdraw(request):

# For checking user account for validation -
# https://www.paypal.com/in/smarthelp/article/how-do-i-grant-access-to-addressverify-or-getverifiedstatus-to-a-third-party-ts1161

    if request.method == "POST":

        amount_in_credits = request.POST.get("amount_in_credits")
        paypal_id = request.POST.get("paypal_id")
        amount_in_credits = int(amount_in_credits)
        if request.user.credits < amount_in_credits:
            return render(request, 'Transactions/withdraw_amount_page.html', {"message": "You don't have sufficient credits for this transaction"})
        else:
            c = Withdraw.objects.create(paypal_id=paypal_id, amount_in_credits=amount_in_credits)
            # print(c.pk)
            body = {
                "sender_batch_header": {
                    "email_message": "SDK payouts test txn",
                    "note": "Enjoy your Payout!!",
                    "sender_batch_id": "Test_Payemnt_" + str(c.pk),
                    "email_subject": "This is a test transaction from SDK"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "note": f"Your {amount_in_credits / 70}$ Payout!",
                    "amount": {
                        "currency": "USD",
                        "value": round(amount_in_credits / 70, 2)
                    },
                    "receiver": paypal_id,
                    "sender_item_id": "Test_txn_1"
                }, ]
            }
            req = PayoutsPostRequest()
            req.request_body(body)

            try:
                # Call API with your client and get a response for your call
                response = client.execute(req)
                # If call returns body in response, you can get the deserialized version from the result attribute of the response
                batch_id = response.result.batch_header.payout_batch_id
                # print(batch_id)
                if batch_id:
                    # Update User credits
                    cred = User.objects.get(email=request.user)
                    cred.credits = cred.credits - amount_in_credits
                    cred.save()
                    c.user = request.user
                    c.batch_id = batch_id
                    c.save()
                    # Withdraw.objects.create(amount_in_credits=amount_in_credits, paypal_id=paypal_id, user=request.user,
                    #                         batch_id=batch_id)
                    return render(request, 'Transactions/withdraw_successful.html', {'title': "Withdraw Successful"})
            except IOError as ioe:
                # print(ioe)
                if isinstance(ioe, HttpError):
                    # Something went wrong server-side
                    print(ioe.status_code)
                    return render(request, 'Transactions/withdraw_amount_page.html', {"title": "Withdraw"})

    return render(request, 'Transactions/withdraw_amount_page.html', {"title": "Withdraw"})

@login_required()
def withdraw_succesful(request, test=None):
    return render(request, 'Transactions/withdraw_successful.html', {'title': "Withdraw Successful"})

# -----------------------------------ORDERS AND CREDIT MANAGEMENT END----------------------------------------------#

@login_required()
def appliedjobs(request):
    return render(request, 'dashboard/appliedjobs.html', {"title": "Confirmation"})

def terms(request):
    return render(request, 'terms.html', {"title": "Terms and Conditions"})


# -------------------------------------------------- POST A JOB--------------------------------------------------------#

# view of Job Post page
@login_required()
def post(request, job_id=None):
    if request.method == 'POST':
        # user_form = UserForm(request.POST, instance=request.user)
        jobpost_form = Postjob(request.POST, request.FILES)
        # print(jobpost_form.errors)
        if jobpost_form.is_valid():
            title = request.POST.get('title')
            type = request.POST.get('type')
            category = request.POST.get('category')
            location = request.POST.get('location')
            min_salary = request.POST.get('min_salary')
            max_salary = request.POST.get('max_salary')
            tags = request.POST.get('tags')
            description = request.POST.get('description')
            company = request.POST.get('company')
            deadline = request.POST.get('deadline')
            # print(company)
            # created_date = request.POST.get('created_date')
            # published_date = request.POST.get('published_date')
            file_one = request.POST.get('file_one')
            # if Post.objects.get(user=request.user):
            Post.objects.create(user=request.user, title=title, type=type, category=category,
                                              location=location,
                                              min_salary=min_salary, max_salary=max_salary, tags=tags,
                                              description=description,
                                              file_one=file_one, id=job_id, company=company)
            # else:
            # c = Post.objects.get(user=request.user, title=title,tags=tags,description=description,
            #                                   file_one=file_one, company=company, type=type, category=category,
            #                                   location=location).id
            # using django-notifications-hq
            notify.send(User.objects.get(email='ak@gmail.com'), recipient=request.user,
                        verb='Congratulations! You have successfully posted a job - ' + title)
            return HttpResponseRedirect('/post/thankyou')
    return render(request, 'dashboard/post_a_job.html', {"title": "Post A Job", })

# view of Edit the Post Page
def post_edit(request, job_id=None):
    if job_id:
        f = Post.objects.get(pk=job_id)
    else:
        f = None
    if request.method == 'POST':  # If the form has been submitted
        form = Postjob(request.POST, request.FILES, instance=f)
        if form.is_valid():
            form.save()
            return
    else:
        form = Postjob(instance=f)  # An unbound form
    return render(request, 'dashboard/post_a_job.html', {'form': form})


def thank_you_post_job(request):
    return render(request, 'dashboard/post_a_job.html', {"message": "Job Post Success!", })


def post_delete(request, id):
    post_to_delete = get_object_or_404(Post, pk=id).delete()
    return redirect('managejobs')


# --------------------------------------------------- PROFILE---------------------------------------------------------#

# class profile(DetailView):
#     model = Profile
#     slug_field = "username"
#     template_name = "dashboard/profile.html"

@login_required()
def profile(request):
    profiles = Profile.objects.filter(user=request.user)
    # for i in profiles:
        # print(i.skills)
    return render(request, 'dashboard/profile.html',{"profiles":profiles,"file":request.user.profile.profile_file.all()})

@login_required
@transaction.atomic
def profile_edit(request, pk):
    user = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        file_form = ProfileFile(request.POST, request.FILES)
        files = request.FILES.getlist('file')  # field name in model
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        # print(profile_form.errors)
        if user_form.is_valid() and profile_form.is_valid():
            skills = profile_form.cleaned_data.get('skills')
            # print(skills)
            c = request.user.role
            # c = profile_form.cleaned_data.get('account_type')
            # print(c)
            feed_instance = profile_form.save(commit=False)
            feed_instance.user = user #Save the current user instance
            feed_instance.save()
            for f in files:
                # print(f)
                file_instance = File(file=f, user=feed_instance)
                file_instance.save()
            feed_instance = user_form.save()
            if c == 'freelancer':
                return redirect('findjob')
            else:
                return redirect('post')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        file_form = ProfileFile(instance=request.user)
    return render(request, 'dashboard/profile_edit.html', {
        "file":request.user.profile.profile_file.all(),
        'user_form': user_form,
        'profile_form': profile_form,
        'file_form':file_form
    },pk)

# ----------------------------------------------- ERROR MESSAGES------------------------------------------------------#

def handler404(request, exception, *args, template_path="Error Pages/404.html"):
    response = render_to_response(template_path)
    response.status_code = 404
    return response

def handler500(request):
    response = render_to_response("Error Pages/500.html")
    response.status_code = 500
    return response

# ----------------------------------------------- MESSAGE APP ---------------------------------------------------------#


from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from job.models import Message, UserProfile
from job.serializers import MessageSerializer, UserSerializer

@csrf_exempt
def user_list(request, pk=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        if pk:
            users = User.objects.filter(id=pk)
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': request})
        # print(serializer)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            user = User.objects.create_user(username=data['username'], password=data['password'])
            UserProfile.objects.create(user=user)
            return JsonResponse(data, status=201)
        except Exception:
            return JsonResponse({'error': "Something went wrong"}, status=400)


@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        # print(data)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


def chat_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":
        # post = Post.objects.filter(user=request.user).all()
        # dic ={}
        # for i in post:
        #     c = i.applicants.all()
        #     if c.exists():
        #         for i in c:
        #             c
        return render(request, 'chats/chat.html',
                      )
    return render(request, 'chats/chat.html')


def message_view(request, sender, receiver):
    if not request.user.is_authenticated:
        return redirect('index')
    if request.method == "GET":

        return render(request, "chats/messages.html",
                      {'users': User.objects.exclude(username=request.user),
                       'receiver': User.objects.get(id=receiver),
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                   Message.objects.filter(sender_id=receiver, receiver_id=sender)})



# ----------------------------------------------- MESSAGE APP END------------------------------------------------------#
