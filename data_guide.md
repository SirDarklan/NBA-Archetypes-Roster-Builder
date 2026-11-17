# Guide to the NBA Data and Statistics

This guide explains the feature definitions for each CSV. Additional definitions can be found at the [official NBA Stats glossary](https://www.nba.com/stats/help/glossary).


## Generic Statistics

These columns show up in multiple tables and are either metadata such as player and team identifiers. 

| Column | Definition |
|---|---|
| `PLAYER_ID`, `PLAYER_NAME`, `NICKNAME` | Player identifiers and display names. The ID is the reliable key when joining files. |
| `TEAM_ID`, `TEAM_ABBREVIATION` | Team identifier and short team name. |
| `AGE` | Player's age as reported for the season. |
| `GP` | Games played. |
| `W`, `L`, `W_PCT` | Team wins, losses, and win percentage in the games represented by that row. |
| `MIN` | Total minutes played. |
| `SEASON` | Season label, such as `2024-25`. |
| `TEAM_COUNT` | Number of teams represented in the player's season record, useful when the player changed teams during the season. |

## `player_totals.csv`: standard player box-score statistics

Each row contains a player's season totals

### Shooting and scoring

| Column | Definition |
|---|---|
| `FGM`, `FGA`, `FG_PCT` | Field goals made, attempted, and the share of attempts made. Field goals include both two-point and three-point shots. |
| `FG3M`, `FG3A`, `FG3_PCT` | Three-point shots made, attempted, and the share made. |
| `FTM`, `FTA`, `FT_PCT` | Free throws made, attempted, and the share made. |
| `PTS` | Points scored. A made two-pointer is worth 2 points; a made three-pointer is worth 3; a free throw is worth 1. |

### Rebounding, passing, and defense

| Column | Definition |
|---|---|
| `OREB` | Offensive rebounds: rebounds recovered by the player's team after its own missed shot. |
| `DREB` | Defensive rebounds: rebounds recovered after the opponent misses. |
| `REB` | Total rebounds: offensive plus defensive rebounds. |
| `AST` | Assists: passes that directly lead to a teammate's made basket. |
| `TOV` | Turnovers: times the player loses the ball to the other team. |
| `STL` | Steals: times the player takes the ball from the opponen, causing a turnover. |
| `BLK` | Blocks: shots the player blocks an opponent while shooting. |
| `BLKA` | Blocks against: the player's shots that are blocked by an opponent. |
| `PF` | Personal fouls committed by the player. |
| `PFD` | Personal fouls drawn by the player from opponents. |
| `PLUS_MINUS` | Team point difference while the player is on the court. This depends on teammates and opponents too; it is not an individual score. |

### Extra fields 

The file also includes fantasy and milestone statistics: `NBA_FANTASY_PTS`, `WNBA_FANTASY_PTS`, and `FP_HIGH_SCORE` are fantasy-points summaries; `DD2` counts double-doubles (10 or more in two statistical categories in a game); `TD3` counts triple-doubles (10 or more in three categories in a game).

Many of the main counting, percentage, win/loss, and fantasy fields have matching columns ending in `_RANK` (for example, `PTS_RANK`). These are league comparison ranks for the corresponding value. Rank direction and eligibility follow the source table, so use the original statistic when interpreting player performance.

## `team_stats.csv`: the same kind of box score at team level

This file has one team-season summaries. It contains the team versions of games, wins and losses, minutes, field goals, three-pointers, free throws, rebounds, assists, turnovers, steals, blocks, blocks against, fouls, points, and plus-minus, with ranks for the reported stats. For example, `FGM` is the team's made field goals and `PTS` is the team's points. 

## Player directory and profile files

### `player_index.csv`: player directory and biography

This is mainly identity and biography information which includes: player name and ID, team name and city, position, height, weight, college, country, draft year/round/number, roster status, and the years the player was active (`FROM_YEAR`, `TO_YEAR`). It also has `PTS`, `REB`, and `AST` summary fields with `STATS_TIMEFRAME` and `SEASON` indicating the context for those summaries.

### `player_stats.csv`: biography plus a compact season-stat summary

This file contains similar biographical information to `play_index.csv` such as team, age, height, weight, college, country, and draft details. It additionally includes games played (`GP`), points (`PTS`), rebounds (`REB`), assists (`AST`), and selected advanced statistics: net rating (`NET_RATING`), offensive and defensive rebound percentages (`OREB_PCT`, `DREB_PCT`), usage percentage (`USG_PCT`), true shooting percentage (`TS_PCT`), and assist percentage (`AST_PCT`). 

## `player_scoring.csv`: detailed statistics for player's shots and source of points

The file includes player/team identity and context (`AGE`, `GP`, `W`, `L`, `W_PCT`, `MIN`, and `SEASON`), plus these statistics:

| Columns | Definition |
|---|---|
| `PCT_FGA_2PT`, `PCT_FGA_3PT` | Share of the player's field-goal attempts that are two-pointers or three-pointers. |
| `PCT_PTS_2PT`, `PCT_PTS_2PT_MR`, `PCT_PTS_3PT` | Share of the player's points coming from two-point shots, mid-range two-point shots, or three-pointers. |
| `PCT_PTS_FB`, `PCT_PTS_FT`, `PCT_PTS_OFF_TOV`, `PCT_PTS_PAINT` | Share of points coming in transition/fast breaks, from free throws, after turnovers, or in the paint. These are scoring contexts and may overlap in how plays are classified. |
| `PCT_AST_2PM`, `PCT_UAST_2PM` | Share of made two-point field goals that were assisted or unassisted. |
| `PCT_AST_3PM`, `PCT_UAST_3PM` | Share of made three-point field goals that were assisted or unassisted. |
| `PCT_AST_FGM`, `PCT_UAST_FGM` | Share of all made field goals that were assisted or unassisted. |
| `FGM`, `FGA`, `FG_PCT` | Field goals made, attempted, and the share made. |

The file includes a corresponding `_RANK` field for each reported scoring statistic. The ranks compare players in the source's season group.

## `player_advanced.csv`: possession, efficiency, and role statistics

This file includes advanced metrics to describe performance. These measures are more specialized than the standard box score.

### Ratings

| Columns | Definition |
|---|---|
| `OFF_RATING`, `E_OFF_RATING`, `sp_work_OFF_RATING` | Offensive-rating values: points produced per 100 possessions while the player is on court. `E_` is an estimated variant; `sp_work_` is an additional source-provided field. |
| `DEF_RATING`, `E_DEF_RATING`, `sp_work_DEF_RATING` | Defensive-rating values: points allowed per 100 opponent possessions while the player is on court. Lower is generally better, but the value reflects the team context too. |
| `NET_RATING`, `E_NET_RATING`, `sp_work_NET_RATING` | Offensive rating minus defensive rating, with estimated and additional source-provided variants. |
| `PIE` | Player Impact Estimate, a box-score summary comparing a player's recorded contributions with the game totals. |

### Passing, rebounding, and turnovers

| Columns | Definition |
|---|---|
| `AST_PCT` | Share of teammate field goals made while the player is on court that the player assisted. |
| `AST_TO` | Assists divided by turnovers. |
| `AST_RATIO` | Assists per 100 possessions used by the player. |
| `OREB_PCT`, `DREB_PCT`, `REB_PCT` | Estimated share of available offensive, defensive, or total rebounds collected while the player is on court. |
| `TM_TOV_PCT` | Team turnover percentage while the player is on court. |
| `E_TOV_PCT` | Estimated player turnover percentage. |

### Shooting and usage

| Columns | Definition |
|---|---|
| `EFG_PCT` | Effective field-goal percentage; adjusts field-goal percentage to reflect that three-pointers are worth more than two-pointers. |
| `TS_PCT` | True shooting percentage; accounts for field goals, three-pointers, and free throws to summarize scoring efficiency. |
| `USG_PCT`, `E_USG_PCT` | Usage percentage and an estimated variant: the share of team plays a player finishes while on court. These describe offensive involvement. |
| `FGM`, `FGA`, `FG_PCT` | Field goals made, attempted, and the share made. |
| `FGM_PG`, `FGA_PG` | Field goals made and attempted per game. |

### Pace and playing time

| Columns | Definition |
|---|---|
| `PACE`, `E_PACE`, `sp_work_PACE` | Pace estimates: possessions per 48 minutes, with estimated and additional source-provided variants. |
| `PACE_PER40` | Pace expressed per 40 minutes rather than per 48. |
| `POSS` | Estimated number of possessions played. |

This file includes `_RANK` fields for its reported statistics. 

## `defend_rim.csv`: shots defended close to the basket

These rows describe shots opponents took when a player was defending near the rim. The six-foot cutoff is represented by the `_LT_06` suffix.

| Column | Definition |
|---|---|
| `CLOSE_DEF_PERSON_ID` | ID of the player credited as the closest defender. |
| `PLAYER_NAME` | Defender's name. |
| `PLAYER_LAST_TEAM_ID`, `PLAYER_LAST_TEAM_ABBREVIATION` | The player's last team in the season data; this may not identify the team for every split-team row. |
| `PLAYER_POSITION`, `AGE` | Position and age reported by the source. |
| `GP`, `G` | Source game-count. |
| `FREQ` | Frequency of the rim-defense category in the source's defended-shot context. |
| `FGM_LT_06`, `FGA_LT_06` | Opponent field goals made and attempted within six feet while the player defended the shot. |
| `LT_06_PCT` | Opponents' make percentage on those defended attempts: makes divided by attempts. |
| `NS_LT_06_PCT` | Normal/comparison shooting percentage for the shooters on those attempts. |
| `PLUSMINUS` | Difference between the defended make percentage and the comparison percentage. A negative value means opponents made a smaller share than their comparison rate. |

## `hustle.csv`: effort and activity statistics

Hustle statistics record actions such as contests, deflections, screens, loose-ball recoveries, and box-outs. They are counts unless their name begins with `PCT_`.

| Column | Definition |
|---|---|
| `CONTESTED_SHOTS` | Shots the player contested by closing out or raising a hand before release. |
| `CONTESTED_SHOTS_2PT`, `CONTESTED_SHOTS_3PT` | Contested two-point and three-point attempts. |
| `DEFLECTIONS` | Times the defender got a hand on a live ball on a non-shot attempt. |
| `CHARGES_DRAWN` | Charges (charging fouls) the player drew as a defender. |
| `SCREEN_ASSISTS` | Screens set for a teammate that directly led to a made field goal. |
| `SCREEN_AST_PTS` | Points scored on baskets credited as the player's screen assists. |
| `OFF_LOOSE_BALLS_RECOVERED`, `DEF_LOOSE_BALLS_RECOVERED`, `LOOSE_BALLS_RECOVERED` | Loose balls recovered on offense, on defense, and in total. A recovery means gaining sole possession of a live ball not controlled by either team. |
| `PCT_LOOSE_BALLS_RECOVERED_OFF`, `PCT_LOOSE_BALLS_RECOVERED_DEF` | Shares of the player's loose-ball recoveries made on offense or defense. |
| `OFF_BOXOUTS`, `DEF_BOXOUTS`, `BOX_OUTS` | Box-outs made on offense, on defense, and in total. A box-out is an action that prevents an opponent from securing a rebound. |
| `BOX_OUT_PLAYER_TEAM_REBS` | Rebounds secured by the player's team after the player's box-out. |
| `BOX_OUT_PLAYER_REBS` | Rebounds secured by the player after their own box-out. |
| `PCT_BOX_OUTS_OFF`, `PCT_BOX_OUTS_DEF` | Share of the player's box-outs made on offense or defense. |
| `PCT_BOX_OUTS_TEAM_REB` | Share of the player's box-outs that ended in a team rebound. |
| `PCT_BOX_OUTS_REB` | Share of the player's box-outs that ended in a rebound by the player. |

## `shot_zones.csv`: shooting locations by broad court area

Each zone has three measurements: `FGM` (shots made), `FGA` (shots attempted), and `FG_PCT` (share of attempts made). The zones are:

| Zone columns | Definition |
|---|---|
| `Restricted Area` | At the basket, in the small area immediately around the rim. |
| `In The Paint (Non-RA)` | Inside the painted lane, but outside the restricted area. |
| `Mid-Range` | Two-point shots outside the paint. |
| `Left Corner 3`, `Right Corner 3` | Three-pointers taken from the left or right corner. |
| `Corner 3` | Combined left and right corner-three total. This overlaps the two separate corner columns. |
| `Above the Break 3` | Three-pointers taken outside the corners, around the arc. |
| `Backcourt` | Very long shots taken from the backcourt. |


## `game_logs.csv`: player performance in each game

This file has one row per player-game. It includes the game date, opponent/matchup, game result, minutes, the same standard shooting, rebounding, passing, turnover, defensive, and scoring statistics explained for `player_totals.csv`, plus fantasy fields and rankings. 

## Standardization

To compare efficiency across players, per game stats such as points, rebound, and assists can be converted into per minute statistics. We will use per 36 minutes as this is the standard time a starter plays in a 48 minute NBA game.

To compare play styles, we can take PCT statistics relative to their team or for types of shots, we can convert shots into shot share over the total number of shots taken. 


