from aiogram.fsm.state import StatesGroup, State

class RegistrationSG(StatesGroup):
    wait_channel = State()
    wait_name = State()
    wait_phone = State()
    wait_region = State()
    wait_study_status = State()
    wait_age_range = State()
    wait_survey = State()

class ActiveSG(StatesGroup):
    main = State()

class ProfileSG(StatesGroup):
    main = State()
    edit_name = State()
    edit_phone = State()
    edit_region = State()
    edit_study_status = State()
    edit_age_range = State()
    edit_phone_2 = State()

class AdminSG(StatesGroup):
    wait_broadcast = State()
    wait_webinar_year = State()
    wait_webinar_month = State()
    wait_webinar_day = State()
    wait_webinar_hour = State()
    wait_webinar_minute = State()
    wait_webinar_link = State()
    wait_channel_name = State()
    wait_channel_id = State()
    wait_channel_link = State()
    wait_restore = State()
    wait_send_message_id = State()
    wait_send_message_content = State()
    wait_suspicious_broadcast_content = State()
    wait_checkin_text = State()
    wait_checkin_channel = State()
    wait_webinar_restore = State()
