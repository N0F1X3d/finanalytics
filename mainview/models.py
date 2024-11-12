from django.db import models

class Security(models.Model):
    ticker = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.FloatField(default=0)
    #market_cap = models.BigIntegerField()

class Data(models.Model):
    security = models.ForeignKey(Security, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    price = models.FloatField()

class Bond(models.Model):
    ticker = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=100)
    #yield_to_maturity = models.DecimalField(max_digits=5, decimal_places=2)
    current_price = models.FloatField(default=0)
    #duration = models.DecimalField(max_digits=5, decimal_places=2)