# Jobportal

**A Django powered Job portal - HIRE ME**

Project working directory structure-

```
.gitignore
job/
   static/
   templates/
   __init__.py
   admin.py
   apps.py
   forms.py
   models.py
   tests.py
   urls.py
   views.py
Jobportal/
         __init__.py
         settings.py
         urls.py
         wsgi.py
manage.py
README.md
requirements.txt
```

## Requirements

- Python 3.6+

## Test Locally

- `git clone https://github.com/ag602/Jobportal.git`
- `cd Jobportal`
- `Make virtual env`
- `pip install -r requirements.txt`
- `Setup postgres on the system`
- `python3 manage.py makemigrations` and `python3 manage.py migrate`
- `python manage.py runserver`

## PAYPAL REST API Setup

- Log into the Developer Dashboard(https://www.paypal.com/signin?returnUri=https%3A%2F%2Fdeveloper.paypal.com%2Fdeveloper%2Fapplications) with your PayPal account credentials. If you don't have an account, you can click on the sign up option
- On My Apps & Credentials, use the toggle to switch between live and sandbox testing apps
- Navigate to the REST API apps section and click Create App
- Type a name for your app and click Create App. The app details page opens and displays your credentials
- Copy and save the client ID and secret for your app
- Review your app details and save your app
- Go to views.py
- Change SandboxEnvironment to LiveEnvironment and add the credentials(PAYPAL_SECRET & PAYPAL_CLIENT_ID) generated above
- For more help, refer to - https://github.com/paypal/Payouts-Python-SDK

## Libraries/Frameworks used

- For notifications: [django-notifications-hq](https://github.com/django-notifications/django-notifications)
- For Personal Messages: [djangorestframework](https://www.django-rest-framework.org/)
- For Paypal Payments: [django-paypal](https://django-paypal.readthedocs.io/en/stable/)
- For Paypal Payouts: [Payouts-Python-SDK](https://github.com/paypal/Payouts-Python-SDK)
- For Social Login: [social_django](https://python-social-auth.readthedocs.io/en/latest/configuration/django.html)

## Future Work

- Help texts to guide the customers for clarity of a feature
- How it Works? - Should deliver more information for users to know how actually the site works
- Payment Modes, apart from Paypal should work
- Credit management feature more robust and trustable
- Email alerts for a particular search and sorting in Jobs
- Location search Google Maps and Places API Credits
- Share the Job with friends on social media
- Similar Jobs in Job Page
- Credit transaction history
- Messages Dashboard and code improvisation

