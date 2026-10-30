# Nifty IT Membership Candidate: Source Review

**Review date:** 2026-10-30  
**Status:** Quarantined; not approved for modelling  
**Candidate file:** `data/external/reference/unverified/nifty_it_constituent_snapshots_user_supplied_2001_2025.csv`

## Decision

The supplied entry/exit narrative has been converted to the requested two-column `date,tickers` snapshot format, but it must not yet populate `data/external/manual/cross_market/nifty_it_membership.csv`. The supplied text does not provide a row-level source for each snapshot and contains contradictions with official records and public listing histories. Using it as point-in-time truth would create an unmeasured survivorship and classification risk.

The candidate is therefore retained only as a research lead. It is not an input to acquisition, feature generation, model selection, or backtesting.

## Material findings

| Candidate item | Review result | Required resolution |
|---|---|---|
| `2001-01-01` contains `TCS` | Invalid as written: TCS was not listed in 2001; its IPO/listing occurred in 2004. | Obtain an official constituent snapshot effective in 2001. |
| `2001-01-01` and `2004-08-25` contain `MINDTREE` | Invalid as written: Mindtree was not publicly listed during those dates. | Replace only from an official historical constituent file or dated factsheet. |
| 2004 and 2005 snapshots contain 21 symbols | Inconsistent with the stated 20-member architecture. | Identify the actual exit paired with each addition. |
| `2015-05-29` contains `HEXAWARE` | Contradicted by the official IISL release dated 2015-04-20, which explicitly excludes Hexaware effective 2015-05-29. | Reconstruct the full post-change ten-member snapshot from dated primary evidence. |
| `2020-09-25` is described as a Nifty IT change | The official 2020-08-20 semi-annual review states that no change was made to Nifty IT for the 2020-09-25 implementation. | Establish whether the proposed snapshot reflects an earlier event, a later corporate action, or an inaccurate reconstruction. |
| `2021-09-30` | The effective boundary is supported by the official 2021 review. The supplied constituent set still requires a complete dated snapshot or a validated prior state plus the official additions/exclusions. | Retain 2021-09-30 as the effective date only after the full state is reconciled. |
| `2022-11-21` | The LTI/Mindtree merger is real, but the supplied date and entire ten-name state need an index-specific primary source. Corporate records show the scheme effective 2022-11-14 and the company name change effective 2022-11-15. | Obtain the NSE Indices corporate-action notice specifying index treatment and its effective trading boundary. |
| `2025-03-28` | Supported: the official NSE Indices release excludes LTTS and includes OFSS, effective from 2025-03-28 (close of 2025-03-27). | Reconcile the other nine names against a dated official factsheet or constituent file. |
| “No changes in 2026” | Not evidenced by the supplied text. | Verify both 2026 semi-annual reviews before asserting no change. |

## Primary evidence located

1. **NSE Indices, 20 April 2015 — Change in CNX IT Index effective 29 May 2015.** The release reduces the index from 20 to 10 and names ten exclusions, including Hexaware, MphasiS, NIIT Technologies, Persistent Systems, and Tata Elxsi.  
   <https://niftyindices.com/Press_Release/ind_prs20042015.pdf>
2. **NSE Indices, 20 August 2020 — Revision in criteria and replacements in indices.** The release states that no change is made to Nifty IT for the 25 September 2020 implementation.  
   <https://niftyindices.com/Press_Release/ind_prs20082020.pdf>
3. **NSE Indices, 15 September 2021 — Replacements in indices and revision in criteria.** Changes become effective from 30 September 2021, after the close on 29 September.  
   <https://niftyindices.com/Press_Release/ind_prs15092021.pdf>
4. **NSE corporate filing, 15 November 2022 — LTI name changed to LTIMindtree.** This establishes the corporate-name event, not by itself the complete Nifty IT membership state.  
   <https://nsearchives.nseindia.com/corporate/LTI_15112022175430_Intimationofchangeofname.pdf>
5. **NSE Indices, 21 February 2025 — Semi-annual index review.** Nifty IT excludes LTTS and includes OFSS, effective from 28 March 2025.  
   <https://www.niftyindices.com/Press_Release/ind_prs21022025.pdf>
6. **Official current Nifty IT constituent file.** The local copy validates the current ten symbols but cannot establish historical membership.  
   `data/external/reference/current_constituents/ind_niftyitlist.csv`

## Acceptance contract for modelling

The production file must contain one interval per security and use `valid_from` inclusive / `valid_to` exclusive boundaries:

```text
symbol,yahoo_symbol,valid_from,valid_to,announced_at,source_url
```

It may be released from quarantine only when all of the following hold:

1. Every state transition has a primary, dated source URL.
2. Every snapshot has the expected constituent count.
3. Each addition and deletion reconciles exactly with the prior snapshot.
4. Listing dates, mergers, delistings, renames, and Yahoo symbol mappings are temporally valid.
5. The announcement timestamp is retained separately from the effective date.
6. The final state reconciles with the official current constituent file.
7. The audit explicitly identifies any period for which the evidence is incomplete.

## Safe next step

Acquire official historical constituent files or dated Nifty IT factsheets. If only press releases are available, reconstruct the history from one verified baseline by applying each official change sequentially. Do not infer historical Nifty IT membership by filtering today's Nifty IT list, Nifty 50 history, or Nifty 500 history.
