from django import forms
from datetime import date, timedelta
from moex_iss_api import take_data_frame
import pandas as pd  # Импортируем pandas

class ChartForm(forms.Form):
    start = forms.DateField(label='Начало котировок', initial=date.today() - timedelta(days=1))
    end = forms.DateField(label='Конец котировок', initial=date.today())

    def __init__(self, *args, **kwargs):
        self.ticker = kwargs.pop('ticker', None)
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        # Преобразуем start и end в pandas.Timestamp для сравнения
        start = pd.Timestamp(start) if start else None
        end = pd.Timestamp(end) if end else None

        # Проверка: начало котировок не должно превышать конец котировок
        if start and end:
            if start > end:
                self.add_error('start', "Дата начала не может быть позже даты окончания.")
                self.add_error('end', "Дата окончания не может быть раньше даты начала.")

        # Проверка: конец котировок не может быть позже сегодняшнего дня
        if end and end > pd.Timestamp.today():
            self.add_error('end', "Дата окончания не может быть позже сегодняшней даты.")

        # Проверка: начало котировок не может быть меньше определенной даты
        if self.ticker:
            min_date = take_data_frame.get_left_border(self.ticker)
            if min_date:
                min_date = pd.Timestamp(min_date)  # Преобразуем min_date в pandas.Timestamp
                if start and start < min_date:
                    self.add_error('start', f"Дата начала не может быть раньше начала торгов этой бумаги. Дата начала торгов: {min_date}")

        return cleaned_data
