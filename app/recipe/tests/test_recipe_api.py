import random, math
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from faker import Factory
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')
User = get_user_model()

faker = Factory.create()


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': faker.sentence(nb_words=6)[:-1],
        'time_minutes': random.randint(1, 20),
        'price': round(random.uniform(1, 100), 2),
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def get_user():
    return {
        'email': faker.profile(fields=None, sex=None)['mail'],
        'password': faker.password()
    }


def sample_tag(user, name=faker.word(ext_word_list=None)):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name=faker.word(ext_word_list=None)):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(**get_user())
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        for i in range(2):
            sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user = get_user_model().objects.create_user(**get_user())
        sample_recipe(user=user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': faker.sentence(nb_words=6)[:-1],
            'time_minutes': random.randint(1, 20),
            'price': round(random.uniform(1, 100), 2),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            if key == 'price':
                continue
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user)
        payload = {
            'title': faker.sentence(nb_words=6)[:-1],
            'tags': [tag1.id, tag2.id],
            'time_minutes': random.randint(1, 20),
            'price': round(random.uniform(1, 100), 2),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user)
        ingredient2 = sample_ingredient(user=self.user)
        payload = {
            'title': faker.sentence(nb_words=6)[:-1],
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': random.randint(1, 20),
            'price': round(random.uniform(1, 100), 2),
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user)

        payload = {
            'title': faker.sentence(nb_words=6)[:-1],
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])

        tags = recipe.tags.all()

        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': faker.sentence(nb_words=6)[:-1],
            'time_minutes': random.randint(1, 20),
            'price': round(random.uniform(1, 100), 2),
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertAlmostEqual(
            recipe.price,
            Decimal(payload['price'])
        )

        tags = recipe.tags.all()

        self.assertEqual(len(tags), 0)
