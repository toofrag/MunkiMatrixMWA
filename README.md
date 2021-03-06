MunkiMatrixMWA
==============

Displays the Munki repository in a table inside MWA

![Matrix Screenshot](./matrix_screenshot.png?raw=true)


Installing matrix into MWA
==========================

* Log in to the server as the user Munki Web Admin runs as
* cd to the munki web admin virtualenv 
* cd into the munkiwebadmin folder
* clone the matrix repository
     git submodule add https://github.com/toofrag/MunkiMatrixMWA.git matrix
* vi settings.py.  Add 'matrix', to the end of the INSTALLED_APPS list
````
  INSTALLED_APPS = (
    'django.contrib.auth',
    ...
    ...
    'licenses',
    'matrix',
  )
````

* vi urls.py. Add url(r'^matrix/', include('matrix.urls')), into the urlpatterns list
````
      urlpatterns = patterns('',
      ...
          url(r'^licenses/', include('licenses.urls')),
          url(r'^matrix/', include('matrix.urls')),
          # for compatibility with MunkiReport scripts
          url(r'^update/', include('reports.urls')),
      ...
      )
````
* vi templates/base.html. Add the following list item after licenses (about line 90) so matrix appears in the top menu
````
      ...       
      <li {% if page == 'matrix' %} class="active" {% endif %}>
        <a href="{% url 'matrix.views.index' %}">Matrix</a>
      </li>
      ...
````
* Why not restart apache for good measure.
* Done.
