from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from functools import wraps
from django.db.models.fields.related import ForeignKey
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured

import logging
log =  logging.getLogger('log')

def quotation_creator_required(function):
    """
    Decorator that restricts access to the view function based on the report creator or staff/superuser.

    Args:
        function: The view function to be decorated.

    Returns:
        The decorated view function that checks for report creator or staff/superuser permissions.
    """
    from service.models import Quotation    
    def wrap(request, *args, **kwargs):
        """
        Wrapper function that checks if the current user is the report creator or is staff/superuser.
        """ 
        quotation_creator = Quotation.objects.get(pk=kwargs['pk']).creator
        if quotation_creator == request.user or request.user.is_staff or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:            
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__                
    return wrap

class ContentTypeNotFoundException(Exception):
    pass

class ObjectNotFoundException(Exception):
    pass

def customer_or_contributor_required(model_type):
    '''
    'pk' in url required,
    
    'model_type' in 'appname.modelname' format required,
    
    'customer' field required,
    
    check obj is of current user,
    '''
    def decorator(view_func):
        from django.shortcuts import redirect
        @wraps(view_func)
        def wrap(request, *args, obj=None, **kwargs):
            try:
                pk = kwargs['pk']
            except Exception as e:
                log.error(e)                
                raise PermissionDenied("kwargs should have pk")
            
            try:
                app_label = model_type.split('.')[0]
                model = model_type.split('.')[1]
                
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                model_class = content_type.model_class()
                
                #ensure model has 'customer' field
                model_class._meta.get_field('customer')
                
                # ensure request user are cutomer or not
                obj = get_object_or_404(model_class, pk=pk)
                
                if hasattr(obj, 'order_project'):           
                    if request.user == obj.customer or request.user.is_staff or request.user.is_superuser or request.user in obj.order_project.contributing_users:
                        return view_func(request, *args, obj=obj, **kwargs)
                    else:              
                        raise PermissionDenied("Do not have appropriate Permission")
                else:
                    if request.user == obj.customer or request.user.is_staff or request.user.is_superuser:
                        return view_func(request, *args, obj=obj, **kwargs)
                    else:              
                        raise PermissionDenied("Do not have appropriate Permission")                    
            
            except ContentType.DoesNotExist:
                log.error(f"ContentType for {model_type} does not exist")
                raise ContentTypeNotFoundException(f"ContentType for {model_type} does not exist")
            except model_class.DoesNotExist:
                log.error(f"Object with pk={pk} does not exist for {model_type}")
                raise ObjectNotFoundException(f"Object with pk={pk} does not exist for {model_type}")
            except FieldDoesNotExist:
                log.error(f"Model {model_type} does not have a 'customer' field")
                raise ImproperlyConfigured(f"The model {model_type} used with customer_required decorator must have a 'customer' field.")            
            except Exception as e:
                log.error(f"Unexpected error: {e}")
                raise 

        return wrap

    return decorator
