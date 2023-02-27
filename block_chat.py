import json
import sys
import warnings
from datetime import datetime
import os
print(os.getcwd())

from kivy.uix.tabbedpanel import TabbedPanel
from websockets import connect
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
import asyncio
from threading import Thread
from web3 import Web3
from block_chat_widgets import *

Builder.load_file('block_chat.kv')
Window.size = (550, 600)

w3 = ""

class MainLayout(TabbedPanel):

    def __init__(self, **kwargs):
        global w3
        super().__init__(**kwargs)
        self.task = None
        self.async_thread_run = False
        self.async_thread = ""
        self.loop = None
        self.contract_abi = ""
        self.contract = ""
        self.block_filter = ""
        self.streamer_name_valid = False
        self.chain_id = ""
        self.message_counter = 0
        self.donation_counter = 0
        self.load_network()
        wallet_balance = w3.eth.get_balance(bl_chat_set.wallet_address)
        wallet_balance = wallet_balance / 10 ** 18
        self.ids[f'{bl_chat_set.network_active}'].state = 'down'
        self.ids.wallet_address.text = bl_chat_set.wallet_address
        self.ids.private_key.text = bl_chat_set.private_key
        self.ids.contract.text = bl_chat_set.contract_address
        self.ids.polygon_link.text = bl_chat_set.polygon_link
        self.ids.mumbai_link.text = bl_chat_set.mumbai_link
        # Wallet balance
        self.ids.wallet_balance.text = f"Wallet Balance\n\n{wallet_balance: .4f} MATIC"

    def load_network(self):
        global w3
        if bl_chat_set.network_active == 'polygon':
            w3 = Web3(Web3.HTTPProvider(bl_chat_set.polygon_link))
        elif bl_chat_set.network_active == 'mumbai':
            w3 = Web3(Web3.HTTPProvider(bl_chat_set.mumbai_link))
            network_scan_url = f'https://api-testnet.polygonscan.com/api?module=contract&action=getabi&address=0xE21609Fe47957c7d02D89E96241bAB55EE1c6300&apikey='
            network_scan_response = requests.get(network_scan_url)
            network_scan_content = network_scan_response.json()
            self.contract_abi = network_scan_content.get("result")
            self.contract = w3.eth.contract(address="0xE21609Fe47957c7d02D89E96241bAB55EE1c6300", abi=self.contract_abi)
            self.block_filter = w3.eth.filter({'fromBlock': 'latest', 'address': '0xE21609Fe47957c7d02D89E96241bAB55EE1c6300'})
            self.chain_id = 80001

    def update_data(self, focus, input_id, text):
        if not focus:
            print(focus, input_id, text)
            if input_id == 'polygon_link':
                web3 = Web3(Web3.HTTPProvider(text))
                if web3.is_connected():
                    bl_chat_set.polygon_link = text
                    bl_chat_set.polygon_websocket = bl_chat_set.polygon_link.replace('https', 'wss')
            elif input_id == 'mumbai_link':
                web3 = Web3(Web3.HTTPProvider(text))
                if web3.is_connected():
                    bl_chat_set.mumbai_link = text
                    bl_chat_set.mumbai_websocket = bl_chat_set.mumbai_link.replace('https', 'wss')
            elif input_id == 'wallet_address' or input_id == 'contract':
                if not Web3.is_address(text):
                    self.ids[f'{input_id}'].text = 'Wrong Input'
                    return
                else:
                    bl_chat_set.wallet_address = self.ids.wallet_address.text
                    bl_chat_set.contract_address = self.ids.contract.text
            else:
                bl_chat_set.private_key = text

            Settings.update_json(bl_chat_set)

    def change_network(self, input):
        global w3
        bl_chat_set.network_active = input
        if input == 'polygon':
            w3 = Web3(Web3.HTTPProvider(bl_chat_set.polygon_link))
        elif input == 'mumbai':
            w3 = Web3(Web3.HTTPProvider(bl_chat_set.mumbai_link))
        wallet_balance = w3.eth.get_balance(bl_chat_set.wallet_address)
        wallet_balance = wallet_balance / 10 ** 18
        # Wallet balance
        self.ids.wallet_balance.text = f"Wallet Balance\n\n{wallet_balance: .4f} MATIC"
        Settings.update_json(bl_chat_set)

    def on_text_input(self, value):
        if value != "" and self.streamer_name_valid:
            self.ids.send_button.disabled = False
        else:
            self.ids.send_button.disabled = True

    def streamer_log(self, focus, text):
        if not focus:
            streamer_name = self.contract.functions.streamers(text).call()
            if streamer_name != "0x0000000000000000000000000000000000000000":
                self.streamer_name_valid = True
            else:
                self.streamer_name_valid = False
                self.ids.streamer_name.text = "Streamer not found!!"

    def send_message(self, text, viewer, streamer, amount):
        global w3
        if amount == "" and amount is not float:
            self.ids.amount.text = "Error"
            return

        matic_price = self.contract.functions.usdMaticConverter(1).call()
        amount_sent = int(matic_price * float(amount))
        print(f"Amount sent: {amount_sent} Wei, To streamer: {streamer}, From viewer: {viewer}, Superchat: {text}")
        nonce = w3.eth.get_transaction_count(bl_chat_set.wallet_address)

        store_transaction = self.contract.functions.sendSuperChat(streamer, viewer, text).build_transaction(
            {"chainId": self.chain_id, "gasPrice": w3.eth.gas_price, "from": bl_chat_set.wallet_address, "nonce": nonce, 'value': amount_sent})
        signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=bl_chat_set.private_key)
        send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
        w3.eth.wait_for_transaction_receipt(send_store_tx)
        print("Transaction successful")

        self.scroll_widgets_update(text, streamer)
        self.ids.donor_message.text = ""
        self.ids.amount.text = ""

    def scroll_widgets_update(self, text, streamer):

        message_separation = MessageSeparation()
        self.ids.viewer_widgets.add_widget(message_separation)

        now = datetime.now()
        streamer_label = StreamerLabel(text=f"Streamer: {streamer}\nTime: {now.strftime('%H:%M')}\nAmount: {self.ids.amount.text} USD")
        self.ids.viewer_widgets.add_widget(streamer_label)

        sender_text_label = SenderTextLabel(text=text)
        self.ids.viewer_widgets.add_widget(sender_text_label)

        if self.message_counter >= 2:
            self.ids.viewer_scrollview.scroll_y = 0

        self.message_counter += 1

############################################-Streamer Functions-###########################################

    def enable_listening(self, text):
        if text != "":
            self.ids.start_stop.disabled = False
            self.ids.subscribe.disabled = False
            self.ids.unsubscribe.disabled = False
        else:
            self.ids.start_stop.disabled = True
            self.ids.subscribe.disabled = True
            self.ids.unsubscribe.disabled = True

    def event_listening(self, nickname):
        streamer_name = self.contract.functions.streamers(nickname).call()
        if streamer_name == "0x0000000000000000000000000000000000000000":
            self.ids.streamer_nick.text = "Enter valid name here"
            return
        if self.ids.start_stop.text == "Start listening":
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                self.task = asyncio.ensure_future(self.get_event(bl_chat_set.network_active))

            # Thread creation for the async function which will listen to events
            self.async_thread = Thread(target=self.loop.run_forever)
            self.async_thread.start()
            self.async_thread_run = True
            print(f"async_thread: {self.async_thread.is_alive()}")
            self.ids.start_stop.text = "Stop listening"
        # Pausing a listening to events
        elif self.ids.start_stop.text == "Stop listening":
            try:
                self.async_thread_run = False
                self.task.cancel()
                self.loop.call_soon_threadsafe(self.loop.stop)
                self.async_thread.join()
                print(f"async_thread: {self.async_thread.is_alive()}")
                self.ids.start_stop.text = "Start listening"
            except AttributeError:
                pass

    def subscribe_streamer(self, nickname, command):
        global w3

        if command == "subscribe":
            streamer_name = self.contract.functions.streamers(nickname).call()
            if streamer_name != "0x0000000000000000000000000000000000000000":
                self.ids.streamer_nick.text = "Name already in use"
                return
            nonce = w3.eth.get_transaction_count(bl_chat_set.wallet_address)
            store_transaction = self.contract.functions.subscribeStreamer(nickname).build_transaction(
                {"chainId": self.chain_id, "gasPrice": w3.eth.gas_price, "from": bl_chat_set.wallet_address, "nonce": nonce})
            signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=bl_chat_set.private_key)
            send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(send_store_tx)
            print("Transaction successful")

        elif command == "unsubscribe":
            streamer_name = self.contract.functions.streamers(nickname).call()
            if streamer_name != bl_chat_set.wallet_address:
                self.ids.streamer_nick.text = "Not your address"
                return
            nonce = w3.eth.get_transaction_count(bl_chat_set.wallet_address)
            store_transaction = self.contract.functions.unsubscribeStreamer(nickname).build_transaction(
                {"chainId": self.chain_id, "gasPrice": w3.eth.gas_price, "from": bl_chat_set.wallet_address, "nonce": nonce})
            signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=bl_chat_set.private_key)
            send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
            w3.eth.wait_for_transaction_receipt(send_store_tx)
            self.ids.streamer_nick.text = ""
            print("Transaction successful")

    def show_message(self, event):
        Clock.schedule_once(lambda dt: self.update_message(event))

    def update_message(self, event):
        nickname = self.ids.streamer_nick.text
        streamer_name = self.contract.functions.streamers(nickname).call()
        if streamer_name == event['recipient']:
            event_time = int(event['time'])
            event_time = datetime.fromtimestamp(event_time)

            sender_info = SenderInfoLabel(text=f"Donor: {event['donor']}\nTime: {event_time}\nAmount: {event['amount']}")
            self.ids.streamer_widgets.add_widget(sender_info)

            sender_text = SenderTextLabel(text=f"{event['superchat']}")
            self.ids.streamer_widgets.add_widget(sender_text)

            message_separation = MessageSeparation()
            self.ids.streamer_widgets.add_widget(message_separation)

            if self.donation_counter >= 2:
                self.ids.streamer_scrollview.scroll_y = 0

            self.donation_counter += 1

    def log_loop(self, event_filter):
        global w3

        entries = event_filter.get_new_entries()
        while True:
            if len(entries) == 0:
                entries = event_filter.get_new_entries()
                print(f"Length is Zero!!")
                continue
            else:
                print("Passed")
                break
        for event in entries:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    message_event = self.contract.events.Message()
                    receipt = w3.eth.wait_for_transaction_receipt(event['transactionHash'])
                    result = message_event.process_receipt(receipt)
                    print(f"{result[0]['args']}")
                    self.show_message(result[0]['args'])
                    break
                except Exception as e:
                    print(e)
            print("")

    def exit_app(self):
        if self.async_thread_run:
            self.async_thread_run = False
            self.task.cancel()
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.async_thread.join()
        sys.exit()

    async def get_event(self, network):
        global w3
        network_websocket = ""
        if network == "polygon":
            network_websocket = bl_chat_set.polygon_websocket
        elif network == "mumbai":
            network_websocket = bl_chat_set.mumbai_websocket
        print(network_websocket)
        async with connect(f"{network_websocket}") as ws:
            await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["logs", {"address": ['0xE21609Fe47957c7d02D89E96241bAB55EE1c6300']}]}))
            subscription_response = await ws.recv()
            print(f"Subscription response: {subscription_response}")
            while self.async_thread_run:
                try:
                    await asyncio.wait_for(ws.recv(), timeout=300)
                    self.log_loop(event_filter=self.block_filter)
                    print("Event logged")
                except asyncio.exceptions.TimeoutError:
                    self.block_filter = w3.eth.filter({'fromBlock': 'latest', 'address': '0xE21609Fe47957c7d02D89E96241bAB55EE1c6300'})
                except asyncio.CancelledError as e:
                    print(e)
                    break
                except RuntimeError:
                    print("Passed")

# Variables initialisation and JSON updating and loading
class Settings:

    def __init__(self, json_path):
        try:
            with open(json_path, "r") as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            raise ValueError("JSON not found")

        self.polygon_link = data.get('polygon_link')
        self.polygon_websocket = data.get('polygon_websocket')
        self.mumbai_link = data.get('mumbai_link')
        self.mumbai_websocket = data.get('mumbai_websocket')
        self.network_active = data.get('network_active')
        self.contract_address = data.get('contract_address')
        self.wallet_address = data.get('wallet_address')
        self.private_key = data.get('private_key')

    def update_json(self, json_path="BlockChatSettings.json"):
        data = {"polygon_link": self.polygon_link, "polygon_websocket": self.polygon_websocket,
                "network_active": self.network_active, "contract_address": self.contract_address,
                "mumbai_link": self.mumbai_link, "mumbai_websocket": self.mumbai_websocket,
                "wallet_address": self.wallet_address, "private_key": self.private_key}

        with open(json_path, "w") as f:
            data = json.dumps(data, indent=1)
            f.write(data)

bl_chat_set = Settings("BlockChatSettings.json")

class BlockChatApp(App):

    def build(self):
        Window.clearcolor = (51 / 255, 204 / 255, 1, 1)
        layout = MainLayout()
        layout.app = self
        return layout


if __name__ == '__main__':
    BlockChatApp().run()
