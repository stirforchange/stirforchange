from django import forms
from .models import VolunteerSignup, BusinessSignup, VolunteerEvent
import datetime

US_STATES = [
    ('', 'Select State'),
    ('AL','Alabama'),('AK','Alaska'),('AZ','Arizona'),('AR','Arkansas'),
    ('CA','California'),('CO','Colorado'),('CT','Connecticut'),('DE','Delaware'),
    ('FL','Florida'),('GA','Georgia'),('HI','Hawaii'),('ID','Idaho'),
    ('IL','Illinois'),('IN','Indiana'),('IA','Iowa'),('KS','Kansas'),
    ('KY','Kentucky'),('LA','Louisiana'),('ME','Maine'),('MD','Maryland'),
    ('MA','Massachusetts'),('MI','Michigan'),('MN','Minnesota'),('MS','Mississippi'),
    ('MO','Missouri'),('MT','Montana'),('NE','Nebraska'),('NV','Nevada'),
    ('NH','New Hampshire'),('NJ','New Jersey'),('NM','New Mexico'),('NY','New York'),
    ('NC','North Carolina'),('ND','North Dakota'),('OH','Ohio'),('OK','Oklahoma'),
    ('OR','Oregon'),('PA','Pennsylvania'),('RI','Rhode Island'),('SC','South Carolina'),
    ('SD','South Dakota'),('TN','Tennessee'),('TX','Texas'),('UT','Utah'),
    ('VT','Vermont'),('VA','Virginia'),('WA','Washington'),('WV','West Virginia'),
    ('WI','Wisconsin'),('WY','Wyoming'),('DC','District of Columbia'),
]


class VolunteerSignupForm(forms.ModelForm):
    class Meta:
        model  = VolunteerSignup
        fields = ['first_name', 'last_name', 'email', 'phone', 'birthdate', 'school']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'phone':      forms.TextInput(attrs={'placeholder': '(555) 000-0000'}),
            'birthdate':  forms.DateInput(attrs={'type': 'date', 'max': str(datetime.date.today())}),
            'school':     forms.TextInput(attrs={'placeholder': 'School or university name'}),
        }
        labels = {
            'birthdate': 'Date of Birth',
            'school':    'School / University',
        }

    def clean_birthdate(self):
        bd = self.cleaned_data['birthdate']
        today = datetime.date.today()
        age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        if age < 10:
            raise forms.ValidationError("Volunteers must be at least 10 years old.")
        if age > 30:
            raise forms.ValidationError("This form is for volunteers under 30.")
        return bd


class BusinessForm(forms.ModelForm):
    state = forms.ChoiceField(choices=US_STATES, widget=forms.Select())

    class Meta:
        model  = BusinessSignup
        fields = ['business_name', 'contact_name', 'email', 'phone', 'business_type',
                  'street_address', 'city', 'state', 'zip_code',
                  'frequency', 'food_types', 'message']
        widgets = {
            'business_name':  forms.TextInput(attrs={'placeholder': 'Business name'}),
            'contact_name':   forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email':          forms.EmailInput(attrs={'placeholder': 'contact@yourbusiness.com'}),
            'phone':          forms.TextInput(attrs={'placeholder': '(555) 000-0000'}),
            'street_address': forms.TextInput(attrs={'placeholder': '123 Main St'}),
            'city':           forms.TextInput(attrs={'placeholder': 'City'}),
            'zip_code':       forms.TextInput(attrs={'placeholder': 'ZIP Code'}),
            'frequency':      forms.TextInput(attrs={'placeholder': 'e.g. Daily, weekly, after events...'}),
            'food_types':     forms.Textarea(attrs={'placeholder': 'e.g. Prepared meals, baked goods...', 'rows': 3}),
            'message':        forms.Textarea(attrs={'placeholder': 'Any questions or additional details...', 'rows': 3}),
        }
        labels = {
            'street_address': 'Street Address',
            'zip_code':       'ZIP Code',
            'food_types':     'Types of Surplus Food',
            'frequency':      'Donation Frequency',
            'message':        'Anything Else?',
        }
