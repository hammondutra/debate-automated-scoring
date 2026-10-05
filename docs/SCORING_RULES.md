# Scoring rules and assumptions

The project separates format-specific rules from the general ingestion/export pipeline. This document makes the implemented assumptions explicit so tournament organizers can audit them before use.

## TBDEM / World Schools-style preset

The TBDEM preset is designed around the ranking workflow used for the Brazilian national high-school tournament and World Schools-style ballots.

### Adjudicator aggregation

Each adjudicator evaluation is stored as a separate row. Scores for the **same speech slot** are averaged across adjudicators before any team or speaker calculations.

A speech is uniquely identified by:

- round;
- match;
- team;
- debater;
- speech type;
- speaker position.

Including `speaker_position` is important because it preserves double-speech/iron-person cases.

### Team result

For each team in a debate:

```text
team score = sum of adjudicator-averaged speech scores
```

The team with the higher team score receives one win. The historical TBDEM preset allows an exact numerical tie and divides the win equally; the stricter `wsdc` CLI preset rejects tied team totals so the result can be corrected before continuing.

Team standings are sorted by:

1. wins;
2. average team score;
3. lower standard deviation of round team scores.

### Speaker rankings

Substantive speeches and reply speeches are ranked separately so that half-scale reply marks are not mixed into the main speaker average.

The main speaker table reports:

- number of substantive speeches;
- number of rounds appeared;
- average score;
- total score;
- score standard deviation;
- number of rounds in which the speaker delivered multiple substantive speeches;
- award eligibility.

The TBDEM preset uses a minimum of three round appearances for speaker-award eligibility.

### WSDC scoring reference

World Schools judging materials describe substantive marks on a 60–80 scale with an average of 70 and state that reply-speech scores are halved. The current implementation uses those values as validation warnings rather than hard limits so local tournaments can preserve their own authorized scales.

The same judging material states that the higher total team score must correspond to the winning team and that competitive WSDC decisions are not tied. This is why the strict `wsdc` preset rejects an exact team-score tie.

Source:

- World Schools Debating Championships, resources: https://www.wsdcdebating.org/services-4
- WSDC judging material: https://www.wsdcdebating.org/_files/ugd/669183_e826f0d7b5654cc887dee95756efb377.pdf

## British Parliamentary / WUDC preset

The BP implementation expects a finalized panel ballot.

Each room must contain:

- four distinct teams;
- exactly one placement each: 1st, 2nd, 3rd, 4th;
- speaker scores for the speakers on each team.

Team points are assigned as:

| Placement | Team points |
|---:|---:|
| 1st | 3 |
| 2nd | 2 |
| 3rd | 1 |
| 4th | 0 |

Tournament team standings are sorted by total team points and then total speaker points.

The engine also verifies that combined speaker points are compatible with the room ranking: the 1st-place team's combined speaker points must exceed the 2nd-place team's, and so on.

WUDC's current manual describes team points as 3/2/1/0, uses individual speaker marks out of 100, and requires the combined speaker scores of teams to be compatible with the finalized ranking. The current manual page identifies itself as the authoritative rules source for BP debating at WUDC.

Source:

- World Universities Debating Council, WUDC Manual: https://www.worlddebating.org/wudc-manual

## What the project does not automate

The tool does not decide who *ought* to win a debate from speech content. It computes rankings from adjudicators' finalized evaluations. It also does not currently handle pairings, judge allocation, motion release, registration, break generation, or elimination brackets.

Those boundaries keep the project focused on a transparent, testable scoring pipeline rather than duplicating a full tournament-management system.
