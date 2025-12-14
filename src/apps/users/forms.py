from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
