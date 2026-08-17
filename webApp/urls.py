from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet#, MyDRFHTMLView
router = DefaultRouter()
router.register(r'content', ContentViewSet)

#urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)), #/urls/
    path('t2/', views.getDjangoData, name='basePage'),
    path('ericssonRet/', views.funcEricssonRet, name='ret'),
    path('nokia/', views.funcNokia, name='nokia'),
    path('ericsson/', views.funcEricsson, name='ericsson'),
    path('updateDbInfo/', views.funcUpdateDbInfo, name='updateInfo'),
]