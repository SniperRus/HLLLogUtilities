from datetime import timedelta
from enum import Enum, unique
from inspect import isclass

from lib.info_models import *

class Player(InfoModel):
    __key_fields__ = ("steamid", "id", "name",)
    __scope_path__ = "players"
    steamid: str = UnsetField
    name: str = UnsetField
    id: Union[int, str] = UnsetField
    team: Union["Team", Link, None] = UnsetField
    squad: Union["Squad", Link, None] = UnsetField
    role: Union[str, None] = UnsetField
    loadout: Union[str, None] = UnsetField
    level: int = UnsetField
    kills: int = UnsetField
    deaths: int = UnsetField
    alive: bool = UnsetField
    is_vip: bool = UnsetField
    joined_at: datetime = UnsetField
    is_spectator: bool = UnsetField
    score: 'HLLPlayerScore' = UnsetField

    def is_squad_leader(self):
        squad = self.get('squad')
        if squad:
            leader = squad.get('leader')
            if leader:
                if self == leader:
                    return True
                else:
                    return False
        return None

class HLLPlayerScore(InfoModel):
    __scope_path__ = "players.score"
    combat: int = UnsetField
    offense: int = UnsetField
    defense: int = UnsetField
    support: int = UnsetField

class Squad(InfoModel):
    __key_fields__ = ("id", "name", "team")
    __scope_path__ = "squads"
    id: Union[int, str] = UnsetField
    leader: Union["Player", Link, None] = UnsetField
    creator: Union["Player", Link, None] = UnsetField
    name: str = UnsetField
    type: str = UnsetField
    team: Union["Team", Link, None] = UnsetField
    players: Union[Sequence["Player"], Link] = UnsetField
    created_at: datetime = UnsetField

class Team(InfoModel):
    __key_fields__ = ("id", "name",)
    __scope_path__ = "teams"
    id: Union[int, str] = UnsetField
    leader: Union["Player", Link, None] = UnsetField
    name: str = UnsetField
    squads: Union[Sequence["Squad"], Link] = UnsetField
    players: Union[Sequence["Player"], Link] = UnsetField
    created_at: datetime = UnsetField

    def get_unassigned_players(self) -> Sequence["Player"]:
        return [player for player in self.players if player.has('squad') and not player.squad]

class Server(InfoModel):
    __key_fields__ = ("name",)
    __scope_path__ = "server"
    name: str = UnsetField
    map: str = UnsetField
    gamemode: str = UnsetField
    next_map: str = UnsetField
    next_gamemode: str = UnsetField
    round_start: datetime = UnsetField
    state: str = UnsetField
    settings: 'ServerSettings' = UnsetField

class ServerSettings(InfoModel):
    __scope_path__ = "server.settings"
    rotation: List = UnsetField
    max_players: int = UnsetField
    max_queue_length: int = UnsetField
    max_vip_slots: int = UnsetField
    idle_kick_time: timedelta = UnsetField
    max_allowed_ping: int = UnsetField
    team_switch_cooldown: timedelta = UnsetField
    auto_balance: Union[int, bool] = UnsetField
    vote_kick_enabled: bool = UnsetField
    chat_filter: set = UnsetField

#####################################
#              EVENTS               #
#####################################

class EventModel(InfoModel):
    __key_fields__ = ()
    event_time: datetime = None
    
    @pydantic.validator('event_time', pre=True, always=True)
    def set_ts_now(cls, v):
        return v or datetime.utcnow()

class PlayerJoinServerEvent(EventModel):
    __scope_path__ = 'events.player_join_server'
    player: Union[Player, Link] = UnsetField

class ServerMapChangedEvent(EventModel):
    __scope_path__ = 'events.server_map_changed'
    old: str = UnsetField
    new: str = UnsetField

class ServerStateChangedEvent(EventModel):
    __scope_path__ = 'events.server_state_changed'
    old: str = UnsetField
    new: str = UnsetField
    score: str = UnsetField

class TeamCreatedEvent(EventModel):
    __scope_path__ = 'events.team_created'
    team: Union[Team, Link] = UnsetField

class SquadCreatedEvent(EventModel):
    __scope_path__ = 'events.squad_created'
    squad: Union[Squad, Link] = UnsetField

class PlayerJoinTeamEvent(EventModel):
    __scope_path__ = 'events.player_join_team'
    player: Union[Player, Link] = UnsetField
    team: Union[Team, Link] = UnsetField

class PlayerJoinSquadEvent(EventModel):
    __scope_path__ = 'events.player_join_squad'
    player: Union[Player, Link] = UnsetField
    squad: Union[Squad, Link] = UnsetField

class SquadLeaderChangeEvent(EventModel):
    __scope_path__ = 'events.squad_leader_change'
    squad: Union[Squad, Link] = UnsetField
    old: Union[Player, Link, None] = UnsetField
    new: Union[Player, Link, None] = UnsetField

class PlayerSpawnEvent(EventModel):
    __scope_path__ = 'events.player_spawn'
    player: Union[Player, Link] = UnsetField

class PlayerRevivedEvent(EventModel):
    __scope_path__ = 'events.player_revived'
    player: Union[Player, Link] = UnsetField
    other: Union[Player, Link, None] = UnsetField

class PlayerChangeRoleEvent(EventModel):
    __scope_path__ = 'events.player_change_role'
    player: Union[Player, Link] = UnsetField
    old: Union[str, None] = UnsetField
    new: Union[str, None] = UnsetField

class PlayerChangeLoadoutEvent(EventModel):
    __scope_path__ = 'events.player_change_loadout'
    player: Union[Player, Link] = UnsetField
    old: Union[str, None] = UnsetField
    new: Union[str, None] = UnsetField

class PlayerEnterAdminCamEvent(EventModel):
    __scope_path__ = 'events.player_enter_admin_cam'
    player: Union[Player, Link] = UnsetField

class PlayerUseItemEvent(EventModel):
    __scope_path__ = 'events.player_use_item'
    player: Union[Player, Link] = UnsetField
    item: str = UnsetField

class PlayerMessageEvent(EventModel):
    __scope_path__ = 'events.player_message'
    player: Union[Player, Link, str] = UnsetField
    message: str = UnsetField
    channel: Any = UnsetField

class PlayerWoundEvent(EventModel):
    __scope_path__ = 'events.player_wound'
    player: Union[Player, Link] = UnsetField
    other: Union[Player, Link] = UnsetField
    item: str = UnsetField

class PlayerDownedEvent(EventModel):
    __scope_path__ = 'events.player_downed'
    player: Union[Player, Link] = UnsetField
    other: Union[Player, Link] = UnsetField
    item: str = UnsetField
    headshot: bool = UnsetField
    distance: float = UnsetField

    @property
    def is_teamkill(self):
        if self.get('player') and self.get('other'):
            return self.player.get('team') and self.player.get('team') == self.other.get('team')
        else:
            return None
    
    @property
    def is_suicide(self):
        if self.has('player') and self.has('other'):
            return self.player == self.other
        else:
            return None

class PlayerDeathEvent(EventModel):
    __scope_path__ = 'events.player_death'
    player: Union[Player, Link, str] = UnsetField
    other: Union[Player, Link, None] = UnsetField
    item: str = UnsetField
    headshot: bool = UnsetField
    distance: float = UnsetField

    @property
    def is_teamkill(self):
        if self.get('player') and self.get('other'):
            return self.player.get('team') and self.player.get('team') == self.other.get('team')
        else:
            return None
    
    @property
    def is_suicide(self):
        if self.has('player') and self.has('other'):
            return self.player == self.other
        else:
            return None

class PlayerLevelUpEvent(EventModel):
    __scope_path__ = 'events.player_level_up'
    player: Union[Player, Link] = UnsetField
    old: int = UnsetField
    new: int = UnsetField

class PlayerExitAdminCamEvent(EventModel):
    __scope_path__ = 'events.player_exit_admin_cam'
    player: Union[Player, Link] = UnsetField

class PlayerLeaveSquadEvent(EventModel):
    __scope_path__ = 'events.player_leave_squad'
    player: Union[Player, Link] = UnsetField
    squad: Union[Squad, Link] = UnsetField

class PlayerLeaveTeamEvent(EventModel):
    __scope_path__ = 'events.player_leave_team'
    player: Union[Player, Link] = UnsetField
    team: Union[Team, Link] = UnsetField

class PlayerLeaveServerEvent(EventModel):
    __scope_path__ = 'events.player_leave_server'
    player: Union[Player, Link] = UnsetField

class SquadDisbandedEvent(EventModel):
    __scope_path__ = 'events.squad_disbanded'
    squad: Union[Squad, Link] = UnsetField

class TeamDisbandedEvent(EventModel):
    __scope_path__ = 'events.team_disbanded'
    team: Union[Team, Link] = UnsetField


class PrivateEventModel(EventModel):
    """A special event model that simply flags
    this event as one that should not be adopted
    by info trees."""

class UpdateEvent(PrivateEventModel):
    __scope_path__ = 'events.update'
class MountEvent(PrivateEventModel):
    __scope_path__ = 'events.mount'
class DismountEvent(PrivateEventModel):
    __scope_path__ = 'events.dismount'
class SettingUpdateEvent(PrivateEventModel):
    __scope_path__ = 'events.setting_update'
    key: str
    old: Any
    new: Any

#####################################

@unique
class EventTypes(Enum):

    def __str__(self):
        return self.name

    update = UpdateEvent
    mount = MountEvent
    dismount = DismountEvent
    setting_update = SettingUpdateEvent
    
    # In order of evaluation!
    player_join_server = PlayerJoinServerEvent
    server_map_changed = ServerMapChangedEvent
    server_state_changed = ServerStateChangedEvent
    team_created = TeamCreatedEvent
    squad_created = SquadCreatedEvent
    player_join_team = PlayerJoinTeamEvent
    player_join_squad = PlayerJoinSquadEvent
    squad_leader_change = SquadLeaderChangeEvent
    player_spawn = PlayerSpawnEvent
    player_revived = PlayerRevivedEvent
    player_change_role = PlayerChangeRoleEvent
    player_change_loadout = PlayerChangeLoadoutEvent
    player_enter_admin_cam = PlayerEnterAdminCamEvent
    player_use_item = PlayerUseItemEvent
    player_message = PlayerMessageEvent
    player_wound = PlayerWoundEvent
    player_downed = PlayerDownedEvent
    player_death = PlayerDeathEvent
    player_level_up = PlayerLevelUpEvent
    player_exit_admin_cam = PlayerExitAdminCamEvent
    player_leave_squad = PlayerLeaveSquadEvent
    player_leave_team = PlayerLeaveTeamEvent
    player_leave_server = PlayerLeaveServerEvent
    squad_disbanded = SquadDisbandedEvent
    team_disbanded = TeamDisbandedEvent

    @classmethod
    def _missing_(cls, value):
        try:
            return cls[value]
        except KeyError:
            return super()._missing_(cls, value)
    
    @classmethod
    def all(cls):
        """An iterator containing all events, excluding private ones."""
        return (cls._member_map_[name] for name in cls._member_names_)
    @classmethod
    def public(cls):
        """An iterator containing all events, excluding private ones."""
        return (cls._member_map_[name] for name in cls._member_names_ if not issubclass(cls._member_map_[name].value, PrivateEventModel))

#Events = pydantic.create_model('Events', __base__=InfoModel, **{event.name: (List[event.value], Unset) for event in EventTypes.public()})
class Events(InfoModel):
    player_join_server: List['PlayerJoinServerEvent'] = UnsetField
    server_map_changed: List['ServerMapChangedEvent'] = UnsetField
    server_state_changed: List['ServerStateChangedEvent'] = UnsetField
    team_created: List['TeamCreatedEvent'] = UnsetField
    squad_created: List['SquadCreatedEvent'] = UnsetField
    player_join_team: List['PlayerJoinTeamEvent'] = UnsetField
    player_join_squad: List['PlayerJoinSquadEvent'] = UnsetField
    squad_leader_change: List['SquadLeaderChangeEvent'] = UnsetField
    player_spawn: List['PlayerSpawnEvent'] = UnsetField
    player_revived: List['PlayerRevivedEvent'] = UnsetField
    player_change_role: List['PlayerChangeRoleEvent'] = UnsetField
    player_change_loadout: List['PlayerChangeLoadoutEvent'] = UnsetField
    player_enter_admin_cam: List['PlayerEnterAdminCamEvent'] = UnsetField
    player_use_item: List['PlayerUseItemEvent'] = UnsetField
    player_message: List['PlayerMessageEvent'] = UnsetField
    player_wound: List['PlayerWoundEvent'] = UnsetField
    player_downed: List['PlayerDownedEvent'] = UnsetField
    player_death: List['PlayerDeathEvent'] = UnsetField
    player_level_up: List['PlayerLevelUpEvent'] = UnsetField
    player_exit_admin_cam: List['PlayerExitAdminCamEvent'] = UnsetField
    player_leave_squad: List['PlayerLeaveSquadEvent'] = UnsetField
    player_leave_team: List['PlayerLeaveTeamEvent'] = UnsetField
    player_leave_server: List['PlayerLeaveServerEvent'] = UnsetField
    squad_disbanded: List['SquadDisbandedEvent'] = UnsetField
    team_disbanded: List['TeamDisbandedEvent'] = UnsetField

    def __getitem__(self, key) -> List[InfoModel]:
        return obj_getattr(self, str(EventTypes(key)))
    def __setitem__(self, key, value):
        setattr(self, str(EventTypes(key)), value)

    def add(self, *events: Union[EventModel, Type[EventModel]]):
        """Populate this model with events.

        Events are placed in the right attribute automatically. If
        still `Unset` they will be initialized. Note that private
        event models cannot be added.

        Passing an event class instead of an object will initialize
        the corresponding property. This will prevent this property
        from be overwritten when merging or when automatically
        compiling events.

        Parameters
        ----------
        *events : Union[EventModel, Type[EventModel]]
            The events to add and event types to initialize
        """
        for event in events:
            if isclass(event):
                if not issubclass(event, EventModel) or issubclass(event, PrivateEventModel):
                    raise ValueError("%s is a subclass of PrivateEventModel or is not an event")
                etype = EventTypes(event)
                if self[etype] is Unset:
                    self[etype] = InfoModelArray()
            else:
                if not isinstance(event, EventModel) or isinstance(event, PrivateEventModel):
                    raise ValueError("%s is of type PrivateEventModel or is not an event model")
                etype = EventTypes(event.__class__)
                if self[etype] is Unset:
                    self[etype] = InfoModelArray([event])
                else:
                    self[etype].append(event)

# ----- Info Hopper -----

class InfoHopper(ModelTree):
    players: List['Player'] = UnsetField
    squads: List['Squad'] = UnsetField
    teams: List['Team'] = UnsetField
    server: 'Server' = None
    events: 'Events' = None
    __solid__: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.server:
            self.server = Server(self)
        if not self.events:
            self.events = Events(self)
        obj_setattr(self, '__solid__', not self.__config__.allow_mutation)
    
    def __getattribute__(self, name: str):
        if name in obj_getattr(self, '__fields__'):
            res = super().__getattribute__(name)
            if res is Unset:
                raise AttributeError(name)
            return res
        else:
            return super().__getattribute__(name)

    def add_players(self, *players: 'Player'):
        self._add('players', *players)
    def add_squads(self, *squads: 'Squad'):
        self._add('squads', *squads)
    def add_teams(self, *teams: 'Team'):
        self._add('teams', *teams)
    def set_server(self, server: 'Server'):
        self.server = server
  
    def find_players(self, single=False, ignore_unknown=False, **filters) -> Union['Player', List['Player'], None]:
        return self._get('players', multiple=not single, ignore_unknown=ignore_unknown, **filters)
    def find_squads(self, single=False, ignore_unknown=False, **filters) -> Union['Squad', List['Squad'], None]:
        return self._get('squads', multiple=not single, ignore_unknown=ignore_unknown, **filters)
    def find_teams(self, single=False, ignore_unknown=False, **filters) -> Union['Team', List['Team'], None]:
        return self._get('teams', multiple=not single, ignore_unknown=ignore_unknown, **filters)

    @property
    def team1(self):
        return self.teams[0]
    @property
    def team2(self):
        return self.teams[1]
    
    @classmethod
    def gather(cls, *infos: 'InfoHopper'):
        """Gathers and combines all :class:`InfoHopper`s
        and returns a new hopper"""
        info = cls()
        for other in infos:
            if not other:
                continue
            info.merge(other)
        return info
        
    def compare_older(self, other: 'InfoHopper'):
        events = Events(self)

        # Since this method should only be used once done with
        # combining data from all sources, and events are never
        # really referenced backwards, it is completely safe to
        # pass objects directly. Much more reliable than Links.

        if self.has('players') and other.has('players'):
            others = InfoModelArray(other.players)
            for player in self.players:
                match = self._get(others, multiple=False, ignore_unknown=True, **player.get_key_attributes())
                if match:
                    del others[others.index(match)]

                    # Role Change Event

                    if player.has('role') and match.has('role'):
                        if player.role != match.role:
                            events.add(PlayerChangeRoleEvent(self, player=player.create_link(with_fallback=True), old=match.role, new=player.role))

                    # Loadout Change Event

                    if player.has('loadout') and match.has('loadout'):
                        if player.loadout != match.loadout:
                            events.add(PlayerChangeLoadoutEvent(self, player=player.create_link(with_fallback=True), old=match.loadout, new=player.loadout))

                    # Level Up Event

                    if player.has('level') and match.has('level'):
                        if player.level > match.level:
                            events.add(PlayerLevelUpEvent(self, player=player.create_link(with_fallback=True), old=match.level, new=player.level))

                if not player.get('joined_at'):
                    if match:
                        player.joined_at = match.get('joined_at') or player.__created_at__
                    else:
                        player.joined_at = player.__created_at__

                if not match:
                    events.add(PlayerJoinServerEvent(self, player=player.create_link(with_fallback=True)))
                
                if player.get('squad'):
                    if not match or ( not match.get('squad') ) or ( player.squad.get_key_attributes() != match.squad.get_key_attributes() ):
                        events.add(PlayerJoinSquadEvent(self, player=player.create_link(with_fallback=True), squad=player.squad.create_link(with_fallback=True)))
                if match and match.get('squad'):
                    if ( not player.get('squad') ) or ( player.squad.get_key_attributes() != match.squad.get_key_attributes() ):
                        events.add(PlayerLeaveSquadEvent(self, player=player.create_link(with_fallback=True), squad=match.squad.create_link(with_fallback=True)))
                
                if player.get('team'):
                    if not match or ( not match.get('team') ) or ( player.team.get_key_attributes() != match.team.get_key_attributes() ):
                        events.add(PlayerJoinTeamEvent(self, player=player.create_link(with_fallback=True), team=player.team.create_link(with_fallback=True)))
                if match and match.get('team'):
                    if ( not player.get('team') ) or ( player.team.get_key_attributes() != match.team.get_key_attributes() ):
                        events.add(PlayerLeaveTeamEvent(self, player=player.create_link(with_fallback=True), team=match.team.create_link(with_fallback=True)))

            for player in others:
                events.add(PlayerLeaveServerEvent(self, player=player.create_link(with_fallback=True)))
                if player.get('squad'):
                    events.add(PlayerLeaveSquadEvent(self, player=player.create_link(with_fallback=True), squad=player.squad.create_link(with_fallback=True)))
                if player.get('team'):
                    events.add(PlayerLeaveTeamEvent(self, player=player.create_link(with_fallback=True), team=player.team.create_link(with_fallback=True)))
        
        if self.has('squads') and other.has('squads'):
            others = InfoModelArray(other.squads)
            for squad in self.squads:
                match = self._get(others, multiple=False, ignore_unknown=True, **squad.get_key_attributes())
                if match:
                    del others[others.index(match)]

                    # Squad Leader Change Event

                    if squad.has('leader') and match.has('leader'):
                        if squad.leader != match.leader:
                            old = match.leader.create_link(with_fallback=True) if match.leader else None
                            new = squad.leader.create_link(with_fallback=True) if squad.leader else None
                            events.add(SquadLeaderChangeEvent(self, squad=squad.create_link(with_fallback=True), old=old, new=new))
                
                if not squad.get('created_at'):
                    if match:
                        squad.created_at = match.get('created_at') or squad.__created_at__
                    else:
                        squad.created_at = squad.__created_at__

                if not match:
                    events.add(SquadCreatedEvent(self, squad=squad.create_link(with_fallback=True)))
            
            for squad in others:
                events.add(SquadDisbandedEvent(self, squad=squad.create_link(with_fallback=True)))
        
        if self.has('teams') and other.has('teams'):
            others = InfoModelArray(other.teams)
            for team in self.teams:
                match = self._get(others, multiple=False, ignore_unknown=True, **team.get_key_attributes())
                if match:
                    del others[others.index(match)]
                
                if not team.get('created_at'):
                    if match:
                        team.created_at = match.get('created_at') or team.__created_at__
                    else:
                        team.created_at = team.__created_at__

                if not match:
                    events.add(TeamCreatedEvent(self, team=team.create_link(with_fallback=True)))
            
            for team in others:
                events.add(TeamDisbandedEvent(self, team=team.create_link(with_fallback=True)))

        self_map = self.server.get('map')
        other_map = other.server.get('map')
        if all([self_map, other_map]) and self_map != other_map:
            events.add(ServerMapChangedEvent(self, old=other_map, new=self_map))

        self.events.merge(events)
