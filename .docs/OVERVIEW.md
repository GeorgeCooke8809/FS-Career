# FS Career — Overview & Roadmap

## Pitch

A Microsoft Flight Simulator (2020/2024) career companion app combining:

- **A Pilot's Life** — real airline career progression and a realistic personal/airline economy.
- **Fly The Line: Short Haul Edition** — route generation tied to real-world airline schedules.
- **PACX** — live cabin announcements, ambient cabin/crew audio, and a passenger-satisfaction-driven rating system.

The core loop: join an airline (governed by difficulty tier) → the app generates a real-world route for that airline → the flight plan is pushed to SimBrief → the player flies it, delivering their own PA announcements over mic and hearing the cabin crew's own announcements/boarding music/safety briefing via per-airline audio packs → the flight is scored on **customer satisfaction** (smoothness, timeliness, PA quality, comfort) rather than a traditional numeric pilot rating → results feed career progression, pay, and — in Career mode — a reprimand system for anything a passenger, crew member, or the aircraft itself would realistically report.

## Difficulty Tiers


| Tier         | Airline access                                                                                                                           | Hiring                                                                                                                        | Personal finances | Type ratings                                                                                                                            |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Casual**   | Start at your dream airline immediately                                                                                                  | Instant, no requirements                                                                                                      | Off               | Not gated                                                                                                                               |
| **Standard** | Open market                                                                                                                              | Requirements-gated, auto-accept (no competition)                                                                              | On                | Gated, cost, some airlines will pay for your type rating and any other ratings when switching among their fleet                        |
| **Career**   | Open market, cadetship-style entry (a new player who applies broadly can still land an airline job quickly, no forced GA/regional grind) | Requirements-gated**and** competitive (meeting the bar makes you eligible; a chance/queue element reflects real hiring pools) | On                | Gated; fewer airlines sponsor type ratings on hire and switching around their fleet, and earned ratings carry forward to other airlines |

Reaching the biggest/best-paying majors in Career mode is still a genuine climb (hours, satisfaction history, reprimand-free record) — the cadetship route just means day one doesn't have to be a regional turboprop if the player doesn't want that.

## Airlines & Route Generation

- Bundled static dataset (built from OpenFlights/OurAirports-style data + schedule research): airline → routes → aircraft types → frequency. No live-service dependency; updated periodically.
- **Fully open airline market**: every airline has a computed prestige/pay tier and hiring requirements (flight hours, satisfaction score, reprimand-free streak, required type rating).
- Route generation picks a real route + flight number + aircraft type consistent with what that airline actually flies on that aircraft.
- **Type ratings**: gate which aircraft a player can be assigned. Earning one costs money; some airlines sponsor ratings on hire and when switching among their fleet; once earned, a rating carries forward and is reusable at other airlines.

## Economy

- **Salary & pay tiers**: scaled by airline tier, aircraft type, and seniority/rank.
- **Personal finances** (Standard & Career only, off in Casual): rent/bills/commuting-style expenses layered on top of salary, similar to A Pilot's Life's cost of living.
- Stored in SQLite via SQLAlchemy: finance ledger, career history, satisfaction history.

## Customer Satisfaction Rating (replaces a traditional pilot rating)

Score inputs:

- **Flight smoothness** — landing rate/G-forces, abrupt maneuvers, turbulence handling.
- **Timeliness** — actual vs. scheduled block times (from SimBrief/schedule data).
- **PA/announcement quality** — timing and completeness (see PA System below).
- **Routing/comfort choices** — deviations, cabin comfort factors.

This score is the primary "rating" driving hiring eligibility and career narrative — there is deliberately no separate abstract pilot-skill rating.

## Reprimand System (Career mode)

Triggers only on things a passenger, crew member, or the aircraft would realistically report:

- Hard/unstable landings beyond safe limits.
- Exceedances (overspeed, bank/pitch limits, stall warnings).
- Procedural/safety violations (e.g. continuing an unstabilized approach).
- Anything else a passenger or crew member would plausibly notice and report.

Consequences:

- **Formal warning system** — strikes escalate (verbal → written → final) rather than one event being catastrophic.
- **Pay/bonus impact** — reprimands can block bonuses/raises for a period.
- **Blocks promotion/upgrade eligibility** while a reprimand is open/unresolved.
- **Termination** as a last resort for accumulated strikes or a sufficiently severe single event, forcing a new job search.

## Cabin Announcements & Ambient Audio

- **Player PA**: delivered live over the player's own mic, push-to-talk. No TTS, no speech-to-text/content analysis.
- **Scoring**: based on push-to-talk **duration and timing** relative to the expected window for that flight phase (e.g. a seatbelt-off PA has a different expected length/urgency than a "prepare for landing" cue) — too long is as much a problem as too short/missing.
- **Ambient cabin crew audio**: per-airline **audio packs** (boarding music, safety briefing, generic crew announcements), auto-triggered by flight phase.
- **Copyright**: the app does **not** bundle real airline audio. Packs are user-supplied — the app provides the folder/manifest format and playback engine only.
- Pack format: a folder per airline containing audio files + a manifest (JSON/TOML) mapping flight phase → file.

## SimBrief Integration

- **Outbound**: the app generates the flight (airline, route, flight number, aircraft type) and pushes it to SimBrief via the SimBrief API to pre-populate the OFP request. The player finishes briefing/loading in SimBrief as normal.
- **Inbound**: after the OFP is generated (and potentially after the flight), the app reads back data needed for scoring/economy — at minimum: scheduled/estimated times, passenger count, cruise altitude; likely also fuel figures, route/waypoints, ZFW/TOW, and flight number/callsign.
- **Auth**: player enters their SimBrief username/pilot ID in settings; no OAuth.

## Technology Stack (Python, Windows/MSFS-only for now)

- **GUI**: CustomTkinter, run as a standalone app window (not an in-sim overlay). Real-time data (SimConnect polling) is decoupled from the UI via a background thread feeding a queue, with the UI refreshing on a throttled timer — avoids CustomTkinter/Tkinter redraw bottlenecks without switching frameworks.
- **Sim interface**: `python-simconnect` (SimConnect.py wrapper) for MSFS 2020/2024.
- **Data storage**: SQLite via SQLAlchemy (career profiles, airlines, routes, aircraft, flights, finance ledger, satisfaction history, reprimands).
- **PA capture**: push-to-talk key/button hold duration only — no audio content analysis.
- **Ambient audio playback**: a standard Python audio playback library (e.g. `pygame.mixer` or `sounddevice`), driven by the pack manifest.
- **SimBrief**: REST calls (`requests`) against the public SimBrief API, keyed on the player's username.
- **Packaging**: PyInstaller, Windows-only build (SimConnect is Windows-only regardless).
- **Multiple career profiles**: supported — a player can maintain several independent saves (different difficulty/airline/finances/history) and switch between them.

## Deferred / Out of Scope (for now)

- X-Plane support (architecture should stay loosely decoupled from MSFS specifics where cheap to do so, but not a v1 goal).
- TTS-generated or speech-to-text-analyzed PA content.
- In-sim overlay UI.
- Airline-side simulated economics (load factors, fuel cost, furlough risk) and "career capital" purchases beyond type ratings — could revisit later.
- Live/API-sourced route data (bundled static dataset only for now).

---

## Ordered TODO List

1. **Tech spike**: prove out SimConnect connectivity (read basic sim vars) and the CustomTkinter polling-thread → queue → throttled-UI-refresh pattern in a minimal shell app.
2. **Data layer**: SQLite schema + SQLAlchemy models — career profiles, airlines, routes, aircraft/type ratings, flights, finance ledger, satisfaction history, reprimands.
3. **Airline & route dataset**: build/curate the bundled airline → route → aircraft dataset.
4. **Career profile system**: create/switch/delete multiple profiles; difficulty selection at creation.
5. **Airline market & hiring**: prestige/pay-tier model, requirements engine, and the three difficulty-specific hiring flows (instant / auto-apply / requirements + competition).
6. **Route generation**: given an airline + profile + aircraft/type rating, generate a real-world-consistent flight.
7. **SimBrief integration**: push generated flight to SimBrief OFP request; pull back OFP data.
8. **Type rating system**: earn/hold/sponsor logic, cost/time, carry-forward across airlines.
9. **In-flight monitoring via SimConnect**: flight phase detection, G-forces/landing rate, exceedance detection, timeliness tracking vs. schedule.
10. **Satisfaction scoring engine**: combine smoothness, timeliness, PA quality, and comfort into a per-flight score and rolling career average.
11. **PA push-to-talk system**: hold-duration capture, phase-aware expected-timing windows, scoring integration.
12. **Ambient cabin audio system**: pack manifest spec + loader, phase-triggered playback, pack management UI.
13. **Reprimand system**: detection rules engine, strike tracking, consequences (pay/promotion/termination).
14. **Economy**: salary calculation, personal expense simulation (Standard/Career), finance dashboard.
15. **Career progression UI**: applications, promotions, seniority tracking, career history/logbook.
16. **Polish**: settings screen, PyInstaller packaging, documentation for community audio-pack creators.
