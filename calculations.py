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

# stats from a single match 
def performance_score(match, weights):
    return (
        match["goals"] * weights["goal_weight"]
        + match["assists"] * weights["assist_weight"]
        + match["saves"] * weights["save_weight"]
    )

# returns a list of date and score pairs
def performance_scores(matches, weights):
    scores = []
    for m in matches:
        score = performance_score(m, weights)
        scores.append((m["match_date"], score))
    return scores
