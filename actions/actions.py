import time
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import random


class ActionReload(Action):

    def name(self) -> Text:
        return "action_reload"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # for the sake of simplicity, I didn't validate these values
        phone = tracker.get_slot("phone_number")
        account = tracker.get_slot("account_number")
        amount = tracker.get_slot("amount")

        # dispatcher.utter_message(text=f"{phone}, {account}, {amount}")
        # dispatcher.utter_message(text=f"{type(phone)}, {type(account)}, {type(account)}")

        if phone is None:
            dispatcher.utter_message(text="தொலைபேசி எண் தரப்படவில்லை. மீண்டும் முதலிருந்து ஆரம்பிக்கவும்")
            return []
        elif account is None:
            dispatcher.utter_message(text="கணக்கிலக்கம் தரப்படவில்லை. மீண்டும் முதலிருந்து ஆரம்பிக்கவும்")
            return []
        elif amount is None:
            dispatcher.utter_message(text="தொகை தரப்படவில்லை. மீண்டும் முதலிருந்து ஆரம்பிக்கவும்")
            return []

        if ActionReload.check_amount(int(amount)) == 0:
            dispatcher.utter_message(text="மீள் நிரப்பல் தொகையைவிட அதிகமான / குறைவான தொகையை இட்டுள்ளீர்கள்")
            dispatcher.utter_message(template="utter_reload_failure", phone_number=phone, amount=amount)
        else:
            if ActionReload.check_amount(int(amount)) == 1:
                dispatcher.utter_message(text="கூடுதலாக ஒரு பூச்சியத்தை இட்டுள்ளீர்கள் போலுள்ளது!!!")
            if ActionReload.success_or_failure():
                dispatcher.utter_message(template="utter_reload_success", phone_number=phone, amount=amount)
                SlotSet(key="time_after_last_reload", value=time.time())
            else:
                dispatcher.utter_message(template="utter_reload_failure", phone_number=phone, amount=amount)

        return []

    @staticmethod
    def success_or_failure() -> bool:
        """this is to emulate randomness in output"""
        return random.choice([True, False])

    @staticmethod
    def check_amount(amount: int) -> int:
        typical_amounts: list = [100, 200, 500]
        lower: int = 50
        upper: int = 10000
        if any([(amount / x > 10 and amount % x == 0) for x in typical_amounts]):
            return 1
        if amount < lower or amount > upper:
            return 0


class ActionCancelReload(Action):

    def name(self) -> Text:
        return "action_cancel_reload"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # keep it simple
        phone = tracker.get_slot("phone_number")
        amount = tracker.get_slot("amount")
        last_reload_time = int(tracker.get_slot("time_after_last_reload"))

        if last_reload_time is None or last_reload_time == 0:
            dispatcher.utter_message(text="நீங்கள் கடைசியாக மீள்நிரப்பல் செய்தது போல தெரியவில்லை. ஆகவே இக் கோரிக்கை "
                                          "நிராகரிக்கப்படுகிறது")
        else:
            if time.time() - last_reload_time > 30:
                dispatcher.utter_message(text="மன்னிக்கவும். இக் கோரிக்கைக்கான காலவரையறை முடிந்துவிட்டது")

            else:
                dispatcher.utter_message(template="utter_cancel_success", phone_number=phone, amount=amount)
                SlotSet(key="time_after_last_reload", value=None)

        return []


class ActionRefund(Action):

    def name(self) -> Text:
        return "action_refund"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # keep it simple
        account = tracker.get_slot("account_number")
        amount = tracker.get_slot("amount")
        last_reload_time = int(tracker.get_slot("time_after_last_reload"))

        if last_reload_time is None or last_reload_time == 0:
            dispatcher.utter_message(text="நீங்கள் கடைசியாக மீள்நிரப்பல் செய்தது போல தெரியவில்லை. அல்லது அதனை "
                                          "பிற்பாடு தடுத்து விட்டீர்கள். ஆகவே இக் கோரிக்கை நிராகரிக்கப்படுகிறது")
        else:
            if 30 <= time.time() - last_reload_time <= 60:
                dispatcher.utter_message(text=f"மீள்நிரப்பிய தொகை மறுபடியும் கணக்கிற்கே அனுப்பிவைக்கப்பட்டுள்ளது. "
                                              f"தாெகை: {amount}, கணக்கிலக்கம்: {account}")
                SlotSet(key="time_after_last_reload", value=None)

            elif time.time() - last_reload_time < 30:
                dispatcher.utter_message(text="இக் கோரிக்கை தேவையற்றது. மீள்நிரப்பலை தடை செய்ய முடியும்.")
                return [FollowupAction("action_cancel_reload")]

        return []

class ActionCoverage(Action):

    def name(self) -> Text:
        return "action_tell_coverage"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # keep it simple
        province = tracker.get_slot("province")
        district = tracker.get_slot("district")

        if ActionCoverage.success_or_failure(district):
            dispatcher.utter_message(text=f"உங்கள் மாவட்டத்தில் {ActionCoverage.getRandomCoverage(district)}% கவரேஜ் உள்ளது")
        else:
            dispatcher.utter_message(text=f"உங்கள் மாவட்டத்தில் கவரேஜ் காணமுடியவில்லை. சற்று நேரம் தாமதிக்கவும்.")
            time.sleep(2)
            dispatcher.utter_message(text=f"உங்கள் மாகாணத்தில் {ActionCoverage.getRandomCoverage(province)}% கவரேஜ் உள்ளது")

    @staticmethod
    def success_or_failure(value: str) -> bool:
        """this is to emulate randomness in output"""
        random.seed(value)
        return random.choice([True, False])

    @staticmethod
    def getRandomCoverage(value: str):
        random.seed(value)
        return random.randint(50, 99)
