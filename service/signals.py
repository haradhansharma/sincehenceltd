from django.db.models.signals import post_save
from django.dispatch import receiver



# from service.models import Project, ProjectTodo 
 
# # @receiver(post_save, sender=Project)
# # def update_target_dates(sender, instance, **kwargs):      
# #     ProjectTodo.update_target_dates(instance.pk)

    
# @receiver(post_save, sender=Interactions)
# def update_waited_for_reply(sender, instance, **kwargs):
#     awaiting_value = instance.awaiting        
#     if awaiting_value is not None and awaiting_value >= 0:
#         instance.waited_for_reply = awaiting_value
#         instance.save()