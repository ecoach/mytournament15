from django.conf.urls.defaults import patterns, include, url
from .views import *
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

tournament00_patterns = patterns('',
    # admin
    #url(r'^admin/', include(admin.site.urls)),

    # tournament urls
    url(r'^vote/',  login_required(vote00_view), name='vote'),
    url(r'^',      login_required(info00_view), name='default'),
)

urlpatterns = patterns('',
    url(r'^(?P<bracket>\d+)/',  include(tournament00_patterns, namespace='tournament00')),
    url(r'^',                   login_required(tournament_selector_view), name='default'),
)

