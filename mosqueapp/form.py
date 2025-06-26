from django import forms
from .models import Member,MonthlyAmountSetting
import calendar
import datetime

class AddmemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['member_id', 'member_name', 'member_phone', 'member_email', 'address']
        widgets = {
            'member_id': forms.TextInput(attrs={
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Member ID'
            }),
            'member_name': forms.TextInput(attrs={ 
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Member Name'                                  
                }),
            'member_phone': forms.TextInput(attrs={ 
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Member Phone'
                }),
            'member_email': forms.EmailInput(attrs={ 
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Member Email'
                }),
            'address': forms.Textarea(attrs={ 
                'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter Member Address'
                }),
        }

    def clean_member_id(self):
        member_id = self.cleaned_data.get('member_id')
        if Member.objects.exclude(pk=self.instance.pk).filter(member_id=member_id).exists():
            raise forms.ValidationError("Member ID already exists.")
        return member_id
    
    
    def __init__(self, *args, **kwargs):
        super(AddmemberForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['member_id'].widget.attrs['readonly']=True


class CollectPaymentForm(forms.Form):
    member_id = forms.CharField(
        label="Member ID",
        widget=forms.TextInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Enter Member ID'
        })
    )

    year = forms.ChoiceField(
        label="Year",
        choices=[(y, y) for y in range(2020, datetime.datetime.now().year + 2)],
        initial=datetime.datetime.now().year,
        widget=forms.Select(attrs={'class': 'border rounded px-3 py-2 w-full'})
    )

    months = forms.MultipleChoiceField(
        label="Months",
        choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'grid grid-cols-3 gap-2'})
    )

    amount = forms.IntegerField(
        min_value=1,
        label="Total Amount Paid",
        widget=forms.NumberInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Calculated automatically'
        })
    )

class SetAmountForm(forms.ModelForm):
    class Meta:
        model=MonthlyAmountSetting
        fields=['amount']