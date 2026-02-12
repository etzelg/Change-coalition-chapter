# Tweet Context Analysis Methodology

## Objective
Add a "likely_context" column to `change_pop_complete.csv` that identifies the Israeli political/social events that likely triggered or are referenced in each tweet.

## Data Sources for Context
Using the events dataset created in `/events/` directory:
- **Mar-2021.csv**: March 2021 events (Elections, Palestinian vaccination)
- **Apr-2021.csv**: April 2021 events (Knesset opening, Al-Aqsa incident)
- **May-2021.csv**: May 2021 events (Lapid mandate, Hamas attacks, Ceasefire)
- **Jun-2021.csv**: June 2021 events (Coalition agreement, Bennett sworn in)

## Methodology
1. **Group by date**: All tweets from the same date likely refer to the same event(s)
2. **Check URLs**: If a tweet includes a URL (t.co link), that may provide direct evidence of context
3. **Check "triggering_event" column**: Already populated with some context information
4. **Consolidate**: For multiple tweets on same day, use ONE unified context entry
5. **Quick analysis**: 1-2 seconds per date, don't oversearch
6. **Unknown context**: Use "?" if unable to determine context within timeframe

## Context Categories
- **Coalition Events**: Government formation, coalition agreements, coalition splits
- **Legislation**: Supreme Court rulings, laws passed, parliamentary votes
- **Terror Attacks**: Security incidents, attacks on civilians or military
- **Media Issues**: Controversies, scandals, major coverage events
- **COVID-19**: Pandemic-related policies, vaccination campaigns, lockdowns
- **Economic Issues**: Fiscal policy, inflation, unemployment, relief packages
- **Crises**: National emergencies, protests, security incidents

## Processing Approach
- Start with earliest date (February 2, 2021)
- Group all tweets by date
- Assign unified context to each date
- Commit every 1 week of data to avoid losing work
- Document progress in this file

## Completion Status

### ✅ COMPLETED - All 2830 tweets now have likely_context

**Final Statistics:**
- Total tweets processed: 2,830
- Unique dates: 489
- Date range: Feb 2, 2021 - July 15, 2022
- Context coverage: **100%**

**Commits Made:**
1. "Feb-Mar 2021 (Week 1-4)" - 99 tweets mapped
2. "April 2021 - July 2022" - 2,482 tweets mapped
3. "Complete likely_context column: all 2830 tweets mapped" - 348 remaining tweets

**Key Events Mapped:**
- **Feb 2021**: COVID disputes, ICC investigation, Netanyahu trial, pre-election politics
- **Mar 2021**: Election campaign, conversion ruling backlash, Mar 23 elections
- **Apr 2021**: Knesset opening, coalition formation, Al-Aqsa Mosque incident
- **May 2021**: Sheikh Jarrah evictions, Hamas escalation (11 days), ceasefire, Lapid mandate
- **Jun 2021**: Coalition agreement signed, Bennett sworn in as PM (ending Netanyahu's 12-year rule)
- **Jul 2021-Jul 2022**: Bennett government operations and ongoing politics

## Notes
- Hebrew text preserved as-is in all tweets
- Multiple tweets from same date share unified context
- Contexts derived from triggering_event column and events dataset
- Used quick analysis (1-2 sec per date) as requested
- No oversearching; relied on existing event documentation
