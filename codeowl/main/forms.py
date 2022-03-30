from django import forms


class UserForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Имя пользователя", "class": "form-input"}))
    mail = forms.EmailField(required=True, widget=forms.TextInput(attrs={"placeholder": "Почта", "class": "form-input"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"placeholder": "Пароль", "class": "form-input"}))


class LoginForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"placeholder": "Имя пользователя", "class": "form-input"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"placeholder": "Пароль", "class": "form-input"}))
