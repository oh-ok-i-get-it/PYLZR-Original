import threading
import rtmidi as midi
from ..core import text_styles as txt
from ..core.app_logger import logger


class MIDIOutput:
    """Virtual MIDI port with sound-mode state.

    Creates a virtual port named 'PyLZR-MIDI' if no hardware ports are
    available, otherwise opens the first available port.

    press_note() sends a Note ON followed by a Note OFF after 50 ms.
    toggle_sm() flips the sm_ON flag used by KeyboardMapper and SoundMode.
    """

    def __init__(self):
        self.midiout = midi.MidiOut()
        available = self.midiout.get_ports()
        if available:
            self.midiout.open_port(0)
            logger.info(f'MIDI: opened port "{available[0]}"')
        else:
            self.midiout.open_virtual_port('PyLZR-MIDI')
            logger.info('MIDI: created virtual port "PyLZR-MIDI"')

        self.sm_ON = False

        self._SM_ON_TXT    = txt.RESET + txt.B + txt.GREEN
        self._SM_ON_TXT_B  = txt.B + txt.GREENB + txt.BLACK
        self._SM_OFF_TXT   = txt.RESET + txt.B + txt.RED
        self._SM_OFF_TXT_B = txt.B + txt.REDB + txt.BLACK

    def press_note(self, note: int):
        NOTE_ON  = 0x90
        NOTE_OFF = 0x80
        self.midiout.send_message([NOTE_ON, note, 112])

        def send_off():
            self.midiout.send_message([NOTE_OFF, note, 0])

        t = threading.Timer(0.05, send_off)
        t.daemon = True
        t.start()

    def toggle_sm(self):
        if self.sm_ON:
            print(f"\n{self._SM_OFF_TXT}#### {self._SM_OFF_TXT_B}SOUND MODE OFF{self._SM_OFF_TXT} ####\n{txt.RESET}")
            logger.info('Sound mode: OFF', '#e74c3c')
        else:
            print(f"\n{self._SM_ON_TXT}#### {self._SM_ON_TXT_B}SOUND MODE ON{self._SM_ON_TXT} ####\n{txt.RESET}")
            logger.info('Sound mode: ON', '#2ecc71')
        self.sm_ON = not self.sm_ON
