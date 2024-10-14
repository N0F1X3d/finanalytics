from django.db import models

class Security(models.Model):
    SECID = models.CharField(max_length=20, unique=True)  # Уникальный идентификатор бумаги
    SHORTNAME = models.CharField(max_length=100)          # Краткое название
    BOARDID = models.CharField(max_length=10)             # Идентификатор рынка
    MARKET = models.CharField(max_length=10)              # Тип рынка (shares или bonds)
    updated_at = models.DateTimeField(auto_now=True)      # Время последнего обновления

    def __str__(self):
        return self.SHORTNAME