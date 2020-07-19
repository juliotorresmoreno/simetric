

import requests

def test_sum():
    url = 'http://localhost:8000/api/titanic/?limit=0,2&sex=male&Name=like:Braund&Ticket=like:A&Fare=gt:7&sort=name:desc,Sex:asc'
    r = requests.get(url)
    assert r.status_code == 200, 'consulta a api titanic exitosa'

def test_sum_tuple():
    assert sum((1, 2, 2)) == 6, "Should be 6"

if __name__ == "__main__":
    test_sum()
    test_sum_tuple()
    print("Everything passed")
