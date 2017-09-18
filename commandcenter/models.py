from django.db import models

# Create your models here.
class SiteUsers(models.Model):
    full_name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(default=datetime.datetime.utcnow, blank=True)
    subscription = models.CharField(max_length=10)


class AdminUsers(models.Model):
    yellowant_user_id = models.IntegerField()
    yellowant_integration_id = models.IntegerField(unique=True, null=True)
    yellowant_integration_user_invoke_name = models.CharField(max_length=100)
    yellowant_user_token = models.CharField(max_length=100)