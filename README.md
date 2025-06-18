# Микросервис для скачивания файлов

Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить

Для работы микросервиса нужен docker должен быть установлен

Для создания образа используйте команду

```bash
docker build <image_name> .
```

## Как запустить
После сборки запустите команду

```bash
docker run -d -p 8080:8080 <image_name>
```

Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Изменение параметров

В работе сервиса используются параметры окружения со значениями по умолчанию формируемыми при сборке

'''
ENV STORAGE_DIR=./test_photos/ # general path for stored files

ENV DELAY=1 # in seconds

ENV LOG_LEVEL=DEBUG # using logging module level

ENV CHUNK_SIZE=300000 # in bytes
'''

Для изменения параметров по умолчанию при старте используйте парамерт -e

'''
docker run -d -p 8080:8080 -e DELAY=1 <image_name>
'''

## Как развернуть на сервере

```bash
docker run -d -p 8080:8080 <image_name>
```

После этого перенаправить на микросервис запросы, начинающиеся с `/archive/`. Например:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).



# Microservice for downloading files
The microservice helps the main website built on a CMS by handling requests to download archives with files. The microservice is only capable of packaging files into an archive. Files are uploaded to the server via FTP or through the CMS admin panel.

Archive creation happens dynamically upon user request. The archive is not saved to disk; instead, it is sent directly to the user as it's being packaged.

Unauthorized access to the archive is protected by a hash in the download link address, e.g.: http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/. The hash is determined by the directory name containing the files. The directory structure looks like this:


- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg

## How to install
For the microservice to work, Docker must be installed.

To create an image, use the command:

'''
docker build <image_name> .
'''

## How to start
After building, run the following command:


docker run -d -p 8080:8080 <image_name>
The server will start on port 8080. To check its operation, navigate to http://127.0.0.1:8080/ in your browser.

## Changing parameters
In service operation, environment variables with default values set during assembly are used:

'''
ENV STORAGE_DIR=./test_photos/ # general path for stored files

ENV DELAY=1 # in seconds

ENV LOG_LEVEL=DEBUG # using logging module level

ENV CHUNK_SIZE=300000 # in bytes
'''

To change these default parameters at startup, use the parameter -e:

'''
docker run -d -p 8080:8080 -e DELAY=1 <image_name>
'''

## Deploying on a server

'''
docker run -d -p 8080:8080 <image_name>'''

Then redirect all requests starting with /archive/ to the microservice. For example:


GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea


## Project goals
This code was written for educational purposes—it's a lesson from a course on Python and web development on the site Devman.