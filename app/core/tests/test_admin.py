from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Factory

User = get_user_model()


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        faker = Factory.create()
        self.admin_user = User.objects.create_superuser(
            email=faker.profile(fields=None, sex=None)['mail'],
            password=faker.password()
        )
        self.client.force_login(self.admin_user)
        self.user = User.objects.create_user(
            email=faker.profile(fields=None, sex=None)['mail'],
            password=faker.password(),
            name=faker.profile(fields=None, sex=None)['name'],
        )

    def test_users_listed(self):
        """Test that users are listed on the user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_page_change(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
