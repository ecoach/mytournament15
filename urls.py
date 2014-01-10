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
    #url(r'^register/',  login_required(register_view), name='register'),
    url(r'^register/',  login_required(pdf_register_view), name='register'),
    url(r'^vote/',  login_required(vote_view), name='vote'),
    url(r'^manage_bracket/',  login_required(manage_bracket_view), name='manage_bracket'),
    url(r'^manage_judges/',  login_required(manage_judges_view), name='manage_judges'),
    url(r'^manage_competitors/',  login_required(manage_competitors_view), name='manage_competitors'),
    url(r'^review_bracket/',  login_required(review_bracket_view), name='review_bracket'),
    url(r'^',      login_required(info_view), name='default'),
)

urlpatterns = patterns('',
    url(r'^staff/',  login_required(choose_bracket_view), name='staff'),
    url(r'^new_bracket/',  login_required(new_bracket_view), name='new_bracket'),
    url(r'^choose_bracket/',  login_required(choose_bracket_view), name='choose_bracket'),
    #url(r'^load_brackets/',  login_required(load_brackets_view), name='load_brackets'),
    #url(r'^load_judges/',  login_required(load_judges_view), name='load_judges'),
    #url(r'^load_competitors/',  login_required(load_competitors_view), name='load_competitors'),
    url(r'^tourney_pdf/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.DIR_TOURNEY_PDF}, name='tourney_pdf'),
    url(r'^(?P<bracket>[a-z0-9\-]+)/',  include(tournament_patterns, namespace='bracket')),
    url(r'^',                   login_required(tournament_selector_view), name='default'),
)

