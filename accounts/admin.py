from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sites.models import Site
from .forms import UserCreationForm, UserChangeForm
from .models import *
from django.contrib import messages

class UserProfile(admin.StackedInline):
    model = Profile
    can_delete = False 



class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = [ 'email', 'username', 'is_staff', 'is_active',]
    
    list_filter = ('is_active', 'is_staff', )
    search_fields = ('email', 'phone', 'organization', 'username',  )   
    inlines = [UserProfile]    

admin.site.register(User, UserAdmin)

class ExpertTypeAdmin(admin.ModelAdmin):
    pass  

admin.site.register(ExpertType, ExpertTypeAdmin)

class SkillAdmin(admin.ModelAdmin):
    pass  

admin.site.register(Skill, SkillAdmin)

class ApprovalStatusAdmin(admin.ModelAdmin):
    pass  

admin.site.register(ApprovalStatus, ApprovalStatusAdmin)


class ExpertProfileApprovalRequestInline(admin.TabularInline):
    model = ExpertProfileApprovalRequest
    extra = 1
    fk_name = 'expert_profile'
 

class ExpertiesProfileAdmin(admin.ModelAdmin):
    inlines = [ExpertProfileApprovalRequestInline]    

admin.site.register(ExpertiesProfile, ExpertiesProfileAdmin)




class UserVerificationRequestAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'id_proof', 'address_proof']

admin.site.register(UserVerificationRequest, UserVerificationRequestAdmin)


    
    

    