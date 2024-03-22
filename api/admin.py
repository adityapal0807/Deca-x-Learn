from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Book)
admin.site.register(MindSpace_Conversation)
admin.site.register(Image_conversation)
admin.site.register(Video)