from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Factory
from core import models

faker = Factory.create()
profile = faker.profile(fields=None, sex=None)
password = faker.password()

User = get_user_model()


def sample_user(email='test@email.com', password_='123456'):
    """Create a sample user"""
    return User.objects.create_user(email, password_)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with and email is successful"""
        user = User.objects.create_user(email=profile['mail'])
        user.set_password(password)

        self.assertEqual(user.email, profile['mail'])
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@SOMEDOMAIN.com'
        user = User.objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(None, 'test123')

    def test_new_superuser(self):
        """Test creating a new superuser"""
        user = User.objects.create_superuser('root@email.com', '123456')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name=faker.word(ext_word_list=None)
        )

        self.assertEqual(str(tag), tag.name)
