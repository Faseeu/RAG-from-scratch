import json
import os
from datetime import datetime
from pathlib import Path


def _read(filename):
    """Reads memory from file. Returns [] if file doesn't exist yet."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def conMemory(mode="store", memory=None, filename="conversation_memory.json"):
    if mode == "store":
        full_memory = _read(filename)  # step 1: get old memory
        full_memory.append(memory)  # step 2: add new turn
        with open(filename, "w") as f:
            json.dump(full_memory, f)  # step 3: save it all back
        # pprint("Memory has been saved!!")

    elif mode == "load":
        full_memory = _read(filename)
        # pprint(full_memory[:-5])
        return full_memory[-12:]
        # return full_memory


# mem = conMemory("load")
# print(mem)
# print(len(mem))


class ConversationMemory:
    def __init__(
        self,
        session_id=None,
        session_name: str = "",
        created_at=None,
        last_N=12,
        data_dir="sessions",
        # filename="conversation_memory.json",
    ):

        # self.session_name = session_name if session_name else input("Enter a SESSION NAME:- \n")
        self.session_name = (
            input("Enter a SESSION NAME:- \n") if session_name == "" else session_name
        )

        if created_at is None:
            self.created_at = datetime.now()
        else:
            self.created_at = created_at
        self.session_id = (
            (f"{self.created_at.strftime('%Y%m%d_%H%M%S')}{self.session_name}")
            if session_id is None
            else session_id
        )
        self.last_N = last_N

        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.filename = f"{self.session_id}.json"
        self.filepath = Path(os.path.join(self.data_dir, self.filename))
        # if self.filepath.exists() is not True:
        #     self.filepath.touch(exist_ok=True)
        self.history = self._load_once()
        catalog = SessionsIndex()
        catalog.register(
            session_id=self.session_id,
            session_name=self.session_name,
            created_at=self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    def load(self, complete: bool = False):
        """Reads memory from history"""

        full_memory = self.history
        if complete is True:
            return full_memory
        return full_memory[-self.last_N :]

    def store(self, memory):

        full_memory = self.history
        full_memory.append(memory)  # step 2: add new turn
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
                return full_memory[-self.last_N :]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def __str__(self):
        return f"{self.session_id}\n\n{self.session_name}\n\n{self.created_at}\n\n{self.filename}\n{self.filepath}"


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


class SessionsIndex:
    def __init__(self):

        self.filepath = Path("sessions/sessions_index.json")
        self.catalog: list[dict[str, str]] = []

    def register(self, session_id, session_name, created_at=None):
        # try:
        full_catalog = self.show()
        # if created_at is None:
        #     created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        session = {
            "session_id": session_id,
            "session_name": session_name,
            "created_at": created_at,
        }

        if session not in full_catalog:
            full_catalog.append(session)
            with open(self.filepath, "w") as f:
                json.dump(full_catalog, f)

    # except ValueError as e:
    #     raise e("This session is already registered in the catalog")

    def show(self):
        try:
            if self.filepath.exists() is not True:
                self.filepath.touch(exist_ok=True)

            with open(self.filepath, "r") as f:
                full_catalog = json.load(f)
                return full_catalog
        except (FileNotFoundError, json.JSONDecodeError):
            return []


def resume_or_create_session():
    option = input(
        "Enter 'n' if you want to create a new session\nEnter 'r' if you wna to resume an older one"
    )
    if option == "n":
        session_name = input("What do you want to name this conversation? :\n")
        return ConversationMemory(session_name=session_name)
    elif option == "r":
        catalog = SessionsIndex()
        sessions = catalog.show()
        for i, session in enumerate(sessions):
            name = session["session_name"]
            sid = session["session_id"]
            created_at = session["created_at"]
            print(f"""
        Session Number: {i}  -- Session Name: {name}
        Session ID:    {sid} -- Created at:  {created_at}
            """)
        session_num = int(input("Enter the Session Number you want to resume"))
        chosen_session = sessions[session_num]
        name = chosen_session["session_name"]
        sid = chosen_session["session_id"]
        created_at = datetime.strptime(
            chosen_session["created_at"], "%Y-%m-%dT%H:%M:%S"
        )

        return ConversationMemory(
            session_id=sid, session_name=name, created_at=created_at
        )
    else:
        print("The only aavailble options are 'n' and 'r'")
        return resume_or_create_session()


# mem = ConversationMemory(session_name="yo")
# mem.store({"question": "test", "answer": "test"})
# print(mem)
# memSe = SessionsIndex()
# print(memSe.show())
