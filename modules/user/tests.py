from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from modules.user.models import UserProfile
from modules.user.forms import UserForm, UserProfileForm
import json


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            full_name='Test User',
            phone='081234567890',
            address='Test Address'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.full_name, 'Test User')
        self.assertEqual(profile.phone, '081234567890')
        self.assertTrue(profile.is_active)
    
    def test_user_profile_str(self):
        """Test string representation of profile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser's Profile")
    
    def test_user_profile_defaults(self):
        """Test default values"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertTrue(profile.is_active)
        self.assertEqual(profile.full_name, '')
        self.assertEqual(profile.phone, '')
        self.assertEqual(profile.address, '')


class UserFormTest(TestCase):
    """Test UserForm validation and behavior"""
    
    def test_valid_user_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'newuser',
            'full_name': 'New User',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'is_staff': False,
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'full_name': 'New User',
            'password': 'testpass123',
            'confirm_password': 'differentpass',
            'is_staff': False,
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match', str(form.errors))
    
    def test_username_required(self):
        """Test that username is required"""
        form_data = {
            'full_name': 'New User',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_full_name_split(self):
        """Test that full name is split into first and last name"""
        form_data = {
            'username': 'testuser',
            'full_name': 'John Doe',
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
    
    def test_single_name(self):
        """Test full name with single word"""
        form_data = {
            'username': 'testuser',
            'full_name': 'John',
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, '')


class UserProfileFormTest(TestCase):
    """Test UserProfileForm"""
    
    def test_valid_profile_form(self):
        """Test form with valid data"""
        form_data = {
            'phone': '081234567890',
            'address': 'Test Address',
            'is_active': True
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_profile_form(self):
        """Test form with empty optional fields"""
        form_data = {
            'phone': '',
            'address': '',
            'is_active': True
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())


class UserListViewTest(TestCase):
    """Test user list view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user1',
            password='userpass'
        )
        UserProfile.objects.create(user=self.regular_user, full_name='User One')
    
    def test_user_list_requires_login(self):
        """Test that user list requires authentication"""
        response = self.client.get(reverse('user:user_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_user_list_requires_admin(self):
        """Test that user list requires admin privileges"""
        self.client.login(username='user1', password='userpass')
        response = self.client.get(reverse('user:user_list'))
        self.assertEqual(response.status_code, 302)  # Redirect (not authorized)
    
    def test_user_list_accessible_by_admin(self):
        """Test that admin can access user list"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('user:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_list.html')
    
    def test_user_list_context_data(self):
        """Test context data in user list"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('user:user_list'))
        self.assertIn('users', response.context)
        self.assertIn('total_users', response.context)
        self.assertIn('active_users', response.context)
        self.assertIn('inactive_users', response.context)
    
    def test_user_list_search(self):
        """Test search functionality"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('user:user_list') + '?search=user1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search_query'], 'user1')
    
    def test_user_list_status_filter(self):
        """Test status filter"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('user:user_list') + '?status=active')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_filter'], 'active')


class UserDetailViewTest(TestCase):
    """Test user detail view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        UserProfile.objects.create(
            user=self.test_user,
            full_name='Test User',
            phone='081234567890'
        )
    
    def test_user_detail_requires_login(self):
        """Test that user detail requires authentication"""
        response = self.client.get(
            reverse('user:user_detail', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 302)
    
    def test_user_detail_accessible_by_admin(self):
        """Test that admin can access user detail"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_detail', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_detail.html')
    
    def test_user_detail_context(self):
        """Test context data in user detail"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_detail', args=[self.test_user.id])
        )
        self.assertIn('user_data', response.context)
        self.assertIn('profile', response.context)
        self.assertEqual(response.context['user_data'], self.test_user)
    
    def test_user_detail_creates_profile_if_missing(self):
        """Test that profile is created if it doesn't exist"""
        new_user = User.objects.create_user(
            username='newuser',
            password='newpass'
        )
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_detail', args=[new_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())


class UserCreateViewTest(TestCase):
    """Test user creation view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
    
    def test_user_create_get(self):
        """Test GET request to create user"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('user:user_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_form.html')
        self.assertEqual(response.context['mode'], 'create')
    
    def test_user_create_post_valid(self):
        """Test POST with valid data"""
        self.client.login(username='admin', password='adminpass')
        data = {
            'username': 'newuser',
            'full_name': 'New User',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'phone': '081234567890',
            'address': 'Test Address',
            'is_staff': False,
            'is_active': True
        }
        response = self.client.post(
            reverse('user:user_create'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_create_post_invalid(self):
        """Test POST with invalid data"""
        self.client.login(username='admin', password='adminpass')
        data = {
            'full_name': 'New User',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }
        response = self.client.post(
            reverse('user:user_create'),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')


class UserEditViewTest(TestCase):
    """Test user edit view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        UserProfile.objects.create(user=self.test_user, full_name='Test User')
    
    def test_user_edit_get(self):
        """Test GET request to edit user"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_edit', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_form.html')
        self.assertEqual(response.context['mode'], 'edit')
    
    def test_user_edit_post_valid(self):
        """Test POST with valid data"""
        self.client.login(username='admin', password='adminpass')
        data = {
            'username': 'testuser',
            'full_name': 'Updated Name',
            'phone': '081234567890',
            'address': 'Updated Address',
            'is_staff': False,
            'is_active': True
        }
        response = self.client.post(
            reverse('user:user_edit', args=[self.test_user.id]),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        
        # Verify update
        self.test_user.refresh_from_db()
        self.test_user.profile.refresh_from_db()
        self.assertEqual(self.test_user.profile.phone, '081234567890')
    
    def test_user_edit_change_password(self):
        """Test changing user password"""
        self.client.login(username='admin', password='adminpass')
        data = {
            'username': 'testuser',
            'full_name': 'Test User',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'is_staff': False,
            'is_active': True
        }
        response = self.client.post(
            reverse('user:user_edit', args=[self.test_user.id]),
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify password changed
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.check_password('newpassword123'))


class UserDeleteViewTest(TestCase):
    """Test user delete view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_user_delete_success(self):
        """Test successful user deletion"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('user:user_delete', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertFalse(User.objects.filter(id=self.test_user.id).exists())
    
    def test_user_delete_self_prevention(self):
        """Test that user cannot delete themselves"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('user:user_delete', args=[self.admin_user.id])
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())
    
    def test_user_delete_invalid_method(self):
        """Test DELETE with GET method"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_delete', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 400)


class UserToggleStatusViewTest(TestCase):
    """Test user toggle status view"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass',
            is_active=True
        )
    
    def test_toggle_status_activate_to_deactivate(self):
        """Test toggling active user to inactive"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('user:user_toggle_status', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)
    
    def test_toggle_status_deactivate_to_activate(self):
        """Test toggling inactive user to active"""
        self.test_user.is_active = False
        self.test_user.save()
        
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('user:user_toggle_status', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 200)
        
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)
    
    def test_toggle_status_self_prevention(self):
        """Test that user cannot toggle their own status"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(
            reverse('user:user_toggle_status', args=[self.admin_user.id])
        )
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
    
    def test_toggle_status_invalid_method(self):
        """Test toggle with GET method"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(
            reverse('user:user_toggle_status', args=[self.test_user.id])
        )
        self.assertEqual(response.status_code, 400)


class IntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True,
            is_superuser=True
        )
    
    def test_complete_user_lifecycle(self):
        """Test create, view, edit, toggle, and delete user"""
        self.client.login(username='admin', password='adminpass')
        
        # Create user
        create_data = {
            'username': 'lifecycle_user',
            'full_name': 'Lifecycle User',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'phone': '081234567890',
            'address': 'Test Address',
            'is_staff': False,
            'is_active': True
        }
        create_response = self.client.post(
            reverse('user:user_create'),
            data=create_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(create_response.status_code, 200)
        
        user = User.objects.get(username='lifecycle_user')
        
        # View user detail
        detail_response = self.client.get(
            reverse('user:user_detail', args=[user.id])
        )
        self.assertEqual(detail_response.status_code, 200)
        
        # Edit user
        edit_data = {
            'username': 'lifecycle_user',
            'full_name': 'Updated Lifecycle User',
            'phone': '089876543210',
            'address': 'Updated Address',
            'is_staff': False,
            'is_active': True
        }
        edit_response = self.client.post(
            reverse('user:user_edit', args=[user.id]),
            data=edit_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(edit_response.status_code, 200)
        
        # Toggle status
        toggle_response = self.client.post(
            reverse('user:user_toggle_status', args=[user.id])
        )
        self.assertEqual(toggle_response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Delete user
        delete_response = self.client.post(
            reverse('user:user_delete', args=[user.id])
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(User.objects.filter(id=user.id).exists())