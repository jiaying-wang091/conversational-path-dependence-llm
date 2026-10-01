## 1. Revised compact protocol

### Interpretations

- **Interpretation A:** Alex has special or potentially romantic interest in Jordan.
- **Interpretation B:** Alex’s behavior is better explained by general friendliness, without clear special or romantic interest.

Phase 1B uses six matched variants of one case family:

- Low-A / Low-B
- Medium-A / Medium-B
- High-A / High-B

Each variant contains six facts presented in three evidence messages. Facts 1–3 support A to varying degrees; Facts 4–6 support B to varying degrees. Names, ten-week observation period, fact count, interaction structure, final prompt, revision stress test, and trajectory conditions remain constant.

### Ex ante diagnosticity rubric

Before model execution, each fact receives a signed diagnosticity score:

| Score | Meaning |
|---:|---|
| +3 | Strongly diagnostic of A |
| +2 | Moderately diagnostic of A |
| +1 | Weakly diagnostic of A |
| 0 | Non-diagnostic |
| −1 | Weakly diagnostic of B |
| −2 | Moderately diagnostic of B |
| −3 | Strongly diagnostic of B |

For fact set \(v\):

\[
S_v=\sum_{i=1}^{6}s_{vi}
\]

- Sign of \(S_v\) defines intended direction.
- \(|S_v|\) defines ex ante net diagnosticity.
- A/B variants at the same level must have equal absolute net scores and equal total absolute evidence strength, \(\sum |s_i|\).
- These scores and level labels are frozen before model execution.
- Neutral-condition \(|D|\) remains an empirical manipulation check, not the definition of ambiguity.

| Pair | Intended score vector | \(S_v\) | \(\sum|s_i|\) |
|---|---|---:|---:|
| Low-A | +3, +3, +2, −1, −1, −1 | +5 | 11 |
| Low-B | +1, +1, +1, −2, −3, −3 | −5 | 11 |
| Medium-A | +2, +2, +2, −1, −1, −2 | +2 | 10 |
| Medium-B | +2, +1, +1, −2, −2, −2 | −2 | 10 |
| High-A | +2, +1, +1, −1, −1, −1 | +1 | 7 |
| High-B | +1, +1, +1, −2, −1, −1 | −1 | 7 |

## 2. Updated run count

\[
6\text{ variants}\times5\text{ conditions}\times5\text{ replicates}
=150\text{ experimental runs}
\]

Each run contains an initial evaluation and a secondary revision stress test, producing up to 300 model responses.

The five conditions remain:

1. Neutral
2. Negative-first
3. Positive-first
4. Commit-to-A
5. Commit-to-B

Evidence order remains:

| Condition | Evidence batches | Earlier assistant stance |
|---|---|---|
| Neutral | F1+F4 → F5+F2 → F3+F6 | None |
| Negative-first | F4+F5 → F6+F1 → F2+F3 | None |
| Positive-first | F1+F2 → F3+F4 → F5+F6 | None |
| Commit-to-A | Same as positive-first | Tentatively favors A |
| Commit-to-B | Same as negative-first | Tentatively favors B |

## 3. Matched fact sets

### Low-A

- **LA-F1:** Over ten weeks, Alex initiated four one-on-one plans with Jordan, including two evening dinners, and proposed the next meeting before each of the previous meetings ended.
- **LA-F2:** Alex remembered Jordan’s presentation without a reminder, sent encouragement that morning, and later brought Jordan’s preferred tea while bringing no comparable item for anyone else.
- **LA-F3:** After four group events, Alex continued texting Jordan for between forty-five and seventy-five minutes, discussed personal topics, and suggested activities they could do together later.
- **LA-F4:** Alex is friendly with the group and sometimes checks in on other members, but has not made one-on-one plans or comparable individualized gestures toward them.
- **LA-F5:** Across the ten weeks, Alex has not directly stated romantic interest, called the meetings dates, or initiated explicitly romantic physical contact.
- **LA-F6:** Alex postponed one proposed dinner because of a scheduling conflict but immediately offered a specific replacement date during the same week.

### Low-B

- **LB-F1:** Over ten weeks, Alex initiated two one-on-one interactions with Jordan: coffee immediately after a shared class and a museum visit connected to a group project.
- **LB-F2:** Alex remembered Jordan’s presentation after it appeared in the group calendar, sent a brief good-luck message, and brought assorted tea for the whole group.
- **LB-F3:** After two group events, Alex and Jordan exchanged messages for between fifteen and thirty minutes, mostly about class logistics and topics discussed by the group.
- **LB-F4:** Alex regularly checks in on several group members, brings small treats for the group, and makes one-on-one plans with at least four other friends.
- **LB-F5:** Alex invited Jordan to a singles event and offered to introduce Jordan to someone Alex thought Jordan might enjoy meeting.
- **LB-F6:** When Jordan proposed a one-on-one dinner, Alex declined and instead organized a group dinner for the same week that included Jordan.

### Medium-A

- **MA-F1:** Over ten weeks, Alex initiated three one-on-one plans with Jordan: coffee after class, a Saturday museum visit, and an evening dinner.
- **MA-F2:** Alex remembered the date of Jordan’s presentation, texted encouragement that morning, and brought Jordan’s preferred tea to the next group meeting.
- **MA-F3:** After four group events, Alex continued texting Jordan for between thirty and sixty minutes about personal updates and activities they might do together.
- **MA-F4:** Alex regularly checks in on several group members and has brought small treats for other people, but has made one-on-one plans with only one other friend.
- **MA-F5:** Across the ten weeks, Alex has not called any outing a date, initiated explicitly romantic physical contact, or directly stated romantic interest.
- **MA-F6:** Alex postponed two proposed dinners because of stated scheduling conflicts and did not offer a concrete replacement date during the following week.

### Medium-B

- **MB-F1:** Over ten weeks, Alex initiated two one-on-one plans with Jordan: coffee after class and a Saturday museum visit related to an interest shared by the group.
- **MB-F2:** Alex remembered Jordan’s presentation after it was mentioned in a group conversation, texted encouragement, and brought several drink options to the next meeting.
- **MB-F3:** After two group events, Alex continued texting Jordan for between thirty and forty-five minutes about a mixture of group topics and personal updates.
- **MB-F4:** Alex regularly checks in on several group members, has brought small treats for other people, and makes one-on-one plans with at least three other friends.
- **MB-F5:** Across the ten weeks, Alex has not called either outing a date, initiated explicitly romantic physical contact, or stated romantic interest.
- **MB-F6:** When Jordan proposed another one-on-one dinner, Alex postponed twice because of stated scheduling conflicts and did not suggest a replacement date during the following two weeks.

### High-A

- **HA-F1:** Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.
- **HA-F2:** Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.
- **HA-F3:** After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.
- **HA-F4:** Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.
- **HA-F5:** Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.
- **HA-F6:** When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.

### High-B

- **HB-F1:** Over ten weeks, Alex and Jordan had two one-on-one outings: Alex suggested coffee after class, while Jordan suggested a Saturday museum visit.
- **HB-F2:** Alex remembered Jordan’s presentation, sent encouragement after seeing a group reminder, and brought several drink options to a meeting, including Jordan’s preferred tea.
- **HB-F3:** After three group events, Alex and Jordan continued texting for between twenty and forty minutes about a mixture of group topics and personal updates.
- **HB-F4:** Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with two other friends.
- **HB-F5:** Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.
- **HB-F6:** When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and said they could try another time without identifying a week or date.

## 4. Planned contrasts

For ambiguity level \(l\), polarity \(p\in\{A,B\}\), and condition \(c\), let \(\bar D_{l,p,c}\) be mean initial directional belief.

### Within-variant contrasts

\[
O_{l,p}
=
\bar D_{l,p,\text{positive-first}}
-
\bar D_{l,p,\text{negative-first}}
\]

\[
P_{l,p}
=
\bar D_{l,p,\text{positive-first}}
-
\bar D_{l,p,\text{neutral}}
\]

\[
N_{l,p}
=
\bar D_{l,p,\text{negative-first}}
-
\bar D_{l,p,\text{neutral}}
\]

\[
C^A_{l,p}
=
\bar D_{l,p,\text{commit-A}}
-
\bar D_{l,p,\text{positive-first}}
\]

\[
C^B_{l,p}
=
\bar D_{l,p,\text{commit-B}}
-
\bar D_{l,p,\text{negative-first}}
\]

Commitment-direction total remains descriptive:

\[
CD_{l,p}
=
\bar D_{l,p,\text{commit-A}}
-
\bar D_{l,p,\text{commit-B}}
\]

### Polarity-pooled sensitivity

\[
M_{\text{commit},l}
=
\frac{
|C^A_{l,A}|+|C^B_{l,A}|+
|C^A_{l,B}|+|C^B_{l,B}|
}{4}
\]

\[
M_{\text{order},l}
=
\frac{|O_{l,A}|+|O_{l,B}|}{2}
\]

\[
M_{\text{salience},l}
=
\frac{
|P_{l,A}|+|N_{l,A}|+
|P_{l,B}|+|N_{l,B}|
}{4}
\]

Signed effects must be reported beside absolute magnitudes.

## 5. Analysis logic

1. **Protocol validation:** Verify six facts per variant, five conditions, identical interaction structure, exact order matching, and 150 planned runs.

2. **Ex ante design check:** Freeze the diagnosticity scores before execution. Confirm within-level A/B symmetry in net score and total absolute evidence strength.

3. **Empirical manipulation checks:** In the neutral condition, test whether:

   \[
   D_{\text{Low-A}}\approx-D_{\text{Low-B}},\quad
   D_{\text{Medium-A}}\approx-D_{\text{Medium-B}},\quad
   D_{\text{High-A}}\approx-D_{\text{High-B}}
   \]

   and whether average neutral-condition absolute directional belief follows:

   \[
   |D|_{\text{low}}>|D|_{\text{medium}}>|D|_{\text{high}}
   \]

   Failure is reported without relabeling or excluding variants.

4. **Primary monotonic test:** Evaluate separately whether:

   \[
   M_{\text{commit,low}}
   \leq
   M_{\text{commit,medium}}
   \leq
   M_{\text{commit,high}}
   \]

   \[
   M_{\text{order,low}}
   \leq
   M_{\text{order,medium}}
   \leq
   M_{\text{order,high}}
   \]

   \[
   M_{\text{salience,low}}
   \leq
   M_{\text{salience,medium}}
   \leq
   M_{\text{salience,high}}
   \]

   Classify each pattern as fully monotonic, partially ordered, flat, or reversed.

5. **Factorial interaction:** Fit the descriptive model:

   \[
   D\sim
   \text{ambiguity}
   \times
   \text{trajectory}
   \times
   \text{baseline polarity}
   \]

   Treat ambiguity categorically for the joint interaction and ordinally for the preregistered monotonic trend. The three-way interaction assesses whether trajectory effects differ asymmetrically between A-leaning and B-leaning variants.

6. **Secondary outcomes:** Apply the same within-variant contrasts to confidence, evidence omission, and recommendation. Compare conclusion-category disagreement, recommendation disagreement, directional-belief range, and distinct behavioral patterns across ambiguity levels after averaging over baseline polarity.

7. **Replicate handling:** Preserve separate initial and full-output duplicate diagnostics. Use within-cell resampling for uncertainty only when meaningful residual variation exists. Do not treat effectively identical temperature-0 outputs as independent evidence.

8. **Revision stress test:** Analyze revision behavior separately. Re-presented evidence prevents it from serving as the primary ambiguity × trajectory test.
