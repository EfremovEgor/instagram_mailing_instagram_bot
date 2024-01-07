from dataclasses import dataclass, field


@dataclass
class AccountDetails:
    login: str
    password: str


@dataclass
class BotSettings:
    name: str
    interaction_interval: list[int]
    cookies_path: str = None


@dataclass
class DriverSettings:
    proxy_url: str = None


@dataclass
class Message:
    sender: str
    message: str


@dataclass
class MessageThread:
    username: str
    messages: list[Message] = field(default_factory=list)
