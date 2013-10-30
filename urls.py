from django.conf.urls.defaults import patterns, include, url
from .views import *
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

tournament_patterns = patterns('',
    # admin
    #url(r'^admin/', include(admin.site.urls)),

    # tournament urls
    #url(r'^load_judges/',  login_required(load_judges_view), name='load_judges'),
    #url(r'^load_competitors/',  login_required(load_competitors_view), name='load_competitors'),
    url(r'^register/',  login_required(register_view), name='register'),
    url(r'^vote/',  login_required(vote_view), name='vote'),
    url(r'^',      login_required(info_view), name='default'),
)

urlpatterns = patterns('',
    url(r'^load_brackets/',  login_required(load_brackets_view), name='load_brackets'),
    url(r'^load_judges/',  login_required(load_judges_view), name='load_judges'),
    url(r'^load_competitors/',  login_required(load_competitors_view), name='load_competitors'),
    url(r'^(?P<bracket>[a-z0-9\-]+)/',  include(tournament_patterns, namespace='tourney')),
    url(r'^',                   login_required(tournament_selector_view), name='default'),
)

