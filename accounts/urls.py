
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, PasswordChangeDoneView 
from .forms import LoginForm
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(redirect_authenticated_user=True, template_name='registration/login.html',  authentication_form=LoginForm), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'), 
    path("password_reset/done/",  views.CustomPasswordResetDoneView.as_view(), name="password_reset_done" ),
    path("reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(),  name="password_reset_confirm" ),
    path("reset/done/", views.CustomPasswordResetCompleteView.as_view(),  name="password_reset_complete", ),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),   
    path('settings/', views.profile_setting, name='profile_setting'), 
    path('dashboard/', views.DashboardView.as_view(), name='user_dashboard'), 
    path('orders/', views.OrdersView.as_view(), name='user_orders'), 
    path('due-orders/', views.DueOrdersView.as_view(), name='due_orders'), 
    path('incomplete-orders/', views.IncompleteOrdersView.as_view(), name='incomplete_orders'), 
    
    path('projects/', views.DashboardView.as_view(), name='user_projects'), 
    path('recent-activities/', views.RecentActivityView.as_view(), name='user_recents_activity'), 
    path('recent-comments/', views.RecentCommentsView.as_view(), name='user_recents_comments'), 
    path('expert-profiles/', views.ExpertiseProfile.as_view(), name='expert_profiles'), 
    path('expert-profiles/<uuid:profile_id>/edit/', views.ExpertiseProfile.as_view(), name='edit_expert_profile'),
    path('expert-profiles/<uuid:profile_id>/delete/', views.ExpertiseProfile.as_view(), name='delete_expert_profile'),
    
    path('verification-request/', views.VerificationRequest.as_view(), name='verification_request'), 
    # path('verification/<uuid:verification_request_id>/<str:image_type>/', views.serve_image, name='serve_verification_image'),
    
    path('submit-approval-request/<uuid:profile_id>/', views.SubmitApprovalRequest.as_view(), name='submit_approval_request'),
    path('delete-approval-request/<uuid:profile_id>/<int:request_id>/delete', views.SubmitApprovalRequest.as_view(), name='delete_approval_request'),
    
    
    
    
    
    
    
    path('order/<uuid:pk>', views.OrderDetails.as_view(), name='order'), 
    path('order/project-interation/<uuid:pk>/<int:todo_id>/submit/', views.OrderDetails.as_view(), name='submit_interaction'), 
    path('order/project-interation/<uuid:pk>/<int:todo_id>/<int:interaction_id>/accept/', views.OrderDetails.as_view(), name='accept_reply'), 
    
    
    
    
    
    path('change_pass/', views.password_change, name='change_pass'),   
    path(
        "password_change/done/",
        views.CustomPasswordChangeDoneView.as_view(),
        name="password_change_done",
    ), 
    path('delete-avatar/', views.delete_avatar, name='delete_avatar'),  
]












