import time
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import random


class ActionReload(Action):
    """This is an action for Reload related stories"""

    def name(self) -> Text:
        return "action_reload"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # for the sake of simplicity, I didn't validate these values
        phone = tracker.get_slot("phone_number")
        account = tracker.get_slot("account_number")
        amount = float(tracker.get_slot("amount"))

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

        # typically the phone number and account number are validated using backend systems
        # here I haven't added any of them
        if ActionReload.check_amount(amount) == 0:
            # if the amount exceeds allocated value, returns an error message
            dispatcher.utter_message(text="மீள் நிரப்பல் தொகையைவிட அதிகமான / குறைவான தொகையை இட்டுள்ளீர்கள்")
            dispatcher.utter_message(template="utter_reload_failure", phone_number=phone, amount=amount)
        else:
            if ActionReload.check_amount(amount) == 1:
                # warns user when amount is unusually large
                dispatcher.utter_message(text="கூடுதலாக ஒரு பூச்சியத்தை இட்டுள்ளீர்கள் போலுள்ளது!!!")
            if ActionReload.success_or_failure():
                # above condition randomises the output
                dispatcher.utter_message(template="utter_reload_success", phone_number=phone, amount=amount)
                SlotSet(key="time_after_last_reload", value=time.time())
            else:
                dispatcher.utter_message(template="utter_reload_failure", phone_number=phone, amount=amount)

        return []

    @staticmethod
    def success_or_failure() -> bool:
        """
        this is to emulate randomness in output
        because in real scenario, the success or failure depends on backend systems.
        I have used randomization to emulate that behaviour so all outputs can be displayed
        """
        return random.choice([True, False])

    @staticmethod
    def check_amount(amount: float) -> int:
        """
        returns 0 if the amount exceeds the limit.
        also if the amount is unusually large, it returns 1
        I have seen some bots do this in other situations... for example when food order is unusual for a person's taste
        I wanted to emulate that behaviour, but this just checks if the amount is a big multiple of 100s, or 200s or 500s
        because people mistakenly add extra zeroes
        """
        typical_amounts: list = [100, 200, 500]
        lower: int = 50
        upper: int = 10000
        if any([(amount / x > 10 and amount % x == 0) for x in typical_amounts]):
            return 1
        if amount < lower or amount > upper:
            return 0


class ActionCancelReload(Action):
    """an action which acts when user cancels reloads"""

    def name(self) -> Text:
        return "action_cancel_reload"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # haven't added any validation
        # see above comments for detailed explanation
        phone = tracker.get_slot("phone_number")
        amount = float(tracker.get_slot("amount"))
        last_reload_time = float(tracker.get_slot("time_after_last_reload"))

        if last_reload_time is None or last_reload_time == 0:
            dispatcher.utter_message(text="நீங்கள் கடைசியாக மீள்நிரப்பல் செய்தது போல தெரியவில்லை. ஆகவே இக் கோரிக்கை "
                                          "நிராகரிக்கப்படுகிறது")
        else:
            # if more than 30s past last reload time, the cancel request would be denied
            if time.time() - last_reload_time > 30:
                dispatcher.utter_message(text="மன்னிக்கவும். இக் கோரிக்கைக்கான காலவரையறை முடிந்துவிட்டது")

            else:
                dispatcher.utter_message(template="utter_cancel_success", phone_number=phone, amount=amount)
                SlotSet(key="time_after_last_reload", value=None)

        return []


class ActionRefund(Action):
    """an action which acts when user wants a refund"""

    def name(self) -> Text:
        return "action_refund"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # keep it simple
        account = tracker.get_slot("account_number")
        amount = float(tracker.get_slot("amount"))
        last_reload_time = int(tracker.get_slot("time_after_last_reload"))

        if last_reload_time is None or last_reload_time == 0:
            dispatcher.utter_message(text="நீங்கள் கடைசியாக மீள்நிரப்பல் செய்தது போல தெரியவில்லை. அல்லது அதனை "
                                          "பிற்பாடு தடுத்து விட்டீர்கள். ஆகவே இக் கோரிக்கை நிராகரிக்கப்படுகிறது")
        else:
            # if more than 30s and less than 60s past last reload time, the refund request would be accepted
            if 30 <= time.time() - last_reload_time <= 60:
                dispatcher.utter_message(text=f"மீள்நிரப்பிய தொகை மறுபடியும் கணக்கிற்கே அனுப்பிவைக்கப்பட்டுள்ளது. "
                                              f"தாெகை: {amount}, கணக்கிலக்கம்: {account}")
                SlotSet(key="time_after_last_reload", value=None)

            elif time.time() - last_reload_time < 30:
                dispatcher.utter_message(text="இக் கோரிக்கை தேவையற்றது. மீள்நிரப்பலை தடை செய்ய முடியும்.")
                return [FollowupAction("action_cancel_reload")]

        return []


class ActionCoverage(Action):
    """an action which acts when user asks for a coverage percentage for his area"""

    def name(self) -> Text:
        return "action_tell_coverage"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # usually it will ask for specific place and goes above in area if the coverage information is not available
        # i am keeping this simple by just asking district and province
        province = tracker.get_slot("province")
        district = tracker.get_slot("district")

        # see above comments for info about randomness
        if ActionCoverage.success_or_failure(district):
            dispatcher.utter_message(
                text=f"உங்கள் மாவட்டத்தில் {ActionCoverage.getRandomCoverage(district)}% கவரேஜ் உள்ளது")
        else:
            # if it cannot find coverage for a specific district, it finds for province
            dispatcher.utter_message(text=f"உங்கள் மாவட்டத்தில் கவரேஜ் காணமுடியவில்லை. சற்று நேரம் தாமதிக்கவும்.")
            time.sleep(2)
            dispatcher.utter_message(
                text=f"உங்கள் மாகாணத்தில் {ActionCoverage.getRandomCoverage(province)}% கவரேஜ் உள்ளது")

    @staticmethod
    def success_or_failure(value: str) -> bool:
        """this is to emulate randomness in output"""
        random.seed(value)
        return random.choice([True, False])

    @staticmethod
    def getRandomCoverage(value: str):
        """returns a random value between 50 and 99"""
        random.seed(value)
        return random.randint(50, 99)
