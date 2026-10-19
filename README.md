# SFV I-485 tracker

A Claude skill for employment-based I-485 applicants whose case is at the San Fernando Valley field office. It reads the community-reported cases once or twice a day, tells you what changed for people in your cohort, and estimates when your case is likely to be approved.

Built for the SFV filers community. Free, open source, no server: everything runs in your own Claude account.

> **Not legal advice.** All dates and percentages are estimates from self-reported cases plus judgment priors. They are not USCIS statistics and they will be wrong some of the time. Talk to your attorney about your case.

## What you get

A short, phone-friendly message on your schedule:

- **Your outlook:** chance of approval by the next few checkpoints, a median date, and the main risks (interview, RFE, visa pause, retrogression, straggler).
- **What's new:** approvals, FTA0/FTA1, RFEs and transfers in your transfer batch first, then in your visa pool at SFV.
- **Similar approvals:** the approved cases most like yours, with transfer-to-approval gaps.
- **Visa Bulletin:** when a new month is out, where your PD stands.
- A chart of simulated approval dates.

## How it works

**Sources**
- [San Fernando Filers sheet](https://docs.google.com/spreadsheets/d/14d7MktWRIB7Wb7qvKDlVALyVz9KzgU5h2oLrBQhZxvo/edit) (SFV cases)
- [I-485 Status Update Sheet](https://docs.google.com/spreadsheets/d/16v6fSbpwfIKNCK8sSM1EjDrZSlQi98i-ZntlU5HHM-Y/edit) (all field offices)
- [Visa Bulletin](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html)
- Reddit, only if your Claude account has a Reddit connector. Most don't; see [Reddit](#reddit).

**Model**

SFV has cleared cases roughly in transfer-date batches per category. The model simulates 200,000 futures:

1. Where the "frontier" (the latest transfer date being approved in your category) is today.
2. How fast it moves, fitted from recent approvals.
3. Your position within your batch, plus a chance of being picked up out of order.
4. Tail delays: interview, RFE, visa pause, retrogression, being a batch straggler.

The parameters are re-fitted to your category, PD and transfer date at setup, then updated on every run as new approvals come in. The script is in [`model/aos_model.py`](model/aos_model.py) if you want to read it or run it yourself.

## Requirements

- A Claude account with **code execution and file creation** turned on (Settings > Capabilities on Free, Pro and Max).
- A **Claude Project** for the tracker. The tracker keeps its state in one Project doc, so scheduled runs can pick up where the last one stopped.
- **Scheduled tasks**, if you want automatic runs. Without them you can run the check by hand.
- Some usage per run. Once daily is plenty for most people.

## Install

1. Download [`sfv-i485-tracker.zip`](sfv-i485-tracker.zip?raw=1) from this repo (on the file page, use the download button).
2. In Claude, go to **Customize > Skills**, click **+**, then **Create skill > Upload a skill**, and upload the zip. ([Claude help article](https://support.claude.com/en/articles/12512180-use-skills-in-claude))
3. Create a Project, for example "Green card tracker".
4. In a chat inside that Project, type `/sfv-i485-tracker` or "set up my I-485 tracker".

To build the zip yourself: zip the `sfv-i485-tracker/` folder (the folder, not just the file). If you change `SKILL.md`, rebuild the zip in the same commit so the two stay in sync.

## Setup

Setup takes about five minutes. Have these ready, or paste your Emma transcripts and case history and let Claude pull the dates out:

- Category and chargeability
- Whether you are a national of one of the countries of concern (75/39 list)
- Priority date, I-485 receipt date and receipt block
- Concurrent I-140 filing, I-485J filed
- Biometrics date
- Field office transfer date, local or non-local, and how you know
- Interview waiver: stated? when? re-confirmed after transfer?
- Any FTA0, FTA1, silent update or RFE dates
- Your username or Unique Entry ID in the sheets, so your own rows are skipped

Then choose a cadence. Claude saves the state, creates a scheduled task called "I-485 cohort check", and runs the first check.

## Day to day

| Say | What happens |
|---|---|
| "run my cohort check" | Runs a check now |
| "update my case: FTA0 today" | Records the event, reruns the model |
| "update my case: transferred to SFV on Oct 6" | Updates your transfer date and frontier |
| "change my tracker cadence to weekdays" | Updates the scheduled task |
| Paste a Reddit thread or group chat export | Counts any new cases in it |

An example state file is in [`examples/`](examples/i485-tracker.example.md).

## Reddit

Claude cannot read Reddit by default, and there is currently no Reddit connector in the Claude directory. The tracker works without Reddit: the two sheets carry most of the same cases. If you see a relevant thread, paste its text into your tracker chat and say "update my case". If a Reddit connector becomes available, setup will offer it.

## Limits

- **Only as good as the sheets.** Self-reported, incomplete and sometimes wrong. If people stop reporting, the model goes stale.
- **Built around SFV EB-2 batching.** Other categories and field offices may not batch the same way. EB-1 and EB-3 batches at SFV have run ahead of EB-2, so the model fits them separately.
- **Countries of concern.** These cases have not moved with the ROW batches. With few approvals to fit on, the outlook is flagged as likely optimistic.
- **Not modeled:** cases with a non-current PD, and cases without a field office transfer yet.

## Privacy

- Your case details stay in your own Claude Project. Nothing is sent anywhere except the reads of the public sheets and the Visa Bulletin.
- The sheets are public community data. Please keep reporting your own case there: the tracker only works because people do.

## Contributing

Issues and pull requests are welcome, especially:

- Calibration: comparing predicted against actual approval dates
- Support for other field offices and their community sheets
- Better handling of countries-of-concern cases

## Credits

Thanks to the maintainers of the San Fernando Filers sheet and the I-485 Status Update Sheet, and to everyone who reports their case.

## License

[MIT](LICENSE)
