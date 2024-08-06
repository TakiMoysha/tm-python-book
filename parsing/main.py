#! python

import requests

if __name__ == "__main__":
    url = "https://lemanapro.ru/product/" + '...'
    response = requests.get(url)
    print(response.text)
