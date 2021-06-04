import pytest
from copy import deepcopy

from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.authtoken.models import Token

from backend.models import Product, User


class UserAPITests(APITestCase):
    """ Tests for working with users. """

    url = reverse('backend:user-register')
    login_url = reverse('backend:user-login')
    details_url = reverse('backend:user-details')

    data = {
        'first_name': 'Name1',
        'last_name': 'Name2',
        'email': 'name2@mail.com',
        'password': 'name1name2',
        'company': 'Company1',
        'position': 'Position1',
        'contacts': []
    }

    def setUp(self):
        return super().setUp()

    def create_user(self):
        data = deepcopy(self.data)
        contact = data.pop('contacts', [])
        password = data.pop('password')

        user = User.objects.create(**data, type='buyer')
        user.is_active = True
        user.set_password(password)
        user.save()

    def test_register_user(self):
        """ Checks for new user registrations. """

        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.data['email'], 'name2@mail.com')

    def test_create_user_not_field(self):
        """
        Checks for new user registrations,
        if not all fields are specified.
        """

        data = deepcopy(self.data)
        data.pop('email')

        response = self.create_user()

        self.assertEqual(self.failureException, AssertionError)

    def test_create_user_not_valid_field(self):
        """
        Checks for new user registrations,
        field isn't valid.
        """

        data = deepcopy(self.data)
        self.data['email'] = ''

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Errors', response.data)
        self.assertEqual(response.data['Status'], False)

    def test_create_user_wrong_field(self):
        """
        Checks for new user registrations,
        field is wrong.
        """

        data = deepcopy(self.data)
        self.data.pop('last_name')

        response = self.client.post(self.url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Errors', response.data)
        self.assertEqual(response.data['Status'], False)

    def test_user_login(self):
        """ Checks for login is success. """

        self.create_user()
        email = self.data['email']
        password = self.data['password']
        login_data = dict(email=email, password=password)

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Status', response.data)
        self.assertEqual(response.data['Status'], True)

    def test_user_login_not_field(self):
        """
        Checks for login, if not all fields are specified.
        """

        self.create_user()
        email = self.data['email']
        password = self.data['password']
        login_data = dict(email=email, password=password)
        login_data.pop('email')

        response = self.client.post(self.login_url, login_data, format='json')

        self.assertEqual(self.failureException, AssertionError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_contact_view(self):
        """ Get user contacts. """

        url_contact = reverse('backend:user-contact')

        self.create_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        response = self.client.get(url_contact, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.data)

    def test_get_contact_view_not_authorize(self):
        """ Get user contacts without authorization. """

        url_contact = reverse('backend:user-contact')

        response = self.client.get(url_contact, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Error', response.data)
        self.assertEqual(response.data['Status'], False)

    def test_post_contact_view(self):
        """ Create user's contacts. """

        url_contact = reverse('backend:user-contact')

        self.create_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {
            "city": "Miass",
            "street": "Veteranov",
            "house": "9",
            "structure": "0",
            "building": "0",
            "apartment": "0",
            "phone": "8-800-555-35-35"
        }

        response = self.client.post(url_contact, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('Error', response.data)
        self.assertEqual(response.data['Status'], True)

    def test_post_contact_view_not_field(self):
        """ Create user's contacts, if not all fields are specified. """

        url_contact = reverse('backend:user-contact')

        self.create_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {
            "city": "Miass",
            "structure": "12",
            "building": "0",
            "apartment": "0",
            "phone": "8-800-777"
        }

        response = self.client.post(url_contact, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Errors', response.data)
        self.assertEqual(response.data['Status'], False)

    def test_del_contact_view(self):
        """ Delete user contact. """

        url_contact = reverse('backend:user-contact')

        self.create_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {"items": "10"}

        response = self.client.delete(url_contact, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['Status'], True)

    def test_del_contact_view_not_fields(self):
        """ Delete user contact, if not all fields are specified. """

        url_contact = reverse('backend:user-contact')

        self.create_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {"items": ''}

        response = self.client.delete(url_contact, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['Status'], False)
