import json
import sys
import threading
import time
import warnings
from datetime import datetime as d
import time as t
from websockets import connect
import requests
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
import asyncio
from threading import Thread
from event_reader_widgets import *
from web3 import Web3

Builder.load_file('event_reader.kv')
Window.size = (1200, 600)

w3 = ""

class MainLayout(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contract_address = None
        self.contract = ""
        self.task = None
        self.loop = None
        self.events = []
        self.block_filter = ""
        self.async_thread = ""
        self.async_thread_run = False
        self.run_time = True
        self.counter = 0
        self.w3 = ""
        self.run_update_time()
        self.run_check_network()
        self.ids[f"{ev_read_set.network_active}"].state = "down"

    # Time display function
    def update_time(self):
        while self.run_time is True:
            # timestamp to time format (delay time)
            present_time = d.now()
            present_time = present_time.strftime('%H:%M  %d/%m/%y')  # Present time formatting
            self.ids.time_label.text = present_time
            t.sleep(1/4)

    # Thread creation for time display
    def run_update_time(self):
        t1 = Thread(target=self.update_time)  # Set a thread for time label
        t1.start()

    # Checks if api from dApp provider is valid
    def check_network(self, http_link, toggle_id):
        web3 = Web3(Web3.HTTPProvider(f"{http_link}"))
        if web3.is_connected():
            if toggle_id == "mainnet":
                self.ids.goerli.disabled = False
                self.ids.goerli.enable()
            elif toggle_id == "goerli":
                self.ids.mainnet.disabled = False
                self.ids.mainnet.enable()
            self.ids[f"{toggle_id}"].disabled = False
            self.ids[f"{toggle_id}"].enable()
            print("Checked")
        else:
            self.ids[f"{toggle_id}"].disabled = True
            self.ids[f"{toggle_id}"].disable()
            print("Network unavailable")

    # Creates threads in order to check apis from different providers at the same time
    def run_check_network(self):
        infura_thread = threading.Thread(target=self.check_network, args=(ev_read_set.infura_link, "mainnet",))
        bsc_thread = threading.Thread(target=self.check_network, args=(ev_read_set.bsc_link, "bsc",))
        bsc_testnet_thread = threading.Thread(target=self.check_network, args=(ev_read_set.bsc_testnet_link, "bsc_testnet",))
        polygon_thread = threading.Thread(target=self.check_network, args=(ev_read_set.polygon_link, "polygon",))
        mumbai_thread = threading.Thread(target=self.check_network, args=(ev_read_set.mumbai_link, "mumbai",))

        infura_thread.start()
        bsc_thread.start()
        bsc_testnet_thread.start()
        polygon_thread.start()
        mumbai_thread.start()

        infura_thread.join()
        bsc_thread.join()
        bsc_testnet_thread.join()
        polygon_thread.join()
        mumbai_thread.join()

    # Displays designated text on a comment bar when hovered over various icons
    def update_tag(self, text):
        self.ids.comment_tag.text = text

    # Deletes whatever text is in text filed when clicked on it
    def click_in_text(self, focus):
        if focus:
            self.ids.contract_input.text = ""

    # Function that commences contract entering into the dApp
    def enter_contract(self, text_input):
        # Stops loading in case the address is invalid
        if not Web3.is_address(text_input):
            self.ids.contract_input.text = "Wrong input"
        else:
            # Stops listening to any events from contract added previously
            self.ids.address_enter_button.disable()
            if self.async_thread:
                self.event_listening(command="stop")
            self.ids.address_enter_button.disabled = True
            self.ids.stop_button.enable()
            self.ids.stop_button.disabled = False
            # Commences loading contract into the dApp
            self.load_contract(text_input)

    # Selects network based on the toggle button input
    @staticmethod
    def network_selection(network):
        global w3
        print(network)
        ev_read_set.network_active = network
        if network == "goerli" or network == "mainnet":
            ev_read_set.infura_link = f"https://{network}.infura.io/v3/{ev_read_set.infura_api}"
            ev_read_set.infura_websocket = f"wss://{network}.infura.io/ws/v3/{ev_read_set.infura_api}"
            w3 = Web3(Web3.HTTPProvider(ev_read_set.infura_link))
        elif network == "bsc":
            w3 = Web3(Web3.HTTPProvider(ev_read_set.bsc_link))
        elif network == "bsc_testnet":
            w3 = Web3(Web3.HTTPProvider(ev_read_set.bsc_testnet_link))
        elif network == "polygon":
            w3 = Web3(Web3.HTTPProvider(ev_read_set.polygon_link))
        elif network == "mumbai":
            w3 = Web3(Web3.HTTPProvider(ev_read_set.mumbai_link))

        Settings.update_json(ev_read_set)

    # Loads ABI of a designated contract first, from which it picks event names and displays them on labels
    def load_contract(self, address):
        global w3
        # network_scan_url = ""
        self.contract_address = Web3.to_checksum_address(address)
        ev_read_set.contract_address = self.contract_address
        try:
            # ABI extraction
            if ev_read_set.network_active == "mainnet":
                network_scan_url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.etherscan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.infura_link))
            elif ev_read_set.network_active == "goerli":
                network_scan_url = f'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.etherscan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.infura_link))
            elif ev_read_set.network_active == "bsc":
                network_scan_url = f'https://api.bscscan.com/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.bsc_scan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.bsc_link))
            elif ev_read_set.network_active == 'bsc_testnet':
                network_scan_url = f'https://api-testnet.bscscan.com/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.bsc_scan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.bsc_testnet_link))
            elif ev_read_set.network_active == 'polygon':
                network_scan_url = f'https://api.polygonscan.com/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.polygonscan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.polygon_link))
            else:
                network_scan_url = f'https://api-testnet.polygonscan.com/api?module=contract&action=getabi&address={self.contract_address}&apikey={ev_read_set.polygonscan_api}'
                w3 = Web3(Web3.HTTPProvider(ev_read_set.mumbai_link))

            # contract ABI extraction via Etherscan API
            network_scan_response = requests.get(network_scan_url)
            network_scan_content = network_scan_response.json()
            contract_abi = network_scan_content.get("result")
            contract_abi_dict = json.loads(contract_abi)
            # Event name extraction and label creation
            for i, j in enumerate(contract_abi_dict):
                if contract_abi_dict[i]['type'] == "event":
                    self.events.append(contract_abi_dict[i]['name'])
                    print(contract_abi_dict[i]['name'])
                    event_name_label = EventLabel(text=f"{contract_abi_dict[i]['name']}")
                    self.ids.event_name_widgets.add_widget(event_name_label)

            # contract setup
            self.contract = w3.eth.contract(address=self.contract_address, abi=contract_abi)
            self.block_filter = w3.eth.filter({'fromBlock': 'latest', 'address': self.contract_address})
            self.ids.play_button.enable()
            self.ids.play_button.disabled = False
            self.ids.pause_button.enable()
            self.ids.pause_button.disabled = False
            Settings.update_json(ev_read_set)
        # Exception handling in case either contract or network selections are not correct
        except json.decoder.JSONDecodeError as e:
            self.ids.comment_tag.text = "Error occurred!!"

    # Starting or stopping listening to events on the blockchain network
    def event_listening(self, command):
        if command == "play":
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            # get_event function shows deprecation warning, however in this instance, create_task function cannot be used,
            # otherwise it would result in getting a RuntimeError when attempting to stop listening to it
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                self.task = asyncio.ensure_future(self.get_event(ev_read_set.network_active))

            # Thread creation for the async function which will listen to events
            self.async_thread = Thread(target=self.loop.run_forever)
            self.async_thread.start()
            self.ids.play_button.disabled = True
            self.async_thread_run = True
            print(f"async_thread: {self.async_thread.is_alive()}")
        # Pausing a listening to events
        elif command == "pause" or command == "stop":
            try:
                self.async_thread_run = False
                self.task.cancel()
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.async_thread.join()
                print(f"async_thread: {self.async_thread.is_alive()}")
            except AttributeError:
                pass
        # When stop button is hit, both event memory and contract data and ABI are all erased in addition to event listening interruption
        if command == "stop":
            self.ids.contract_input.text = ""
            self.ids.event_name_widgets.clear_widgets()
            self.ids.event_display.clear_widgets()
            self.events = []
            self.ids.address_enter_button.enable()
            self.ids.address_enter_button.disabled = False
            self.ids.play_button.disable()
            self.ids.play_button.disabled = True
            self.ids.pause_button.disable()
            self.ids.pause_button.disabled = True
            self.ids.stop_button.disable()
            self.ids.stop_button.disabled = True
        elif command == "pause":
            self.ids.play_button.enable()
            self.ids.play_button.disabled = False

    # Function which manages displaying events on the screen
    def show_events(self, event_name, logged_events):
        logged_events = dict(logged_events)
        event_time = d.now()
        event_time = event_time.strftime('%H:%M:%S')
        for key, value in logged_events.items():
            try:
                # Clock library has to be used for widget creation because GUI and event listening are ran in different threads and
                # since show_event is run the event listening thread, it cannot perform any graphic operations on the App, which is why
                # it has to be transferred back to the GUI thread via launching the update_events method via Clock library
                Clock.schedule_once(lambda dt: self.update_events(event_name, event_time, key, value))
                time.sleep(0.04)
            except Exception as e:
                print(e)

    # A function which adds widgets into the screen with information emitted by the events
    def update_events(self, event_name, event_time, key, value):
        # Displays name of the event
        event_name_label = EventNameLabel(text=f"{event_name}")
        # Displays time when the event was logged in on the screen.
        # Note: It does not have to correspond with block.timestamp information emitted in the event itself.
        event_time_label = EventTimeLabel(text=f"{event_time}")
        # Key to a specific value in the event emitted
        event_key_label = EventTimeLabel(text=f"{key}")
        # The value itself
        event_value_label = EventValueLabel(text=f"{value}")

        # Widget creation
        self.ids.event_display.add_widget(event_name_label)
        self.ids.event_display.add_widget(event_time_label)
        self.ids.event_display.add_widget(event_key_label)
        self.ids.event_display.add_widget(event_value_label)

    def log_loop(self, event_filter):
        entries = event_filter.get_new_entries()
        # When message is successfully received and log_loop method is triggered, "event_filter.get_new_entries()" does not catch the message
        # successfully on first attempt and remains empty and skips the for loop. This is why there is the infinite loop bellow, which repeats
        # the "event_filter.get_new_entries()" until it catches the message so that it can proceed and decode the transaction receipt and
        # get the events
        while True:
            if len(entries) == 0:
                entries = event_filter.get_new_entries()
                print(f"Length is Zero!!")
                continue
            else:
                print("Passed")
                break
        for event in entries:
            for x, y in enumerate(self.events):
                # warning functions need to be set to ignore UserWarning, otherwise it will pop up in the program every time emitted event name mismatches
                # the event put into "message_event" variable from "events" list
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    try:
                        message_event = eval(f"self.contract.events.{self.events[x]}()")
                        receipt = w3.eth.wait_for_transaction_receipt(event['transactionHash'])
                        result = message_event.process_receipt(receipt)
                        # If the event name picked from events list matches the event name emitted. It will successfully store the information in "result"
                        # variable and print it out.
                        print(f"Result from event {self.events[x]}: {result[0]['args']}")
                        self.show_events(self.events[x], result[0]['args'])
                        break
                    except Exception as e:
                        # If the event name picked from events list mismatched the event name actually emitted, no content will be stored into the "result"
                        # variable and when attempting to print out the result above, it will get an IndexError exception.
                        print(e)
            print("")

    # An async function which listens to the events via websocket and is run independently of the rest of the program
    async def get_event(self, network):
        global w3
        network_websocket = ""
        if network == "mainnet" or network == "goerli":
            network_websocket = ev_read_set.infura_websocket
        elif network == "bsc":
            network_websocket = ev_read_set.bsc_websocket
        elif network == "bsc_testnet":
            network_websocket = ev_read_set.bsc_testnet_websocket
        elif network == "polygon":
            network_websocket = ev_read_set.polygon_websocket
        elif network == "mumbai":
            network_websocket = ev_read_set.mumbai_websocket
        print(network_websocket)
        async with connect(f"{network_websocket}") as ws:
            await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["logs", {"address": [f'{self.contract_address}']}]}))
            # Wait for the subscription completion.
            subscription_response = await ws.recv()
            print(f"Subscription response: {subscription_response}, address: {self.contract_address}")
            while self.async_thread_run:
                try:
                    # Wait for the message in websockets and print the contents.
                    # block_filter has to be reset every 300 seconds.
                    await asyncio.wait_for(ws.recv(), timeout=300)
                    self.log_loop(event_filter=self.block_filter)
                    print("Event logged")
                except asyncio.exceptions.TimeoutError:
                    self.block_filter = w3.eth.filter({'fromBlock': 'latest', 'address': self.contract_address})
                except asyncio.CancelledError as e:
                    print(e)
                    break
                except RuntimeError:
                    print("Passed")

    def exit_app(self):
        self.event_listening(command="stop")
        self.run_time = False  # Threaded loop kill
        sys.exit()  # Program termination

class SettingsPopup(Popup):

    def __init__(self, **kwargs):
        super(SettingsPopup, self).__init__(**kwargs)
        self.ids.infura_api.text = ev_read_set.infura_api
        self.ids.polygon_api.text = ev_read_set.polygon_link
        self.ids.mumbai_api.text = ev_read_set.mumbai_link
        self.ids.bsc_api.text = ev_read_set.bsc_link
        self.ids.bsc_testnet.text = ev_read_set.bsc_testnet_link
        self.ids.etherscan_api.text = ev_read_set.etherscan_api
        self.ids.bscscan_api.text = ev_read_set.bsc_scan_api
        self.ids.polygonscan_api.text = ev_read_set.polygonscan_api
        self.run_checks()

    def run_checks(self):
        infura_thread = threading.Thread(target=self.check_connectivity, args=(ev_read_set.infura_link, "infura_connectivity",))
        polygon_thread = threading.Thread(target=self.check_connectivity, args=(ev_read_set.polygon_link, "polygon_connectivity",))
        mumbai_thread = threading.Thread(target=self.check_connectivity, args=(ev_read_set.mumbai_link, "mumbai_connectivity",))
        bsc_thread = threading.Thread(target=self.check_connectivity, args=(ev_read_set.bsc_link, "bsc_connectivity",))
        bsc_testnet_thread = threading.Thread(target=self.check_connectivity, args=(ev_read_set.bsc_testnet_link, "bsc_testnet_connectivity",))

        infura_thread.start()
        polygon_thread.start()
        mumbai_thread.start()
        bsc_thread.start()
        bsc_testnet_thread.start()

        infura_thread.join()
        polygon_thread.join()
        mumbai_thread.join()
        bsc_thread.join()
        bsc_testnet_thread.join()

    def check_connectivity(self, link, network_id):
        web3 = Web3(Web3.HTTPProvider(f"{link}"))
        print(web3.is_connected())
        if web3.is_connected():
            self.ids[f"{network_id}"].http_valid()
        else:
            self.ids[f"{network_id}"].http_incorrect()

    def update_infura_api(self, focus, text):
        global w3
        if focus:
            self.ids.infura_api.text = ""
        else:
            ev_read_set.infura_api = text
            ev_read_set.infura_link = f"https://{ev_read_set.network_active}.infura.io/v3/{text}"
            ev_read_set.infura_websocket = f"wss://{ev_read_set.network_active}.infura.io/ws/v3/{text}"
            print(Web3(Web3.HTTPProvider(f"{ev_read_set.infura_link}")).is_connected())
            self.check_connectivity(link=ev_read_set.infura_link, network_id="infura_connectivity")

    def update_polygon_http(self, focus, text):
        global w3
        if focus:
            self.ids.polygon_api.text = ""
        else:
            ev_read_set.polygon_link = text
            ev_read_set.polygon_websocket = ev_read_set.polygon_link.replace("https", "wss")
            print(Web3(Web3.HTTPProvider(f"{ev_read_set.polygon_link}")).is_connected())
            self.check_connectivity(link=ev_read_set.polygon_link, network_id="polygon_connectivity")

    def update_mumbai_http(self, focus, text):
        global w3
        if focus:
            self.ids.mumbai_api.text = ""
        else:
            ev_read_set.mumbai_link = text
            ev_read_set.mumbai_websocket = ev_read_set.mumbai_link.replace("https", "wss")
            print(Web3(Web3.HTTPProvider(f"{ev_read_set.mumbai_link}")).is_connected())
            self.check_connectivity(link=ev_read_set.mumbai_link, network_id="mumbai_connectivity")

    def update_bsc_http(self, focus, text):
        global w3
        if focus:
            self.ids.bsc_api.text = ""
        else:
            ev_read_set.bsc_link = text
            ev_read_set.bsc_websocket = ev_read_set.bsc_link.replace("https", "wss")
            print(Web3(Web3.HTTPProvider(f"{ev_read_set.bsc_link}")).is_connected())
            self.check_connectivity(link=ev_read_set.bsc_link, network_id="bsc_connectivity")

    def update_bsc_testnet_http(self, focus, text):
        global w3
        print(focus, text)
        if focus:
            self.ids.bsc_testnet.text = ""
        else:
            ev_read_set.bsc_testnet_link = text
            ev_read_set.bsc_testnet_websocket = ev_read_set.bsc_testnet_link.replace("https", "wss")
            print(Web3(Web3.HTTPProvider(f"{ev_read_set.bsc_testnet_link}")).is_connected())
            self.check_connectivity(link=ev_read_set.bsc_testnet_link, network_id="bsc_testnet_connectivity")

    def update_scan_api(self, focus, text, input_id):
        if focus:
            self.ids[f"{input_id}"].text = ""
        else:
            if input_id == "etherscan_api":
                ev_read_set.etherscan_api = text
            elif input_id == "polygonscan_api":
                ev_read_set.polygonscan_api = text
            elif input_id == "bscscan_api":
                ev_read_set.bsc_scan_api = text

    @staticmethod
    def save_data():
        Settings.update_json(ev_read_set)

# Variables initialisation and JSON updating and loading
class Settings:

    def __init__(self, json_path):
        try:
            with open(json_path, "r") as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            raise ValueError("JSON not found")

        self.infura_api = data.get('infura_api')
        self.infura_link = data.get('infura_link')
        self.infura_websocket = data.get('infura_websocket')
        self.polygon_link = data.get('polygon_link')
        self.polygon_websocket = data.get('polygon_websocket')
        self.mumbai_link = data.get('mumbai_link')
        self.mumbai_websocket = data.get('mumbai_websocket')
        self.bsc_link = data.get('bsc_link')
        self.bsc_websocket = data.get('bsc_websocket')
        self.bsc_testnet_link = data.get('bsc_testnet_link')
        self.bsc_testnet_websocket = data.get('bsc_testnet_websocket')
        self.etherscan_api = data.get('etherscan_api')
        self.bsc_scan_api = data.get('bscscan_api')
        self.polygonscan_api = data.get('polygonscan_api')
        self.network_active = data.get('network_active')
        self.contract_address = data.get('contract_address')

    def update_json(self, json_path="EventReaderSettings.json"):
        data = {"infura_api": self.infura_api, "infura_link": self.infura_link, "infura_websocket": self.infura_websocket,
                "polygon_link": self.polygon_link, "polygon_websocket": self.polygon_websocket, "etherscan_api": self.etherscan_api,
                "network_active": self.network_active, "contract_address": self.contract_address, "bscscan_api": self.bsc_scan_api,
                "polygonscan_api": self.polygonscan_api, "mumbai_link": self.mumbai_link, "mumbai_websocket": self.mumbai_websocket,
                "bsc_link": self.bsc_link, "bsc_websocket": self.bsc_websocket, "bsc_testnet_link": self.bsc_testnet_link,
                "bsc_testnet_websocket": self.bsc_testnet_websocket}

        with open(json_path, "w") as f:
            data = json.dumps(data, indent=1)
            f.write(data)

ev_read_set = Settings("EventReaderSettings.json")

class EventReaderApp(App):

    def build(self):
        Window.clearcolor = (1/2 ,179/255 ,1 ,1)
        layout = MainLayout()
        layout.app = self
        return layout

if __name__ == '__main__':
    EventReaderApp().run()
