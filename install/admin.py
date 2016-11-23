from django.contrib import admin

# Register your models here.
from install import models

class SaltAdmin(admin.ModelAdmin):
    list_display = ('name','create_date','colored_status','Autherized_date','memo')
admin.site.register(models.SaltMinion,SaltAdmin)