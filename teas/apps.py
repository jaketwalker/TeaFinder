"""
    apps.py
    Purpose: define Django apps
    
    Created By: Jake Walker
    Created Date: 12/8/2016
    Notes: Created first app containing "teas" - the base TeaFinder
"""

from django.apps import AppConfig


class TeasConfig(AppConfig):
    name = 'teas'
