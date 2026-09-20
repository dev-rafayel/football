"""
calculations.py

Takes the raw match rows from the database and works out totals,
averages, and a weighted "performance score" for each match.
"""


def total_stats(matches):
    totals = {"goals": 0, "assists": 0, "saves": 0, "minutes_played": 0}
    for m in matches:
        totals["goals"] += m["goals"]
        totals["assists"] += m["assists"]
        totals["saves"] += m["saves"]
        totals["minutes_played"] += m["minutes_played"]
    return totals


def average_stats(matches):
    if not matches:
        return {"goals": 0, "assists": 0, "saves": 0}

    totals = total_stats(matches)
    count = len(matches)
    return {
        "goals": totals["goals"] / count,
        "assists": totals["assists"] / count,
        "saves": totals["saves"] / count,
    }


def performance_score(match, weights):
    """Weighted score for a single match row."""
    return (
        match["goals"] * weights["goal_weight"]
        + match["assists"] * weights["assist_weight"]
        + match["saves"] * weights["save_weight"]
    )


def performance_scores(matches, weights):
    """Returns a list of (date, score) pairs, one per match, in order.
    Used later to plot the trend line."""
    scores = []
    for m in matches:
        score = performance_score(m, weights)
        scores.append((m["match_date"], score))
    return scores
