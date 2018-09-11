
from django.conf.urls import url,include
from django.conf import settings
from django.conf.urls.static import static
from . import views
app_name = 'music'
urlpatterns = [
    url(r'^$',views.index,name="index"),
    url(r'^show$',views.showlinks,name="showlinks"),
    url(r'^fetchfile$',views.fetchfile,name="fetchfile"),
    url(r'^player$',views.player,name='player')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)