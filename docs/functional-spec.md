---
title: "Tekton — Functional specification"
refines: RFD 1 (docs/rfd-0001.md)
companion: docs/technical-spec.md
state: draft
date: 2026-09-28
---

# Tekton — Functional specification

This document describes **what Tekton does** for its user, step by step. [RFD 1](rfd-0001.md) is the base: it sets the goals, the legal framework and the high-level architecture. The [technical specification](technical-spec.md) (TS) describes **how** it is built.

The spec covers the full 9-step vision. Items marked **[v1]** are in the first release; everything else is planned for later releases (see [§14 Release scope](#14-release-scope)). Identifiers in `code` (decision keys, enum values) are the ones stored and exchanged by the system; the interface shows translated labels for them.

## 1. Principles

1. **Agents do the heavy lifting.** Research, searching listing sites, collecting prices, reading regulations and documents, checks, drafting, comparing quotes and monitoring are done by AI agents. Design assumption: agents are more thorough than a person at this kind of work, so the operator's time goes to what only they can do.
2. **The operator does what needs a real identity, a body or a voice.** That means signing, paying, phone calls, holding accounts, going to the notary, town hall, bank or the plot, and deciding. Everything the operator must do shows up as an **operator task** (sarcină pentru operator) that agents prepare as far as they can.
3. **The operator decides.** Agents propose; a decision is recorded only when the operator confirms it. Agents never sign and never pay.
4. **Every claim has a source.** Anything an agent asserts in the interface carries a source and a verification date. An unsourced claim is dropped before it reaches the interface, and the run is marked *partial*.
5. **Human-friendly first.** Tekton optimizes for the operator's clarity and effort, not for the smallest amount of software. Each screen answers three questions: *where am I, what is blocking me, what should I do next*.
6. **Personal data stays local by default.** Personal documents, and everything derived from them, leave the workstation (for a cloud model) only with the operator's consent (§12). Agents that browse the web see only public data and the parts of the brief they need.
7. **Law 169/2026 only.** Projects whose applications started before 25 August 2026 (under Law 50/1991) are out of scope. Documents issued under the old law that turn up in a new project are handled by §4.5.

## 2. Glossary (EN – RO)

| English | Romanian | Meaning in Tekton |
| --- | --- | --- |
| Operator | Operator / proprietar | The person using Tekton; the future owner of the house |
| Agent | Agent | An AI worker session (headless Claude Code or similar) that performs a task |
| Run | Rulare | One piece of agent work on one subject; it may span several sessions when it waits for the operator |
| Watcher | Supraveghetor programat | A scheduled job that checks something periodically (§10) |
| Operator task | Sarcină pentru operator | Something only the operator can do; closed with proof |
| Approval request | Cerere de aprobare | An outbound action or privacy release waiting for the operator's yes/no (§8) |
| Decision | Decizie | A typed, versioned value set by the operator (e.g. `casa.persoane`) with rationale and sources |
| Proposal | Propunere | A value an agent suggests for a decision; the operator accepts, edits or rejects it |
| Derived value | Valoare calculată | A value Tekton computes from decisions, facts and rules (e.g. land budget, price per m²) |
| Brief | Temă / program | What house the operator wants: people, rooms, levels, floor area |
| Locality | Localitate | A village or town (SIRUTA code); belongs to a UAT |
| UAT | UAT (comună / oraș / municipiu) | The administrative unit with the town hall, PUG and taxes |
| Built-up area | Intravilan | Land inside the locality's building perimeter |
| Land book extract | Extras de carte funciară (extras CF) | Registry extract: owner, encumbrances, mortgages, disputes |
| Urban planning certificate | Certificat de urbanism (CU) | Town hall document stating the plot's rules and the approvals required |
| Approvals | Avize | Approvals listed in the CU (utilities, fire, environment, …) |
| Building permit | Autorizație de construire (AC) | Permit, valid 3 years |
| Notification procedure | Procedura de notificare | Building without a permit, for eligible houses (§6) |
| Permit design documentation | PAC (formerly DTAC) | The design package submitted for the permit |
| Detailed design | Proiect tehnic de execuție (PTh) | Construction design used for quotes and building |
| Bill of quantities | Listă de cantități / antemăsurătoare | Item list builders price, so quotes are comparable |
| Local urban plan / regulation | PUG / RLU | General urban plan and its local regulation |
| RLU zone | Zonă / UTR din RLU | A zone of the RLU with its own rules (POT, CUT, height, …) |
| Land occupancy ratio | POT | Max share of the plot covered by the building footprint |
| Floor area ratio | CUT | Max ratio of total floor area to plot area |
| Gross floor area | Suprafață desfășurată | Sum of all floor areas |
| Footprint | Amprentă la sol | Area of the plot covered by the building |
| Land registration | Intabulare | Registering ownership in the land book |
| Handover | Recepție | Acceptance of works: at completion, and final after the warranty |
| Knowledge base | Bază de cunoștințe publice | `public_knowledge/`: public rules with source and date (§11) |

## 3. Actors

| Actor | Can | Cannot |
| --- | --- | --- |
| **Operator** | Decide, approve, sign, pay, call, visit, hold accounts, upload proof, lower a privacy class, dismiss a plot | — |
| **Agents** | Research the web, search listing sites, read documents their privacy tier allows, compute checks, draft emails and documents, propose decisions, propose knowledge updates, create operator tasks | Sign, pay, phone, log into the operator's accounts, send anything without the rule in §9, record a decision, change a plot's status, lower a privacy class, read data outside their tier |
| **Watchers** | Start agent runs or system checks on a schedule | Same limits as agents |
| **External parties** | Town hall, notary, bank, architect, engineers, builders, utilities: reached through the project mailbox or by the operator | — |

One operator per instance [v1]. Every event records its author (operator, a named agent run, a scheduled job, or the system), so a second person (e.g. a partner) can be added later without changing the history.

## 4. The workflow

The steps follow the order in which the cost of mistakes grows. Step identifiers are `1` … `6`, `7a` (permit), `7n` (notification), `8`, `9`.

```mermaid
flowchart TD
    S1["1. Brief, budget, financing"] --> S2["2. Area"]
    S2 --> S3["3. Search and shortlist"]
    S3 --> S4{"4. Plot due diligence<br/>before any deposit"}
    S4 -- nu --> S3
    S4 -- da --> S5["5. Purchase"]
    S5 --> S6["6. Design"]
    S6 --> S7{"procedure"}
    S7 -- notificare --> S7N["7n. Notification"]
    S7 -- autorizare --> S7A["7a. CU, approvals, permit"]
    S7N --> S8["8. Construction"]
    S7A --> S8
    S8 --> S9["9. Handover and final paperwork"]
```

### 4.1 Step mechanics [v1]

**States:** `blocked`, `available`, `in_progress`, `done`, `needs_revalidation`, `not_applicable` (the branch of step 7 that was not chosen).

| From | What happens | To |
| --- | --- | --- |
| `blocked` | Every step it depends on is `done` (for step 8: `7a` **or** `7n`) | `available` |
| `available` | The operator sets a decision, or an agent run starts on the step | `in_progress` |
| `in_progress` | The operator presses **Done** (allowed only when the step can complete, below) | `done` |
| `done` | The operator reopens the step, or edits one of its decisions | `in_progress`; dependent `done` steps → `needs_revalidation` |
| `done` | A decision it depends on changes, a check it owns changes result, or an earlier step leaves `done` | `needs_revalidation` |
| `needs_revalidation` | The operator reviews the impact and confirms | `done` |
| `needs_revalidation` | The operator changes a decision in the step | `in_progress` |
| any | `proiect.procedura` selects the other branch of step 7 | `not_applicable` |
| `not_applicable` | `proiect.procedura` changes back to this branch | `blocked` or `available`, as its dependencies allow |

- While an earlier step is not `done`, a later step is **shown** as blocked, but its recorded state (e.g. `needs_revalidation`) is kept and returns when the earlier step is done again.
- **Can complete** when every required decision is set, every required check passes, no proposal on a required decision is pending, and every required operator task is resolved (completed with its proof verified, or cancelled). A check can pass, fail or be *de verificat*; each step says whether *de verificat* is acceptable, and then shows it as a warning (step 2 accepts it, because the zone of a future plot is not known yet). For decisions per plot or per locality the step says which subjects count: step 2 needs at least one locality in `zona.localitati` that is not failing, step 4 needs the chosen plot. Only changes to those subjects move a done step back to revalidation; a new candidate plot does not reopen step 3. Tekton computes this and lists the blocking items; the Done button explains why it cannot be pressed.
- **Each step screen shows:**
  - the earlier decisions it depends on
  - its decisions, each with any pending agent proposal next to it (§4.12)
  - derived values and checks, with their formula and sources
  - agent findings with sources, and the runs in progress
  - the operator tasks and approval requests for this step
- **Going back:** before reopening a step or changing a decision, the screen previews the impact, e.g. "2 plots on the shortlist would be over budget", "notification eligibility would be lost: floor area 162 m² > 150 m²".
- **Legal cost of going back:** flagged explicitly. After the permit, a design change needs a modification permit (autorizație de modificare), with no new permit fee if it is within the original permit's validity.
- **Steps not built yet** (outside v1) appear on the map as *coming later*, with a short description; they are not a workflow state.
- **History:** an append-only event list. Nothing is deleted; a change is a new version.

### 4.2 Step 1 — Brief, budget and financing (Program, buget și finanțare) [v1]

**Goal:** what house, and how much money in total, from every funding source and over time. A bank loan is optional.

**Decisions**

| Key | Type | Req. | Notes |
| --- | --- | --- | --- |
| `casa.tip` | enum `unifamiliala`, `alta` | yes | Single-family house or other |
| `casa.persoane` | integer ≥ 1 | yes | People living in the house |
| `casa.camere` | room list | yes | Each room: kind (`dormitor`, `living`, `bucatarie`, `baie`, `birou`, `depozitare`, `altele`) and target area |
| `casa.regim_inaltime` | enum `p`, `d_p`, `p_m`, `p_1`, `d_p_1`, `p_1_m` | yes | Levels (parter, demisol + parter, mansardă, etaj) |
| `casa.subsol` | boolean | yes | Basement |
| `casa.suprafata_desfasurata_mp` | area (m²) | yes | Gross floor area |
| `casa.amprenta_mp` | area (m²) | yes | Footprint; an agent proposes it from the floor area and levels, stating how mansard and demisol levels were counted |
| `casa.locuire` | enum `permanenta`, `sezoniera` | yes | Permanent or seasonal |
| `procedura.tinta` | enum `notificare`, `autorizare`, `indiferent` | yes | Target procedure (§6) |
| `finantare.surse` | list of funding sources | yes | At least one. Each source: kind (`economii` own savings or money already available, `credit_bancar` bank loan, `imprumut_familie` loan from family or friends, `venituri_viitoare` future earnings set aside over time, `altele` other), amount (a lump sum, or a monthly amount with a start and an end month), availability date, certainty (`sigur` confirmed, `probabil` likely, `incert` uncertain), and a free note |
| `finantare.venit_net_lunar` | money | no | Household net monthly income; used only for the bank-loan estimate when a `credit_bancar` source exists |
| `buget.categorii` | allocation per category | yes | Planned amount per budget category (below) |

**Derived values:** `buget.total` (the sum of the `sigur` and `probabil` funding sources; `incert` sources are shown apart and not counted; the operator may override it), `finantare.flux` (cash-flow timeline: money available per month from the sources' dates, against the planned spending order of the categories; months with a shortfall are flagged), `buget.teren_max` (the land category of `buget.categorii`), `buget.rezerva_ratio` (the reserve category as a share of the total), `buget.estimare` (Tekton's estimate per category, from the brief and the researched unit costs), `finantare.credit_estimat` (Tekton's bank-loan estimate, from the declared income and the researched lending rules; only when a `credit_bancar` source exists). All `finantare.*` values, entered or derived, are `local_only` (§12): they are computed by Tekton on the machine and are never shown to cloud or web agents.

**Checks:** the allocation adds up to at most `buget.total`; the cash-flow timeline has no shortfall month before the planned end of construction (a warning, not a blocker, while any source is `incert`); the reserve is between 10% and 15%; the rooms fit in the floor area (sum of room areas × 1.2 for walls and circulation ≤ floor area). While the operator edits the allocation, the totals and the reserve share update live.

**Budget categories:** `teren` (land); `notar_taxe` (notary, taxes and land registration); `proiectare_studii` (architect, topographic survey, geotechnical study, engineers); `avize_taxe` (approvals and fees); `racordari` (utility connections); `constructie` (construction, by stage later); `curte` (yard and fences); `mobilare` (furnishing, optional); `rezerva` (reserve, 10–15%).

**What agents do**

- Research unit costs for the region (cost per m² for construction, notary fees, design fees, utility connection tariffs) and current lending rules (maximum debt-to-income ratio, rates, terms, down payment), from public sources. These agents see only public data and the brief.
- Tekton turns them into the estimates above with fixed formulas, locally; no agent reads any `finantare.*` value. An agent proposes the planned amounts (`buget.categorii`) and the footprint from the cost estimates and the land budget only. If the operator wants agent help that needs the total, they can share a coarse budget band (for example "250–300k EUR") through the consent dialog (§12); the exact sources, amounts, dates and income are never shared.
- Compute notification eligibility from the brief (§6) and explain which fields break it.

**Operator tasks:** only when a `credit_bancar` source exists, talk to 1–3 banks for a pre-approval (pre-aprobare); the agent prepares the documents list and the questions from public lending rules, and the proof is the bank's written offer or a meeting-result form, which updates that source's amount and certainty. For a `imprumut_familie` source, an optional task records the agreement (amount, date, repayment terms) with a signed note or message as proof.

### 4.3 Step 2 — Area (Zona) [v1]

**Goal:** choose the localities where to search.

**Decisions**

| Key | Type | Req. | Notes |
| --- | --- | --- | --- |
| `zona.criterii` | distance criteria | yes | Per destination (a named city, hospital, school, transport, shops): maximum travel time |
| `zona.localitati` | ranked list of localities | yes | Candidate localities, best first |

**Locality entity (Localitate):** SIRUTA code, name, UAT and its type (`comuna`, `oras`, `municipiu`), whether the UAT is in a metropolitan area, distances and travel times, known utilities (water, sewage, gas, electricity, internet), known protected zones, price per m², validation status.

- Localities come from the national SIRUTA list. The operator can add one by searching its name (with or without diacritics); agents add neighbours of the chosen ones.
- **Price per m²** is computed by Tekton from the listing samples agents collect (price, area, intravilan land only, link, date): median, spread and sample size, shown with every listing behind it.

**What agents do**

- Compute distances and travel times from OpenStreetMap data (a system job): to the city, hospitals, schools, transport, shops.
- **Collect land listings from listing sites** (imobiliare.ro, OLX, storia, and others) per locality, within the site limits of §10, and store them as samples.
- Fetch the UAT's PUG/RLU into the knowledge base if missing (§11). If the town hall provides it only at the counter, the operator uploads the copy and confirms where it came from; the rules are then used, marked *de verificat*.

**Validation of each locality:**

- *minimum plot needed for a zone* = max(footprint ÷ POT max, floor area ÷ CUT max, minimum lot of the zone)
- the zone of a future plot is unknown, so Tekton uses the residential zone of the RLU with the smallest minimum plot, names that zone, and marks the result *de verificat* until step 3 knows the plot's zone
- it passes if *price per m² × minimum plot needed ≤ `buget.teren_max`*
- EUR prices are converted at the BNR rate of the day the validation ran; the rate is shown, and a later rate change re-runs the validation only when it moves more than 2%.
- If `procedura.tinta = notificare`, localities belonging to a `comuna` pass; villages belonging to an `oras` or `municipiu`, and UATs in a metropolitan area, are marked *de verificat*; the town itself is marked "breaks notification" (§6).

**Operator tasks:** optional visit to the area (a task with a checklist the agent prepares).

**Can complete** when at least one locality in `zona.localitati` passes validation or is *de verificat* (not failing); *de verificat* is shown as a warning.

**Revalidation link:** a budget or brief change in step 1, or a price-per-m² refresh, re-runs the validation of every locality.

### 4.4 Step 3 — Search and shortlist (Căutarea și lista scurtă) [v1]

**Goal:** a shortlist of plots, each with a complete sheet (fișă de teren).

**Plot entity (Teren):** listing links (one plot may appear on several sites), locality, location, cadastral number (număr cadastral) if known, area, price, frontage, access, utilities, intravilan status, **RLU zone** (with its source and status: confirmed, inferred, unknown), own lot and own access, inside a protected zone, PUG compliance, photos, seller contact.

- **Identity:** the cadastral number when known; otherwise site + listing id. When agents find the same plot on another site, they link the listing to the existing plot; two plots found to be the same are merged, and everything that pointed to either now points to the surviving one.
- **Status** is shown, never set by agents, and follows from the decisions: `candidat` (found), `pe_lista_scurta` (in `teren.lista_scurta` and not rejected), `respins` (verdict `nu`, or dismissed by the operator with a reason), `ales` (`teren.ales`), `cumparat` (step 5). A listing removed from its site is flagged, not rejected.
- When agents suspect two plots are the same, they suggest a merge; the operator confirms it on the Plots screen (it also counts in *needs your attention*).

**What agents do**

- Search listing sites continuously in the chosen localities (a watcher, §10). They deduplicate the same plot across sites and track price changes and removals.
- Determine the plot's RLU zone, protected zones and PUG compliance from the PUG maps or documents; an unknown value keeps the related checks *de verificat* and adds a question for the seller or the town hall.
- Filter against the rules: intravilan; RLU rules of the zone (POT, CUT, height, setbacks, minimum lot); area ≥ minimum plot needed; access; utilities; budget; notification eligibility when it is the target.
- Build the **plot sheet (fișa de teren):**
  - which documents it has (extras CF, cadastru, CU, utility approvals)
  - which documents are still needed
  - the estimated effort and cost to get them
  - a fit score, with each rule linked to its source
- Propose additions to the shortlist, and draft emails to sellers for missing information (sent under §9).

**Operator tasks:** phone the seller (the agent prepares the questions); visit the plot (with a checklist: access, slope, neighbours, water, power lines, photos).

**Decisions**

| Key | Type | Req. | Notes |
| --- | --- | --- | --- |
| `teren.lista_scurta` | list of plots | yes | The shortlist chosen by the operator |

**Derived value:** `teren.lista_scurta_activa` — the shortlist without rejected plots.

**Can complete** when the active shortlist holds at least one plot.

The Plots screen owns the plot list, map and sheet; steps 3 and 4 link to it with the right filters.

### 4.5 Step 4 — Plot due diligence (Verificarea terenului, înainte de orice avans) [v1]

**Goal:** a yes or no on a plot, before paying any deposit. Due diligence can run on several shortlisted plots in parallel; each has its own verdict.

**What agents do**

- Read the land book extract (extras CF):
  - owner(s), matching the seller
  - encumbrances (sarcini), mortgages (ipoteci), disputes (litigii), easements (servituți)
  - area in the land book vs the listing
- Estimate the utility connection costs (racordări) from the utilities' public tariffs and the distance to the networks.
- **Choose the right CU type** among the five in Law 169/2026 and fill in the application (cerere) and the documents list.
- Once the CU is issued, read it: the approvals required (avize), the zone rules, and anything that blocks building. Update the approvals list as data.
- **Old-law documents:** a CU or approval issued under Law 50/1991 is recorded as issued under the old law. It is informational only; the verdict needs a CU under Law 169/2026.
- Check the plot against the RLU and against notification eligibility (§6).
- Prepare the questions for an architect's opinion (părerea unui arhitect).
- Propose the **verdict** with its reasons (each with a source) and risks (each with a cost estimate).

**Operator tasks**

- Order the extras CF on ANCPI ePay: log in and pay. The agent gives the exact cadastral number and fields. Proof: the receipt and the downloaded PDF.
- Submit the CU application at the town hall or on its portal, and pay the fee. Proof: the registration number (număr de înregistrare) and the receipt.
- Pick up the CU if it isn't delivered electronically. Proof: the CU document.
- Get an architect's opinion (call or meeting). Proof: the call- or meeting-result form, or the architect's written note.

**Decisions**

| Key | Type | Scope | Req. | Notes |
| --- | --- | --- | --- | --- |
| `teren.verdict` | verdict (`da`, `nu`, `de_verificat`, with reasons and risks) | per plot | for the chosen plot | Proposed by an agent, set by the operator |
| `teren.ales` | plot | project | yes | The plot to buy; its verdict must be `da` |

- `nu` marks the plot `respins` with the reason, so it leaves the active shortlist; step 3 stays done, and the operator continues with another shortlisted plot or goes back to step 3.
- `de_verificat` keeps the step in progress and creates the tasks needed to resolve the open points.
- `da` lets the operator choose it: **`teren.ales`** (the plot to buy). The step can complete when `teren.ales` is set and its verdict is `da`.

### 4.6 Step 5 — Purchase (Cumpărarea)

**What agents do**

- Review the draft preliminary contract (antecontract): price, deposit (avans), conditions for returning the deposit (e.g. the loan being refused), deadlines, penalties.
- Track the mortgage process: documents list, valuation (evaluare), approval deadlines.
- Prepare the documents list for the notary.
- Check the land registration (intabulare) once done, from a new extras CF.

**Operator tasks:** sign the preliminary contract, pay the deposit, sign the loan agreement, attend the notary, pay taxes and fees. Each one needs proof.

**Decisions:** `cumparare.pret_final`, `cumparare.data_notar`, `cumparare.credit` (terms).

### 4.7 Step 6 — Design (Proiectarea)

**What agents do**

- Shortlist architects: check signing rights in the OAR Register (Tabloul OAR), their portfolio, and fees. Draft the quote requests.
- Generate the **design brief (tema de proiectare)** directly from the step 1 decisions and the CU.
- Organize the topographic survey (ridicare topografică) and the geotechnical study (studiu geotehnic): find providers, draft requests, compare quotes.
- Confirm the procedure: notification or permit (§6).
- Review design versions against the brief, the RLU, the budget and notification eligibility, and flag drift (e.g. floor area creeping past 150 m²).

**Operator tasks:** meet architects, sign the design contract, pay stage invoices, give access to the plot for the survey.

**Decisions:** `proiect.arhitect`, `proiect.procedura` (final: `notificare` or `autorizare`; selects step `7n` or `7a`, the other becomes `not_applicable`), `proiect.versiune_aprobata`.

### 4.8 Step 7 — Authorization (Autorizarea)

**7a. Permit (autorizare).** Path: CU → approvals (avize) → PAC → building permit (autorizație de construire).

- Agents track every approval listed in the CU as an item with its authority, documents, fee, legal deadline, status and proof.
- They draft the applications and follow up by email.
- Deadlines: 30 days for issuing the permit. The permit is valid 3 years; its expiry goes on the calendar with reminders.

**7n. Notification (notificare).**

- The design is approved by the county chief architect (arhitectul-șef al județului).
- The notification is submitted; the answer is due within 15 working days, and **silence means approval (tacit)**.
- Tekton computes the working-day deadline, excluding public holidays, and records the tacit approval when it expires with no answer.

**Operator tasks:** submit and pay at each authority, pick up approvals, sign with a qualified electronic signature (semnătură electronică calificată) where filing is digital.

### 4.9 Step 8 — Construction (Execuția)

**What agents do**

- Once the detailed design (PTh) and the **bill of quantities** are ready, draft quote requests for builders on the same items.
- **Vet builders:**
  - financial statements (bilanțuri, from the Ministry of Finance)
  - court records (portal.just.ro)
  - company data (ONRC)
  - past projects
- **Compare quotes line by line:** missing items, unit price outliers, totals vs the budget.
- Review the construction contract: stages, payment schedule, warranty, penalties, and who supplies which materials.
- Track the site by stage: planned vs actual dates, payments vs budget, photos and site reports.

**Operator tasks:** meet builders, sign the contract, pay each stage (proof: invoice and receipt), visit the site at each milestone (checklist and photos).

### 4.10 Step 9 — Handover and final paperwork (Recepția și actele finale)

- **Handover at completion of works (recepția la terminarea lucrărilor):** agents prepare the file and the checklist of defects to note.
- **Final handover (recepția finală)**, when the warranty period ends. A calendar milestone years later, with reminders.
- **Land registration of the house (intabularea construcției):** the agent prepares the documents; the operator submits and pays.
- **Tax declaration at the town hall (declararea la primărie):** the agent prepares the form and the deadline.

### 4.11 Derived values

Derived values are computed by Tekton, never typed by an agent. Each shows its formula and inputs. Some can be overridden by the operator (e.g. the total budget): an override is kept when inputs change, and the screen then shows "computed value would now be X" with a button to drop the override. Price per m² is a derived value computed from the listing samples; when new samples change a validation result, the dependent steps move to `needs_revalidation`.

### 4.12 Agent proposals [v1]

An agent never sets a decision. It **proposes** a value, with rationale and sources. The proposal appears **inline next to the field** in the step: "Agent suggests 42,000 EUR · 3 sources · Accept / Edit / Reject". Accepting or editing records the decision as the operator's; rejecting records the reason, which the agent sees on its next run. A proposal based on personal documents stays *local only* when accepted, unless the operator chooses to release it in the same dialog. The Home screen shows a **needs your attention** list that counts pending proposals, operator tasks and approval requests, each linking to where it is handled.

## 5. Budget (cross-cutting) [v1 for steps 1–4]

- One budget from step 1 to step 9, with the categories of §4.2.
- For each category: **planned** (step 1), **committed** (amounts the operator has agreed to pay: a signed contract or accepted quote; entered by the operator in v1, by agents from contracts later), **paid** (receipts), **remaining**.
- **Currency:** the budget is kept in RON. Amounts may be entered or found in EUR; each is stored with its currency and converted with the BNR rate of a stated date: the payment date for payments, the day of the evaluation for plans and validations (the rate of the last banking day on or before that date, with the rate's date shown). If no rate is available, the conversion is marked *de verificat*.
- Every payment is linked to an operator task, a budget category and its proof. It is recorded as soon as the operator closes the task with the receipt (*unverified*), and becomes *verified* after the proof check (§7). If a check finds a mismatch and the operator corrects the proof, the corrected payment replaces the old one.
- Alerts when a category exceeds its plan, when the reserve drops below 10%, or when the total goes over `buget.total`.

## 6. Notification eligibility (cross-cutting) [v1]

Law 169/2026 allows building by notification (notificare) instead of a permit when **all** of the conditions hold. The authoritative list, with article references and the input each condition is checked against, will live in `public_knowledge/lege/169-2026/notificare.yaml`; the table below is a summary, and the file wins:

| Condition | Checked against |
| --- | --- |
| A single single-family house (casă unifamilială) | `casa.tip` (step 1) |
| With its own lot and own access | Plot facts (steps 3–4) |
| Ground floor only (P), or demisol + parter (D+P); no basement (subsol) | `casa.regim_inaltime`, `casa.subsol` (step 1) |
| At most 150 m² gross floor area (suprafață desfășurată) | `casa.suprafata_desfasurata_mp` (step 1, watched in step 6) |
| In the intravilan of a rural locality of a commune (comună), not a town | Locality and UAT (step 2), plot intravilan (steps 3–4) |
| Outside protected zones | Plot facts (steps 3–4) |
| Compliant with the PUG | Plot facts (steps 3–4, 6) |
| Design approved by the county chief architect | Step 6–7n |

- The operator may set the target `procedura.tinta = notificare` in step 1. That target then **filters** localities in step 2 and plots in step 3.
- A live status is shown in the app header: **eligibil / neeligibil / de verificat**, for the house in general until a plot is chosen, and for the chosen plot afterwards. Plot and locality screens show their own status. The failing or unverified conditions are listed.
- If the rules file is missing or invalid, the status is *de verificat* with the reason.
- Final confirmation happens in step 6, with the architect.
- **Open legal points**, marked *de verificat* with the source of the interpretation until practice is clear:
  - rural localities inside metropolitan areas (the published exclusion concerns outbuildings of up to 50 m², not explicitly the 150 m² house)
  - villages that belong to a town or municipality
  - whether a demisol counts as a basement

## 7. Operator tasks (Sarcini pentru operator) [v1]

A dedicated inbox, always visible, with a counter. It is the main place the operator works from.

**Each task has:**

- a title, a type, its step and subject (plot, approval, …)
- why it matters, and whether it is **required** for the step to complete
- a deadline (derived from the law or a watcher when relevant)
- everything the agent prepared: who to contact, phone numbers, address and opening hours, questions to ask, documents to bring, exact form fields, amounts, each with the source it came from
- the required proof
- a status: `open`, `in_progress`, `completed`, `cancelled`; plus the proof check: `unchecked`, `verified`, `mismatch`

**Task types and required proof.** A task can require several proof items (e.g. ordering the extras CF needs both the receipt and the downloaded document).

| Type | Example | Proof items |
| --- | --- | --- |
| `plata` (payment) | CU fee, deposit | **Receipt (chitanță / dovada plății)** with amount and date |
| `portal` (portal request) | Order the extras CF on ANCPI ePay | Confirmation number, the downloaded document, and a receipt when there is a fee |
| `telefon` (phone call) | Ask a seller about access | Call-result form (the agent's questions, answered) |
| `deplasare` (visit) | Town hall, plot visit, site | Registration number and a photo of the stamped copy, or the checklist with photos |
| `semnare` (signing) | Preliminary contract, design contract | The signed document |
| `intalnire` (meeting) | Architect, bank | Meeting-result form and any documents received |
| `cont` (account setup) | **Create the project Gmail** and connect it | The connection succeeds (checked automatically) |

- **Payment details and links are checked by the operator.** For `plata` and `portal` tasks, the payee, IBAN, amount and any link show where the agent found them; details that come from an email or a web page, and links outside the official sites, are marked *unverified* until the operator confirms them in the task. Links always show their site.
- The **Done** button explains what is missing until every required proof item is attached. Files are uploaded first (with progress), then attached as proof items.
- After closing, an agent **checks the proof** (amount and date on the receipt, registration number format, signatures present). On a mismatch the task reopens with an explanation. If no local model is available, the operator can confirm the proof themselves, or release it for a cloud check. A run waiting on the task continues after the check passes, the operator confirms it, or the task is cancelled.
- Tasks are created by agents or watchers, or manually by the operator, who picks a type; the type sets the proof.

## 8. Approval requests (Cereri de aprobare) [v1]

Approval requests cover **outbound actions and privacy**, not decisions (decisions are handled by §4.12):

| Kind | Created when | What the operator sees |
| --- | --- | --- |
| `email_send` | An agent drafts an email whose type is set to *send after approval* | Recipient (and where the address came from), subject, body, attachments |
| `knowledge_change` | An agent proposes a change to `public_knowledge/` | The file diff and its sources (only verified official sources are accepted) |
| `privacy_consent` | A cloud run needs data marked *local only*, or no local model is available for local-only work | Which document or data, which agent, why |

- They are created by Tekton when the agent drafts or proposes; the screen is rendered from what will actually happen, and the agent's explanation appears in a separate, labelled block.
- The operator can approve, reject with a reason, or edit and approve (email text and knowledge content can be edited; consent cannot). An edit is checked again before it is applied.
- A privacy consent can be given **for this run only** (the default) or **always** for that document, thread or sender.
- The agent run waits and resumes after the answer, even days later. A run that waits for more than 30 days is cancelled, its pending requests expire, and the operator is told.
- **Not gated:** reading public web pages, listing sites and public registers. These are logged with their sources.

## 9. Project mailbox and email [v1]

- A **dedicated project mailbox**, for example `casa.<familie>@gmail.com`. Creating it is an operator task, together with the Google Cloud OAuth client Tekton needs (the agent prepares step-by-step instructions). It is connected to Tekton through Google OAuth.
- **Sending** is configured per message type. Each type is either `draft_only` (Tekton keeps the draft; the operator can copy it or push it to Gmail's drafts with one click and send it from there) or `send_after_approval`.
  - Types: `intrebare_vanzator` (seller questions), `cerere_informatii_primarie` (requests to the town hall), `cerere_oferta` (quote requests: architect, survey, geotechnical study, builders), `urmarire_aviz` (follow-ups on approvals), `raspuns_fir` (replies in existing threads).
  - Default: `send_after_approval`.
- **Recipients:** agents write only to people already in the thread, to contacts stored with the plot, locality or professional the run is about (the approval shows where each address came from), or to contacts the operator confirmed. A personal attachment is flagged in the approval.
- **Reading:** agents read incoming mail in the project mailbox. They link each thread to its step and entity (plot, professional, approval), extract facts as proposals, and create tasks.
- **Privacy:** mail is *local only* by default. The operator can mark a thread, or a sender for all future messages, as *cloud allowed* (§12), after a confirmation that says what changes.
- Email content is **untrusted**. Instructions inside an email are never followed; they are shown to the operator as content. Emails are displayed safely: no scripts, no remote images unless the operator asks, links open in a new tab.
- If the Gmail connection expires, a `cont` task to reconnect appears and a notification is shown.

## 10. Watchers (Supraveghere programată) [v1]

Watchers are scheduled jobs that run while the stack is up. Some start agent runs, others are system checks. Their results arrive as proposals, operator tasks or notifications. Agent watchers ship **disabled**; the operator enables them during setup, after choosing the listing sites and the monthly cost cap.

| Watcher | Kind | Default interval | Output |
| --- | --- | --- | --- |
| New and changed plot listings in the candidate localities | agent | Daily | New candidates with a pre-filled sheet; price changes; removed listings |
| Listing samples for price per m² | agent | Weekly | New samples; revalidation if a locality's validation flips |
| Distances and travel times for new localities | system | On change | Distances on the locality |
| Project mailbox | system (sync) + agent (triage) | Every 15 minutes | Threads linked, facts proposed, tasks created |
| Legal deadlines (CU validity, 15 working days, permit expiry, final handover) | system | Daily | Reminders and escalating tasks |
| Stale knowledge (verification date older than 6 months) | agent | Weekly | Reverification runs and proposed updates |
| Legal changes (amendments to Law 169/2026, new orders) | agent | Weekly | Proposed updates to the national rules |
| BNR exchange rates | system | Daily | Rates for conversions |
| Backup | system | Daily | Backup status; a notification on failure or when the last success is older than 48 hours |

- Watchers can be paused, run on demand, or have their interval changed from the UI.
- Runs missed while the machine was off run once at startup.
- A watcher that fails three times in a row notifies the operator.
- **Listing sites:** per-site limits on request rate and pages per run; a site that blocks Tekton (repeated refusals) is paused for 24 hours and the operator is told.

## 11. Knowledge base (`public_knowledge/`) [v1]

- A directory in the Tekton repository that is **committed and pushed**, so it is shared with everyone who uses Tekton.
- It holds public rules only:
  - **National:** the steps, deadlines, CU types, notification conditions and forms from Law 169/2026 and Order 975/2026; the public holidays per year; the SIRUTA list of localities.
  - **Local:** PUG/RLU rules per zone, local council decisions (HCL), local taxes and the infrastructure levy, and town hall procedures (portal, opening hours, fees).
- Every file has a **source** and a **verification date**; a rule inside a file can carry its own when it differs. It never contains personal data.
- **Agents read it first**, before doing new research, and treat it as information to check, not as instructions. When they learn something new or find a rule out of date, they **propose a change**, backed by a source they actually fetched from an official site.
- **The flow:** an agent proposes → the operator reviews the diff in the app and approves → Tekton commits it on a `knowledge/*` branch in the operator's repository, without touching the working copy → the operator pushes and opens the PR. From approval on, Tekton already uses the approved content, even before it is merged; approved content that never gets merged can be dropped from the Knowledge screen.
- Uncertain interpretations are stored with the status `de_verificat` and the source of the interpretation.

## 12. Documents and personal data [v1]

- All documents live locally in Tekton's document store: extras CF, CU, contracts, receipts, photos, IDs, offers, designs, snapshots of web sources.
- **Each document has** a type, its step and linked entities, its origin (uploaded, fetched by an agent, email attachment), its date, and a **privacy class:**
  - `public`: listings, laws, regulations, web snapshots
  - `personal_local` (**local only**): the default for anything the operator uploads, and for email and attachments
  - `personal_cloud` (**cloud allowed**): after the operator's consent, per document, email thread or sender
- **Derived data inherits the class.** Text extracted from a document, agent results computed from `personal_local` data, and anything an agent writes after reading such data are `personal_local` too. Only the operator can lower a class, after a confirmation that names what changes; each change is recorded.
- **Financing stays local.** Everything under financing (funding sources, amounts, dates, certainty, income, the loan estimate, the cash-flow timeline) and the budget total are local only, even though the operator typed them; Tekton computes the estimates itself on the machine, and no consent can release them except as a coarse budget band.
- **What agents see** depends on their tier:

| Tier | Who | Sees |
| --- | --- | --- |
| Web | Agents that browse the internet | Public data and the brief they need to search: house type, levels and basement, floor area and footprint (to filter plots by the rules), target procedure (to filter by notification), land budget (to filter by price), travel criteria and candidate localities (where to search), and the shortlist (which plots to watch). Never financing data (`finantare.*`: sources, amounts, dates, income) or personal documents, and never a value that came from a personal document |
| Cloud | Agents on cloud models without web access | Public data, what the operator typed (brief, budget allocation, rationale) except financing, `personal_cloud` data. Never `finantare.*` or the budget total; a coarse budget band only if the operator releases it (consent dialog) |
| Local only | Agents on local models, no web access | Everything |

- If no local model is available, local-only work waits and the UI says so, offering to release the data for a cloud run instead (a `privacy_consent` request).
- Documents can be previewed and downloaded. Every agent claim that comes from a document links back to the page.

## 13. Interface [v1]

- **Language:** English first, with every text in translation catalogues from day one so Romanian can be added (including Romanian plural forms and number formats). Romanian legal terms (CF, CU, PAC, avize) are kept, with explanations.
- **Main screens**
  - **Home:** the 9-step map with states; the current step (the first one not done); notification eligibility; the budget summary; the next deadlines; the **needs your attention** list (§4.12).
  - **Step:** decisions with proposals inline, derived values and checks, agent findings with sources, runs in progress, tasks and approvals for the step, history; step-specific panels (room list, budget allocation, localities, plot verdicts).
  - **Operator tasks:** the inbox (§7).
  - **Approvals:** the queue (§8).
  - **Plots:** a list and a map with filters, and the plot sheet (fișa de teren), where per-plot decisions such as the verdict are made. The map works offline from a local map extract; every map action also exists in the list.
  - **Localities:** candidate localities with their validation.
  - **Budget:** categories with planned, committed, paid and remaining.
  - **Calendar:** legal deadlines and milestones; `.ics` download.
  - **Documents:** a browser with privacy classes.
  - **Mail:** threads, linked to steps and entities.
  - **Agents:** runs (live progress, cost, results, logs, why a run is waiting) and watchers (schedules, last result, failures).
  - **Knowledge:** browse the rules; pending changes with diffs; approved changes not yet merged.
  - **History:** every event, filterable.
  - **Notifications:** the in-app inbox.
  - **Health:** services, model gateway, mailbox connection, watchers, backups, disk space, cost this month.
  - **Settings:** mailbox connection, email rules per type, per-agent model profile overrides, watcher schedules, listing sites, cost caps, backup location.
- **Badges** in the navigation: operator tasks (open), approvals (pending), notifications (unread); Home shows the combined *needs your attention* count.
- Every screen has clear loading, empty (with the next action) and error (with retry) states, and a visible "disconnected" indicator when live updates stop.
- **Accessibility:** keyboard navigation, visible focus that never gets lost when an item disappears, screen-reader labels and announcements for the operator's own actions, and no information carried by colour alone. A button that cannot be used yet stays focusable and explains why.

## 14. Release scope

Tekton is built in workflow order: each step is complete before the next one starts.

| Release | Contents |
| --- | --- |
| **v1** | The workflow engine, decisions, proposals, derived values, history and revalidation; operator tasks with proof; approvals; agent runs and watchers; project mailbox; knowledge base; documents and privacy tiers; budget; calendar; notification eligibility; notifications; health; backup and restore; **steps 1–4 in full** (everything up to the plot verdict, before any deposit) |
| v2 | Steps 5–6: purchase and design, including vetting architects |
| v3 | Step 7: permit and notification variants |
| v4 | Steps 8–9: quotes, builder vetting, site tracking, handover |
| Last | Backup of important documents to Google Drive (OAuth) |

## 15. Non-functional requirements

- **Local only:** the app runs on a Linux workstation (Ubuntu or Rocky) in containers, reachable only from that machine, at one address (`http://127.0.0.1:8080`).
- **Durability over 5 years:** data survives app upgrades; every upgrade takes a backup first, and a failed upgrade can be undone by restoring it. Daily local backups, encrypted, with a tested restore of any retained backup [v1]. Cloud backup comes later.
- **Auditability:** every decision, proposal, task, approval, agent run, email and knowledge change is an event with its author and sources.
- **Honesty of claims:** unsourced claims never reach the interface (principle 4).
- **Cost control:** a monthly cost cap for cloud models; agent watchers pause when it is reached.
- **Legal positioning:** the UI presents information and organization with sources, not legal advice. The wording is to be validated by a lawyer.

## 16. Open questions

- [ ] Wording of "information, not advice", to be validated with a lawyer.
- [ ] The legal points marked *de verificat* in §6.
- [ ] Listing sites' terms of use for automated collection: which sites to include and their limits.
- [ ] Whether someone who is not yet the owner can apply for the CU of a plot (step 4), and with which proof of interest.
- [ ] Long-term community home for `public_knowledge/` (e.g. Code for Romania).
- [ ] Review rules for knowledge contributions from other users (PRs to the repository).
