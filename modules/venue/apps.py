from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model 


def create_default_venue_providers(sender, **kwargs):
    User = get_user_model() 
    
    default_providers = [
        {
            'username': 'admin1',
            'email': 'admin1@lapangin.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'Satu',
        },
        {
            'username': 'admin2',
            'email': 'admin2@lapangin.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'Dua',
        },
        {
            'username': 'admin3',
            'email': 'admin3@lapangin.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'Tiga',
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    # Asumsi field kustom untuk pemilik lapangan adalah 'is_venue_provider'
    PROVIDER_FIELD = 'is_venue_provider' 

    for provider_data in default_providers:
        username = provider_data['username']
        
        # Cek apakah user sudah ada
        if not User.objects.filter(username=username).exists():
            # 1. User belum ada, buat baru
            user = User.objects.create_user(
                username=provider_data['username'],
                email=provider_data['email'],
                password=provider_data['password'],
                first_name=provider_data.get('first_name', ''),
                last_name=provider_data.get('last_name', ''),
            )
            
            # Set field is_venue_provider menjadi True (hanya jika field ini ada)
            if hasattr(user, PROVIDER_FIELD):
                setattr(user, PROVIDER_FIELD, True)
                user.save()
            
            created_count += 1
            
        else:
            # 2. User sudah ada, cek dan update status provider jika belum True
            user = User.objects.get(username=username)
            current_status = getattr(user, PROVIDER_FIELD, False)

            if hasattr(user, PROVIDER_FIELD) and not current_status:
                setattr(user, PROVIDER_FIELD, True)
                user.save()
                updated_count += 1
    
    if created_count > 0 or updated_count > 0:
         print(f"[{sender.label}] Providers: {created_count} created, {updated_count} updated.")
    


class VenueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.venue'
    label = 'venue' # Pastikan label aplikasi diset

    def ready(self):
        """
        Hubungkan signal post_migrate untuk membuat akun provider secara otomatis.
        """
        # Hubungkan fungsi create_default_venue_providers ke signal post_migrate
        post_migrate.connect(create_default_venue_providers, sender=self)