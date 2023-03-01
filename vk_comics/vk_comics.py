from environs import Env
from random import randint
from io import BytesIO
import requests
from urllib import parse


def fetch_xkcd_comics() -> tuple[BytesIO, str]:
    comics_id: int = randint(1, 500)
    comics_info_url: str = f"https://xkcd.com/{comics_id}/info.0.json"
    with requests.get(comics_info_url) as response:
        response.raise_for_status()
        comics_info: dict = response.json()
        comics_image_url: str = comics_info['img']
        comics_comment: str = comics_info['alt']
    with requests.get(comics_image_url) as response:
        response.raise_for_status()
        comics_image: BytesIO = BytesIO(response.content)
    return comics_image, comics_comment


class VkAPIerror(Exception):
    pass


def raise_vk_response_for_error(response: dict) -> bool:
    if response.get('error'):
        raise VkAPIerror(f"Error code:{response['error']}"
                         f"{response['error']['error_msg']}")
    else:
        return True


def get_wall_upload_server_url() -> str:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'photos.getWallUploadServer'
    wall_upload_api_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str] = {
        'access_token': main.vk_access_token,
        'group_id': main.vk_group_id,
        'v': '5.81',
    }
    with requests.get(wall_upload_api_url, params) as response:
        response.raise_for_status()
        response_json: dict = response.json()
    raise_vk_response_for_error(response_json)
    return response_json['response']['upload_url']


def upload_comics_image(comics_wall_upload_server_url: str,
                        comics_image: BytesIO) -> tuple[str, str, str]:
    files: dict[str, tuple[str, bytes]] = {'photo': ('comics.png',
                                           comics_image.getvalue())}
    comics_image.close()
    with requests.post(comics_wall_upload_server_url,
                       files=files) as response:
        response.raise_for_status()
        response_json: dict = response.json()
    raise_vk_response_for_error(response_json)
    return (response_json['server'],
            response_json['photo'],
            response_json['hash'])


def save_wall_comics_image(vk_server: str,
                           comics_json: str,
                           comics_hash: str) -> tuple[str, str]:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'photos.saveWallPhoto'
    save_wall_photo_api_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str] = {
        'access_token': main.vk_access_token,
        'group_id': main.vk_group_id,
        'v': '5.81',
        'server': vk_server,
        'photo': comics_json,
        'hash': comics_hash,
    }
    with requests.post(save_wall_photo_api_url, params=params) as response:
        response.raise_for_status()
        response_json: dict = response.json()
    raise_vk_response_for_error(response_json)
    return (response_json['response'][0]['id'],
            response_json['response'][0]['owner_id'])


def public_post_on_wall(comics_comment: str,
                        comics_image_id: str,
                        comics_image_owner_id: str) -> None:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'wall.post'
    public_pos_on_wall_api_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str | int] = {
        'access_token': main.vk_access_token,
        'v': '5.81',
        'owner_id': f"-{main.vk_group_id}",
        'message': comics_comment,
        'attachments': f"photo{comics_image_owner_id}_{comics_image_id}",
        'from_group': 1,
    }
    with requests.post(public_pos_on_wall_api_url, params=params) as response:
        response.raise_for_status()
        response_json: dict = response.json()
    raise_vk_response_for_error(response_json)


def main() -> None:
    env: Env = Env()
    env.read_env()
    main.vk_access_token: str = env('API_TOKEN')
    main.vk_group_id: str = env('GROUP_ID')
    comics_image: BytesIO
    comics_comment: str
    comics_image, comics_comment = fetch_xkcd_comics()
    comics_wall_upload_server_url: str = get_wall_upload_server_url()
    comics_hash: str
    comics_json: str
    vk_server: str
    vk_server, comics_json, comics_hash = upload_comics_image(
                                                comics_wall_upload_server_url,
                                                comics_image)
    comics_image_id: str
    comics_image_owner_id: str
    comics_image_id, comics_image_owner_id = save_wall_comics_image(
                                                                vk_server,
                                                                comics_json,
                                                                comics_hash)
    public_post_on_wall(comics_comment, comics_image_id, comics_image_owner_id)


if __name__ == '__main__':
    main()
