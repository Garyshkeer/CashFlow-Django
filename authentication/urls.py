from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('edit', views.edit, name='edit'),
    path('profile', views.profile, name='profile'),
    path('features', views.features, name='features'),
    path('contacts', views.contacts, name='contacts'),
    path('why', views.why, name='why_cash_flow'),
    path('addbankincomes', views.addNewBankCard, name='bankcard'),
    path('addbankcardname', views.addBankName, name='bankname'),
    re_path(r'^accounts/$', views.AccountListView.as_view(), name='account'),
    path('inflow_create', views.inflow_create, name='inflow_create'),
    path('inflow_save', views.inflow_save, name='inflow_save'),
    path('inflow_list', views.inflow_list, name='inflow_list'),
    path('inflow_edit/<int:pk>', views.inflow_edit, name='inflow_edit'),
    path('inflow_edit/<int:pk>/update', views.inflow_update, name='inflow_update'),
    path('inflow_edit/<int:pk>/delete', views.inflow_delete, name='inflow_delete'),
    path('inflow_detail/<int:pk>', views.inflow_detail, name='inflow_detail'),
    path('category_create', views.category_create, name='category_create'),
    path('category_save', views.category_save, name='category_save'),
    path('category_list', views.category_list, name='category_list'),
    path('category_detail/<int:pk>', views.category_detail, name='category_detail'),
    path('category_edit/<int:pk>', views.category_edit, name='category_edit'),
    path('category_edit/<int:pk>/update', views.category_update, name='category_update'),
    path('category_edit/<int:pk>/delete', views.category_delete, name='category_delete'),
    path('outflow_create', views.outflow_create, name='outflow_create'),
    path('outflow_save', views.outflow_save, name='outflow_save'),
    path('outflow_list', views.outflow_list, name='outflow_list'),
    path('outflow_list/', views.outflow_list, name='outflow_list'),
    path('outflow_detail/<int:pk>', views.outflow_detail, name='outflow_detail'),
    path('outflow_edit/<int:pk>', views.outflow_edit, name='outflow_edit'),
    path('outflow_edit/<int:pk>/update', views.outflow_update, name='outflow_update'),
    path('outflow_edit/<int:pk>/delete', views.outflow_delete, name='outflow_delete'),
    path('accounts/<int:pk>/delete', views.DeleteAccountView.as_view(), name='delete_account')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
