import random
from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Factory
from core import models
from unittest.mock import patch

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

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name=faker.word(ext_word_list=None)
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title=faker.sentence(nb_words=6)[:-1],
            time_minutes=random.randint(1, 20),
            price=round(random.uniform(1, 100), 2)
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
