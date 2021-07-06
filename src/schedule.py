from typing import Dict, Iterator, List, Optional, Set, Tuple
from model import Availability, Contestant, Day, Host, Match, Session, Timeslot, MatchConfig
from flow import FlowNetwork, Edge
import itertools


class Schedule:
    # schedule config
    max_parallel: int  # maximum number of parallel match
    max_per_day: int   # maximum number of match in a day
    days: List[Day]
    contestants: List[Contestant]
    hosts: List[Host]
    sessions: List[Session]
    matches: List[Match]

    # actual scheduled matches
    schedule: Optional[List[Tuple[Match, MatchConfig]]]
    unscheduled_matches: Optional[Set[Match]]
    # number of person (host included) that is scheduled match in his preferred timeslot (counted repeatedly if a person joins two matches in his preferred time)
    preferred_count: Optional[int]

    def __init__(self,
                 max_parallel: int,
                 max_per_day: int,
                 days: List[Day],
                 contestants: List[Contestant],
                 hosts: List[Host],
                 sessions: List[Session],
                 matches: List[Match],
                 schedule: Optional[List[Tuple[Match, MatchConfig]]] = None,
                 unscheduled_matches: Optional[Set[Match]] = None,
                 preferred_count: Optional[int] = None):
        """ Basically a method to hard code your schedule """
        self.max_parallel = max_parallel
        self.max_per_day = max_per_day
        self.days = days
        self.contestants = contestants
        self.hosts = hosts
        self.sessions = sessions
        self.matches = matches
        self.schedule = schedule
        self.unscheduled_matches = unscheduled_matches
        self.preferred_count = preferred_count

    def valid_schedule(self):
        return self.schedule != None and self.unscheduled_matches != None and self.preferred_count != None

    def generate_schedule(max_parallel: int,
                          max_per_day: int,
                          days: List[Day],
                          contestants: List[Contestant],
                          hosts: List[Host],
                          sessions: List[Session],
                          matches: List[Match],
                          hosts_availability: Dict[Host, Availability],
                          hosts_preference: Dict[Host, Availability],
                          contestants_availability: Dict[Contestant, Availability],
                          contestants_preference: Dict[Contestant, Availability]) -> 'Schedule':
        """ Generate schedule based on availability """
        for host in hosts:
            hosts_availability[host] = hosts_availability[host] - \
                hosts_preference[host]
            for item in hosts_preference[host]:
                assert isinstance(item, Timeslot)

        for contestant in contestants:
            contestants_availability[contestant] = contestants_availability[contestant] - \
                contestants_preference[contestant]
            for item in contestants_preference[contestant]:
                assert isinstance(item, Timeslot)
        # Construct flow network
        node_gen: Iterator[int] = itertools.count(0)
        source: int = next(node_gen)
        sink: int = next(node_gen)
        match_layer: Dict[Match, int] = {
            match: next(node_gen) for match in matches}
        match_config_layer: Dict[MatchConfig, int] = {MatchConfig(host, Timeslot(day, session)): next(node_gen)
                                                      for day in days for session in sessions for host in hosts}
        timeslot_layer: Dict[Timeslot, int] = {Timeslot(day, session): next(
            node_gen) for day in days for session in sessions}
        day_layer: Dict[Day] = {day: next(node_gen) for day in days}
        nodes: int = next(node_gen)
        network: FlowNetwork = FlowNetwork(nodes)
        match_config_edges: Dict[Tuple[Match, MatchConfig], Edge] = {}

        for match in matches:
            network.add_edge(source, match_layer[match], capacity=1, cost=0)
            for host in hosts:
                preferred_timeslots = hosts_preference[host].intersection(contestants_preference[match[0]].intersection(
                    contestants_preference[match[1]]))
                partially_preferred_timeslots = hosts_preference[host].intersection(contestants_preference[match[0]].intersection(
                    contestants_availability[match[1]]).union(contestants_availability[match[0]].intersection(contestants_preference[match[1]])))
                available_timeslots = hosts_preference[host].intersection(contestants_availability[match[0]].intersection(
                    contestants_availability[match[1]]))

                for timeslot in preferred_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=1+1+1)
                for timeslot in partially_preferred_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=1+1+nodes)
                for timeslot in available_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=1+nodes+nodes)

                preferred_timeslots = hosts_availability[host].intersection(contestants_preference[match[0]].intersection(
                    contestants_preference[match[1]]))
                partially_preferred_timeslots = hosts_availability[host].intersection(contestants_preference[match[0]].intersection(
                    contestants_availability[match[1]]).union(contestants_availability[match[0]].intersection(contestants_preference[match[1]])))
                available_timeslots = hosts_availability[host].intersection(contestants_availability[match[0]].intersection(
                    contestants_availability[match[1]]))

                for timeslot in preferred_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=nodes+1+1)
                for timeslot in partially_preferred_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=nodes+nodes+1)
                for timeslot in available_timeslots:
                    match_config = MatchConfig(host, timeslot)
                    match_config_edges[(match, match_config)] = network.add_edge(
                        match_layer[match], match_config_layer[match_config], capacity=1, cost=nodes+nodes+nodes)

        for day in days:
            network.add_edge(day_layer[day], sink,
                             capacity=max_per_day, cost=0)
            for session in sessions:
                timeslot = Timeslot(day, session)
                network.add_edge(
                    timeslot_layer[timeslot], day_layer[day], capacity=max_parallel, cost=0)
                for host in hosts:
                    network.add_edge(match_config_layer[MatchConfig(
                        host, timeslot)], timeslot_layer[timeslot], capacity=max_parallel, cost=0)

        network.min_cost_max_flow(source, sink)

        schedule = Schedule(max_parallel, max_per_day, days,
                            contestants, hosts, sessions, matches, schedule=[], unscheduled_matches=set(matches), preferred_count=0)
        for ((match, config), edge) in match_config_edges.items():
            if edge.flow == 1:
                schedule.schedule.append((match, config))
                schedule.preferred_count += edge.cost % nodes
                schedule.unscheduled_matches.remove(match)
        # sort by match day, then by match session, then by match host
        schedule.schedule.sort(key=lambda match: (days.index(
            match[1].timeslot.day), sessions.index(match[1].timeslot.session), hosts.index(match[1].host)))
        return schedule

    def better_than(self, schedule: 'Schedule') -> bool:
        assert self.valid_schedule()
        assert schedule.valid_schedule()

        # schedule with less scheduled match should be preferred
        if len(self.unscheduled_matches) != len(schedule.unscheduled_matches):
            return len(self.unscheduled_matches) < len(schedule.unscheduled_matches)

        # a good schedule should maximise preferred_count
        if self.preferred_count != schedule.preferred_count:
            return self.preferred_count > schedule.preferred_count

        # minimise maximum parallel match
        if self.max_parallel != schedule.max_parallel:
            return self.max_parallel < schedule.max_parallel

        # minimise maximum number of matches per day
        if self.max_per_day != schedule.max_per_day:
            return self.max_per_day < schedule.max_per_day

        return False  # two schedules are equally as good
