from django.db import models


class Success(models.Model):
    State=models.CharField(max_length=20)
    Crop=models.CharField(max_length=20)
    SuccessRate=models.DecimalField(max_digits=12,decimal_places=4,default=0.0)
