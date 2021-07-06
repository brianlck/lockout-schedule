from flow import FlowNetwork
import unittest
from model import Timeslot

from schedule import Schedule


class FlowTest(unittest.TestCase):
    def test_small_case(self):
        """Source: https://www.luogu.com.cn/problem/P3381"""
        nodes = 4
        source = 4 - 1  # -1 from 1-based to 0-based
        sink = 3 - 1
        network = FlowNetwork(nodes)
        network.add_edge(4-1, 2-1, 30, 2)
        network.add_edge(4-1, 3-1, 20, 3)
        network.add_edge(2-1, 3-1, 20, 1)
        network.add_edge(2-1, 1-1, 30, 9)
        network.add_edge(1-1, 3-1, 40, 5)
        flow, cost = network.min_cost_max_flow(source, sink)
        self.assertEqual(flow, 50)
        self.assertEqual(cost, 280)


class TestSchedule(unittest.TestCase):
    def test_small_schedule(self):
        schedule = Schedule.generate_schedule(max_parallel=3,
                                              max_per_day=6,
                                              days=["10/7", "11/7", "12/7"],
                                              contestants=[
                                                  "lckcode", "benson1029", "chengheichit", "ethening"],
                                              hosts=["host1", "host2"],
                                              sessions=["Afternoon",
                                                        "Evening", "Night"],
                                              matches=[("lckcode", "benson1029"), ("chengheichit", "ethening"), (
                                                  "lckcode", "chengheichit"), ("ethening", "benson1029")],
                                              hosts_availability={"host1": set([Timeslot("10/7", "Afternoon"), Timeslot("10/7", "Evening"), Timeslot("10/7", "Night"), Timeslot("11/7", "Afternoon"), Timeslot(
                                                  "11/7", "Evening"), Timeslot("11/7", "Night"), Timeslot("12/7", "Afternoon"), Timeslot("12/7", "Evening"), Timeslot("12/7", "Night")]), "host2": set([Timeslot("10/7", "Evening"), Timeslot("10/7", "Night"), Timeslot("11/7", "Afternoon"), Timeslot(
                                                      "11/7", "Evening"), Timeslot("12/7", "Evening")])},
                                              hosts_preference={"host1": set([Timeslot("10/7", "Night"), Timeslot(
                                                  "11/7", "Evening"), Timeslot("11/7", "Night"), Timeslot("12/7", "Afternoon"), Timeslot("12/7", "Evening"), Timeslot("12/7", "Night")]), "host2": set([Timeslot("10/7", "Evening"), Timeslot("10/7", "Night"), Timeslot("12/7", "Evening")])},
                                              contestants_availability={"lckcode": set([Timeslot("10/7", "Afternoon"), Timeslot("10/7", "Evening"), Timeslot(
                                                  "11/7", "Evening"), Timeslot("11/7", "Night"), Timeslot("12/7", "Evening")]), "benson1029": set([Timeslot("10/7", "Evening"), Timeslot("10/7", "Night"), Timeslot(
                                                      "11/7", "Evening"), Timeslot("11/7", "Night")]), "chengheichit": set([Timeslot("10/7", "Afternoon"),  Timeslot("12/7", "Afternoon"), Timeslot("12/7", "Evening"), Timeslot("12/7", "Night")]), "ethening": set([Timeslot("10/7", "Afternoon"), Timeslot("10/7", "Evening"), Timeslot("10/7", "Night"), Timeslot("11/7", "Afternoon"), Timeslot(
                                                          "11/7", "Evening"), Timeslot("12/7", "Night")])},
                                              contestants_preference={"lckcode": set([Timeslot("10/7", "Afternoon"), Timeslot("11/7", "Night"), Timeslot("12/7", "Evening")]), "benson1029": set([Timeslot("11/7", "Night")]), "chengheichit": set([Timeslot("10/7", "Afternoon"), Timeslot("12/7", "Night")]), "ethening": set([Timeslot("10/7", "Afternoon"), Timeslot("10/7", "Evening"), Timeslot("11/7", "Afternoon"), Timeslot("12/7", "Night")])})
        self.assertEqual(schedule.preferred_count, 9)
        self.assertEqual(len(schedule.unscheduled_matches), 0)
