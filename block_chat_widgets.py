from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

class SettingsInput(TextInput):
    pass

class SettingsLabel(Label):
    pass

class ViewerLabel(SettingsLabel):
    pass

class NetworkToggle(ToggleButton, ToggleButtonBehavior):

    def __init__(self, **kwargs):
        super().__init__()

    def on_state(self, widget, value):
        if value == 'down':
            self.col = (0/255, 77/255, 0, 1)
        else:
            self.col = (128/255, 77/255, 0, 1)

class StreamerLabel(SettingsLabel):
    pass

class SenderTextLabel(SettingsLabel):
    pass

class SeparateLabel(Label):
    pass

class MessageSeparation(SeparateLabel):
    pass

class SenderInfoLabel(StreamerLabel):
    pass