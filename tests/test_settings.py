import unittest
from unittest.mock import patch
from src.helpers.settings import get_settings, Settings


class TestSettings(unittest.TestCase):

    @patch.dict('os.environ', {
        'APP_NAME': 'TestApp',
        'APP_VERSION': '0.0.1',
        'DOC_LOCATION_SAVE': '/tmp/docs',
        'CONFIG_DIR': '/tmp/config',
        'DATABASE_URL': 'sqlite:///test.db',
        'EMBEDDING_MODEL': 'test-embedding',
        'HUGGINGFACE_TOKIENS': 'fake-token',
        'DEFAULT_SYSTEM_PROMPT': 'You are a helpful assistant.',
        'ENABLE_MEMORY': 'true',

        'FILE_ALLOWED_TYPES': '["pdf", "txt"]',
        'FILE_MAX_SIZE': '1048576',
        'FILE_DEFAULT_CHUNK_SIZE': '512',
        'CHUNKS_OVERLAP': '10',
        'GPU_AVAILABLE': 'false',

        'LOG_LEVEL': 'DEBUG',

        'CPU_THRESHOLD': '80',
        'MEMORY_THRESHOLD': '75',
        'MONITOR_INTERVAL': '30',
        'DISK_THRESHOLD': '70',
        'GPUs_THRESHOLD': '90',

        'TELEGRAM_BOT_TOKEN': 'fake-token',
        'TELEGRAM_CHAT_ID': '123456'
    })
    def test_settings_loading(self):
        # Clear the cache so patched env vars are used
        get_settings.cache_clear()

        settings = get_settings()

        self.assertEqual(settings.APP_NAME, 'TestApp')
        self.assertTrue(settings.ENABLE_MEMORY)
        self.assertEqual(settings.FILE_MAX_SIZE, 1048576)
        self.assertEqual(settings.FILE_ALLOWED_TYPES, ["pdf", "txt"])
        self.assertEqual(settings.GPU_AVAILABLE, False)
        self.assertEqual(settings.LOG_LEVEL, 'DEBUG')


if __name__ == '__main__':
    unittest.main()
