from typing import NewType, List, Tuple, Set

Day = NewType('Day', str)
Session = NewType('Session', str)
Host = NewType('Host', str)
Contestant = NewType('Contestant', str)
Match = NewType('Match', Tuple[str])
Timeslot = NewType('Timeslot', Tuple[Day, Session])
Availability = NewType('Availability', Set[Timeslot])
MatchConfig = NewType('MatchConfig', Tuple[Host, Timeslot])