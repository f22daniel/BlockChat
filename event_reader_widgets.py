from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivymd.uix.behaviors import HoverBehavior
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.button import Button

class SettingsButton(Button, ButtonBehavior, HoverBehavior):
    settings_image = ObjectProperty(None)
    enter_image = Animation(rot_angle=0, duration=0.01) + Animation(rot_angle=-60, duration=0.2)
    leave_image = Animation(rot_angle=-60, duration=0.01) + Animation(rot_angle=0, duration=0.2)

    def __init__(self, **kwargs):
        super(SettingsButton, self).__init__(**kwargs)
        self.image_anim = None
        self.press_anim = None

    def on_press(self):
        self.press_anim = Animation(col=(0, 0, 179 / 255, 1), duration=0.2)
        self.image_anim = Animation(color=(1, 1, 1, 1 / 2), duration=0.2)
        self.press_anim.start(self)
        self.image_anim.start(self.settings_image)

    def on_release(self):
        self.press_anim = Animation(col=(51 / 255, 51 / 255, 1, 1), duration=0.2)
        self.image_anim = Animation(color=(1, 1, 1, 1), duration=0.2)
        self.press_anim.start(self)
        self.image_anim.start(self.settings_image)

    # Function which runs when mouse hoveres over the widget
    def on_enter(self):
        self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
        self.press_anim.start(self)
        self.enter_image.start(self.settings_image)

    # Function which runs when mouse leaves the widget
    def on_leave(self):
        self.press_anim = Animation(col=(51 / 255, 51 / 255, 1, 1), duration=0.2)
        self.press_anim.start(self)
        self.leave_image.start(self.settings_image)

class TaskButton(Button, ButtonBehavior, HoverBehavior):

    task_image = ObjectProperty(None)
    shrink_image = Animation(size_hint=[0.8, 0.8], duration=0.2)
    expand_image = Animation(size_hint=[1, 1], duration=0.2)
    hover_image = Animation(size_hint=[1.1, 1.1], duration=0.2) + Animation(size_hint=[1, 1], duration=0.2)

    def __init__(self, **kwargs):
        super(TaskButton, self).__init__(**kwargs)
        self.image_anim = None
        self.press_anim = None

    def on_press(self):
        self.press_anim = Animation(col=(0, 0, 179 / 255, 1), duration=0.2)
        self.press_anim.start(self)
        self.shrink_image.start(self.task_image)

    def on_release(self):
        self.press_anim = Animation(col=(51 / 255, 51 / 255, 1, 1), duration=0.2)
        self.press_anim.start(self)
        self.expand_image.start(self.task_image)

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
            self.press_anim.start(self)
            self.hover_image.start(self.task_image)

    def on_leave(self):
        if not self.disabled:
            self.press_anim = Animation(col=(51 / 255, 51 / 255, 1, 1), duration=0.2)
            self.press_anim.start(self)

    def enable(self):
        enable_animation = Animation(col=(51/255, 51/255, 1, 1), duration=0.2)
        enable_animation.start(self)
        self.image_anim = Animation(color=(1, 1, 1, 1), duration=0.2)  # Color for picture when button released
        self.image_anim.start(self.task_image)

    def disable(self):
        disable_animation = Animation(col=(51/255, 26/255, 0, 1/2), duration=0.2)
        disable_animation.start(self)
        self.image_anim = Animation(color=(1, 1, 1, 1/2), duration=0.2)  # Color for picture when button pressed
        self.image_anim.start(self.task_image)

class CloseButton(TaskButton):

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
            self.press_anim.start(self)
            self.hover_image.start(self.task_image)

class PlayButton(TaskButton):

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
            self.press_anim.start(self)
            self.hover_image.start(self.task_image)

class PauseButton(TaskButton):

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
            self.press_anim.start(self)
            self.hover_image.start(self.task_image)

class StopButton(TaskButton):

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230 / 255, 1), duration=0.2)
            self.press_anim.start(self)
            self.hover_image.start(self.task_image)

class DefaultButton(Button, ButtonBehavior, HoverBehavior):

    def __init__(self, **kwargs):
        super(DefaultButton, self).__init__(**kwargs)
        self.image_anim = None
        self.press_anim = None
        self.disabled = True

    def on_press(self):
        self.press_anim = Animation(col=(0, 0, 179/255, 1), duration=0.2)
        self.press_anim.start(self)

    def on_release(self):
        self.press_anim = Animation(col=(51/255, 51/255, 1, 1), duration=0.2)
        self.press_anim.start(self)

    def on_enter(self):
        if not self.disabled:
            self.press_anim = Animation(col=(0, 0, 230/255, 1), duration=0.2)
            self.press_anim.start(self)

    def on_leave(self):
        if not self.disabled:
            self.press_anim = Animation(col=(51/255, 51/255, 1, 1), duration=0.2)
            self.press_anim.start(self)

    def enable(self):
        enable_animation = Animation(col=(51/255, 51/255, 1, 1), duration=0.2)
        enable_animation.start(self)

    def disable(self):
        # print("Disabled")
        disable_animation = Animation(col=(51/255, 26/255, 0, 1/2), duration=0.2)
        disable_animation.start(self)

class NetworkToggle(ToggleButton, ToggleButtonBehavior, HoverBehavior):

    network_image = ObjectProperty(None)
    click_image = Animation(size_hint=[0.8, 0.8], duration=0.2) + Animation(size_hint=[1, 1], duration=0.2)
    hover_image = Animation(size_hint=[1.1, 1.1], duration=0.2) + Animation(size_hint=[1, 1], duration=0.2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_anim = None
        self.press_image = None
        self.leave_anim = None
        self.hover_anim = None
        self.press_anim = None
        self.background_color = (0, 0, 0, 0)
        self.disabled = True

    def on_press(self):
        if self.state == "normal":
            self.state = "down"
        else:
            self.click_image.start(self.network_image)

    def on_state(self, widget, value):
        if value == "down":
            self.press_anim = Animation(col=(40/255, 40/255, 160/255, 1), duration=0.2)
            self.press_anim.start(self)
            self.press_image = Animation(color=(1, 1, 1, 1/2), duration=0.2)
            self.press_image.start(self.network_image)
        else:
            self.press_anim = Animation(col=(20/255, 100/255, 1, 1), duration=0.2)
            self.press_anim.start(self)
            self.press_image = Animation(color=(1, 1, 1, 1), duration=0.2)
            self.press_image.start(self.network_image)

    def on_enter(self):
        if not self.disabled:
            self.hover_anim = Animation(col=(40/255, 80/255, 180/255, 1), duration=0.2)
            self.hover_anim.start(self)
            self.hover_image.start(self.network_image)

    def on_leave(self):
        if not self.disabled:
            if self.state == "down":
                self.leave_anim = Animation(col=(40/255, 40/255, 160/255, 1), duration=0.2)
                self.leave_anim.start(self)
            else:
                self.leave_anim = Animation(col=(20/255, 100/255, 1, 1), duration=0.2)
                self.leave_anim.start(self)

    def enable(self):
        enable_animation = Animation(col=(51/255, 51/255, 1, 1), duration=0.2)
        enable_animation.start(self)
        self.image_anim = Animation(color=(1, 1, 1, 1), duration=0.2)  # Color for picture when button released
        self.image_anim.start(self.network_image)

    def disable(self):
        # print("Disabled")
        disable_animation = Animation(col=(51/255, 26/255, 0, 1/2), duration=0.2)
        disable_animation.start(self)
        self.image_anim = Animation(color=(1, 1, 1, 1 / 2), duration=0.2)  # Color for picture when button pressed
        self.image_anim.start(self.network_image)

class EthereumToggle(NetworkToggle):
    pass

class BinanceToggle(NetworkToggle):
    pass

class BinanceTestToggle(NetworkToggle):
    pass

class PolygonToggle(NetworkToggle):
    pass

class MumbaiToggle(NetworkToggle):
    pass

class GoerliToggle(NetworkToggle):
    pass

class StandardLabel(Label):
    pass

class EventLabel(StandardLabel):
    pass

class TimeLabel(Label):
    pass

class EventNameLabel(TimeLabel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding_x = 15

    # A function which dynamically adjusts Label's length based on the length of the text
    def on_text(self, instance, value):
        self.width = len(value) * self.font_size + self.padding_x

class EventTimeLabel(EventNameLabel):
    pass

class EventKeyLabel(EventNameLabel):
    pass

class EventValueLabel(EventNameLabel):
    pass

class ConnectivityLabel(Label):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.incorrect_animation = None
        self.valid_animation = None

    def http_valid(self):
        self.valid_animation = Animation(col=(0, 1, 0, 1), duration=0.3)
        self.valid_animation.start(self)

    def http_incorrect(self):
        self.incorrect_animation = Animation(col=(1, 0, 0, 1), duration=0.3)
        self.incorrect_animation.start(self)