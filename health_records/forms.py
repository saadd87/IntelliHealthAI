from django import forms
from .models import HealthRecord

class HealthRecordForm(forms.ModelForm):

    class Meta:
        model = HealthRecord

        fields = [
            'age',
            'weight',
            'height',
            'blood_pressure',
            'glucose_level'
        ]

        widgets = {
    'age': forms.NumberInput(attrs={'class':'form-control'}),
    'height': forms.NumberInput(attrs={'class':'form-control'}),
    'weight': forms.NumberInput(attrs={'class':'form-control'}),
    'blood_pressure': forms.TextInput(attrs={'class':'form-control','placeholder':'120/80'}),
    'glucose_level': forms.NumberInput(attrs={'class':'form-control'}),
}