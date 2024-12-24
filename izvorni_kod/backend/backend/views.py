from django.contrib.auth import logout
from django.http import HttpResponseRedirect

def custom_admin_logout(request):
    """
    Custom Logout View for Superusers.
    Ensures session is destroyed and redirects appropriately.
    """
    logout(request)
    return HttpResponseRedirect('/admin/login/')  # Redirect to admin login page
