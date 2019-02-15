import logging
import requests

from torrt.base_notifier import BaseNotifier
from torrt.utils import NotifierClassesRegistry

LOGGER = logging.getLogger(__name__)


class TelegramNotifier(BaseNotifier):
    """Telegram bot notifier. See instructions how to create bot at https://core.telegram.org/bots/api"""
    alias = 'telegram'
    url = 'https://api.telegram.org/bot'

    def __init__(self, token, chat_id, proxies=None, tor_address=None):
        """
        :param tor_address:
        :param proxies:
        :param token: str - Telegram's bot token
        :param chat_id: str - Telegram's chat ID
        """

        self.token = token
        self.chat_id = chat_id
        if tor_address:
            self.proxies = {'http': 'socks5://{}'.format(tor_address),
                            'https': 'socks5://{}'.format(tor_address)}
        else:
            self.proxies = proxies

        self.r_kwargs = {'proxies': self.proxies}

    def make_message(self, torrent_data):
        return '''The following torrents were updated:\n%s''' \
               % '\n'.join(map(lambda t: t['name'], torrent_data.values()))

    def test_configuration(self):
        url = '%s%s/getMe' % (self.url, self.token)
        r = requests.get(url, **self.r_kwargs)
        return r.json().get('ok', False)

    def send_message(self, msg):
        url = '%s%s/sendMessage' % (self.url, self.token)
        r = requests.post(url, data={'chat_id': self.chat_id, 'text': msg}, **self.r_kwargs)
        if r.json()['ok']:
            LOGGER.info('Telegram message was sent to user %s' % self.chat_id)
        else:
            LOGGER.error('Telegram notification not send: %s' % r.json()['description'])


NotifierClassesRegistry.add(TelegramNotifier)
