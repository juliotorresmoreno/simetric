
import unittest
from django.test import TestCase, Client
# Create your tests here.

class SimpleTest(unittest.TestCase):
    def test_api(self):
        c = Client()
        response = c.get('/api/titanic/?limit=0,2&sex=male&Name=like:Braund&Ticket=like:A&Fare=gt:7&sort=name:desc,Sex:asc')
        self.assertEqual(response.status_code, 200)