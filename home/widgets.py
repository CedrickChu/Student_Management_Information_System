from django import forms
from datetime import date

class CustomDatePickerWidget(forms.DateInput):
    DATE_INPUT_WIDGET_REQUIRED_FORMAT = '%Y-%m-%d'

    def __init__(self, attrs=None, format=None):
        default_attrs = {'class': 'form-control', 'type': 'date'}
        if attrs:
            default_attrs.update(attrs)
        
        self.format = format or self.DATE_INPUT_WIDGET_REQUIRED_FORMAT
        super().__init__(attrs=default_attrs, format=self.format)

class PastCustomDatePickerWidget(CustomDatePickerWidget):

    def __init__(self, attrs=None, format=None):
        default_attrs = {'class': 'form-control', 'type': 'date', 'max': date.today().strftime('%Y-%m-%d')}
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(attrs=default_attrs, format=format)