from typing import Dict

def get_config() -> Dict:
    return {
        'use': {
            'viewport': {'width': 1280, 'height': 720},
            'screenshot': 'only-on-failure',
            'video': 'retain-on-failure',
            'trace': 'retain-on-failure',
            'headless': False
        },
        'browser': 'chromium',
        'base_url': 'http://localhost:3000',
        'expect': {
            'timeout': 5000,
            'to_have_text': {
                'timeout': 2000
            }
        },
        'timeout': 30000,
        'retries': 2
    } 