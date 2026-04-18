import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

df = pd.read_csv("Filemaker_CLEAN.csv")
df = df[["uniqname", "class_year", "experience_type", "year", "term_season"]].dropna()
df["experience_type"] = df["experience_type"].str.strip()
df = df.drop_duplicates()

# ── Build per-student engagement counts, anchored to their first-seen class year ──
engagement_counts = df.groupby("uniqname").size().rename("total")
first_class = df.groupby("uniqname")["class_year"].first()  # class year at first interaction

student_df = pd.concat([engagement_counts, first_class], axis=1).reset_index()

# ── Bucket into depth tiers ──
def depth_tier(n):
    if n == 1:
        return "1 (one-and-done)"
    elif n == 2:
        return "2"
    elif n <= 5:
        return "3–5"
    else:
        return "6+"

student_df["depth"] = student_df["total"].apply(depth_tier)

order_class = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
order_depth  = ["1 (one-and-done)", "2", "3–5", "6+"]
colors       = ["#d0d0d0", "#a3c4e8", "#4a90d9", "#1a4f8a"]

student_df["class_year"] = pd.Categorical(student_df["class_year"], categories=order_class, ordered=True)
student_df["depth"]      = pd.Categorical(student_df["depth"],      categories=order_depth,  ordered=True)
student_df = student_df[student_df["class_year"].notna()]

# ── Pivot to stacked proportions ──
pivot = (
    student_df.groupby(["class_year", "depth"], observed=True)
    .size()
    .unstack("depth", fill_value=0)
)
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

# ── Plot ──
fig, ax = plt.subplots(figsize=(9, 5))

bottoms = np.zeros(len(pivot_pct))
for tier, color in zip(order_depth, colors):
    if tier in pivot_pct.columns:
        vals = pivot_pct[tier].values
        bars = ax.bar(pivot_pct.index, vals, bottom=bottoms, color=color,
                      label=tier, width=0.55, edgecolor="white", linewidth=0.6)
        # Label segments that are wide enough to read
        for bar, v, b in zip(bars, vals, bottoms):
            if v > 6:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        b + v / 2, f"{v:.0f}%",
                        ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        bottoms += vals

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, 100)
ax.set_xlabel("Class year at first interaction", fontsize=11)
ax.set_ylabel("Share of students", fontsize=11)
ax.set_title("Engagement depth by class year\n(anchored to student's first recorded interaction)", fontsize=12)
ax.legend(title="Experiences", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

# Annotate one-and-done rate explicitly
for i, cy in enumerate(pivot_pct.index):
    v = pivot_pct.loc[cy, "1 (one-and-done)"] if "1 (one-and-done)" in pivot_pct.columns else 0
    ax.text(i, v / 2, f"{v:.0f}%", ha="center", va="center",
            fontsize=8, color="#333", fontweight="bold")

plt.tight_layout()
plt.savefig("engagement_funnel.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Summary table for advisors ──
summary = pivot.copy()
summary["total_students"] = summary.sum(axis=1)
summary["one_and_done_%"] = (summary.get("1 (one-and-done)", 0) / summary["total_students"] * 100).round(1)
summary["highly_engaged_%"] = (summary.get("6+", 0) / summary["total_students"] * 100).round(1)
print("\n=== Advisor Summary Table ===")
print(summary[["total_students", "one_and_done_%", "highly_engaged_%"]].to_string())