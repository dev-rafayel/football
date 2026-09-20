import matplotlib.pyplot as plt

from calculations import performance_scores


def plot_player_trend(player_name, matches, weights):
    if not matches:
        print("No matches to plot for this player yet.")
        return

    data = performance_scores(matches, weights)
    dates = [d for d, _ in data]
    scores = [s for _, s in data]

    plt.figure(figsize=(9, 5))
    plt.plot(dates, scores, marker="o", color="#2b7a0b")
    plt.title(f"Performance trend - {player_name}")
    plt.xlabel("Match date")
    plt.ylabel("Performance score")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
