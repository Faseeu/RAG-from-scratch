import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

# def _read(filename):
#     """Reads memory from file. Returns [] if file doesn't exist yet."""
#     try:
#         with open(filename, "r") as f:
#             return json.load(f)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return []


# def conMemory(mode="store", memory=None, filename="conversation_memory.json"):
#     if mode == "store":
#         full_memory = _read(filename)  # step 1: get old memory
#         full_memory.append(memory)  # step 2: add new turn
#         with open(filename, "w") as f:
#             json.dump(full_memory, f)  # step 3: save it all back
#         # pprint("Memory has been saved!!")

#     elif mode == "load":
#         full_memory = _read(filename)
#         # pprint(full_memory[:-5])
#         return full_memory[-12:]
#         # return full_memory


# mem = conMemory("load")
# print(mem)
# print(len(mem))

# def sessions_index(
#     session_id=None,
#     session_name=None,
#     mode="show",
#     created_at=None,
#     filename="sessions/sessions_index.json",
# ):
#     if created_at is None:
#         created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
#     if mode == "show":
#         full_index = _read(filename)
#         return full_index
#     elif mode == "register":
#         session = {
#             "session_id": session_id,
#             "session_name": session_name,
#             "created_at": created_at,
#         }
#         full_index = _read(filename)  # step 1: get old memory
#         full_index.append(session)  # step 2: add new turn
#         with open(filename, "w") as f:
#             json.dump(full_index, f)


@dataclass
class MemTurn:
    question: str = ""
    answer: str = ""
    mem: dict = field(default_factory=dict)


# @dataclass
# class MemStructure:
#     memories: list[MemTurn] = field(default_factory=list)


@dataclass
class Session:
    session_id: str
    session_name: str
    created_at: str

    @classmethod
    def create_new(cls, session_id: str | None = None, session_name: str | None = None):
        if not session_name:
            session_name = input("Enter a SESSION NAME:- \n")
        now = datetime.now()

        session_id = (
            (f"{now.strftime('%Y%m%d_%H%M%S')}_{session_name}")
            if session_id is None
            else session_id
        )

        return cls(
            session_id=session_id,
            session_name=session_name,
            created_at=now.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        )


class ConversationMemory:
    def __init__(
        self,
        session: Session,
        # session_id=None,
        # session_name: str = "",
        # created_at=None,
        last_n: int = 12,
        data_dir: Path = "sessions",
        # filename="conversation_memory.json",
    ):
        self.session = session

        self.last_n = last_n

        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.filename = f"{self.session.session_id}.json"
        self.filepath = Path(os.path.join(self.data_dir, self.filename))
        # if self.filepath.exists() is not True:
        #     self.filepath.touch(exist_ok=True)
        self.history = self._load_once()

    def load(self, complete: bool = False):
        """Reads memory from history"""

        if complete is True:
            return self.history
        return self.history[-self.last_n :]

    def store(self, memory: MemTurn):

        full_memory = self.history
        full_memory.append(asdict(memory))  # step 2: add new turn
        with open(self.filepath, "w") as f:
            json.dump(full_memory, f)
            print("STORED SUCCESSFULLY")

    def _load_once(self, complete=True):
        """Reads memory from file. Returns [] if file doesn't exist yet."""
        try:
            with open(self.filepath, "r") as f:
                full_memory = json.load(f)
                if complete is True:
                    return full_memory
                return full_memory[-self.last_n :]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def __str__(self):
        s = self.session
        return f"{s.session_id}\n\n{s.session_name}\n\n{s.created_at}\n\n{self.filename}\n{self.filepath}"


class SessionsIndex:
    def __init__(self,data_dir:str = "sessions"):

        self.filepath = Path(data_dir)/"sessions_index.json"
        # self.catalog: list[dict[str, str]] = []

    def register(self, session: Session):
        # try:
        sessions = self.show()
        # if created_at is None:
        #     created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        # session = {
        #     "session_id": session_id,
        #     "session_name": session_name,
        #     "created_at": created_at,
        # }
        # session = Session(
        #     session_id=session_id,
        #     session_name=session_name,
        #     created_at=created_at,
        # )

        # existing_ids = [entry["session_id"] for entry in sessions]
        existing_ids = [s.session_id for s in sessions]

        if session.session_id in existing_ids:
            print("Session already registered, skipping.")
            return

        sessions.append(session)
        with open(self.filepath, "w") as f:
            json.dump([asdict(s) for s in sessions], f)

    # except ValueError as e:
    #     raise e("This session is already registered in the catalog")

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


def resume_or_create_session():
    time_fmt = "%Y-%m-%dT%H:%M:%S.%f"
    option = input(
        "Enter 'n' if you want to create a new session:\t\nEnter 'r' if you wna to resume an older one:\t"
    )
    if option == "n":
        # session_name = input("What do you want to name this conversation? :\n")
        session = Session.create_new()
        new_session = ConversationMemory(session)
        catalog = SessionsIndex()
        catalog.register(session)
        print(
            f"REGISTERING: id={session.session_id}, name={session.session_name}, created={session.created_at}"
        )
        # catalog.register(
        #     session_id=new_session.session_id,
        #     session_name=new_session.session_name,
        #     created_at=new_session.created_at.strftime(time_fmt),
        # )
        return new_session
    elif option == "r":
        catalog = SessionsIndex()
        sessions = catalog.show()
        for i, session in enumerate(sessions):
            name = session.session_name
            sid = session.session_id
            created_at = session.created_at
            print(f"""
        Session Number: {i}  -- Session Name: {name}
        Session ID:    {sid} -- Created at:  {created_at}
            """)
        session_num = int(input("Enter the Session Number you want to resume:\t"))
        chosen_session = sessions[session_num]
        # name = chosen_session.session_name
        # sid = chosen_session.session_id
        # created_at = datetime.strptime(chosen_session.created_at, time_fmt)

        return ConversationMemory(chosen_session)
    else:
        print("The only aavailble options are 'n' and 'r'")
        return resume_or_create_session()


# mem = ConversationMemory(session_name="yo")
# mem.store({"question": "test", "answer": "test"})
# print(mem)
# memSe = SessionsIndex()
# print(memSe.show())
