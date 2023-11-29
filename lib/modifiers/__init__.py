from .base import Modifier
from .bolt_only import BoltActionsOnlyModifier
from .enforce_name_validity import EnforceNameValidityModifier
from .modifier_notif import ModifierNotifModifier
from .no_medic import NoMedicModifier
from .no_panther import NoPantherModifier
from .one_arty import OneArtyModifier

from typing import Tuple, Type

__all__ = (
    'ALL_MODIFIERS',
    'get_modifier',
    'Modifier',
    'ModifierFlags',

    'BoltActionsOnlyModifier',
    'EnforceNameValidityModifier',
    'ModifierNotifModifier',
    'NoMedicModifier',
    'NoPantherModifier',
    'OneArtyModifier',
)

ALL_MODIFIERS: Tuple[Type[Modifier], ...] = (
    BoltActionsOnlyModifier,
    EnforceNameValidityModifier,
    ModifierNotifModifier,
    NoMedicModifier,
    NoPantherModifier,
    OneArtyModifier,
)

INTERNAL_MODIFIERS: Tuple[Type[Modifier], ...] = tuple(
    modifier for modifier in ALL_MODIFIERS
    if modifier.config.hidden
)


from lib.info.types import Flags
from discord.flags import flag_value, fill_with_flags

@fill_with_flags()
class ModifierFlags(Flags):

    @flag_value
    def no_panther(self):
        return 1 << 0

    @flag_value
    def one_arty(self):
        return 1 << 1

    # @flag_value
    # def no_medic(self):
    #     return 1 << 2

    @flag_value
    def bolt_only(self):
        return 1 << 10

    def get_modifier_types(self):
        for modifier_id, enabled in self:
            if enabled:
                yield next((m for m in ALL_MODIFIERS if m.config.id == modifier_id), None)
