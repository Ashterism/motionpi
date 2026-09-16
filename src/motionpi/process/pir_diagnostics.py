import json
import os
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone


class PIRDiagnostics:
    """Process-shared PIR and capture diagnostics stored in the data directory."""

    MAX_EVENTS = 100

    def __init__(self, storage):
        self.storage = storage
        self.filepath = storage.meta_dir / "pir_diagnostics.json"
        self._lock = threading.RLock()

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    @staticmethod
    def _default_state():
        return {
            "gpio": 17,
            "pir_state": "UNKNOWN",
            "state_since": None,
            "last_high": None,
            "last_low": None,
            "capture_state": "idle",
            "last_capture_trigger": None,
            "events": [],
            "test": {
                "status": "idle",
                "started_at": None,
                "ends_at": None,
                "duration_seconds": 60,
                "summary": None,
            },
        }

    def _load(self):
        state = self.storage.read_json(self.filepath)
        if not isinstance(state, dict):
            return self._default_state()

        default = self._default_state()
        default.update(state)
        if not isinstance(default.get("events"), list):
            default["events"] = []
        if not isinstance(default.get("test"), dict):
            default["test"] = self._default_state()["test"]
        return default

    def _save(self, state):
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.filepath.with_name(
            f".{self.filepath.name}.{os.getpid()}.tmp"
        )
        with open(temporary, "w") as handle:
            json.dump(state, handle)
        os.replace(temporary, self.filepath)

    def _add_event(self, state, message, event_type):
        state["events"].append(
            {
                "time": self._timestamp(),
                "epoch": time.time(),
                "type": event_type,
                "message": message,
            }
        )
        state["events"] = state["events"][-self.MAX_EVENTS :]

    def record_reading(self, reading, source="sensor"):
        new_state = "HIGH" if bool(reading) else "LOW"
        now = time.time()

        with self._lock:
            state = self._load()
            previous = state.get("pir_state", "UNKNOWN")
            should_save = False

            if previous != new_state:
                should_save = True
                state["pir_state"] = new_state
                state["state_since"] = self._timestamp()
                state["last_high" if new_state == "HIGH" else "last_low"] = state[
                    "state_since"
                ]

                if previous in ("HIGH", "LOW"):
                    self._add_event(
                        state,
                        f"PIR {previous} → {new_state}",
                        "pir_transition",
                    )

                test = state.get("test", {})
                if test.get("status") == "running":
                    test["transition_count"] = test.get("transition_count", 0) + (
                        1 if previous in ("HIGH", "LOW") else 0
                    )
                    if new_state == "HIGH":
                        test["motion_events"] = test.get("motion_events", 0) + 1
                        last_low = test.get("_last_low_epoch")
                        if last_low is not None:
                            test.setdefault("_low_gaps", []).append(now - last_low)
                        test["_high_started_epoch"] = now
                    else:
                        high_started = test.get("_high_started_epoch")
                        if high_started is not None:
                            test.setdefault("_high_durations", []).append(
                                now - high_started
                            )
                            test["_high_started_epoch"] = None
                        test["_last_low_epoch"] = now

            test = state.get("test", {})
            if test.get("status") == "running" and source == "test":
                test["samples"] = test.get("samples", 0) + 1
                should_save = True

            if should_save:
                self._save(state)
            return deepcopy(state)

    def set_capture_state(self, capture_state, triggered=False):
        with self._lock:
            state = self._load()
            previous = state.get("capture_state")
            if previous == capture_state and not triggered:
                return

            state["capture_state"] = capture_state

            if triggered:
                state["last_capture_trigger"] = self._timestamp()
                self._add_event(state, "Capture triggered by PIR rising edge", "capture")
            elif previous != capture_state:
                labels = {
                    "idle": "Capture state: idle",
                    "capturing": "Capture state: capturing",
                    "cooldown": "Capture state: cooldown",
                }
                self._add_event(
                    state,
                    labels.get(capture_state, f"Capture state: {capture_state}"),
                    "capture_state",
                )

            self._save(state)

    def start_test(self, duration_seconds=60):
        now = time.time()
        with self._lock:
            state = self._load()
            state["test"] = {
                "status": "running",
                "started_at": self._timestamp(),
                "ends_at": datetime.fromtimestamp(
                    now + duration_seconds, timezone.utc
                ).isoformat(timespec="milliseconds"),
                "duration_seconds": duration_seconds,
                "summary": None,
                "samples": 0,
                "transition_count": 0,
                "motion_events": 0,
                "_high_started_epoch": now
                if state.get("pir_state") == "HIGH"
                else None,
                "_last_low_epoch": None,
                "_high_durations": [],
                "_low_gaps": [],
            }
            self._add_event(state, "60-second PIR test started", "test")
            state["capture_state"] = "idle"
            self._save(state)

    def complete_test(self):
        now = time.time()
        with self._lock:
            state = self._load()
            test = state.get("test", {})

            if test.get("status") != "running":
                return

            high_durations = list(test.get("_high_durations", []))
            high_started = test.get("_high_started_epoch")
            if high_started is not None:
                high_durations.append(now - high_started)

            low_gaps = test.get("_low_gaps", [])
            test["status"] = "complete"
            test["summary"] = {
                "motion_events": test.get("motion_events", 0),
                "transition_count": test.get("transition_count", 0),
                "high_durations_seconds": [round(value, 1) for value in high_durations],
                "shortest_gap_seconds": round(min(low_gaps), 1) if low_gaps else None,
                "sensor_state": state.get("pir_state", "UNKNOWN"),
                "samples": test.get("samples", 0),
            }

            for key in list(test):
                if key.startswith("_"):
                    test.pop(key)

            self._add_event(state, "60-second PIR test completed", "test")
            self._save(state)

    def fail_test(self, error):
        with self._lock:
            state = self._load()
            test = state.get("test", {})
            test["status"] = "error"
            test["error"] = str(error)
            for key in list(test):
                if key.startswith("_"):
                    test.pop(key)
            self._add_event(state, f"PIR test failed: {error}", "error")
            self._save(state)

    def snapshot(self):
        with self._lock:
            state = self._load()

        now = time.time()
        state["transitions_last_60_seconds"] = sum(
            1
            for event in state.get("events", [])
            if event.get("type") == "pir_transition"
            and now - event.get("epoch", 0) <= 60
        )

        test = state.get("test", {})
        if test.get("status") == "running":
            ends_at = datetime.fromisoformat(test["ends_at"]).timestamp()
            test["remaining_seconds"] = max(0, round(ends_at - now))
        else:
            test["remaining_seconds"] = 0

        for key in list(test):
            if key.startswith("_"):
                test.pop(key)

        state["events"] = list(reversed(state.get("events", [])))
        return state
