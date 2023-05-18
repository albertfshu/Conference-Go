from django.db import models


class AccountVO(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    is_active = models.BooleanField()
    updated = models.DateTimeField()
