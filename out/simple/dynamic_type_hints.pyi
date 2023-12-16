from functools import cached_property as cached_property

class BaseSpell:
    spell_name: str
    spell_description: str
    def cast(self, *args, **kwargs) -> None: ...

class FireSchool:
    klass: str

class FireBall(BaseSpell, FireSchool):
    spell_name: str
    spell_description: str
    @cached_property
    def school_class(self): ...
    def cast(self, exitcode: int = ..., **kwrags) -> None: ...

class SpellBook:
    def __init__(self, spells: dict) -> None: ...
    def __getattr__(self, __name: str): ...
