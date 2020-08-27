from .models import Entry
from django import forms
from bootstrap_modal_forms.forms import BSModalForm

class EntryForm(BSModalForm):
    class Meta:
        model = Entry
        exclude = ("id","user","initiallyScanned")
        widgets = {
            'query': forms.TextInput(attrs={'size':50})
        }
    
    def clean(self):
        cleaned_data=super(EntryForm, self).clean()
        sources = [cleaned_data.get("cl"),cleaned_data.get("rv"),cleaned_data.get("gc")]
        if all(not source for source in sources):
            self.add_error('rv', "At least one source must be selected.")
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")
        if min_price is not None and max_price is not None and max_price < min_price:
            self.add_error('min_price', "Min Price is higher than Max Price.")
        return cleaned_data
