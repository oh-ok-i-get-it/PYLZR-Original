from ..core import text_styles as txt

# Maps Qt key codes to MIDI note numbers (60 = C3, sequential from there).
_KEY_TO_MIDI = {
    49: 60,        # 1
    50: 61,        # 2
    51: 62,        # 3
    52: 63,        # 4
    53: 64,        # 5
    54: 65,        # 6
    55: 66,        # 7
    56: 67,        # 8
    57: 68,        # 9
    48: 69,        # 0
    45: 70,        # -
    61: 71,        # =
    16777217: 72,  # TAB
    81: 73,        # q
    87: 74,        # w
    69: 75,        # e
    82: 76,        # r
    84: 77,        # t
    89: 78,        # y
    85: 79,        # u
    73: 80,        # i
    79: 81,        # o
    80: 82,        # p
    91: 83,        # [
    93: 84,        # ]
    65: 85,        # a
    83: 86,        # s
    68: 87,        # d
    70: 88,        # f
    71: 89,        # g
    72: 90,        # h
    74: 91,        # j
    75: 92,        # k
    76: 93,        # l
    59: 94,        # ;
    39: 95,        # '
    90: 96,        # z
    88: 97,        # x
    67: 98,        # c
    86: 99,        # v
    66: 100,       # b
    78: 101,       # n
    77: 102,       # m
    44: 103,       # ,
    46: 104,       # .
    47: 105,       # /
    32: 106,       # SPACE
    16777220: 107, # ENTER
    16777248: 108, # L_SHIFT
}

_KEY_NAMES = {
    49: '1',  50: '2',  51: '3',  52: '4',  53: '5',
    54: '6',  55: '7',  56: '8',  57: '9',  48: '0',
    45: '-',  61: '=',  16777217: 'TAB',
    81: 'q',  87: 'w',  69: 'e',  82: 'r',  84: 't',
    89: 'y',  85: 'u',  73: 'i',  79: 'o',  80: 'p',
    91: '[',  93: ']',
    65: 'a',  83: 's',  68: 'd',  70: 'f',  71: 'g',
    72: 'h',  74: 'j',  75: 'k',  76: 'l',
    59: ';',  39: "'",
    90: 'z',  88: 'x',  67: 'c',
    86: 'v',  66: 'b',  78: 'n',  77: 'm',
    44: ',',  46: '.',  47: '/',
    32: 'SPACE', 16777220: 'ENTER', 16777248: 'L_SHIFT',
}


class KeyboardMapper:
    """Routes Qt key codes to MIDI notes via a static lookup table.

    handle_key() is a no-op when sound mode is active (midi_out.sm_ON).
    Left Shift (16777248) is intentionally excluded from routing here —
    it is intercepted upstream in the main window to toggle sound mode.
    """

    def __init__(self, midi_out):
        self._midi = midi_out

    def handle_key(self, key_num: int):
        if self._midi.sm_ON:
            return
        note = _KEY_TO_MIDI.get(key_num)
        if note is not None:
            name = _KEY_NAMES.get(key_num, str(key_num))
            print(
                txt.B + txt.CYANB + txt.BLACK + 'Pressed:' +
                txt.RESET + txt.CYAN + txt.B + f' {name}' + txt.RESET
            )
            print(f'midi value: {note}')
            self._midi.press_note(note)
