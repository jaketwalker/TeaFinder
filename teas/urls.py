"""
    urls.py
    Purpose: define URLs and regex for each website
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index, name="index"),
    url(r"tealist/(?P<tea_type>.*)$", views.tea_list, name="tealist"),
    url(r"search$", views.search_render_page, name="search"),
    url(r"search/results$", views.search, name="search_results")
]