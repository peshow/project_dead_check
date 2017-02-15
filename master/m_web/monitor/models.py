from django.db import models

# Create your models here.
class Schema(models.Model):
    name = models.CharField(max_length=50)
    display = models.CharField(max_length=200)
    deleted = models.BooleanField(default=False)
    

class Field(models.Model):
    schema = models.ForeignKey(Schema)
    name = models.CharField(max_length=45)
    field_type = models.IntegerField()
    

class Dead_Setting(models.Model):
    

class Log_Setting(models.Model):
    project = models.CharField(max_length=50)
