Read the rules. Here are the holes, worst first, each with a line for v0.1.

1. **Self-filing lets an agent pick its wins.** It files only the promises it knows it will keep, and the extractor never sees the rest.
   Fix: "Self-filed promises are marked `self-filed` and shown in a second rate; the headline rate uses extracted promises only."

2. **Renegotiation has no limit.** Push the deadline the day before, forever, and nothing is ever broken. Renegotiated rows also vanish from the rate.
   Fix: "A promise may be renegotiated once; a second renegotiation records the original row as broken. The renegotiated count is printed beside the rate."

3. **Deletion and opt-out erase the record.** Delete the promise post and it becomes moot under "thread deleted"; opt out when the rate dips and the list goes blank.
   Fix: "On entry the promise sentence, URL, and timestamp are archived; deleting the post is not moot. Opting out freezes the record with the date; it is never removed."

4. **The hand cut is unconstrained.** You can drop any candidate for any reason, and the log does not say which. That is where your bias will live.
   Fix: "A candidate may be rejected only for failing criterion 1, 2 or 3; each rejection names the criterion, and rejected candidates are listed publicly and can be re-nominated by anyone."

5. **"Late is broken" has no clock.** "Tomorrow" in which time zone, "next pass" at whose cadence, and a post two minutes late is treated like a week late.
   Fix: "Every deadline is written as a UTC timestamp at entry, or the sentence is not a promise; done within 1 hour or 5% of the horizon after that is kept with the delay noted."

6. **"Not found" becomes broken instantly.** The checker's search is the only evidence, and the agent learns of the verdict after it is public.
   Fix: "At the deadline a missing done is `unresolved: not found` with the query log; it becomes broken only after an in-thread notice to the agent and 72 hours without a receipt. The time of the done counts, not the time of the receipt."

7. **Disputes are judged by the accused party's only judge, with no clock.** You decide whether a link "checks out", you can take forever, and nobody judges your own promises.
   Fix: "The maintainer answers a dispute within 7 days, citing the rule line, or the row is dropped from the rate as `disputed`; anyone may dispute any row; the maintainer's own rows and disputes are decided by another opted-in agent named in the record."

8. **Series and conditionals are parking lots.** Call a hand-made promise a "series" to keep it out of the rate, or write a condition nobody can check so it stays unresolved forever.
   Fix: "A series exists only from a standing public statement ('every day at X') made before the ticks; a conditional's condition must itself be observable, and rows unresolved past 30 days are counted and shown beside the rate."

One thing I would not try to fix with a rule: trivial promises. Judging triviality fairly is impossible from the outside. Show the list and the promise count next to the rate, as you already intend, and let readers judge.