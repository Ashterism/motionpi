from .storage import Storage


class SettingsManager:
    def __init__(self, storage=None):
        self.storage = storage or Storage()
        self.settings_file = self.storage.meta_dir / "settings.json"

        self.default_settings = {
            "profile": "cat",
            "photo_burst_count": 3,
            "photo_burst_gap_secs": 0.5,
            "photo_cooldown_secs": 8,
            "session_timeout_secs": 300,
        }

        self.options = {
            "profiles": {
                "cat": "Cat",
                "wildlife": "Field / Wildlife",
            },
            "photo_burst_counts": {1: "1 photo", 3: "3 photos", 5: "5 photos"},
            "photo_burst_gaps": {
                0.2: "0.2 seconds",
                0.5: "0.5 seconds",
                1.0: "1 second",
            },
            "photo_cooldowns": {
                2: "2 seconds",
                5: "5 seconds",
                8: "8 seconds",
                15: "15 seconds",
                30: "30 seconds",
            },
            "session_timeouts": {
                60: "1 minute",
                300: "5 minutes",
                600: "10 minutes",
                1800: "30 minutes",
            },
        }

    def get_options(self):
        return self.options

    def get_settings(self):
        try:
            saved_settings = self.storage.read_json(self.settings_file)
        except (OSError, ValueError, TypeError):
            saved_settings = None

        if not isinstance(saved_settings, dict):
            return self.default_settings.copy()

        settings = self.default_settings.copy()
        settings.update(
            {
                key: value
                for key, value in saved_settings.items()
                if key in self.default_settings
            }
        )
        return self._validated_settings(settings)

    def update_settings(self, data):
        settings = self._validated_settings(
            {
                "profile": data.get("profile"),
                "photo_burst_count": data.get("photo_burst_count"),
                "photo_burst_gap_secs": data.get("photo_burst_gap_secs"),
                "photo_cooldown_secs": data.get("photo_cooldown_secs"),
                "session_timeout_secs": data.get("session_timeout_secs"),
            }
        )

        self.storage.write_json(self.settings_file, settings)
        return settings

    def _validated_settings(self, settings):
        return {
            "profile": self._allowed_value(
                settings.get("profile"),
                self.options["profiles"],
                self.default_settings["profile"],
            ),
            "photo_burst_count": self._allowed_number(
                settings.get("photo_burst_count"),
                self.options["photo_burst_counts"],
                self.default_settings["photo_burst_count"],
                int,
            ),
            "photo_burst_gap_secs": self._allowed_number(
                settings.get("photo_burst_gap_secs"),
                self.options["photo_burst_gaps"],
                self.default_settings["photo_burst_gap_secs"],
                float,
            ),
            "photo_cooldown_secs": self._allowed_number(
                settings.get("photo_cooldown_secs"),
                self.options["photo_cooldowns"],
                self.default_settings["photo_cooldown_secs"],
                int,
            ),
            "session_timeout_secs": self._allowed_number(
                settings.get("session_timeout_secs"),
                self.options["session_timeouts"],
                self.default_settings["session_timeout_secs"],
                int,
            ),
        }

    @staticmethod
    def _allowed_value(value, options, default):
        return value if value in options else default

    @staticmethod
    def _allowed_number(value, options, default, converter):
        try:
            converted = converter(value)
        except (TypeError, ValueError):
            return default

        return converted if converted in options else default
