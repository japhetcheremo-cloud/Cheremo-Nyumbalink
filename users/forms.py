from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']

def validate_image_file(file):
    """Validate uploaded image extension, size and readability."""
    if not file:
        return file
    import os
    from PIL import Image

    ext = os.path.splitext(file.name)[1].lower().lstrip('.')
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Unsupported file format '.{ext}'. Allowed formats: JPG, JPEG, PNG, WEBP.")

    # Max 5MB
    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Image file is too large (maximum 5MB allowed).")

    # Verify Pillow can open and identify it as an image
    try:
        file.seek(0)
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception:
        raise ValidationError("The uploaded file is corrupt or not a valid image.")

    return file


def validate_doc_file(file):
    """Validate uploaded verification documents (PDF or common image)."""
    if not file:
        return file
    import os

    ext = os.path.splitext(file.name)[1].lower().lstrip('.')
    allowed = ['pdf', 'jpg', 'jpeg', 'png', 'webp']
    if ext not in allowed:
        raise ValidationError(f"Unsupported file format '.{ext}'. Allowed formats: PDF, JPG, JPEG, PNG, WEBP.")

    if file.size > 5 * 1024 * 1024:
        raise ValidationError("Document file is too large (maximum 5MB allowed).")

    return file


class CustomUserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password:
            if password_confirm and password != password_confirm:
                self.add_error('password_confirm', "Passwords do not match.")

            # Run Django standard password validators configured in AUTH_PASSWORD_VALIDATORS
            user = CustomUser(
                username=cleaned_data.get('username', ''),
                email=cleaned_data.get('email', '')
            )
            try:
                validate_password(password, user=user)
            except ValidationError as error:
                self.add_error('password', error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        user.set_password(password)
        if commit:
            user.save()
        return user


class ProfileSettingsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        current_user = self.instance
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=current_user.pk).exists():
            raise ValidationError("This email is already in use by another account.")
        return email

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture and hasattr(picture, 'file'):
            validate_image_file(picture)
        return picture
