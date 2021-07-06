from typing import Dict, List, Optional
from schedule import Schedule
from model import Day, Session, Contestant, Host, Match, Availability, Timeslot
import argparse
import json
import sys

# command line config
parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description='Generate match schedule given availability of contestant')
parser.add_argument('data_path', type=str, help='file to availability data')
parser.add_argument('-o', type=str, help='file to output schedule')

# parse arguments
args = parser.parse_args()

# read data and parse data
data_file = open(args.data_path, 'r')
data = json.load(data_file)

max_parallel: int = data['max_parallel']
days: List[Day] = data['days']
sessions: List[Session] = data['sessions']
contestants: List[Contestant] = data['contestants']
hosts: List[Host] = data['hosts']
matches: List[Match] = [(match['contestant1'], match['contestant2'])
                        for match in data['matches']]
hosts_availability: Dict[Host, Availability] = {
    host: {Timeslot(timeslot['day'], timeslot['session']) for timeslot in _} for (host, _) in data['hosts_availability'].items()}
hosts_preference: Dict[Host, Availability] = {
    host: {Timeslot(timeslot['day'], timeslot['session']) for timeslot in _} for (host, _) in data['hosts_preference'].items()}
contestants_availability: Dict[Contestant, Availability] = {
    contestant: {Timeslot(timeslot['day'], timeslot['session']) for timeslot in _} for (contestant, _) in data['contestants_availability'].items()}
contestants_preference: Dict[Contestant, Availability] = {
    contestant: {Timeslot(timeslot['day'], timeslot['session']) for timeslot in _} for (contestant, _) in data['contestants_preference'].items()}

# main
best_schedule: Optional[Schedule] = None
for parallel in range(1, max_parallel+1):
    for max_per_day in range(1, len(days) * len(sessions) + 1):
        schedule = Schedule.generate_schedule(parallel, max_per_day, days, contestants, hosts, sessions,
                                              matches, hosts_availability, hosts_preference, contestants_availability, contestants_preference)
        if best_schedule == None or schedule.better_than(best_schedule):
            best_schedule = schedule

output_stream = sys.stdout
if args.o != None:
    output_stream = open(args.o, 'w')

for (match, config) in best_schedule.schedule:
    print('----- {} vs {} -----'.format(match[0], match[1]), file=output_stream)
    print('Host: {}'.format(config.host), file=output_stream)
    print('Date: {}'.format(config.timeslot.day), file=output_stream)
    print('Session: {}'.format(config.timeslot.session), file=output_stream)
    print('', file=output_stream)

print('-----------------', file=output_stream)
print('Preferred count: {}'.format(schedule.preferred_count), file=output_stream)
print('Max parallel: {}'.format(schedule.max_parallel), file=output_stream)
print('Unscheduled Matches: {}'.format(schedule.unscheduled_matches), file=output_stream)

