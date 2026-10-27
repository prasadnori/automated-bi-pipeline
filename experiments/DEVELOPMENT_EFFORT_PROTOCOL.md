# Controlled comparison: development effort

## Purpose
Compare the effort required to implement the same rule in three approaches:
`no_of_employees >= 0`, with offending record IDs reported.

## Approaches
1. Proposed framework: `DataQualityProfiler` and its configurable numeric rule.
2. Plain pandas: direct mask and record-ID extraction.
3. Existing validation tool: Pandera schema/check.

## Fair procedure
- Use the same dataset, rule, expected output, Python version, and machine.
- Start each attempt from a clean copy of the starter project.
- Give each implementer the same written requirement and no implementation hints.
- Start timing when the requirement is opened; stop when the implementation passes the same acceptance tests.
- Record active implementation minutes, number of edits/runs, and whether the first attempt passes.
- Ideally have at least three implementers or repeat the task on separate days. One person's timings alone are anecdotal.
- Do not count package installation or environment troubleshooting as coding time; record those separately.
- Verify all three methods report exactly the same offending record IDs before comparing effort.

## Results table (fill with measured observations; do not estimate)
| Approach | Active minutes | Runs/edits | Passes acceptance test? | Notes |
|---|---:|---:|---|---|
| Proposed framework | TBD | TBD | TBD | |
| Plain pandas | TBD | TBD | TBD | |
| Pandera | TBD | TBD | TBD | |

Runtime from `compare_quality_check.py` is a separate measure and must not be presented as development effort.


## Validity warning for this current project

The current author has already seen the framework and comparison implementations during development. Therefore, a stopwatch timing by this same author now is **not** a blinded, controlled development-effort experiment. Do not present it as such. For a defensible comparison, recruit independent implementers who have not seen the implementations, or report a clearly labeled single-developer exploratory observation and its limitation. Never fill the table with estimated or reconstructed times.
