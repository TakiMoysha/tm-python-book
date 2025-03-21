from functools import cached_property


class BaseSpell:
    spell_name: str
    spell_description: str

    def cast(self, *args, **kwargs):
        pass


class FireSchool:
    klass = "Fire"


class FireBall(BaseSpell, FireSchool):
    spell_name = "Meteor"
    spell_description = "Shoot a ball of fire"

    @cached_property
    def school_class(self):
        return f"School: {self.klass}"

    def cast(self, exitcode=0, **kwrags):
        exit(exitcode + 42)


class SpellBook:
    _spells: dict[str, BaseSpell]

    def __init__(self, spells: dict) -> None:
        self._spells = spells.copy()

    def __getattr__(self, __name: str):
        if __name in self._spells:
            return self._spells[__name].cast

        raise NotImplementedError(f"Spell {__name} not found")


if __name__ == "__main__":
    # SpellBook dynamically assigns names to attributes,
    # for solve this problem using stubgen from mypy
    spells = SpellBook({"meteor": FireBall()})
    spells.meteor()
