from django.db import models

class Security(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    market_cap = models.BigIntegerField()

class Bond(models.Model):
    identifier = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    yield_to_maturity = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DecimalField(max_digits=5, decimal_places=2)