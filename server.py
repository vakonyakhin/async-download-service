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
    download_dir= os.path.join(storage_dir, path)
    logging.info(f'download dir is {download_dir}')


    if not os.path.exists(download_dir):
        logging.info(f'Folder does not exist')
        await handle_404(request)

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f'attachment; filename=photos.zip'
    response.enable_chunked_encoding()
    await response.prepare(request)

    zip_params = ['zip', '-r', '-', '-j', download_dir]
    proc = await create_subprocess_exec(
            *zip_params,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    logging.debug(f'Run archivw process - {proc.pid}.')

    try:
        while not proc.stdout.at_eof():

                stdout_data = await proc.stdout.read(chunk_size_bytes)
                logging.debug(f'Read archive chunk ... ')

                await response.write(stdout_data)
                logging.debug(f'Sending archive chunk ..')
                await sleep(delay)
        logging.debug('End of the stream')

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
               
    logging_level = os.environ['LOG_LEVEL']

    logging.basicConfig(filename='app.log', filemode='w', level=logging_level)
    logging.debug(f'logging level is --- {logging_level}')

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', get_archive_handler),
        web.get('/archive/{tail:.*}', handle_404)
    ])
    web.run_app(app, host='127.0.0.1', port=8888)
