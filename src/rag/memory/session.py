import json
from dataclasses import asdict
from pathlib import Path

from src.rag.interface.data import Session


class SessionsIndex:
    def __init__(self, data_dir: str = "sessions"):

        self.filepath = Path(data_dir) / "sessions_index.json"
        # self.catalog: list[dict[str, str]] = []

    def register(self, session: Session):
        # try:
        sessions = self.show()


        existing_ids = [s.session_id for s in sessions]

        if session.session_id in existing_ids:
            print("Session already registered, skipping.")
            return

        sessions.append(session)
        with open(self.filepath, "w") as f:
            json.dump([asdict(s) for s in sessions], f)


    def show(self) -> list[Session]:
        try:
            if self.filepath.exists() is not True:
                self.filepath.touch(exist_ok=True)

            with open(self.filepath, "r") as f:
                raw = json.load(f)
                sessions = [Session(**entry) for entry in raw]
                return sessions
        except (FileNotFoundError, json.JSONDecodeError):
            return []
