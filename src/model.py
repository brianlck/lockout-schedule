from dataclasses import dataclass
from typing import NewType, List, Tuple, Set

Day = NewType('Day', str)
Session = NewType('Session', str)
Host = NewType('Host', str)
Contestant = NewType('Contestant', str)
Match = NewType('Match', Tuple[str])

@dataclass
class Timeslot:
    day: Day
    session: Session
    def __init__(self, day: Day, session: Session) -> None:
        self.day = day
        self.session = session
    def __hash__(self) -> int:
        return hash((self.day, self.session))
    def __eq__(self, other: 'Timeslot') -> bool:
        return self.day == other.day and self.session == other.session

@dataclass
class MatchConfig:
    host: Host
    timeslot: Timeslot
    def __init__(self, host: Host, timeslot: Timeslot) -> None:
        self.host = host
        self.timeslot = timeslot
    def __hash__(self) -> int:
        return hash((self.host, self.timeslot))
    def __eq__(self, other: 'MatchConfig') -> bool:
        return self.host == other.host and self.timeslot == other.timeslot
    
Availability = NewType('Availability', Set[Timeslot])
