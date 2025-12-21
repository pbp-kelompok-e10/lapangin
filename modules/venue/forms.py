from django import forms
from django.forms import ModelForm
from .models import Venue

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'city', 'country', 'capacity', 'price', 'thumbnail', 'description', 'facilities', 'rules']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none'}),
            'city': forms.TextInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none'}),
            'country': forms.TextInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none'}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none'}),
            'price': forms.NumberInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'w-full text-gray-500 text-sm font-poppins'}),
            'description': forms.Textarea(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none', 'rows': 3}),
            'facilities': forms.Textarea(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none', 'rows': 3, 'placeholder': 'Pisahkan dengan baris baru. Contoh:\nParkir luas\nKamar mandi\nWifi gratis'}),
            'rules': forms.Textarea(attrs={'class': 'w-full text-gray-500 text-sm font-poppins outline-none', 'rows': 3, 'placeholder': 'Pisahkan dengan baris baru. Contoh:\nDilarang merokok\nJaga kebersihan'})
        }
        labels = {
            'name': 'Nama Stadion',
            'city': 'Kota',
            'country': 'Negara',
            'capacity': 'Kapasitas Kursi',
            'price': 'Harga (Rp)',
            'thumbnail': 'Gambar Thumbnail',
            'description': 'Deskripsi stadion',
            'facilities': 'Fasilitas Venue',
            'rules': 'Aturan Venue'
        }

    def __init__(self, *args, **kwargs):
        super(VenueForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False