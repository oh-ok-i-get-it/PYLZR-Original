# ANSI terminal color and formatting escape codes.

# Foreground colors
BLUE   = '\033[34m'
GREEN  = '\033[32m'
RED    = '\033[31m'
YELLOW = '\033[33m'
PURPLE = '\033[35m'
CYAN   = '\033[36m'
WHITE  = '\033[37m'
BLACK  = '\033[30m'

# Background colors
BLACKB  = '\033[40m'
REDB    = '\033[41m'
GREENB  = '\033[42m'
YELLOWB = '\033[43m'
BLUEB   = '\033[44m'
PURPLEB = '\033[45m'
CYANB   = '\033[46m'
WHITEB  = '\033[47m'

# Text formatting
B    = '\033[1m'
BOFF = '\033[22m'
I    = '\033[3m'
IOFF = '\033[23m'
U    = '\033[4m'
UOFF = '\033[24m'

RESET = '\033[0m'

# Preset combinations
WARNING = B + I + U + REDB

__all__ = [
    'BLUE', 'GREEN', 'RED', 'YELLOW', 'PURPLE', 'CYAN', 'WHITE', 'BLACK',
    'BLACKB', 'REDB', 'GREENB', 'YELLOWB', 'BLUEB', 'PURPLEB', 'CYANB', 'WHITEB',
    'B', 'BOFF', 'I', 'IOFF', 'U', 'UOFF', 'RESET',
    'WARNING',
]
