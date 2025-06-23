import logging
import os
import aiofiles
from asyncio import create_subprocess_exec, subprocess, sleep, CancelledError
from aiohttp import web


async def handle_index_page(request):
    """Handle GET requests for the root page."""
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def get_archive_handler(request):
    """Handle GET requests for archiving files."""
    chunk_size_bytes = int(os.environ['CHUNK_SIZE'])
    delay = int(os.environ['DELAY'])
    storage_dir = os.environ['STORAGE_DIR']

    path = request.match_info.get('archive_hash')
    download_dir = os.path.join(storage_dir, path)
    logging.info(f'Download directory is {download_dir}')

    if not os.path.exists(download_dir):
        logging.info('Directory does not exist')
        await handle_404(request)
        return

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename=photos.zip'
    await response.prepare(request)

    zip_params = ['zip', '-r', '-', '-j', download_dir]
    proc = await create_subprocess_exec(
        *zip_params,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
        )
    logging.info(f'Started ZIP process PID={proc.pid}')

    try:
        while not proc.stdout.at_eof():
            stdout_data = await proc.stdout.read(chunk_size_bytes)
            logging.info('Reading archive chunk...')
            await response.write(stdout_data)
            logging.info('Sent archive chunk.')
            await sleep(delay)
        logging.info('Archive streaming complete.')

        stdout, stderr = await proc.communicate()
        logging.info(f'Final communication with process {proc.pid}')

    except ConnectionResetError:
        logging.info('Connection reset by client.')
        logging.info(f'Terminating ZIP process PID={proc.pid}')

    except CancelledError:
        logging.info('Coroutine cancelled.')
        raise

    finally:
        if proc.returncode is None:
            logging.info(f'ZIP process {proc.pid} terminated.')
            proc.terminate()
        elif proc.returncode != 0:
            logging.error(
                f'Zip process failed with exit code {proc.returncode}'
                )
        return response


async def handle_404(request):
    """Handle all other non-matching routes returning a 404 Not Found."""
    return web.Response(text="Архив не существует или был удален.", status=404)


if __name__ == '__main__':
    logging_level = os.environ["LOG_LEVEL"]
    logging.basicConfig(filename='app.log', filemode='w', level=logging_level)
    logging.info(f'Logging level set to {logging_level}')

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', get_archive_handler),
        web.get('/archive/{tail:.*}', handle_404)
    ])
    web.run_app(app)
