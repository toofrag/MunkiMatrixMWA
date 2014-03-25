from django.conf.urls import patterns, url

from matrix import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='matrix')
)
