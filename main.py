import time
import json
import requests


def uncode_date(code_date):
    date = time.strftime("__%d-%m-%Y_%H-%M", time.localtime(code_date))
    return date


class VkGetPhotos:
    def __init__(self, token, cnt=5, version='5.130'):
        self.url = 'https://api.vk.com/method/'
        self.token = token
        self.version = version
        self.cnt = cnt
        self.params = {
            'access_token': self.token,
            'v': self.version     
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_photos(self):
        photos_url = self.url + 'photos.get'
        photos_paramas = {
            'owner_id': self.owner_id,
            'album_id': 'profile',
            'rev': 1,
            'extended': 1,
            'count': self.cnt
        }
        res = requests.get(photos_url, params={**self.params, **photos_paramas}).json()
        if res != None:
            print('Сведения о фотографиях успешно получены', '\n')
        else:
            print('Ошибка при получении сведений о фотографиях', '\n')
        return res['response']['items']


class YandexDiskUploader:
    def __init__(self, user_token, dir_name='Upload_Photos', json_file='photos.json'):
        self.url = 'https://cloud-api.yandex.net:443/v1/disk/resources'
        self.upload_url = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        self.dir_name = dir_name
        self.json_file = json_file
        self.token = user_token
        self.vk = VkGetPhotos(vk_token)

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_dir(self):
        headers = self.get_headers()
        params = {'path': self.dir_name}
        res = requests.get(self.url, headers = headers, params=params)
        try:
            res.raise_for_status()
        except requests.HTTPError:
            pass
        if res.status_code == 200:
            print('Папка для загрузки была создана ранее', '\n')
        else:
            res = requests.put(self.url, headers = headers, params=params)
            try:
                res.raise_for_status()
            except requests.HTTPError:
                pass
            if res.status_code == 201:
                print('Папка для загрузки успешно создана', '\n')
            else:
                print('Ошибка при создании папки для загрузки', '\n')

    def upload_photos(self):
        headers = self.get_headers()
        photos_list = []

        for photo in self.vk.get_photos():
            params_get = {
                'path': self.dir_name + '/' + str(photo['likes']['count']) + '.jpg'
                }
            photo_dict = {}
            
            res_get = requests.get(self.url, headers = headers, params=params_get)
            try:
                res_get.raise_for_status()
            except requests.HTTPError:
                photo_dict['file_name'] = str(photo['likes']['count']) + '.jpg'
            else:
                photo_dict['file_name'] = str(photo['likes']['count']) + uncode_date(photo['date']) + '.jpg'

            res_post = requests.post(self.upload_url, headers=headers, params={
                'url': photo['sizes'][-1]['url'],
                'path': self.dir_name + '/' + photo_dict['file_name']
            }).json()

            res_success = requests.get(res_post['href'], headers=headers).json()
            print(f"Файл {photo_dict['file_name']} ({len(photos_list) + 1}/{self.vk.cnt}) загружается на яндекс диск")
            while res_success['status'] != 'success':
                time.sleep(2)
                res_success = requests.get(res_post['href'], headers=headers).json()
                if res_success['status'] == 'failed':
                    print(f"При загрузке файла {photo_dict['file_name']} ({len(photos_list) + 1}/{self.vk.cnt}) на яндекс диск произошла ошибка", '\n')
            print(f"Файл {photo_dict['file_name']} ({len(photos_list) + 1}/{self.vk.cnt}) успешно загружен на яндекс диск", '\n')

            photo_dict['size'] = str(photo['sizes'][-1]['width']) + 'x' + str(photo['sizes'][-1]['height']) + "(" + str(photo['sizes'][-1]['type']) + ")"
            photos_list.append(photo_dict)
        
        with open('photos.json', "w") as f:
            json.dump(photos_list, f, ensure_ascii=False, indent=2)
            print(f"Сведения о загруженных фотографиях записаны в файл {self.json_file}")

    def _get_upload_link(self):
        headers = self.get_headers()
        params = {
            'path': f"{self.dir_name}/{self.json_file}",
            'overwrite': True
        }
        res = requests.get(self.upload_url, headers=headers, params=params)
        return res.json()

    def upload_file(self):
        href = self._get_upload_link().get('href', '')
        res = requests.put(href, data=open(self.json_file, 'rb'))
        if res.status_code == 201:
            print(f"Файл {self.json_file} успешно загружен на яндекс диск в папку с фотографиями", '\n')
        else:
            print(f"При загрузке файла {self.json_file} произошла ошибка", '\n')

    def upload(self):
        print('Начало выполнения программы', '\n')
        self.create_dir()
        self.upload_photos()
        self.upload_file()
        print('Конец выполнения программы', '\n')

         
if __name__ == '__main__':
    vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    yandex = YandexDiskUploader('ВСТАВЬТЕ СЮДА ТОКЕН YANDEX DISK API')
    yandex.upload()