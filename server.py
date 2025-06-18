import logging
import os
import aiofiles
from asyncio import create_subprocess_exec, subprocess, sleep, CancelledError
from aiohttp import web


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def get_archive_handler(request):

    chunk_size_bytes = int(os.environ['CHUNK_SIZE'])
    delay = int(os.environ['DELAY'])
    storage_dir = os.environ['STORAGE_DIR']
    
    path = request.match_info.get('archive_hash')
    storage_photo = os.path.join(storage_dir, path)
    logging.info(f'storage dir is {storage_photo}')


    if not os.path.exists(storage_photo):
        logging.info(f'Folder does not exist')
        await handle_404(request)

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f'attachment; filename=photos.zip'
    await response.prepare(request)

    zip_params = ['zip', '-r', '-', '-j', storage_photo]
    proc = await create_subprocess_exec(
            *zip_params,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    logging.debug(f'Run archivw process - {proc.pid}.')

    try:
        while True:

                stdout_data = await proc.stdout.read(chunk_size_bytes)
                logging.debug(f'Read archive chunk ... ')
                if not stdout_data:
                    logging.debug('End of the stream')
                    break

                logging.debug(f'Sending archive chunk ..')
                await response.write(stdout_data)
                await sleep(delay)


    except ConnectionResetError:
        logging.debug('Download was interrupted')
        logging.debug(f'Process pid is necessary to stop - {proc.pid}. ')
        proc.terminate()
        logging.debug(f'Process stopped... ')

    except CancelledError:
        logging.debug('Stop coroutines')
        proc.terminate()
        raise

    finally:
        return response


async def handle_404(request):
    return web.Response(text="Архив не существует или был удален", status=404)


if __name__ == '__main__':
               
    logging_level = os.environ["LOG_LEVEL"]

    logging.basicConfig(filename='app.log', filemode='w', level=logging_level)
    logging.debug(f'logging level is --- {logging_level}')

    #archive_handler = functools.partial(archivate, storage_dir=args.dir, delay=delay)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', get_archive_handler),
        web.get('/archive/{tail:.*}', handle_404)
    ])
    web.run_app(app)
