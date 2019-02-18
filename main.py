import os
import requests
from dotenv import load_dotenv
import random


def fetch_picture(image_name, url):
    directory = 'images'
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, image_name)
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)


def get_auth_params():
    TOKEN = os.getenv('TOKEN')
    GROUP_ID = os.getenv('GROUP_ID')
    version = 5.92
    params = {
        'access_token': TOKEN,
        'group_id': GROUP_ID,
        'v': version
    }
    return params


def main():
    load_dotenv()
    url, comment = get_random_picture_url_and_comment()
    fetch_picture('xkcd.png', url)
    auth_params = get_auth_params()
    upload_photo_params = upload_photo(auth_params)
    save_photo_params = save_wall_photo(auth_params, upload_photo_params)
    photo_id = get_photo_id(save_photo_params['response'][0])
    wall_post(auth_params, photo_id, comment)
    os.remove('images/xkcd.png')


def get_random_picture_url_and_comment():
    url = 'http://xkcd.com/info.0.json'
    response = requests.get(url)
    total_pictures = response.json()['num']
    picture_num = random.randint(0, total_pictures)
    url = 'http://xkcd.com/{}/info.0.json'.format(picture_num)
    response = requests.get(url)
    data = response.json()
    return data['img'], data['alt']


def wall_post(auth_params, photo_id, comment):
    url = 'https://api.vk.com/method/wall.post'
    params = auth_params
    params['attachments'] = photo_id
    params['owner_id'] = '-{group_id}'.format(**params)
    params["from_group"] = 1
    params['message'] = comment
    response = requests.post(url=url, params=params)
    return response.json()


def get_photo_id(photo_params):
    return "photo{owner_id}_{id}".format(**photo_params)


def get_upload_url(auth_params):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url=url, params=auth_params)
    return response.json()['response']['upload_url']


def upload_photo(auth_params):
    api_host = get_upload_url(auth_params)
    image_path = 'images/xkcd.png'
    params = auth_params
    with open(image_path, 'rb') as file:
        files = {"photo": file}
        response = requests.post(url=api_host, files=files, params=params)
    return response.json()


def save_wall_photo(auth_params, upload_photo_params):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = dict(auth_params, **upload_photo_params)
    response = requests.post(url=url, params=params)
    return response.json()


if __name__ == '__main__':
    main()

