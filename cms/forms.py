from django import forms
from cms.models import BlogComments

from core.helper import get_4_parameter




class BlogSearchForm(forms.Form):
    search_query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':"Search ..."}))
    

class NewsSearchForm(forms.Form):

    categories, top_views, blog_archive, featured_blogs = get_4_parameter() 

    q = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'bg-transparent border rounded-0 border-1 form-control form-control-lg input-color-form',
            'id': 'q',
            'placeholder' : 'Write title or body terms'
        }),
        required=False  
    )
   
    selected_category = forms.MultipleChoiceField(
        choices=[(cat.slug, cat.title) for cat in categories],  
        widget=forms.SelectMultiple(attrs={
            'class': 'bg-transparent border rounded-0 border-1 form-select form-select-lg input-color-form',
            'id': 'selected_category',
            'multiple': "multiple",
            'placeholder' : 'Select Categories'
        }),
        required=False
    )
    selected_archive = forms.MultipleChoiceField(
        choices=[(ba.get('month').strftime('%B-%Y'), ba.get('month').strftime('%B-%Y')) for ba in blog_archive],
        
        widget=forms.SelectMultiple(attrs={
            'class': 'bg-transparent border rounded-0 border-1 form-select form-select-lg input-color-form',
            'id': 'selected_archive',
            'placeholder' : 'Select Month'
        }),
        required=False
    )


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComments
        fields = ['comments']
        
        widgets = {
            'comments' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' : 6
            })
        }
        labels = {
            'comments' : ''
        }