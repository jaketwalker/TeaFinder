"""
    views.py
    Purpose: direct HTTP requests, perform web back-end logic
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import FloatField, ExpressionWrapper, F, Q
from functools import reduce
import operator

from teas.models import TeasSourcesView, TeaTypes, Tags, TeasTags
import teas.helpers.SearchFunctions as Search


def index(request):
    """Render homepage"""
    context = {
        "tea_types": TeaTypes.objects.order_by("TeaType")
    }
    return render(request, "teas/index.html", context)


def search_render_page(request):
    """Render basic search page"""
    context = {
        "tea_types": TeaTypes.objects.order_by("TeaType"),
        "tags": Tags.objects.order_by("TagName")
    }
    return render(request, "teas/search.html", context)


def search(request):
    """Perform search and render search results"""
    
    # Get search criteria from the posted values on the serach page
    search_text = request.POST["search_text"]
    tea_types = request.POST.getlist("tea_types")
    tags = request.POST.getlist("tags[]")
    
    # Parse the search text into its respective keywords.  
    search_text = Search.parse_search_text(search_text)
    
    # Get teas that match all criteria
    teas = TeasSourcesView.objects.all()
    
    # SEARCH STRING
    if len(search_text) > 0:
        teas = teas.filter(
            # http://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
            reduce(operator.and_, (Q(TeaDescription__icontains=criteria) for criteria in search_text))
            )
    
    # TEA TYPES
    if len(tea_types) > 0:
        teas = teas.filter(
            # http://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
            reduce(operator.or_, (Q(TeaTypeID__exact=int(criteria)) for criteria in tea_types))
            )
    
    # FILTER BY TAGS
    if len(tags) > 0:
        
        # Collect all teas that contain all of the selected tags:
        tea_id = {tea.TeaID for tea in TeasTags.objects.all()}
        for tag in tags:
            tea_id = {tea.TeaID for tea in TeasTags.objects.filter(TagID=int(tag)) if tea.TeaID in tea_id}
        
        # Then filter the tea set to the ones contained in the above results.  If no teas found with the list of tags, return 
        # no results
        if len(tea_id) == 0:
            teas = []
        else: 
            teas = teas.filter(
                    # http://stackoverflow.com/questions/4824759/django-query-using-contains-each-value-in-a-list
                    reduce(operator.or_, (Q(TeaID__exact=tea.ID) for tea in tea_id))
                    )
        
        # Sort the final results:
        if teas:
            teas = teas.annotate(ordering=ExpressionWrapper(F("CostOz") + 0, output_field=FloatField())).order_by("ordering", "TeaType")
    
    # Render the search results
    return tea_list(request, teas_query_set=teas)


def tea_list(request, tea_type="", teas_query_set=None):
    """Render list of teas from tea types, all teas, or serach results"""
    
    # Begin with an empty header to update later
    header = ""
    
    # If no teas are passed into the function (typically from a web search)
    if teas_query_set is None:
        # If tea type was passed in, filter teas by tea type and set the header accordingly
        if len(tea_type) > 0:
            teas_query_set = TeasSourcesView.objects \
                        .filter(TeaType=tea_type) \
                        .annotate(ordering=ExpressionWrapper(F("CostOz") + 0, output_field=FloatField())) \
                        .order_by("ordering", "TeaType")
                        
            # Pluralize for display purposes:
            header = tea_type + 's'
        
        else:
            # If tea type is also not specified, return all teas.
            teas_query_set = TeasSourcesView.objects \
                        .annotate(ordering=ExpressionWrapper(F("CostOz") + 0, output_field=FloatField())) \
                        .order_by("ordering", "TeaType")
                        
            # Display header for HTML
            header = "Tea List"
            
    # If a query set of teas passed in, display those teas.
    else:
        if len(teas_query_set) == 0:
            header = "No matches found"
        else:
            header = "Search Results"

    # Render the tea list page
    context = {
        "tea_list": teas_query_set,
        "tea_types": TeaTypes.objects.all().order_by("TeaType"),
        "tea_type_filter": header
    }
    return render(request, "teas/tealist.html", context)
