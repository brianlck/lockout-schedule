# lockout-schedule
A command line tool to schedule matches for jsoi lockout tournament 2020-21

In a setting of N matches, M days, C contestants, H hosts, K sessions where each host and participant has a list availability and preferred time slot, the tool generates a schedule that fulfills the following critieria in order (for tie break purposes).

1. Maximise the number of scheduled match
2. Maximise the number of occasions in which participant/host participates in his preferred timeslot
3. Minimise the maximum number of parallel match in all timeslot
4. Minimise the maximum number of matches per day

Under a fixed bound of maximum number of parallel, and maximum number of matches per day, the problem can be solved with a min cost max flow algorithm on a flow network of 5 layers with 2 + N + H * K * M + K * M + M nodes in total with complexity of O(N^2 H K M).

The general problem can then be solved by exhausting the two parameters.
Total Complexity: O(N^2 H K^2 M^2) assuming the maximum number of parallel matches is constant bounded
