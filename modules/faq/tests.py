from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import FAQ 

class FAQTestSetup(TestCase):
    """menyiapkan pengguna dan data awal"""
    
    def setUp(self):
        self.client = Client()
        
        self.user_standard = User.objects.create_user(
            username='userbiasa',
            email='user@example.com',
            password='password123',
            is_staff=False 
        )
        
        self.user_admin = User.objects.create_user(
            username='admin_test',
            email='admin@example.com',
            password='password123',
            is_staff=True 
        )
        
        self.faq1 = FAQ.objects.create(
            question='Q1 tentang Pembayaran',
            answer='Jawaban 1',
            category='pembayaran', # Kategori
            created_by=self.user_admin
        )
        self.faq2 = FAQ.objects.create(
            question='Q2 tentang Venue',
            answer='Jawaban 2',
            category='venue', # Kategori
            created_by=self.user_admin
        )

        # Definisi URL 
        self.list_url = reverse('faq:faq_list')
        self.add_url = reverse('faq:add_faq')
        self.edit_url = reverse('faq:edit_faq', args=[self.faq1.id])
        self.delete_url = reverse('faq:delete_faq', args=[self.faq1.id])
        self.filter_url = reverse('faq:filter_faq')

class FAQAccessTest(FAQTestSetup):

    def test_admin_can_access_admin_views(self):
        """Admin (is_staff=True) harus bisa mengakses views Tambah dan Edit."""
        self.client.login(username='admin_test', password='password123')
        response_add = self.client.get(self.add_url)
        self.assertEqual(response_add.status_code, 200, "Admin gagal mengakses halaman Tambah FAQ")
        
        response_edit = self.client.get(self.edit_url)
        self.assertEqual(response_edit.status_code, 200, "Admin gagal mengakses halaman Edit FAQ")


    def test_standard_user_cannot_access_admin_views(self):
        """Pengguna biasa (is_staff=False) TIDAK BOLEH mengakses views admin."""
        self.client.login(username='userbiasa', password='password123')
        response_add = self.client.get(self.add_url)
        self.assertRedirects(response_add, self.list_url, status_code=302, target_status_code=200, 
                             msg_prefix="User biasa gagal mengakses Add FAQ")
        
        response_edit = self.client.get(self.edit_url)
        self.assertRedirects(response_edit, self.list_url, status_code=302, target_status_code=200,
                             msg_prefix="User biasa gagal mengakses Edit FAQ")


    def test_anonymous_user_is_redirected_by_login_required(self):
        """Pengguna anonim harus diarahkan ke halaman login."""
        response_add = self.client.get(self.add_url)
        self.assertEqual(response_add.status_code, 302)
        # Diarahkan ke halaman login 
        self.assertTrue(response_add.url.startswith(reverse('accounts:login')), 
                        "Anonim gagal diarahkan ke halaman login")

class FAQCUDTest(FAQTestSetup):

    def test_add_faq_and_auto_set_created_by(self):
        self.client.login(username='admin_test', password='password123')
        
        new_faq_data = {
            'question': 'FAQ Baru dari Tes',
            'answer': 'Ini adalah jawaban baru.',
            'category': 'umum'
        }
        
        initial_count = FAQ.objects.count()
        response = self.client.post(self.add_url, data=new_faq_data, follow=True)
        
        # 1. Cek Redirect
        self.assertRedirects(response, self.list_url)
        
        # 2. Cek Penambahan
        self.assertEqual(FAQ.objects.count(), initial_count + 1)
        
        # 3. Cek Logika created_by
        new_faq = FAQ.objects.get(question='FAQ Baru dari Tes')
        self.assertEqual(new_faq.created_by, self.user_admin) 
        

    def test_edit_faq_updates_data_and_preserves_created_by(self):
        """Menguji pembaruan data FAQ."""
        self.client.login(username='admin_test', password='password123')

        updated_data = {
            'question': 'Q1 Diubah oleh Admin!',
            'answer': 'Jawaban baru setelah diedit.',
            'category': 'booking'
        }
        
        response = self.client.post(self.edit_url, data=updated_data, follow=True)
        
        # 1. Cek Redirect
        self.assertRedirects(response, self.list_url)
        
        # 2. Ambil ulang objek
        self.faq1.refresh_from_db()
        self.assertEqual(self.faq1.question, 'Q1 Diubah oleh Admin!')
        self.assertEqual(self.faq1.category, 'booking')
        self.assertEqual(self.faq1.created_by, self.user_admin) 


    def test_delete_faq_removes_object(self):
        """Menguji penghapusan objek FAQ."""
        self.client.login(username='admin_test', password='password123')
        
        initial_count = FAQ.objects.count()
        
        # View delete_faq
        response = self.client.get(self.delete_url, follow=True) 
        
        # 1. Cek Redirect
        self.assertRedirects(response, self.list_url)
        
        # 2. Cek Penghapusan
        self.assertEqual(FAQ.objects.count(), initial_count - 1)
        self.assertFalse(FAQ.objects.filter(id=self.faq1.id).exists())

class FAQFilterTest(FAQTestSetup):
    
    def test_filter_by_specific_category(self):
        """Menguji filter AJAX"""
        
        # Akses filter
        response = self.client.get(self.filter_url, {'category': 'venue'}, 
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.faq2.question)
        self.assertNotContains(response, self.faq1.question)
        
        
    def test_filter_by_all(self):
        """Menguji filter 'all' mengembalikan semua data."""
        
        response = self.client.get(self.filter_url, {'category': 'all'}, 
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, self.faq1.question)
        self.assertContains(response, self.faq2.question)