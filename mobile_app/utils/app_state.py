class AppState:
    pending_otp_email = ""
    active_meeting_id = None

    @classmethod
    def clear_auth_flow(cls):
        cls.pending_otp_email = ""

    @classmethod
    def clear_meeting_flow(cls):
        cls.active_meeting_id = None

    @classmethod
    def clear_all(cls):
        cls.pending_otp_email = ""
        cls.active_meeting_id = None