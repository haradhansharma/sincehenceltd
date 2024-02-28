# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.core.files.storage import default_storage


# from .models import ImageRecords

# @receiver(post_save)
# def save_image_records(sender, instance, **kwargs):
#     if hasattr(instance, 'post_save_signal_for_images'):
#         img_fields = instance.post_save_signal_for_images()
#         if img_fields is not None:
#             for field_name in img_fields:            

#                 field = getattr(instance, field_name)
#                 if field or field is not None:
             
#                     ImageRecords.objects.create(
#                         obj_id=instance.id,
#                         obj_model=sender.__name__,
#                         obj_field=field_name,
#                         obj_url=field
#                     )
#                     print('image record created in signal')
   
                
# @receiver(post_delete, sender=ImageRecords)
# def delete_image_file(sender, instance, **kwargs):
#     if instance.obj_url:  
#         file_path = instance.obj_url
#         default_storage.delete(file_path)

# from django.contrib.auth import get_user

# @receiver(post_save)
# def log_model_changes(sender, instance, created, **kwargs):
#     print(kwargs)
#     # if hasattr(instance, 'add_to_activity'):
#     #     action = 'Added' if created else 'Updated'
#     #     model_name = sender.__name__
#     #     object_id = instance.id
#     #     details = ""

#     #     if not created:
#     #         # If not created, this is an update
#     #         original_instance = sender.objects.get(pk=instance.pk)
#     #         details = "Updated fields:\n"
#     #         for field in instance._meta.fields:
#     #             field_name = field.name
#     #             if getattr(original_instance, field_name) != getattr(instance, field_name):
#     #                 details += f"- {field_name}: {getattr(original_instance, field_name)} -> {getattr(instance, field_name)}\n"

#     #     UserActivityLog.objects.create(
#     #         user=instance.add_to_activity,
#     #         action=action,
#     #         model_name=model_name,
#     #         object_id=object_id,
#     #         details=details
#     #     )

# # @receiver(post_delete)
# # def log_model_deletion(sender, instance, **kwargs):
# #     if hasattr(instance, 'add_to_activity'):
# #         action = 'Deleted'
# #         model_name = sender.__name__
# #         object_id = instance.id
# #         details = ""
        
# #         UserActivityLog.objects.create(
# #             user=instance.add_to_activity,
# #             action=action,
# #             model_name=model_name,
# #             object_id=object_id,
# #             details=details
# #         )
