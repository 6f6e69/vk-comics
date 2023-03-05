from io import BytesIO
from random import randint

from environs import Env
import requests
from urllib import parse


def fetch_xkcd_comic() -> tuple[BytesIO, str]:
    comic_id: int = randint(1, 500)
    comic_info_url: str = f"https://xkcd.com/{comic_id}/info.0.json"
    with requests.get(comic_info_url) as response:
        response.raise_for_status()
        response: dict = response.json()
        comic_image_url: str = response['img']
        comic_comment: str = response['alt']
    with requests.get(comic_image_url) as response:
        response.raise_for_status()
        comic_image: BytesIO = BytesIO(response.content)
    return comic_image, comic_comment


class VkAPIerror(Exception):
    pass


def raise_vk_response_for_error(response: dict) -> None:
    if response.get('error'):
        raise VkAPIerror(f"Error code:{response['error']}"
                         f"{response['error']['error_msg']}")


def get_wall_upload_server_url(vk_access_token: str,
                               vk_group_id: str) -> str:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'photos.getWallUploadServer'
    method_full_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str] = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': '5.81',
    }
    with requests.get(method_full_url, params) as response:
        response.raise_for_status()
        response: dict = response.json()
    raise_vk_response_for_error(response)
    return response['response']['upload_url']


def upload_comic_image(comic_wall_upload_server_url: str,
                       comic_image: BytesIO) -> tuple[str, str, str]:
    files: dict[str, tuple[str, bytes]] = {'photo': ('comics.png',
                                           comic_image.getvalue())}
    comic_image.close()
    with requests.post(comic_wall_upload_server_url,
                       files=files) as response:
        response.raise_for_status()
        response: dict = response.json()
    raise_vk_response_for_error(response)
    vk_server: str = response['server']
    comic_image_attributes: str = response['photo']
    comic_image_hash: str = response['hash']
    return vk_server, comic_image_attributes, comic_image_hash


def save_wall_comic_image(vk_access_token: str,
                          vk_group_id: str,
                          vk_server: str,
                          comic_image_attributes: str,
                          comic_image_hash: str) -> tuple[str, str]:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'photos.saveWallPhoto'
    method_full_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str] = {
        'access_token': vk_access_token,
        'group_id': vk_group_id,
        'v': '5.81',
        'server': vk_server,
        'photo': comic_image_attributes,
        'hash': comic_image_hash,
    }
    with requests.post(method_full_url, params=params) as response:
        response.raise_for_status()
        response: dict = response.json()
    raise_vk_response_for_error(response)
    comic_image_id: str = response['response'][0]['id']
    comic_image_owner_id: str = response['response'][0]['owner_id']
    return comic_image_id, comic_image_owner_id


def publish_post_on_wall(vk_access_token: str,
                         vk_group_id: str,
                         comics_comment: str,
                         comics_image_id: str,
                         comics_image_owner_id: str) -> None:
    vk_api_url: str = 'https://api.vk.com/method/'
    method_name: str = 'wall.post'
    method_full_url: str = parse.urljoin(vk_api_url, method_name)
    params: dict[str, str | int] = {
        'access_token': vk_access_token,
        'v': '5.81',
        'owner_id': f"-{vk_group_id}",
        'message': comics_comment,
        'attachments': f"photo{comics_image_owner_id}_{comics_image_id}",
        'from_group': 1,
    }
    with requests.post(method_full_url, params=params) as response:
        response.raise_for_status()
        response: dict = response.json()
    raise_vk_response_for_error(response)


def main() -> None:
    env: Env = Env()
    env.read_env()
    vk_access_token: str = env('VK_API_TOKEN')
    vk_group_id: str = env('VK_GROUP_ID')
    comic_image: BytesIO
    comic_comment: str
    comic_image, comic_comment = fetch_xkcd_comic()
    comic_wall_upload_server_url: str = get_wall_upload_server_url(
                                                      vk_access_token,
                                                      vk_group_id)
    vk_server: str
    comic_image_attributes: str
    comic_image_hash: str
    vk_server, comic_image_attributes, comic_image_hash = upload_comic_image(
                                                  comic_wall_upload_server_url,
                                                  comic_image)
    comic_image_id: str
    comic_image_owner_id: str
    comic_image_id, comic_image_owner_id = save_wall_comic_image(
                                                        vk_access_token,
                                                        vk_group_id,
                                                        vk_server,
                                                        comic_image_attributes,
                                                        comic_image_hash)
    publish_post_on_wall(vk_access_token,
                         vk_group_id,
                         comic_comment,
                         comic_image_id,
                         comic_image_owner_id)


if __name__ == '__main__':
    main()
