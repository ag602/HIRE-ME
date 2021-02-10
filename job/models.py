# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
from job.managers import UserManager
from django.db.models import Count, F, Value


# FOR EXTENDING USER MODEL AND MULTI USER TYPES -
# https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html

# FOR USER ONLINE/OFFLINE SHOW (using django memcached) -
# http://www.djangocurrent.com/2011/07/django-using-cashing-to-track-online.html

class User(AbstractUser):
    # username = None
    role = models.CharField(max_length=12, blank=True, null=True, error_messages={
        'required': "Account Type must be provided"
    })
    email = models.EmailField(unique=True, blank=False, null=True,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              })
    username = models.CharField(max_length=100, null=True, blank=True)
    credits = models.BigIntegerField(null=True, blank=True, default=100)
    # online = models.CharField(max_length=100, null=True, blank=True)
    # last_seen = models.CharField(max_length=100, null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def last_seen(self):
        return cache.get('seen_%s' % self.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                    seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    def __str__(self):
        return str(self.email)

    objects = UserManager()

class Contact(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    message = models.CharField(max_length=10000, null=True, blank=True)

class Product(models.Model):
    name = models.CharField(max_length=191)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    slug = models.SlugField()
    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post', null=True, blank=True,)
    title = models.CharField(max_length=200, null=True, blank=True)
    company = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=500,  null=True, blank=True)
    category = models.CharField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    deadline =  models.DateField( null=True, blank=True,)
    min_salary = models.CharField(max_length=500, null=True, blank=True)
    max_salary = models.CharField(max_length=500,  null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True,)
    file_one = models.FileField(upload_to='Jobpost/%Y/%m/%d/',null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    # slug = models.SlugField(null=True,blank=True)
    #
    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(Post, self).save(*args, **kwargs)
    # file_two = models.FileField(upload_to='Jobpost/%Y/%m/%d/', null=True, blank=True,)
    #
    # def publish(self):
    #     self.published_date = timezone.now()
    #     self.save()

    def __str__(self):
        return str(self.title)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_bookmark")
    job = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='job_bookmark', null=True, blank=True,)

    def __str__(self):
        return str(self.job)

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    print(instance.user.user.email)
    return 'applications/%s/%s' % (instance.user.user.email, filename)

class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,related_name="applicant")
    email = models.CharField(max_length=200, null=True, blank=True)
    job = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='applicants', null=True, blank=True,)
    applied_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    cv = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    # applicants = models.Manager()
    def __str__(self):
        return self.user.email


class Accepted(models.Model):
    accept = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='accepted_job_name')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='accepted_user')
    terms = models.CharField(max_length=10, null=True, blank=True)
    review = models.CharField(max_length=20000, null=True, blank=True)
    on_time = models.CharField(max_length=3, null=True, blank=True)
    rating = models.CharField(max_length=3, null=True, blank=True)
    on_budget = models.CharField(max_length=3, null=True, blank=True)
    review_created_at = models.DateTimeField(default=timezone.now, null=True, blank=True, )
    def __str__(self):
        return str(self.accept)


class Coupon(models.Model):
    coupon = models.CharField(max_length=200, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return str(self.coupon)

class PaymentRefill(models.Model):
    plan = models.CharField(max_length=200, null=True, blank=True)
    money = models.IntegerField(null=True, blank=True)
    vat = models.IntegerField(null=True, blank=True)
    total = models.IntegerField(null=True, blank=True)

import uuid
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_payment')
    # paypal_ipn = models.ForeignKey(, on_delete=models.CASCADE, null=True, blank=True, related_name='user_payment')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True, related_name='coupon_name')
    total_cost = models.IntegerField(null=True, blank=True)
    plan = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    is_completed = models.BooleanField(default=False)
    def __str__(self):
        return "%s (%s)" %(self.user, self.invoice_id)

class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_withdraw')
    paypal_id = models.EmailField(blank=True, null=True,)
    amount_in_credits = models.IntegerField(blank=True, null=True)
    batch_id = models.CharField(max_length=20, null=True,blank=True)
    # sender_batch_id = models.AutoField(primary_key=True, default=1, verbose_name=id)

    # def __str__(self):
    #     return str(self.user)

def profile_pic(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    print(instance.user.email)
    return 'docs/images/%s/%s' % (instance.user.email, filename)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',db_index=True, null=True, blank=True)
    pic = models.FileField(upload_to=profile_pic,null=True,blank=True)
    skills = models.CharField(max_length=500, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    intro = models.TextField(max_length=500,null=True, blank=True)


def user_directory_path_one(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    print(instance.user.user.email)
    return 'docs/%s/%s' % (instance.user.user.email, filename)

class File(models.Model):
    file = models.FileField(upload_to=user_directory_path_one,null=True,blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='profile_file')

# Now we are hooking the create_user_profile and save_user_profile methods to the User model, whenever a save event occurs
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # creates model object with user instance
    if created:
        Profile.objects.create(user=instance)

  # if user object does not exist, then create the object and save the instance associated with the user object
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)
        instance.profile.save()


# ----------------------------------------------- MESSAGE APP ---------------------------------------------------------#
import datetime
from django.core.cache import cache


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)
# ----------------------------------------------- MESSAGE APP END------------------------------------------------------#
