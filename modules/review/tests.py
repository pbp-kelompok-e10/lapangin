from decimal import Decimal
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Review
from .forms import ReviewForm
import uuid
from modules.venue.models import Venue

class ReviewModuleTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User',
        )
        
        cls.other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        
        cls.admin_user = User.objects.create_user(
            username='adminuser',
            password='password123',
            is_staff=True,
            is_superuser=True
        )
        

        cls.venue = Venue.objects.create(
            name='Test Venue',
            rating=0,
            capacity=100,
            price=100
        )
        
        cls.review = Review.objects.create(
            venue=cls.venue,
            user=cls.user,
            rating=5.0,
            comment="Initial review!"
        )
        cls.venue.refresh_from_db()
        cls.NON_EXISTENT_UUID = uuid.uuid4()

    def setUp(self):
        self.client = Client()
        
        try:
            self.add_review_url = reverse('review:add_review')
            self.get_reviews_url = reverse('review:get_venue_reviews', kwargs={'venue_id': self.venue.id})
            self.edit_review_url = reverse('review:edit_review', kwargs={'review_id': self.review.id})
            self.delete_review_url = reverse('review:delete_review', kwargs={'review_id': self.review.id})
        except:
            print("WARNING: URL names (e.g., 'add_review') not found. View tests will fail.")
            print("Please configure your modules/reviews/urls.py")

    def test_review_model_creation(self):
        self.assertEqual(self.review.user.username, 'testuser')
        self.assertEqual(self.review.venue.name, 'Test Venue')
        self.assertEqual(self.review.rating, 5.0)
        self.assertEqual(str(self.review), "Review for Test Venue by testuser")
        self.assertIsNotNone(self.review.created_at)

    def test_review_form_valid(self):
        form_data = {'rating': 4.0, 'comment': 'This is a test.'}
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        form_data = {'comment': 'Missing rating.'}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_model_creation(self):
        self.assertEqual(self.review.user.username, 'testuser')
        self.assertEqual(self.review.venue.name, 'Test Venue')
        self.assertEqual(self.review.rating, 5.0)
        self.assertEqual(str(self.review), "Review for Test Venue by testuser")
        self.assertIsNotNone(self.review.created_at)

    def test_review_form_valid(self):
        form_data = {'rating': 4.0, 'comment': 'This is a test.'}
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid(self):
        form_data = {'comment': 'Missing rating.'}
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_signal_updates_rating_on_create(self):
        """Test the signal updates venue rating when a new review is created."""
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.rating, 5.0)
        
        Review.objects.create(
            venue=self.venue,
            user=self.other_user,
            rating=3.0,
            comment="It was okay."
        )
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.rating, 4.0)

    def test_signal_updates_rating_on_update(self):
        """Test the signal updates venue rating when a review is updated."""
        self.assertEqual(self.venue.rating, 5.0)
        
        self.review.rating = 1.0
        self.review.save()
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.rating, 1.0)

    def test_signal_updates_rating_on_delete(self):
        """Test the signal updates venue rating when a review is deleted."""
        self.assertEqual(self.venue.rating, 5.0)
        
        self.review.delete()
        
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.rating, 0)
        
    def test_signal_rounding_logic(self):
        """Test the signal's rounding logic."""
        self.review.delete()
        
        Review.objects.create(venue=self.venue, user=self.user, rating=4.0)
        Review.objects.create(venue=self.venue, user=self.other_user, rating=4.1)

        self.venue.refresh_from_db()
        self.assertEqual(self.venue.rating, Decimal('4.1'))

    def test_add_review_success_new(self):
        """Test successfully adding a new review."""
        self.client.login(username='otheruser', password='password123')
        data = {
            'venue_id': self.venue.id,
            'rating': 4.0,
            'comment': 'A new review.'
        }
        response = self.client.post(self.add_review_url, data)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertIn('Terima kasih', json_response['message'])
        self.assertTrue(Review.objects.filter(user=self.other_user, venue=self.venue).exists())

    def test_add_review_success_update(self):
        """Test successfully updating an existing review via add_review."""
        self.client.login(username='testuser', password='password123')
        data = {
            'venue_id': self.venue.id,
            'rating': 1.0,
            'comment': 'Updated my review.'
        }
        response = self.client.post(self.add_review_url, data)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertIn('diperbarui', json_response['message'])
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 1.0)
        self.assertEqual(Review.objects.count(), 1)

    def test_add_review_not_logged_in(self):
        """Test add_review view when user is not logged in."""
        data = {'venue_id': self.venue.id, 'rating': 4.0}
        response = self.client.post(self.add_review_url, data)
        # @login_required redirects to login page
        self.assertEqual(response.status_code, 302)

    def test_add_review_invalid_data(self):
        """Test add_review with invalid form data (missing rating)."""
        self.client.login(username='testuser', password='password123')
        data = {'venue_id': self.venue.id, 'comment': 'No rating.'}
        response = self.client.post(self.add_review_url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_add_review_venue_not_found(self):
        """Test add_review with a non-existent venue_id."""
        self.client.login(username='testuser', password='password123')
        data = {'venue_id': 'ffffffff-ffff-ffff-ffff-ffffffffffff', 'rating': 4.0}
        response = self.client.post(self.add_review_url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Venue tidak ditemukan.')
        
    def test_add_review_wrong_method(self):
        """Test add_review with GET method (should be 405)."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.add_review_url)
        self.assertEqual(response.status_code, 405)


    # --- Tests for edit_review ---

    def test_edit_review_get_data_success(self):
        """Test GET request to edit_review to fetch review data."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.edit_review_url)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response['success'])
        self.assertEqual(Decimal(json_response['data']['rating']), self.review.rating)

    def test_edit_review_post_success(self):
        """Test POST request to edit_review to update review data."""
        self.client.login(username='testuser', password='password123')
        data = {'rating': 2.0, 'comment': 'Just updated it.'}
        response = self.client.post(self.edit_review_url, data)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertTrue(json_response['success'])
        self.assertEqual(Decimal(json_response['review']['rating']), 2.0)
        
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 2.0)

    def test_edit_review_permission_denied(self):
        """Test editing a review owned by another user."""
        self.client.login(username='otheruser', password='password123')
        data = {'rating': 2.0, 'comment': 'Trying to hack.'}
        response = self.client.post(self.edit_review_url, data)
        
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        self.assertIn('izin', response.json()['message'])

    def test_edit_review_permission_success_admin(self):
        """Test an admin can edit another user's review."""
        self.client.login(username='adminuser', password='password123')
        data = {'rating': 1.0, 'comment': 'Admin edit.'}
        response = self.client.post(self.edit_review_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 1.0)
        
    def test_edit_review_not_found(self):
        """Test editing a review that does not exist."""
        self.client.login(username='testuser', password='password123')
        url = reverse('review:edit_review', kwargs={'review_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)



    def test_delete_review_success(self):
        """Test successfully deleting a review as the owner."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.delete_review_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())

    def test_delete_review_permission_denied(self):
        """Test deleting a review as a non-owner."""
        self.client.login(username='otheruser', password='password123') 
        response = self.client.post(self.delete_review_url)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['status'], 'error')
        self.assertTrue(Review.objects.filter(pk=self.review.id).exists())

    def test_delete_review_not_found(self):
        """Test deleting a review that does not exist."""
        self.client.login(username='testuser', password='password123')
        url = reverse('review:delete_review', kwargs={'review_id': 999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)



    def test_get_venue_reviews_authenticated(self):
        """Test getting reviews as a logged-in user."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.get_reviews_url)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response['reviews']), 1)
        self.assertEqual(json_response['reviews'][0]['id'], self.review.id)
        self.assertEqual(json_response['current_user_id'], self.user.id)

    def test_get_venue_reviews_anonymous(self):
        response = self.client.get(self.get_reviews_url)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response['reviews']), 1)
        self.assertIsNone(json_response['current_user_id'])
        
    def test_get_venue_reviews_not_found(self):
        url = reverse('review:get_venue_reviews', kwargs={'venue_id': self.NON_EXISTENT_UUID})
        with self.assertRaises(Venue.DoesNotExist):
            self.client.get(url)