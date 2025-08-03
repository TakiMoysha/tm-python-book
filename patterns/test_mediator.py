import logging
import pytest
from abc import ABC

logging.basicConfig(level=logging.DEBUG)


class Mediator(ABC):
    """
    Behavioral design pattern.

    Making objects independent of each other and decoupling their communication.
    """

    def notify(self, sendre: object, event: str) -> None:
        logging.info(f"{sendre.__class__.__name__}:{event}")


class ActionMediator(Mediator):
    def notify(self, sendre: object, event: str) -> None:
        print(f"{sendre.__class__.__name__}:{event}")


class CommandMediator(Mediator):
    def notify(self, sendre: object, event: str) -> None:
        print(f"{sendre.__class__.__name__}:{event}")


class ComponentObject:
    def __init__(self, mediator: Mediator) -> None:
        self._mediator = mediator
        self._mediator.notify(self, f"created:{self.__class__.__name__}")


class DomainComponentFirst(ComponentObject):
    def __init__(self, mediator: Mediator) -> None:
        super().__init__(mediator)

    def action_accomplished(self) -> None:
        self._mediator.notify(self, f"{self.__class__.__name__}:action_accomplished")


class DomainComponentSecond(ComponentObject):
    def __init__(self, mediator: Mediator) -> None:
        super().__init__(mediator)

    def action_accomplished(self) -> None:
        self._mediator.notify(self, f"{self.__class__.__name__}:action_accomplished")


# ================================================================================ ENTRYPOINT


def test_mediator_action() -> None:
    mediator = ActionMediator()
    first = DomainComponentFirst(mediator)
    second = DomainComponentSecond(mediator)
    first.action_accomplished()
    second.action_accomplished()


def test_mediator_command() -> None:
    mediator = CommandMediator()
    first = DomainComponentFirst(mediator)
    second = DomainComponentSecond(mediator)
    first.action_accomplished()
    second.action_accomplished()
