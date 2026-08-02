---
layout: post
title: "APY, Compounding, and What Your Savings Will Really Earn"
date: 2026-07-04 13:05:30 +0000
categories: [interest-rates]
description: "APY already includes compounding. Here is the formula, what daily versus monthly is really worth, and how to check what your accounts actually paid you."
tags: [interest-rates, apy, compound-interest, 2026]
redirect_from:
  - /2026/03/27/how-to-calculate-the-apy-for-high-yield-savings-accounts/
  - /2026/05/18/understanding-compounding-interest-on-high-yield-savings-a-comprehensive-guide/
  - /2026/06/27/what-you-should-know-about-compounding-interest-in-high-yield-accounts/
  - /2026/07/14/how-does-compounding-work-in-savings-accounts/
  - /2026/07/21/how-to-estimate-potential-earnings-from-different-savings-options/
  - /2026/07/09/how-to-easily-track-interest-earnings-across-different-savings-options/
---

![A savings balance rising in monthly steps as each interest payment starts earning interest of its own](/assets/pin-images/2026-07-04-understanding-apy-what-it-means-for-your-savings-strategy.png)

> **Short answer:** APY is the interest rate with compounding already folded in, which makes it the only number that compares two deposit accounts fairly. Balance × APY gives you a usable one-year estimate. Everything below is about the places that shortcut breaks — contributions, promo windows, mid-month deposits, fees, and tax — and how to verify what the bank actually paid you.

Two accounts can advertise the same interest rate and pay different amounts. Two accounts can advertise different rates and pay nearly the same amount. The number that settles it is APY, and once you know how it is built you can stop guessing and start checking.

## APY vs Interest Rate: One Formula, One Difference

A bank can quote you two numbers about the same account. The **interest rate** (also called the nominal rate) is the annual rate applied to your balance before any compounding. The **annual percentage yield** is what you end up with after that interest is credited and starts earning interest itself.

The conversion is one line:

`APY = (1 + r/n)^n - 1`

where `r` is the nominal annual rate as a decimal and `n` is the number of compounding periods per year. Running it backwards works too, which is useful when a disclosure gives you APY and you want the underlying rate:

`r = n x ((1 + APY)^(1/n) - 1)`

This is not a convention the industry invented on its own. Truth in Savings — implemented as Regulation DD, [12 CFR Part 1030](https://www.consumerfinance.gov/rules-policy/regulations/1030/) — requires depository institutions to disclose the annual percentage yield and sets out how it is computed. That is why APY is the comparable number and the nominal rate is not. If a marketing page shows only "interest rate," the account disclosure will still carry the APY. Find it there before you decide.

## What Compounding Frequency Is Actually Worth

Compounding frequency gets more attention than it deserves. Here is the whole effect, using a single assumed nominal rate so the only thing changing is how often interest is applied.

Suppose the nominal rate is 4.00% and you deposit $10,000 for one year with no additions or withdrawals:

| Compounding | APY from the formula | Interest on $10,000 after one year |
|---|---|---|
| Annually | 4.0000% | $400.00 |
| Quarterly | 4.0604% | $406.04 |
| Monthly | 4.0742% | $407.42 |
| Daily (365) | 4.0808% | $408.08 |

The gap between the worst and best case is about $8 per $10,000 per year. The gap between monthly and daily is 66 cents. That is worth knowing, and it is not worth chasing. A quarter-point difference in the headline APY between two banks is worth roughly $25 on the same balance — thirty times the daily-versus-monthly difference.

The practical rule: compare APY to APY and let compounding frequency break ties, not decisions.

## How Banks Actually Credit Interest

Between the formula and your statement sit three mechanics that decide when money shows up.

**Accrual vs posting.** Interest usually accrues daily and posts once per statement cycle. A balance that earned interest all month shows no change until posting day. Closing an account mid-cycle can mean forfeiting accrued-but-unposted interest unless the disclosure says otherwise — check that clause before you move a large balance.

**Balance computation method.** Regulation DD permits the daily balance method (interest applied to each day's ending balance) or the average daily balance method (one average across the cycle). The institution has to tell you which it uses. For a stable balance the two land in the same place; for a balance that swings mid-cycle they do not.

**Which balance counts.** Deposits that have not cleared may sit in your available balance without being in your interest-bearing ledger balance yet. A transfer that lands on the last business day of a cycle may earn nothing that cycle.

None of this changes the annual math much. All of it changes whether the first month looks the way you expected.

## The Same $10,000 in Savings, a Money Market Account, and a CD

Deposit products differ less in mechanics than in what they demand from you in exchange for the rate. Put the same money in each and the comparison gets concrete. The APYs below are assumptions — substitute the ones you are actually being offered.

Suppose $10,000, held for one year:

| Where it sits | Assumed APY | Interest after one year | What you give up |
|---|---|---|---|
| High-yield savings | 4.00% | $400.00 | Rate can change any day |
| Money market account | 3.75% | $375.00 | Balance tiers, transaction limits, more fee exposure |
| 12-month CD | 4.25% | $425.00 | Access, until maturity or a penalty |

Across three very different products the spread is $50 on $10,000 — half a percent of the balance. That is the honest scale of the decision for most savers, and it is why liquidity and fee terms usually deserve more weight than the last few basis points.

Two structural differences matter more than the numbers above. A CD's APY is fixed for the term, so it is the only one of the three that cannot be cut out from under you. A money market account often prices in tiers, meaning the advertised APY may apply only above a balance threshold — the mechanics of that are covered in [what a money market account is and how it works](/2026/06/02/what-is-a-money-market-account-and-how-does-it-work/). Savings APYs are variable by design and can be repriced without notice.

For the current baseline on any of these, the FDIC publishes [national rates and rate caps](https://www.fdic.gov/national-rates-and-rate-caps) each month. Look it up before you compare offers so you know whether a quoted APY is genuinely above average or just above your current bank.

## Run Your Own Number

Enter your current balance, the APY from your bank's rate sheet, whatever you add each month, and the number of years you plan to leave it — the table shows what you put in versus what the interest added, year by year.

{% include tools/apy-calculator.html %}

## Adding Monthly Contributions Without Breaking the Math

Balance × APY works for a lump sum sitting still. It falls apart the moment you contribute, because each deposit earns for only part of the year.

The version that handles contributions:

`Ending balance = P x (1+m)^n + C x (((1+m)^n - 1) / m)`

where `m` is the monthly rate equivalent to your APY — `m = (1 + APY)^(1/12) - 1` — `n` is the number of months, `P` is the starting balance, and `C` is the monthly contribution.

Note what `m` is *not*: it is not the APY divided by twelve. Dividing by twelve double-counts compounding and overstates the result, because APY already contains it.

Suppose you start with $10,000 at 4.00% APY and add $200 at the end of every month for five years:

- Monthly equivalent rate: `(1.04)^(1/12) - 1 = 0.327%`
- Growth factor over 60 months: `(1.00327)^60 = 1.2167`
- Starting balance grows to `$10,000 x 1.2167 = $12,166.53`
- Contributions grow to `$200 x 66.179 = $13,235.81`
- Ending balance: **$25,402.34**

You paid in $22,000 of that. Interest supplied $3,402.34. The same $10,000 left alone for five years with no contributions would have reached $12,166.53 — interest of $2,166.53 against $2,000 of simple interest, so compounding itself contributed $166.53. Deposits, not compounding, do most of the work at these rates over this horizon.

## What the Estimate Leaves Out: Fees, Taxes, and Inflation

Three things sit between the calculator's output and your actual result.

**Fees behave like negative APY.** A $5 monthly maintenance fee is $60 a year. On a $10,000 balance that is 0.60 percentage points off your yield — larger than most rate differences you would switch banks over. On a $1,000 balance it is 6.00 points, which can take a high-yield account below zero. Where those charges hide and how to get them waived is covered in [the fees that quietly eat your savings interest](/2026/06/26/how-to-identify-and-avoid-common-fees-in-high-yield-options/).

**Interest is ordinary income.** After-tax yield is roughly `APY x (1 - your marginal rate)`. Assuming a combined marginal rate of 25%, a 4.00% APY nets about 3.00%. The IRS explains what has to be reported in [Topic 403, Interest Received](https://www.irs.gov/taxtopics/tc403); your actual bracket comes from your return, not from an estimate.

**Inflation decides whether you gained anything.** Nominal growth and real growth are different questions, and subtracting one from the other is a rough cut rather than the correct formula. That calculation gets its own treatment in [what inflation does to your savings APY](/2026/07/23/how-to-evaluate-the-risk-of-inflation-on-your-savings-accounts/).

## Where APY Estimates Go Wrong

**Promotional windows.** A headline APY that applies for an intro period and then reverts is not the APY you earn. Suppose an account pays 5.00% for the first three months and 3.50% after, on $10,000. The first quarter produces about $122.72; the remaining nine months on the grown balance produce about $264.57. Total for the year is roughly $387 — an effective 3.87%, not 5.00%. Blend before you compare, and put the reversion date in your calendar.

**Balance tiers.** When APY steps up at a threshold, the advertised rate is the top tier. If your balance sits below it, or drops below it after a withdrawal, your effective yield is the blend of the tiers your money actually occupied.

**Mid-month deposits.** Money earns from the day it is credited, not from the day you decided to save it. Under a daily balance method at 4.00% APY, $10,000 deposited on the 20th of a 30-day month earns about $11.83 that cycle. The same $10,000 present for all 30 days earns about $32.29. Nothing is wrong; the estimate simply assumed a full period.

**Variable rates that moved.** A savings or money market APY can change during the year. An estimate made in January describes a rate that may not have survived to December, which is why the tracking step below matters more than the estimate did.

## Tracking What You Actually Earned

Every statement carries an "interest paid this period" line and, usually, a year-to-date total. Those two figures let you audit the rate rather than trust it.

To reverse-engineer what you were really paid over a period:

`Effective annual rate = (1 + interest paid / average balance)^(365 / days in period) - 1`

If that comes out meaningfully below the APY you signed up for, the likely explanations are a rate cut, a tier you fell out of, a fee netted against interest, or a mid-period deposit that earned for fewer days. Each is checkable against the same statement.

At tax time, banks report deposit interest on Form 1099-INT. Two points worth internalizing: there is a reporting threshold below which the payer is not required to send you a form, and interest is taxable whether or not a form arrives. The [IRS page on Form 1099-INT](https://www.irs.gov/forms-pubs/about-form-1099-int) has the current instructions. Reconcile the form against your own year-to-date total when it shows up — mismatches usually trace to an account you forgot you had.

## A Spreadsheet Layout for Multi-Account Savers

Once you hold more than two accounts, memory stops working. One tab, one row per account, refreshed quarterly:

| Column | What goes in it | Why it earns its space |
|---|---|---|
| Institution | Bank or credit union name | Insurance is per institution, not per account |
| Account type | Savings, MMA, CD, checking | Sets which rules apply |
| Opened / matures | Dates | CD maturity and grace windows are easy to miss |
| Current balance | From the statement | Denominator for every check below |
| APY as disclosed | From the rate sheet, with the date you checked | Rates move; an undated APY is not evidence |
| Compounding / posting | Daily, monthly; posting day | Explains timing surprises |
| Interest paid this period | From the statement | The number that settles arguments |
| Effective rate | Formula from the section above | Catches silent cuts |
| Fees charged | From the statement | Converts to negative yield |
| Next review date | A date, not "soon" | The only column that makes the sheet get used |

The one column people leave out is "APY as disclosed, with the date you checked." Without it you cannot tell the difference between a bank that cut your rate and a memory that drifted.

For rate direction generally, the [Federal Reserve's monetary policy page](https://www.federalreserve.gov/monetarypolicy.htm) is the primary source. Deposit APYs follow policy rates loosely and on their own schedule, so treat it as context rather than a forecast for your account.

## APY Confusions Worth Sorting Out

**Does daily compounding beat monthly by enough to switch banks?** No. On $10,000 at a 4.00% nominal rate the difference is under a dollar a year. Switch for APY, fees, or access — not for compounding frequency.

**Why is my posted interest lower than balance × APY ÷ 12?** Most often because your balance was not at that level for the full cycle, or the rate changed, or a fee was netted out. Recompute using average balance for the cycle rather than the closing balance.

**Can my APY change after I open the account?** On savings and money market accounts, yes — those rates are variable and the disclosure permits repricing. A CD's rate is fixed for its term. If a variable rate matters to your plan, the [pre-opening checks for a high-yield savings account](/2026/06/15/what-to-consider-when-opening-a-high-yield-savings-account/) cover what to verify in the account agreement.

**Do I owe tax on interest if no form arrives?** Yes. The reporting threshold governs whether the bank must send a form, not whether the income is taxable.

**Is a higher APY always the better account?** Only after fees, minimums, and access terms are equal. A fee-carrying account with a higher headline rate frequently nets less, especially on smaller balances.

## Turning APY Into a Real Number

Pull the most recent statement for every deposit account you hold. Write down the balance, the interest paid, and the APY currently disclosed — with today's date next to it. Run the effective-rate formula on each one. Where the result trails the disclosed APY, find out which of the four causes explains it. Where the disclosed APY itself trails the FDIC national average for that product, you have a specific, checkable reason to move money rather than a vague sense that you could be doing better.
