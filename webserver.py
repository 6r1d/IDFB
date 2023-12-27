"""
Classes:
    - TriageWebServer: HTTP server class for the triage bot.

Example usage:

    rotation_path = Path('./rotation')
    server = TriageWebServer(rotation_path)
    await server.start_http_server(
        bot=telegram_bot,
        address='0.0.0.0',
        port=8080
    )
"""

from pathlib import Path
from json import dumps
from aiohttp import web
from hash import file_id_generator

class TriageWebServer:
    """
    HTTP server class for the triage bot.
    """

    def __init__(self, rotation_path: Path):
        """
        Pre-configure the runner.
        """
        self.rotation_path = rotation_path
        self.runner = None

    async def serve_main_page(self, _):
        """
        Returns:
            (Response): aiohttp text page
        """
        return web.Response(text='Feedback processing server is working.')

    def generate_feedback_path(self) -> Path:
        """
        Returns:
            Path: the path for a new feedback rotation record
        """
        return self.rotation_path / f'{file_id_generator()}.json'

    async def handle_feedback_request(self, request):
        """
        Returns:
            Response: the result of the feedback processing
        """
        status = 200
        response_text = 'Feedback processed'
        request_data: str = dumps(await request.json())
        try:
            with open(self.generate_feedback_path(), 'w', encoding='utf-8') as fb_file:
                fb_file.write(request_data)
        except PermissionError:
            status = 500
            response_text = 'Incorrect permissions; unable to send feedback.'
        except UnicodeEncodeError:
            status = 500
            response_text = 'Incorrect input; unable to send feedback.'
        except OSError:
            status = 500
            response_text = 'An I/O error occurred; unable to send feedback.'
        return web.Response(text=response_text, status=status)

    async def start_http_server(self, address='0.0.0.0', port=8080, bot=None):
        """
        Start an AsyncIO server.

        Args:
            address (str): server address string, typically 0.0.0.0
            port (int): server port
            rotation_path (pathlib.Path): path for file rotation
            bot (TriageTelegramBot): bot instance
        """
        app = web.Application()
        app['bot'] = bot
        app.add_routes([
            web.get('/', self.serve_main_page),
            web.post('/feedback', self.handle_feedback_request)
        ])
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, address, port)
        await site.start()
        return self
