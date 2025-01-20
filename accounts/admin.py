from django.contrib import admin
from .models import Participant,Organizer,CustomUser
# Register your models here.


admin.site.register(Participant)
admin.site.register(Organizer)
admin.site.register(CustomUser)
