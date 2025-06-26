from django.urls import path
from django.contrib.auth import views as auth_views

from mosqueapp.views import (Dashboard,LoginView,LogoutView,add_member,member_list,delete_member,edit_member_details,
                export_members_csv,collect_payment,PaymentDetails,set_monthly_amount,collect_payment_page,
                fetch_member_info,get_member_payments_for_year,set_inactive,set_active,export_payments_csv,see_inactive_members)

urlpatterns=[
    path('',LoginView,name="login"),
    path('logout',LogoutView,name='logout'),
    path('add-member-form',add_member,name="add-member-form"),
    path("dashboard/",Dashboard,name='dashboard'),
    path('member-list',member_list,name='member-list'),
    path('inactive-members',see_inactive_members,name='inactive-members'),
    path('set-inactive/<int:id>/',set_inactive,name='set-inactive'),
    path('set-active/<int:id>/',set_active,name='set-active'),
    path('delete-member/<int:id>',delete_member,name='delete-member'),
    path('edit-member/<int:id>',edit_member_details,name='edit-member'),
    path('members/export/', export_members_csv, name='export-members'),
    path('set-monthly-amount',set_monthly_amount,name='set-monthly-amount'),
    path('payment-details',PaymentDetails,name='payment-details'),
    path('collect-payment/',collect_payment, name='collect-payment'),
    path('collect-payment-page/',collect_payment_page, name='collect-payment-page'),
    path('fetch_member_info/',fetch_member_info, name='fetch_member_info'),
    path('get_member_payments_for_year/',get_member_payments_for_year, name='get_member_payments_for_year'),
    path('payments/export/', export_payments_csv, name='export-payments'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='mosqueapp/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='mosqueapp/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='mosqueapp/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='mosqueapp/password_reset_complete.html'), name='password_reset_complete'),
]