## Автопостер xckd-комиксов

Программа скачивает случайный коммикс с [xckd](https://xkcd.com/) и размещает
его в вашей группе в социальной сети [Вконтакте](https://vk.com/).

## Установка

В системе должен быть установлен интерпретатор языка `Python` версии
`3.10` и выше.

```
python3 --version
```

Рекомендуется использовать 
[виртуальное окружение](https://docs.python.org/3/library/venv.html).
Выполните эти команды находясь в рабочей директории.

```
python3 -m venv env
source env/bin/activate # Unix-based
.\venv\Scripts\activate # Windows
```

Скачайте [архив](https://github.com/6f6e69/vk-comics/archive/refs/heads/main.zip) 
с файлами программы и разархивируйте в рабочую директорию. 


Используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей. 

```
pip install -r requirements.txt
```

### Настройка проекта

Для того чтобы взаимодействовать с API [vk.com](https://vk.com/):
- [зарегистрируйте приложение](https://vk.com/dev) и получите `access_token`
- узнайте `id` группы в которую будете размещать комиксы,
[онлайн сервис]()
Создайте в папке проекта `.env` файл и запишите туда `access_token` и `id` группы.
```
VK_API_TOKEN=vk1.a.NF0yWo9VYmExAw3aw75DWJh6E2vcpP85mXYoKsf93b1rYHG
VK_GROUP_ID=123456789
```


## Использование

Запустите программу из командной строки.

```
python3 python3 vk_comics/vk_comics.py
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).