from django import forms

class StatusSelectWidget(forms.Select):
    def __init__(self, *args, **kwargs):
        choices = [
            ('is_active', 'Active'),
            ('is_sold', 'Sold'),
            ('is_hold', 'Hold'),
        ]
        super().__init__(choices=choices, *args, **kwargs)