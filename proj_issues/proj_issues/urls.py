from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic.base import RedirectView, TemplateView

from proj_issues import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),

    url(r'^issues/', include('issues.urls')),
    url(r'^admin/', include(admin.site.urls)),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + patterns('',
    url(r'', RedirectView.as_view(url="/admin/issues/issue/") ),
         )

    # (r'^media/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
