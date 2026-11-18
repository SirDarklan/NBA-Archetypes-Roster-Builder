"""Prepare player-season features for NBA archetype clustering.

Pipeline stages:
1. Keep player-seasons with at least 400 total minutes
2. Create shot-zone attempt shares and select the initial feature list
3. Export pairwise feature correlations and identify redundant features.
4. Export the retained unscaled features, then z-score those features.

"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Input paths and joined-table schema.
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent

MERGED_DATA_PATH = PROJECT_DIR / "data" / "player_season_joined.csv"

OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

# Outputs results of all feature correlation pairs
CORRELATION_PAIRS_PATH = OUTPUT_DIR / "feature_correlation_pairs.csv"

# Filtered table for selected uncorrelated features
FILTERED_FEATURES_PATH = OUTPUT_DIR / "clustering_features.csv"

# Filtered table for selected uncorrelated features standardized 
STANDARDIZED_FEATURES_PATH = OUTPUT_DIR / "clustering_features_standardized.csv"

# Reference for scaling interpretation
SCALING_STATS_PATH = OUTPUT_DIR / "feature_scaling_stats.csv"

# Set minimum minutes to be 400 per season 
MINUTES_COLUMN = "MIN_player_totals"
MINUTES_MIN = 400

# create screen assists per 36 metric not just raw screen assist
HUSTLE_MINUTES_COLUMN = "MIN_hustle"
SCREEN_ASSISTS_COLUMN = "SCREEN_ASSISTS_hustle"
SCREEN_ASSISTS_PER36 = "SCREEN_ASSISTS_PER36"

# Shot-zone FGA source columns. We use the combined Corner 3 field only and not the left/right corners.
# Backcourt attempts are excluded from the denominator because they are not meaningful shot-location choice.
SHOT_ZONE_FGA_COLUMNS = {
    "restricted_area": "Restricted Area_FGA_shot_zones",
    "paint_non_ra": "In The Paint (Non-RA)_FGA_shot_zones",
    "mid_range": "Mid-Range_FGA_shot_zones",
    "corner_3": "Corner 3_FGA_shot_zones",
    "above_break_3": "Above the Break 3_FGA_shot_zones",
}

SHOT_SHARE_FEATURES = [
    "SHOT_SHARE_PAINT_NON_RA",
    "SHOT_SHARE_MID_RANGE",
    "SHOT_SHARE_CORNER_3",
    "SHOT_SHARE_ABOVE_BREAK_3",
]

# Initial candidate features. 
# Percentage/rate fields describe where their production comes from. 
# Efficiency and quality metrics are left out so clusters focus on playing style.

INITIAL_FEATURES = [
    # Role and involvement from player_advanced.csv.
    "USG_PCT_player_advanced",
    "AST_PCT_player_advanced",
    "OREB_PCT_player_advanced",
    "DREB_PCT_player_advanced",
    # Scoring profile percentages from player_scoring.csv.
    "PCT_FGA_3PT_player_scoring",
    "PCT_PTS_2PT_MR_player_scoring",
    "PCT_PTS_3PT_player_scoring",
    "PCT_PTS_PAINT_player_scoring",
    "PCT_PTS_FT_player_scoring",
    "PCT_PTS_FB_player_scoring",
    # Shot zone location shares created from shot_zones.csv below.
    *SHOT_SHARE_FEATURES,
    # Hustle features.
    "PCT_LOOSE_BALLS_RECOVERED_DEF_hustle",
    "PCT_BOX_OUTS_DEF_hustle",
    # Frequency of rim protection from defend_rim.csv
    "FREQ_defend_rim",
    # Screening role.
    SCREEN_ASSISTS_PER36,
]

# Threshold to drop 
CORRELATION_THRESHOLD = 0.90

# Keep all shooting metrics in the initial analysis.
# If one of these four overlaps strongly with another feature, 
# prefer dropping it so shot-zone shares remain the main description of shot location.
DROP_PREFERENCE = {
    "PCT_FGA_3PT_player_scoring",
    "PCT_PTS_2PT_MR_player_scoring",
    "PCT_PTS_3PT_player_scoring",
    "PCT_PTS_PAINT_player_scoring",
}

# Metadata columns are copied through to the output CSVs but never standardized
# or used to calculate correlations. 
OUTPUT_METADATA_COLUMNS = [
    "PLAYER_ID",
    "PLAYER_NAME",
    "SEASON",
    "TEAM_ID",
    "TEAM_ABBREVIATION",
    "PLAYER_POSITION_defend_rim",
    "GP_player_totals",
    "MIN_player_totals",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV into a list of row dictionaries."""
    with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    """Write rows using a stable field order and create the output directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def number(value: Any) -> float:
    """Convert a CSV value to a number."""
    return float(value)


def shot_attempts(value: Any) -> float:
    """Treat blank shot-zone counts as zero attempts."""
    return float(value or 0)


def create_shot_zone_shares(
    rows: list[dict[str, Any]],
) -> None:
    """Add four shot-location shares from mutually exclusive zone attempts.

    Blank FGA cells are treated as zero attempts. A row with zero attempts in
    the five tracked zones receives zero for each share. Restricted-area share
    is intentionally left as the reference location, reducing the number of
    composition features that sum to one.
    """
    for row in rows:
        attempts = {
            zone: shot_attempts(row.get(column))
            for zone, column in SHOT_ZONE_FGA_COLUMNS.items()
        }
        denominator = sum(attempts.values()) or 1
        row["SHOT_SHARE_PAINT_NON_RA"] = attempts["paint_non_ra"] / denominator
        row["SHOT_SHARE_MID_RANGE"] = attempts["mid_range"] / denominator
        row["SHOT_SHARE_CORNER_3"] = attempts["corner_3"] / denominator
        row["SHOT_SHARE_ABOVE_BREAK_3"] = attempts["above_break_3"] / denominator


def create_screen_assist_rate(rows: list[dict[str, Any]]) -> None:
    """Create screen assists per 36 minutes from Hustle totals."""
    # Rate feature per 36 minutes
    for row in rows:
        row[SCREEN_ASSISTS_PER36] = (
            number(row.get(SCREEN_ASSISTS_COLUMN))
            / number(row.get(HUSTLE_MINUTES_COLUMN))
            * 36
        )


def calculate_correlations(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """ Pearson correlation for every pair in the initial feature list."""
    # Create numeric vector for each candidate and then run all pairs
    values = {
        feature: [number(row.get(feature)) for row in rows]
        for feature in INITIAL_FEATURES
    }

    pairs: list[dict[str, Any]] = []

    # Calculate correlation for each pair 
    for first_index, feature_a in enumerate(INITIAL_FEATURES):
        for feature_b in INITIAL_FEATURES[first_index + 1 :]:
            correlation = statistics.correlation(values[feature_a], values[feature_b])
            pairs.append(
                {
                    "FEATURE_1": feature_a,
                    "FEATURE_2": feature_b,
                    "PEARSON_R": correlation,
                    "ABS_PEARSON_R": abs(correlation),
                    "ABOVE_THRESHOLD": abs(correlation) >= CORRELATION_THRESHOLD,
                }
            )
    return pairs


def choose_correlated_features_to_drop(
    correlation_pairs: list[dict[str, Any]],
) -> tuple[list[str], dict[tuple[str, str], str]]:
    """Greedily drop one feature from each highly correlated active pair.

    When both features remain, the earlier feature in INITIAL_FEATURES is kept.
    We can review the correlation report and change the initial feature order 
    or list when domain knowledge supports a different choice.
    """
    # Start with strongest pairs
    priority = {feature: index for index, feature in enumerate(INITIAL_FEATURES)}
    candidate_pairs = [
        pair
        for pair in correlation_pairs
        if pair["ABOVE_THRESHOLD"]
    ]
    candidate_pairs.sort(key=lambda pair: pair["ABS_PEARSON_R"], reverse=True)

    # Remove each explicitly deprioritized shooting metric if it has at least one high-correlation relationship. 
    # This avoids leaving a metric in the final list just because its strongest correlated partner was removed first.
    dropped = {
        feature
        for pair in candidate_pairs
        for feature in (pair["FEATURE_1"], pair["FEATURE_2"])
        if feature in DROP_PREFERENCE
    }
    decisions: dict[tuple[str, str], str] = {}
    for pair in candidate_pairs:
        feature_a = pair["FEATURE_1"]
        feature_b = pair["FEATURE_2"]
        preferred_drops = [
            feature for feature in (feature_a, feature_b)
            if feature in DROP_PREFERENCE
        ]
        if preferred_drops:
            decisions[(feature_a, feature_b)] = (
                "Drop " + ", ".join(preferred_drops)
            )
            continue

        if feature_a in dropped or feature_b in dropped:
            decisions[(feature_a, feature_b)] = "Already handled through another correlated pair"
            continue

        drop_feature = feature_a if priority[feature_a] > priority[feature_b] else feature_b
        dropped.add(drop_feature)
        decisions[(feature_a, feature_b)] = f"Drop {drop_feature}; retain the higher-priority feature"

    retained = [feature for feature in INITIAL_FEATURES if feature not in dropped]
    return retained, decisions


def metadata_columns_for_output(rows: list[dict[str, Any]]) -> list[str]:
    """Return available metadata fields in the requested stable order."""
    return [column for column in OUTPUT_METADATA_COLUMNS if column in rows[0]]


def standardize_features(
    rows: list[dict[str, Any]],
    retained_features: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Population-z-score retained features while preserving metadata fields."""
    # Z-scores center each retained feature at zero and scale it to one std dev
    # Prevents larger numbers from dominating 
    metadata_columns = metadata_columns_for_output(rows)
    standardized: list[dict[str, Any]] = [
        {column: row.get(column, "") for column in metadata_columns}
        for row in rows
    ]
    scaling_stats: list[dict[str, Any]] = []

    for feature in retained_features:
        values = [number(row.get(feature)) for row in rows]
        mean = statistics.fmean(values)
        # Population standard deviation 
        standard_deviation = statistics.pstdev(values)
        for output_row, value in zip(standardized, values):
            output_row[feature] = (value - mean) / standard_deviation
        scaling_stats.append(
            {
                "FEATURE": feature,
                "MEAN": mean,
                "POPULATION_STD": standard_deviation,
            }
        )

    return standardized, scaling_stats


def run_pipeline() -> None:
    """Run the staged feature-preparation workflow on the joined CSV."""
    source_rows = read_csv_rows(MERGED_DATA_PATH)

    # Apply the minutes threshold.
    eligible_rows = [
        row
        for row in source_rows
        if number(row.get(MINUTES_COLUMN)) >= MINUTES_MIN
    ]

    player_rows = eligible_rows

    # Create location shares and the screen-assist rate.
    create_shot_zone_shares(player_rows)
    create_screen_assist_rate(player_rows)

    # Save pairwise correlations, including the decision made for each
    correlation_pairs = calculate_correlations(player_rows)
    retained_features, decisions = choose_correlated_features_to_drop(correlation_pairs)
    for pair in correlation_pairs:
        pair_key = (pair["FEATURE_1"], pair["FEATURE_2"])
        pair["FILTER_DECISION"] = decisions.get(pair_key, "Keep both")
    write_csv_rows(
        CORRELATION_PAIRS_PATH,
        ["FEATURE_1", "FEATURE_2", "PEARSON_R", "ABS_PEARSON_R", "ABOVE_THRESHOLD", "FILTER_DECISION"],
        correlation_pairs,
    )

    # Export the filtered, unscaled modeling table. 
    # Player identifiers, season, and other available 
    # descriptors are retained only as metadata.
    metadata_columns = metadata_columns_for_output(player_rows)
    unscaled_rows = [
        {column: row.get(column, "") for column in metadata_columns + retained_features}
        for row in player_rows
    ]
    write_csv_rows(FILTERED_FEATURES_PATH, metadata_columns + retained_features, unscaled_rows)

    # Standardize the retained features
    standardized_rows, scaling_stats = standardize_features(player_rows, retained_features)
    write_csv_rows(
        STANDARDIZED_FEATURES_PATH,
        metadata_columns + retained_features,
        standardized_rows,
    )
    write_csv_rows(SCALING_STATS_PATH, ["FEATURE", "MEAN", "POPULATION_STD"], scaling_stats)


if __name__ == "__main__":
    run_pipeline()
