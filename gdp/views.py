from django.shortcuts import render 
from django.db.models import Max, Min
from gdp.models import GDP
import math

from bokeh.models import ColumnDataSource, NumeralTickFomatter, HoverTool
from bokeh.embed import components 
from bokeh.plotting import figure 

# Create your views here.
def index(request):
    # define which year we want the data form
    max_year = GDP.objects.aggregate(max_yr=Max('year'))['max_yr']
    min_year = GDP.objects.aggregate(min_yr=Min('year'))['min_yr']
    year = request.GET.get('year', max_year)
    
    # define number of country to fetch
    count = int(request.GET.get('count', 10))
    
    gdps = GDP.objects.filter(year=year).order_by('gdp').reverse()[:count] 
    
    country_names = [d.country for d in gdps]
    country_gdps = [d.gdp for d in gdps] 
    
    cds = ColumnDataSource(
        data=dict(country_names=country_names,country_gdps=country_gdps)
    )
    
    fig = figure(
        x_range=country_names, height=500, title=f"Top {count} GDPs ({year})"
    )
    fig.title.align='center'
    fig.title_text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFomatter(format='$0.0a')
    fig.xaxis.major_label_orientation = math.pi/4
    
    fig.vbar(source=cds, x='country_names', top='country_gdps', width=0.8) 
    
    # hover over barchart
    tooltips = [
        ('Country', '@country_names'),
        ('GDP', '@country_gdps{,}')
    ]
    fig.add_tools(HoverTool(tooltips=tooltips))
    script, div = components(fig) 
    
    # context data
    context = {
        'script': script,
        'div': div,
        'years': range(min_year, max_year + 1),
        'count': count,
        'year_selected': year
    } 
    
    if request.htmx: 
        return render(request, 'partials/gdp-bar.html', context) 
    
    return render(request, 'index.html', context)