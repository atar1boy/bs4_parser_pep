from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_STATUS_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

PEP_TYPES_KEY = {
    'I': 'Informational',
    'P': 'Process',
    'S': 'Standards Track'
}

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
