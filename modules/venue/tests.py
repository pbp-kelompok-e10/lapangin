import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Venue
from .forms import VenueForm

User = get_user_model()

class VenueTest(TestCase):

    def setUp(self):
        """
        Siapkan data awal untuk semua tes.
        Ini berjalan sebelum setiap metode tes.
        """
        self.client = Client()

        # 1. Buat Pengguna
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        self.owner_user = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='password123'
        )

        self.owner_user.is_staff = True
        self.owner_user.save()

        self.regular_user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )

        # 2. Buat Venues
        self.venue1 = Venue.objects.create(
            owner=self.owner_user,
            name='Stadion Gelora',
            city='Jakarta',
            country='Indonesia',
            capacity=80000,
            price=1500.00,
            rating=4.5
        )

        self.venue2 = Venue.objects.create(
            owner=self.owner_user,
            name='Stadion Kanjuruhan',
            city='Malang',
            country='Indonesia',
            capacity=40000,
            price=900.00,
            rating=4.0
        )

        # 3. Data untuk form POST
        self.valid_venue_data = {
            'name': 'Venue Baru',
            'city': 'Bandung',
            'country': 'Indonesia',
            'capacity': 10000,
            'price': 500.00,
        }
        
        self.invalid_venue_data = {
            'name': '',
            'city': 'Bandung',
            'price': -100,
            'capacity': 200
        }

    # ----------------------------------------
    # Tes untuk search_venue (HTML Page)
    # ----------------------------------------

    def test_search_venue_authenticated(self):
        """Tes view search_venue saat pengguna terautentikasi."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('venue:search_venue'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue/search_venue.html')
        self.assertTrue(response.context['can_add_venue'])
        
        # Tes konteks locations_json
        locations = json.loads(response.context['locations_json'])
        self.assertIn({'city': 'Jakarta', 'country': 'Indonesia'}, locations)
        self.assertIn({'city': 'Malang', 'country': 'Indonesia'}, locations)

    def test_search_venue_anonymous(self):
        """Tes view search_venue saat pengguna anonim."""
        response = self.client.get(reverse('venue:search_venue'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue/search_venue.html')
        self.assertFalse(response.context['can_add_venue'])

    # ----------------------------------------
    # Tes untuk venue_detail (HTML Page)
    # ----------------------------------------

    def test_venue_detail_exists(self):
        """Tes view venue_detail dengan ID yang valid."""
        response = self.client.get(reverse('venue:venue_detail', args=[self.venue1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'venue/venue_detail.html')
        self.assertEqual(response.context['venue_id'], self.venue1.id)
        self.assertFalse(response.context['is_admin'])

    def test_venue_detail_is_admin(self):
        """Tes view venue_detail sebagai admin."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('venue:venue_detail', args=[self.venue1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_admin'])

    def test_venue_detail_not_found(self):
        """Tes view venue_detail dengan ID yang tidak ada."""
        response = self.client.get(reverse('venue:venue_detail', args=[9999]))
        
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'venue/venue_not_found.html')

    def test_venue_detail_invalid_id(self):
        """Tes view venue_detail dengan ID yang formatnya salah."""
        response = self.client.get('/venues/venue/abc/')
        
        self.assertEqual(response.status_code, 404)
    # ----------------------------------------
    # Tes untuk get_venue_detail_api (JSON API)
    # ----------------------------------------

    def test_get_venue_detail_api_success(self):
        """Tes API detail venue dengan ID yang valid."""
        response = self.client.get(reverse('venue:get_venue_detail_api', args=[self.venue1.id]))
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['venue']['stadium'], self.venue1.name)
        self.assertEqual(data['venue']['city'], self.venue1.city)

    def test_get_venue_detail_api_not_found(self):
        """Tes API detail venue dengan ID yang tidak ada."""
        response = self.client.get(reverse('venue:get_venue_detail_api', args=[9999]))
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Venue tidak ditemukan.')

    # ----------------------------------------
    # Tes untuk create_venue (JSON API - POST)
    # ----------------------------------------
    
    def test_create_venue_success(self):
        """Tes berhasil membuat venue baru (sebagai owner)."""
        self.client.login(username='owner', password='password123')
        initial_venue_count = Venue.objects.count()
        
        response = self.client.post(reverse('venue:create_venue'), self.valid_venue_data)
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(Venue.objects.count(), initial_venue_count + 1)
        
        # Periksa apakah owner-nya benar
        new_venue = Venue.objects.get(name='Venue Baru')
        self.assertEqual(new_venue.owner, self.owner_user)

    def test_create_venue_invalid_form(self):
        """Tes gagal membuat venue karena form tidak valid."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(reverse('venue:create_venue'), self.invalid_venue_data)
        data = response.json()
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    def test_create_venue_not_authenticated(self):
        """Tes gagal membuat venue karena belum login."""
        response = self.client.post(reverse('venue:create_venue'), self.valid_venue_data)
        # Akan redirect ke halaman login
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_create_venue_wrong_method(self):
        """Tes @require_POST, harus gagal jika pakai GET."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('venue:create_venue'))
        self.assertEqual(response.status_code, 405)

    # ----------------------------------------
    # Tes untuk edit_venue (JSON API - GET/POST)
    # ----------------------------------------

    def test_edit_venue_get_data_as_owner(self):
        """Tes GET data venue untuk diedit (sebagai owner)."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('venue:edit_venue', args=[self.venue1.id]))
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['stadium'], self.venue1.name)

    def test_edit_venue_post_success_as_owner(self):
        """Tes POST update venue (sebagai owner)."""
        self.client.login(username='owner', password='password123')
        updated_data = self.valid_venue_data.copy()
        updated_data['name'] = 'Stadion Gelora (Renovasi)'
        
        response = self.client.post(reverse('venue:edit_venue', args=[self.venue1.id]), updated_data)
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        # Cek database
        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.name, 'Stadion Gelora (Renovasi)')

    def test_edit_venue_post_success_as_admin(self):
        """Tes POST update venue (sebagai admin)."""
        self.client.login(username='admin', password='password123')
        updated_data = self.valid_venue_data.copy()
        updated_data['name'] = 'Stadion Gelora (Admin Edit)'
        
        response = self.client.post(reverse('venue:edit_venue', args=[self.venue1.id]), updated_data)
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        
        self.venue1.refresh_from_db()
        self.assertEqual(self.venue1.name, 'Stadion Gelora (Admin Edit)')

    def test_edit_venue_permission_denied(self):
        """Tes gagal edit venue (bukan owner atau admin)."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('venue:edit_venue', args=[self.venue1.id]), self.valid_venue_data)
        data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Anda tidak punya izin.')
        
    def test_edit_venue_not_found(self):
        """Tes edit venue yang tidak ada."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('venue:edit_venue', args=[9999]))
        self.assertEqual(response.status_code, 404)

    # ----------------------------------------
    # Tes untuk delete_venue (JSON API - POST)
    # ----------------------------------------
    
    def test_delete_venue_success_as_owner(self):
        """Tes berhasil hapus venue (sebagai owner)."""
        self.client.login(username='owner', password='password123')
        venue_id = self.venue1.id
        venue_count = Venue.objects.count()
        
        response = self.client.post(reverse('venue:delete_venue', args=[venue_id]))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(Venue.objects.count(), venue_count - 1)
        self.assertFalse(Venue.objects.filter(id=venue_id).exists())

    def test_delete_venue_success_as_admin(self):
        """Tes berhasil hapus venue (sebagai admin)."""
        self.client.login(username='admin', password='password123')
        venue_id = self.venue2.id
        venue_count = Venue.objects.count()
        
        response = self.client.post(reverse('venue:delete_venue', args=[venue_id]))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(Venue.objects.count(), venue_count - 1)
        self.assertFalse(Venue.objects.filter(id=venue_id).exists())
    
    def test_delete_venue_permission_denied(self):
        """Tes gagal hapus venue (bukan owner atau admin)."""
        self.client.login(username='testuser', password='password123')
        venue_id = self.venue1.id
        venue_count = Venue.objects.count()

        response = self.client.post(reverse('venue:delete_venue', args=[venue_id]))
        data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(Venue.objects.count(), venue_count)
        
    def test_delete_venue_wrong_method(self):
        """Tes @require_POST, harus gagal jika pakai GET."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('venue:delete_venue', args=[self.venue1.id]))
        self.assertEqual(response.status_code, 405) # 405 Method Not Allowed

    # ----------------------------------------
    # Tes untuk search_venues_api (JSON API - GET)
    # ----------------------------------------
    
    def test_search_venues_api_no_filter(self):
        """Tes API pencarian tanpa filter (default sort: price lowToHigh)."""
        response = self.client.get(reverse('venue:search_venues_api'))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['venues']), 2)
        self.assertEqual(data['venues'][0]['stadium'], 'Stadion Kanjuruhan') # price 900
        self.assertEqual(data['venues'][1]['stadium'], 'Stadion Gelora') # price 1500

    def test_search_venues_api_sort_high_to_low(self):
        """Tes API pencarian dengan sorting harga highToLow."""
        response = self.client.get(reverse('venue:search_venues_api'), {'sort': 'highToLow'})
        data = response.json()

        self.assertEqual(len(data['venues']), 2)
        self.assertEqual(data['venues'][0]['stadium'], 'Stadion Gelora') # price 1500
        self.assertEqual(data['venues'][1]['stadium'], 'Stadion Kanjuruhan') # price 900

    def test_search_venues_api_filter_by_name(self):
        """Tes API pencarian dengan filter nama (search term)."""
        response = self.client.get(reverse('venue:search_venues_api'), {'search': 'Gelora'})
        data = response.json()

        self.assertEqual(len(data['venues']), 1)
        self.assertEqual(data['venues'][0]['stadium'], 'Stadion Gelora')

    def test_search_venues_api_filter_by_city(self):
        """Tes API pencarian dengan filter kota."""
        response = self.client.get(reverse('venue:search_venues_api'), {'city': 'Malang'})
        data = response.json()

        self.assertEqual(len(data['venues']), 1)
        self.assertEqual(data['venues'][0]['stadium'], 'Stadion Kanjuruhan')

    def test_search_venues_api_filter_by_capacity(self):
        """Tes API pencarian dengan filter kapasitas (min dan max)."""
        # Tes min capacity
        response_min = self.client.get(reverse('venue:search_venues_api'), {'capacity_min': 50000})
        data_min = response_min.json()
        self.assertEqual(len(data_min['venues']), 1)
        self.assertEqual(data_min['venues'][0]['stadium'], 'Stadion Gelora') # Capacity 80000

        # Tes max capacity
        response_max = self.client.get(reverse('venue:search_venues_api'), {'capacity_max': 50000})
        data_max = response_max.json()
        self.assertEqual(len(data_max['venues']), 1)
        self.assertEqual(data_max['venues'][0]['stadium'], 'Stadion Kanjuruhan') # Capacity 40000
        
    def test_search_venues_api_pagination(self):
        """Tes API pencarian dengan paginasi."""
        # Buat 17 venue tambahan (total 19)
        for i in range(17):
            Venue.objects.create(
                owner=self.owner_user, name=f'Venue {i}', city='Semarang',
                country='Indonesia', capacity=5000, price=200.00 + i
            )
        
        # Halaman 1 (harus ada 18 item)
        response_page1 = self.client.get(reverse('venue:search_venues_api'))
        data_page1 = response_page1.json()
        
        self.assertEqual(len(data_page1['venues']), 18)
        self.assertTrue(data_page1['has_next_page'])
        self.assertEqual(data_page1['current_page'], 1)
        self.assertEqual(data_page1['total_pages'], 2)
        
        # Halaman 2 (harus ada 1 item)
        response_page2 = self.client.get(reverse('venue:search_venues_api'), {'page': 2})
        data_page2 = response_page2.json()
        
        self.assertEqual(len(data_page2['venues']), 1) # Sisa 1 dari total 19
        self.assertFalse(data_page2['has_next_page'])
        self.assertEqual(data_page2['current_page'], 2)