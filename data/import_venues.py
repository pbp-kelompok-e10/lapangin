import random
import django
import pandas as pd
import os
from django.conf import settings
import sys

# Inisialisasi Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lapangin.settings')
django.setup()

from modules.venue.models import Venue

# Path ke dataset
dataset_path = os.path.join(settings.BASE_DIR, 'data/venue_dataset.csv')

# Baca CSV
df = pd.read_csv(dataset_path)

# Bersihkan data (opsional, handle missing values)
df = df.fillna({
    'Confederation': '',
    'HomeTeams': '',
    'IOC': '',
    'Description': '',
    'Thumbnail': ''
})

def generate_fixed_price():
    return random.randint(1000000, 10000000)

# Impor ke model
venues = []
for index, row in df.iterrows():
    price = generate_fixed_price()
    
    venues.append(Venue(
        name=row['Stadium'],
        city=row['City'],
        home_teams=row['HomeTeams'],
        capacity=row['Capacity'],
        country=row['Country'],
        price=price, 
        thumbnail=row['Thumbnail'],
        description=row['Description']
    ))

# Gunakan bulk_create untuk performa
Venue.objects.all().delete()
Venue.objects.bulk_create(venues)

print(f"Data imported successfully! Total venues: {len(venues)}")