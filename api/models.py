from django.db import models
from django.contrib.auth.models import AbstractUser
from builtins import FileExistsError
from django.conf import settings
import os


def validate_file_path(file_path):
    if os.path.exists(file_path):
        raise ValidationError("File or folder already exists")
    

def get_upload_path_book(instance, filename):
    username = instance.user.username
    book_category_and_name = f'{instance.book_category}_{instance.book_name}'
    
    # Build path components
    path_components = [username, book_category_and_name, "books", filename]

    # Join path components and normalize the path
    upload_path = os.path.normpath(os.path.join(*path_components))

    return upload_path

def get_upload_path_video(instance, video_id):
    username= instance.user.username
    path_components=[username,'videos',video_id]
    upload_path = os.path.normpath(os.path.join(*path_components))

    return upload_path

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Parent', 'Parent'),
        ('Faculty', 'Faculty')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    sub_role = models.CharField(max_length=30,blank=True,null=True)

    def __str__(self):
        return f"{self.username} - {self.role} - {self.sub_role}"


class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book_category= models.CharField(max_length=20, blank=False, null=False )
    book_name= models.CharField(max_length=1000, null=False)
    book_file= models.FileField(max_length=300, upload_to=get_upload_path_book )
    upload_path = models.CharField(max_length=500, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Update the upload_path field before saving
        self.upload_path = get_upload_path_book(self, self.book_file.name)
        super().save(*args, **kwargs)

class Video(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_name=models.CharField(max_length=1000, blank=True, null=False)
    video_id=models.CharField(max_length=20, blank=False, null=False )
    video_link=models.CharField(max_length=20, blank=False, null=False )

class MindSpace_Conversation(models.Model):
    user_query = models.TextField(max_length=30000)

class Image_conversation(models.Model):
    user_query = models.CharField(max_length=3000)