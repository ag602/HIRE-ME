from django.contrib import admin
from .models import Post, Profile
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.
# admin.site.register(Post)


class AcceptedAdmin(admin.TabularInline):
    model = Accepted

class ApplicantAdmin(admin.TabularInline):
    model = Applicant

class FinalAdmin(admin.ModelAdmin):
   inlines = [ApplicantAdmin,AcceptedAdmin,]

admin.site.register(Post,FinalAdmin)
# class UserProfileInline(admin.StackedInline):
#     model = Profile
#
# class UserProfileAdmin(UserAdmin):
#     inlines = [ UserProfileInline,]
#
# admin.site.register(User, UserProfileAdmin)
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(Withdraw)

# admin.site.register(Applicant)

admin.site.register(File)
# admin.site.register(Accepted)
admin.site.register(Message)
admin.site.register(UserProfile)
admin.site.register(Coupon)
admin.site.register(PaymentRefill)
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Bookmark)