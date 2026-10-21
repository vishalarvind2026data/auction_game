from os import environ

SESSION_CONFIGS = [
    dict(
        name='live_auction',
        display_name='Real-Time English Auction',
        app_sequence=['live_auction'],
        num_demo_participants=4,   # must be a multiple of C.PLAYERS_PER_GROUP
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = []

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """
SECRET_KEY = 'change-me'
