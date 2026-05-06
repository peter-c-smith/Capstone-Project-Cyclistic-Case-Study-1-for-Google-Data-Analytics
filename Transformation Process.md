Why decimal is nicer for visuals:
The whole minute method uses integer rounding, which creates a few problems in Power BI visuals:

Averages get distorted — if you're showing average ride time in a card or bar chart, integers round every ride to the nearest minute before averaging, so your average itself is less accurate. With decimals, the average is computed from precise values.
Histograms look unnatural — with whole minutes you get artificial spikes at every integer (5 min, 6 min, 7 min) creating a comb-like pattern that doesn't reflect the true distribution of ride times.
Short rides lose resolution — a ride of 90 seconds rounds to 2 minutes as an integer, but shows as 1.5 minutes in decimal, which is meaningfully more accurate especially when many Cyclistic rides are short.
Trend lines are smoother — when plotting ride time over time of day or day of week, decimal values produce smoother, more credible trend lines rather than stepped integers.