from .models import *
def job_post(request):
    if request.user.is_authenticated:
        created_job = Post.objects.filter(user=request.user).count()
        created  = Post.objects.filter(user=request.user)
        applied_jobs = request.user.applicant.all()
        users = User.objects.values()
        user = User.objects.get(email=request.user)
        notifications = user.notifications.all()
        orders = Order.objects.all()
        orders_count = Order.objects.filter(user=request.user).count()
        list_job_id = []
        bookmarks = Bookmark.objects.filter(user=request.user)
        # jobs = Post.objects.all()
        for i in bookmarks:
            list_job_id.append(i.job_id)
        return {
            "created_job": created_job,
            "applied_jobs":applied_jobs,
            "created":created,
            "users":users,
            "notifications":notifications,
            "bookmarks": bookmarks,
            "list": list_job_id,
            "orders":orders,
            "orders_count":orders_count,
        }
    return{
            "hello":"hey"
        }
