from django import forms
from api import models






class SelectForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': "非法用户"
        }
    )

    def clean_user_id(self):
        user_id = self.data.get('user_id')
        obj = models.Enterprise.objects.get(id=user_id)

        return user_id, obj.role



