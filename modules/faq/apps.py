from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_admins(sender, **kwargs):
    #Auto-create 3 default admin accounts

    from django.contrib.auth.models import User
    default_admins = [
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
    
    for admin_data in default_admins:
        username = admin_data['username']

        if not User.objects.filter(username=username).exists():
            # Create new user
            user = User.objects.create_user(
                username=admin_data['username'],
                email=admin_data['email'],
                password=admin_data['password'],
                first_name=admin_data.get('first_name', ''),
                last_name=admin_data.get('last_name', ''),
            )

            user.is_staff = True
            user.save()
            
            created_count += 1
        else:
            # User exists
            user = User.objects.get(username=username)
            if not user.is_staff:
                user.is_staff = True
                user.save()
                updated_count += 1


class FaqConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.faq'

    def ready(self):
        """
        Connect post_migrate signal to auto-create admins
        """
        post_migrate.connect(create_default_admins, sender=self)