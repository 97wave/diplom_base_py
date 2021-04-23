import requests

from pprint import pprint

class VkGetPhotos:
    def __init__(self, token, version='5.130'):
        self.url = 'https://api.vk.com/method/'
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version     
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_photos(self, cnt=5):
        photos_url = self.url + 'photos.get'
        photos_paramas = {
            'owner_id': self.owner_id,
            'album_id': 'profile',
            'rev': 1,
            'extended': 1,
            'photo_sizes': 'o',
            'count': cnt
        }
        res = requests.get(photos_url, params={**self.params, **photos_paramas}).json()
        return res['response']['items']


if __name__ == '__main__':
    vk = VkGetPhotos('958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008')
    pprint(vk.get_photos(1))
    