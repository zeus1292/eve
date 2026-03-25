from abc import ABC, abstractmethod
from models.session import SessionState


class AbstractSessionStore(ABC):
    @abstractmethod
    async def create(self, session: SessionState) -> SessionState:
        ...

    @abstractmethod
    async def get(self, session_id: str) -> SessionState | None:
        ...

    @abstractmethod
    async def update(self, session: SessionState) -> SessionState:
        ...


class InMemorySessionStore(AbstractSessionStore):
    def __init__(self) -> None:
        self._store: dict[str, SessionState] = {}

    async def create(self, session: SessionState) -> SessionState:
        self._store[session.session_id] = session
        return session

    async def get(self, session_id: str) -> SessionState | None:
        return self._store.get(session_id)

    async def update(self, session: SessionState) -> SessionState:
        self._store[session.session_id] = session
        return session


# Singleton — swap this for a RedisSessionStore later
session_store = InMemorySessionStore()
