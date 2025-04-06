"""
Playwright配置
"""

BROWSER_CONFIG = {
    'browser_type': 'chromium',
    'launch_options': {
        'headless': True,
        'args': ['--no-sandbox']
    },
    'context_options': {
        'viewport': {'width': 1920, 'height': 1080},
        'ignore_https_errors': True
    },
    'page_options': {
        'timeout': 30000
    }
} 