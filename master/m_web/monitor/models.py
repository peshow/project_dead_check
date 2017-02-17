from django.db import models

# Create your models here.
class Schema(models.Model):
    name = models.CharField(max_length=50)
    display = models.CharField(max_length=200)
    deleted = models.BooleanField(default=False)
    

class Field(models.Model):
    INT = 0
    FLOAT = 1
    VARCHAR = 2
    BOOL = 3
    DATETIME = 4
    FIELD_CHOICES = (
        (INT, 'INT'),
        (FLOAT, 'FLOAT'),
        (VARCHAR, 'VARCHAR'),
        (BOOL, 'BOOL'),
        (DATETIME, 'DATETIME')
    )
    schema = models.ForeignKey(Schema)
    name = models.CharField(max_length=45)
    display = models.CharField(max_length=100)
    field_type = models.IntegerField(choices=FIELD_CHOICES)
    required = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    default = models.CharField(max_length=200)
    deleted = models.BooleanField(default=False)
    

class Entity(models.Model):
    schema = models.ForeignKey(Schema)


class Value(models.Model):
    entity = models.ForeignKey(Entity)
    field = models.ForeignKey(Field)
    value = models.TextField()
