import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import matplotlib.patches as mpatches

# ── Load + clean ──
df = pd.read_csv("Filemaker_CLEAN.csv")
df = df[["uniqname", "experience_type", "year", "term_season"]].dropna()
df["experience_type"] = df["experience_type"].str.strip()
df = df.drop_duplicates()
# Rename an event
df["experience_type"] = df["experience_type"].replace({
    "Counseling Appointment": "Counseling"
})

season_map = {"WN": 1, "SP": 2, "SU": 3, "FA": 4}
df["season_num"] = df["term_season"].map(season_map)
df = df.sort_values(["uniqname", "year", "season_num"])

# ── Build collapsed sequences (remove consecutive repeats) ──
raw_sequences = df.groupby("uniqname")["experience_type"].apply(list)

def remove_consecutive_duplicates(seq):
    return [seq[i] for i in range(len(seq)) if i == 0 or seq[i] != seq[i - 1]]

collapsed_sequences = raw_sequences.apply(remove_consecutive_duplicates)

# ── Build transition counts ──
transitions = []
for seq in collapsed_sequences:
    for i in range(len(seq) - 1):
        transitions.append((seq[i], seq[i + 1]))

trans_df = pd.DataFrame(transitions, columns=["from", "to"])

counts = trans_df.groupby(["from", "to"]).size().reset_index(name="count")
counts["total"] = counts.groupby("from")["count"].transform("sum")
counts["prob"] = counts["count"] / counts["total"]

# ── Baseline and lift ──
baseline = df["experience_type"].value_counts(normalize=True)
counts["baseline"] = counts["to"].map(baseline)
counts["lift"] = (counts["prob"] / counts["baseline"]).round(2)

# ── Pivot to matrices ──
exp_types = sorted(df["experience_type"].unique())

prob_matrix = counts.pivot(index="from", columns="to", values="prob") \
    .reindex(index=exp_types, columns=exp_types).fillna(0)

lift_matrix = counts.pivot(index="from", columns="to", values="lift") \
    .reindex(index=exp_types, columns=exp_types).fillna(0)

count_matrix = counts.pivot(index="from", columns="to", values="count") \
    .reindex(index=exp_types, columns=exp_types).fillna(0)

# ── Plot ──
fig, ax = plt.subplots(figsize=(8, 6.5))

# Custom smoother colormap
cmap = mcolors.LinearSegmentedColormap.from_list(
    "custom_blues",
    ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]
)

im = ax.imshow(prob_matrix.values, cmap=cmap, vmin=0, vmax=0.6)

n = len(exp_types)
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels(exp_types, rotation=30, ha="right", fontsize=10)
ax.set_yticklabels(exp_types, fontsize=10)

ax.set_xlabel("Next experience", fontsize=11, labelpad=10)
ax.set_ylabel("Current experience", fontsize=11, labelpad=10)
ax.set_title(
    "Experience Transitions\nProbability (P(next | current)) with Lift",
    fontsize=13,
    weight="bold",
    pad=14
)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Subtle gridlines
ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
ax.grid(which="minor", color="#dddddd", linestyle='-', linewidth=0.6)
ax.tick_params(which="minor", bottom=False, left=False)

# ── Cell annotations ──
for i, from_type in enumerate(exp_types):
    for j, to_type in enumerate(exp_types):
        prob = prob_matrix.loc[from_type, to_type]
        lift = lift_matrix.loc[from_type, to_type]

        if prob < 0.02:
            continue

        text_color = "white" if prob > 0.35 else "#222"

        # Probability (main signal)
        ax.text(
            j, i - 0.08, f"{prob:.0%}",
            ha="center", va="center",
            fontsize=10, fontweight="bold", color=text_color
        )

        # Lift (only if meaningful)
        if lift >= 1.2:
            lift_color = "#c0392b" if lift >= 1.5 else "#666"
            ax.text(
                j, i + 0.28, f"{lift:.1f}×",
                ha="center", va="center",
                fontsize=8, color=lift_color
            )

# ── Highlight high-lift cells ──
for i, from_type in enumerate(exp_types):
    for j, to_type in enumerate(exp_types):
        if lift_matrix.loc[from_type, to_type] >= 1.5:
            rect = plt.Rectangle(
                (j - 0.5, i - 0.5),
                1, 1,
                linewidth=2,
                edgecolor="#c0392b",
                facecolor="none"
            )
            ax.add_patch(rect)

# ── Colorbar ──
cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
cbar.set_label("Transition probability", fontsize=10)
cbar.ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x:.0%}")
)

# ── Legend ──
red_patch = mpatches.Patch(
    edgecolor="#c0392b",
    facecolor="none",
    linewidth=2,
    label="High lift (≥ 1.5×)"
)

ax.legend(
    handles=[red_patch],
    loc="upper center",
    bbox_to_anchor=(0.5, -0.18),
    frameon=False,
    fontsize=9
)

plt.tight_layout()
plt.savefig("transition_heatmap.png", dpi=200, bbox_inches="tight")
plt.show()

# ── Advisor-readable summary ──
notable = counts[counts["lift"] >= 1.5].sort_values("lift", ascending=False)

print("\n=== High-lift transitions (lift ≥ 1.5×) ===")
print("These transitions happen significantly more often than chance:\n")

for _, row in notable.iterrows():
    print(
        f"  {row['from']} → {row['to']}: "
        f"{row['prob']:.0%} of students, lift = {row['lift']:.2f}× "
        f"(n={int(row['count'])})"
    )