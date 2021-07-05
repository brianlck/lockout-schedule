from typing import Dict, List, Optional
from schedule import Schedule
from model import Day, Session, Contestant, Host, Match, Availability
import argparse
import json

# command line config
parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description='Generate match schedule given availability of contestant')
parser.add_argument('data_path', type=str, helper='path to availability data')
parser.add_argument('--output_path', type=str, help='path to output schedule')

# parse arguments
args = parser.parse_args()

# read data and parse data
data_file = open(args.data_path, 'r')
data = json.load(data_file.read())

max_parallel: int = data.max_parallel
days: List[Day] = data.days
sessions: List[Session] = data.sessions
contestants: List[Contestant] = data.contestants
hosts: List[Host] = data.hosts
matches: List[Match] = [(match.contestant1, match.contestant2)
                        for match in data.matches]
hosts_availability: Dict[Host, Availability] = [
    (_.host, (_.day, _.session)) for _ in data.hosts_availability]
hosts_preference: Dict[Host, Availability] = [
    (_.host, (_.day, _.session)) for _ in data.hosts_preference]
contestants_availability: Dict[Contestant, Availability] = [
    (_.host, (_.day, _.session)) for _ in data.contestants_availability]
contestants_preference: Dict[Contestant, Availability] = [
    (_.host, (_.day, _.session)) for _ in data.contestants_preference]

# main
best_schedule: Optional[Schedule] = None
for parallel in range(1, max_parallel+1):
    for max_per_day in range(1, len(days) * len(sessions) + 1):
        schedule = Schedule.generate_schedule(parallel, max_per_day, days, contestants, hosts, sessions,
                                              matches, hosts_availability, hosts_preference, contestants_availability, contestants_preference)
        if schedule.better_than(best_schedule):
            best_schedule = schedule

if args.output_path != None:
    output_file = open(args.output_path, 'w')

for (match, config) in best_schedule.schedule:
    print('----- {} vs {} -----'.format(match[0], match[1]), file=output_file)
    print('Host: {}'.format(config[0]), file=output_file)
    print('Date: {}'.format(config[1][0]), file=output_file)
    print('Session: {}'.format(config[1][1]), file=output_file)
    
