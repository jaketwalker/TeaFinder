"""
    admin.py
    Purpose: define functionality of the website admin site
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from django.contrib import admin
from .models import TeaTypes, Sources

# Allow admin to edit via webpage the following database tables:
admin.site.register(TeaTypes)
admin.site.register(Sources)

# TeaFinder_admin
# CommuniTea