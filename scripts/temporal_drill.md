# Temporal kill drill (evidence for Best Use of Temporal)

1. `temporal server start-dev --db-filename .temporal.db`
2. `python -m manual_labor remind worker` (terminal A)
3. Schedule a test task with `every_days` overridden to minutes (TODO: add a `--test-minutes` flag).
4. While the workflow sleeps: `kill -9` the worker. Wait past the timer. Start the worker again.
5. Expect: the notification fires once, right after the worker returns. Screenshot the Temporal UI history.
6. Time-skipping: `pytest tests/test_remind_timeskip.py` (TODO) with `WorkflowEnvironment.start_time_skipping()`
   runs 6 months of reminders in seconds. Save the output to `results/temporal_timeskip.txt`.
