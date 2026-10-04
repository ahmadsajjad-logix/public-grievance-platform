# Civic Access Product Requirements Document

Intelligent Public Grievance and Statutory Escalation Platform

| Document control | Value |
| --- | --- |
| Version | 1.2 — Groq AI and current workflow |
| Date | 5 October 2026 |
| Team leader | Junaid Nagi |
| Context | Pak Angels · Pakistan National Impact Challenge |
| Implementation baseline | Repository revision fff4e06 |
| Live demonstration | https://public-grievance-platform.streamlit.app/ |
| Repository | https://github.com/ahmadsajjad-logix/public-grievance-platform |
| Intended readers | Product owner, engineering, legal/research reviewers, design, QA and prospective implementation partners |

This document defines the intended product and its acceptance criteria. It separates the deployed demonstration from requirements for a reliable public service. Proposed targets, operating roles and release gates below are recommendations for approval, not claims of current capability or committed delivery dates.

## Project Team

| Role | Name | Email | Cell phone |
| --- | --- | --- | --- |
| Team Leader | Junaid Nagi | junaidnagi@gmail.com | 03005525526 |
| Team Member #01 | Maleeha Saeed | maleehasaeed79@gmail.com | 03005359436 |
| Team Member #02 | Sajjad Ahmad | sajjad.danish@gmail.com | 03005996696 |
| Team Member #03 | Anam Arif | anamarif28@gmail.com | 03005025666 |

## 1 Product purpose

Civic Access helps people in Pakistan understand where and how to pursue a public-service complaint. A person describes a problem in English, Urdu or Roman Urdu, confirms the responsible institution, learns the applicable regulatory framework and available remedies, and receives practical help using the official complaint channel.

The primary outcome is a correctly directed, well-prepared complaint that the citizen can submit. A downloadable petition supports that outcome but is not the only product output. Where a department has its own form, the app should help the citizen complete that form, using concise copyable facts and supporting documents where accepted.

The product also supports two related journeys: identifying potentially relevant offence provisions for FIR preparation, and preparing Right to Information requests for public records. These journeys must remain distinct from ordinary service complaints.

### Problem statement

Citizens often do not know which service provider or authority is responsible, whether to approach a regulator first, what evidence to retain, or how to challenge an unresolved complaint. Department websites distribute legal and procedural information across statutes, regulations, manuals, directories and portals. Outdated sources and imprecise filing recipients can make an otherwise valid complaint ineffective.

### Product principles

- Start with the actual service provider where the procedure requires it.

- Explain the institution's powers and limitations before preparing a petition.

- Link legal statements to authoritative sources and disclose research gaps.

- Preserve user control over facts, declarations and submission.

- Make guidance available without collecting identity details.

- Distinguish a draft, a user-reported filing and an independently confirmed submission.

- Prefer an explicit uncertainty message over an invented provision, recipient or deadline.

## 2 Users and core needs

| User | Need | Successful outcome |
| --- | --- | --- |
| Citizen with a service problem | Identify the responsible provider and first complaint channel | Understands where to complain and what to submit |
| Citizen with an unresolved complaint | Determine the eligible next forum | Receives a supported escalation route with exclusions and required prior records |
| Person preparing to report an offence | Understand potentially applicable substantive law and FIR procedure | Receives fact-sensitive guidance without unsupported charges or guaranteed registration |
| Person requesting public records | Identify the record holder and applicable RTI procedure | Prepares a precise request and understands review options |
| Authorized helper | Assist a citizen without changing or inventing facts | Citizen reviews and controls the final complaint |
| Knowledge reviewer | Maintain reliable law, jurisdiction and channel information | Can publish, correct or withdraw reviewed guidance with provenance |

Public demand, adoption and willingness to use the product have not yet been measured. Initial validation should include users with limited familiarity with complaint procedures and users who prefer Urdu.

## 3 Scope and coverage

### Departmental scope

The current directory contains 95 entries, with 95 guidance profiles and 314 reviewed source summaries. An entry can represent a specific institution or a broad provincial service category; these counts do not imply 95 fully verified legal filing endpoints.

| Sector | Included scope and routing requirement |
| --- | --- |
| Electricity | LESCO, IESCO, FESCO, GEPCO, MEPCO, PESCO, HAZECO, HESCO, SEPCO, QESCO and TESCO; K-Electric separately; NEPRA for eligible regulatory complaints. Confirm the supplier shown on the bill. |
| Telecom | Jazz, Zong, Ufone, Telenor, Onic as a PTML brand, PTCL/Flash Fiber and SCOM/SCO in AJK/GB, alongside PTA. Operator-first handling; external territorial escalation for SCO requires verification. |
| Banking | Banking Mohtasib Pakistan and State Bank of Pakistan only. Individual local banks are not separate directory entries. Sunwai guides the citizen to the financial institution first and the competent subsequent forum. SBP must not be represented as a general appeal from BMP. |
| Electronic Media (Radio, TV, Cable TV, etc.) | PEMRA, with complaint-type distinctions. Regional recipient selection must reflect jurisdiction; programme-content provisions must not be reused automatically for cable billing or employment disputes. |
| Gas and petroleum | SNGPL, SSGC and OGRA within their respective service and regulatory scope. |
| Federal administration and taxation | Federal agencies, Wafaqi Mohtasib, FBR/Customs and FTO, with maladministration distinguished from statutory tax appeals. |
| Cybercrime | Current NCCIA reporting guidance, distinguishing criminal reporting from telecom service redress. |
| Provincial and local services | Municipal sanitation, water, police, traffic, food safety, consumer rights, land, health and education; named providers where researched and local-office confirmation where necessary. |
| Provincial oversight and service delays | Provincial ombudsmen and verified RTS mechanisms, subject to territorial and service-notification requirements. |

### PEMRA receiving offices

The province selector offers the relevant Council of Complaints and available PEMRA regional offices. The five Council routes are Islamabad, Punjab, Sindh, Khyber Pakhtunkhwa and Balochistan. A selected regional office receives the complaint and routes Council matters to its provincial Council. AJK and Gilgit-Baltistan retain territorial review guidance because the app does not offer a local PEMRA Council route there.

For providers such as Jazz, a regional office is not a universal filing prerequisite. The selected department or service provider remains the complaint recipient when no regional recipient is available. Legal-grounds and admissibility uncertainty remain separate from this recipient choice.

### Separate sidebar journeys

The navigation shall include Submit Grievance, FIR & Offence Guide, Right to Information (RTI), My drafts & filing records, Analytics & Heatmap, Department Directory and a restricted Knowledge Base administration area in the production product.

RTI shall cover federal and provincial guidance, clearly identifying incomplete operational-channel research. AJK/GB or uncertain jurisdiction must require confirmation rather than inheriting a federal or provincial statute automatically.

### Outside the current release

Automatic complaint submission, authenticated portal autofill, live government status synchronization, guaranteed redress, exhaustive offence coverage, identity verification against NADRA, and universal statutory deadline calculations are outside the current demonstration. Audio recording/transcription is withdrawn because tested Urdu transcription was unreliable. Restoring audio requires a separate quality decision, not merely installing a speech model.

## 4 Current implementation versus target product

| Capability | Baseline on 5 October 2026 | Required direction |
| --- | --- | --- |
| Complaint intake | English, Urdu and Roman Urdu text; optional document uploads and OCR | Validate usability and extraction quality on representative cases |
| Department suggestion | Optional Groq LLM suggestions with catalogue validation; alias/keyword fallback, manual selection and region filters | Improve disambiguation using a reviewed multilingual evaluation set |
| Jurisdiction retrieval | FAISS hashed lexical vectors with fallback; scoped summaries and local page references | Introduce stronger retrieval only after evaluating correctness and abstention |
| Six agents | Six Python workflow stages, with optional Groq assistance for department suggestion and petition wording | Preserve clear responsibilities; autonomous LLMs are not a prerequisite |
| Legal framework and clauses | Source-linked guides; uneven provision-level coverage | Complete issue-specific research and review before calling a route fully verified |
| Exact recipient | PEMRA province Councils and receiving regional offices; selected provider as default recipient elsewhere, with explicit jurisdiction exceptions | Maintain verified role, region, channel and review date per filing route |
| Official-form help | Specific reviewed fields for NCCIA, NEPRA and KWSC; general help elsewhere | Add form-specific guidance to each supported verified electronic route |
| Petition and guidance | PDF petition, filing guide and copyable complaint content | Validate legal relevance, readability and portal compatibility |
| Dispatch | Links and instructions; nothing submitted automatically | Optional approved integrations only in a later release |
| Tracking | Session-local drafts and user-reported filing records | Durable private records and status reconciliation after security work |
| Reminders | User-selected follow-up with calendar download | Calculate statutory dates only from verified rule metadata |
| Analytics | Opt-in grouped category/province/date/status counts | Apply privacy thresholds, durable storage and clear preparation-versus-filing labels |
| FIR guidance | 13 fact-screened scenarios | Expand after legal review and incident-date/territory validation |
| RTI | Sidebar guidance and downloadable text request drafts | Verify missing commission channels and expand jurisdiction-specific assistance |

The supplied Hugging Face resource is a legal text dataset, not a ready hosted LLM. Its text and any model output must not automatically be treated as current legal authority.

## 5 Principal user journeys

### A. First service complaint

Enter the complaint and service location/region; alternatively browse the directory.

Choose Department / Service Provider manually or opt into Groq AI and select suggest Complaint based relevant department. Confirm the suggested provider.

Confirm the provider and read its scope, legal framework, rights, exclusions and first complaint mechanism.

Open the official form/portal, use reviewed phone/WhatsApp guidance, or choose offline preparation.

To prepare a draft, enter applicant name, CNIC number, expiry date and mobile number. Review optional evidence. In Petition & Downloads, review any AI wording and explicitly apply it before it changes the petition.

Review and submit through the receiving authority's process personally; retain the official acknowledgment.

### B. Unresolved complaint

Select the original provider, supply the previous reference when available and identify the complaint stage. The app explains the eligible escalation forum. Without the earlier reference, a draft may still be prepared, but the app must not silently redirect it as a completed escalation. Pending court matters and challenges to formal decisions require separate admissibility or appeal review.

### C. Official portal assistance

The app distinguishes direct complaint forms from login portals, information pages and directories. It explains each reviewed field, supplies copyable facts and requested relief, and states whether a PDF attachment is accepted. If the form does not accept a petition, the petition serves as the citizen's full record and the relevant content is copied into the form. Opening the portal must not transmit case data.

### D. FIR and offence guidance

Choose an incident scenario, answer element-specific factual questions and receive potentially relevant PPC/PECA or other researched provisions. Unsupported or uncertain elements remain uncertain. Explain CrPC reporting procedure separately from substantive offence sections, provide an evidence checklist and a downloadable guide, and direct the user to the competent reporting channel.

### E. RTI request

Choose the government responsible for the record holder, identify the public body, list specific records and dates, and select a preferred access format. Show the applicable framework and first-request instructions. Generate a request draft with applicant placeholders and explain the relevant review or complaint route. Do not generate a statutory request under an unconfirmed territorial law.

## 6 Functional requirements

Priority definitions: P0 is required before a dependable public pilot; P1 improves pilot usability or operations; P2 is a later enhancement. Priority is not an implementation-status claim.

| ID | Priority | Requirement | Acceptance criterion |
| --- | --- | --- | --- |
| IN-01 | P0 | Accept text in English, Urdu and Roman Urdu | Text survives intake, editing and export without loss; unsupported understanding is disclosed. |
| IN-02 | P0 | Permit identity-free access to departmental, FIR and RTI guidance | No CNIC or phone gate appears when browsing guidance or opening official links. |
| IN-03 | P0 | Require applicant name first, then CNIC number, CNIC expiry date and mobile number for grievance petition preparation | Blank or whitespace-only applicant names and missing/invalid identity formats block preparation. Every upload remains optional. Complaint content and a usable route remain necessary. |
| IN-04 | P0 | Make OCR suggestions reviewable | Extracted references/dates are labelled as suggestions; originals are not treated as authenticated evidence. |
| JR-01 | P0 | Support explicit department selection and abstention | Ambiguous or unnamed providers prompt selection; the app does not guess a district office. |
| JR-02 | P0 | Respect provider, territory, issue type and stage | First operator complaints remain with the operator; unrelated department sources are excluded from clause selection. |
| JR-03 | P0 | Present source-backed framework, remedies, exclusions and filing procedure | Every published profile provides provenance and an explicit research status; a general statute is not presented as a proven breach. |
| JR-04 | P0 | Apply banking forum distinctions | Only BMP and SBP appear as banking directory entries; institution-first Sunwai guidance is visible; no automatic BMP-to-SBP appeal exists. |
| AU-01 | P0 | Explain evidence readiness without blocking optional uploads | Display score, checklist and missing items; state that the score measures preparation, not legal merit or admissibility. |
| PB-01 | P0 | Generate fact-preserving, source-linked petitions | No invented facts, staff names or provisions; each included legal provision carries its source and applicability context. |
| PB-02 | P0 | Use the appropriate recipient | Use the selected regional receiving role where supported. Otherwise use the main department/provider without a missing-regional-recipient warning. Retain genuine territorial restrictions, including PEMRA in AJK/GB. |
| PB-03 | P0 | Produce readable downloadable outputs | Urdu shaping, page breaks, long references and English/Urdu content pass visual review; petition and guidance have distinct purposes. |
| DR-01 | P0 | Present the correct official complaint channel prominently | Verified forms/portals appear before drafting; link labels accurately describe the destination. |
| DR-02 | P0 | Separate preparation from submission | Every unsent draft is marked not submitted; an external link click cannot change its status to filed. |
| DR-03 | P1 | Provide maintained field-by-field portal help | Each specific guide records form URL and review date; generic guidance is explicitly labelled. |
| DR-04 | P1 | Support offline filing | Provide sourced receiving-office details, document checklist and delivery-proof instructions; unknown hours remain unknown. |
| TR-01 | P0 | Track truthful status and provenance | User-entered acknowledgments are labelled user reported; no fabricated government tracking number is generated. |
| TR-02 | P0 | Separate reminders from statutory deadlines | Calendar downloads label personal follow-up clearly; legal deadlines require a verified trigger, rule, calendar and exceptions. |
| AN-01 | P0 | Obtain separate analytics consent | No consent means no aggregate write; identity, narrative and attachments are excluded. |
| FI-01 | P0 | Screen offence elements conservatively | Negative or unknown answers do not produce affirmative offence findings; civil/criminal and territorial uncertainty are shown. |
| RT-01 | P0 | Offer a distinct RTI sidebar journey | Users can select the record holder's jurisdiction, read guidance and download a request without completing the grievance identity form. |
| RT-02 | P0 | Distinguish requests from RTI complaints/appeals | First requests address the public body; commission routes are explained separately with source and applicability limits. |
| KB-01 | P0 | Restrict knowledge publication to authorized reviewers | Public users cannot overwrite the shared verified corpus; changes are attributable and reversible. |
| KB-02 | P0 | Record source conflicts and stale information | Conflicting deadlines or procedures create a visible review flag rather than a silently selected rule. |
| EX-01 | P2 | Add authorized autofill or dispatch integrations | Requires channel permission, secure credentials, explicit per-case user approval and authentic submission acknowledgment. |
| AI-01 | P0 | Make external AI assistance explicit and optional | No Groq call without opt-in and an explicit suggestion or preparation action; no call on ordinary rerun. |
| AI-02 | P0 | Validate jurisdiction suggestions and retain fallback | Unknown or cross-territory IDs are rejected; failure leaves rules and manual selection available. |
| AI-03 | P0 | Require review before applying AI petition text | Generated wording leaves the original PDF unchanged until the citizen applies reviewed wording; original intake remains retained. |
| AI-04 | P0 | Limit external data and protect credentials | Exclude separate identity and uploads, mask supported patterns, disclose residual narrative privacy risk and never log keys. |
| AI-05 | P0 | Evaluate AI by language and failure mode | Measure English, Urdu and Roman Urdu routing and fact preservation; test quota, timeout, malformed output and unavailable credentials. |

## 7 Six-agent responsibility model

“Agent” means a bounded specialist responsibility. Six Python workflow stages orchestrate the application. Optional Groq LLM calls support Agent 02 department suggestions and Agent 04 draft wording. The other stages remain deterministic. Product success is measured by correct, reviewable outputs.

| Agent | Inputs | Required output | Boundary |
| --- | --- | --- | --- |
| 01 — Intake & OCR | Citizen narrative and optional files | Preserved facts; suggested account references and dates | No invented facts or automatic trust in OCR; audio currently disabled |
| 02 — Jurisdiction RAG | Confirmed facts, provider, region, stage and reviewed corpus | Validated department suggestion, competent route, retrieved legal context and explicit uncertainty | Must not turn an unreviewed web page or model response into verified law |
| 03 — Audit Readiness | Issue-specific checklist and available documents | Explained readiness percentage and next preparation steps | Missing optional files cannot block a draft; score is not probability of success |
| 04 — Petition Builder | Reviewed facts, remedy and applicable provisions | Original petition plus optional AI wording for explicit user review and application | No automatic allegation that a law was breached |
| 05 — Dispatch & Router | Selected filing route and preparation package | Official links or offline instructions; later, approved integrations | Current release never submits or emails a complaint |
| 06 — Tracker & Analytics | Draft record, user-reported acknowledgment and consent | Personal reminders, honest status labels and privacy-protected aggregates | No claimed live government status without an integration |

Agent 02's research responsibility includes official-site discovery during knowledge maintenance. It does not require unrestricted live crawling during every citizen session. Retrieved files are evidence to review, not instructions to execute.

### Groq AI assistance in the current release

Provider and model. The application calls Groq using the configured GROQ_API_KEY and defaults to openai/gpt-oss-120b. GROQ_MODEL permits configuration. Secrets remain in Streamlit Cloud settings or the local environment and are excluded from source control. Free-tier access has usage limits and is not a promise of unlimited availability.

Department suggestion. AI runs only when the citizen enables Use AI assistance and requests a suggestion. It receives the redacted narrative, selected territory and allowed department catalogue. The application validates the returned category and department ID against that catalogue and territory. The citizen confirms or changes the result. Ambiguous output may ask up to three questions. Rule-based suggestions and manual selection remain available on failure.

Petition wording. With AI enabled, Prepare my grievance requests suggested statement and relief using the complaint, requested remedy and supplied official reference extracts. The original draft remains active until the citizen edits or accepts the suggestion using Use this reviewed wording in my petition. Applying it updates the PDF and copyable complaint text while retaining the original intake facts.

Legal boundary. The LLM does not publish new legal research, establish guilt, select offence charges or independently verify law. Its drafting instructions exclude invented legal sections, deadlines, URLs and legal conclusions. The application supplies its curated provisions separately. AI suggestions must still receive human review. FIR and RTI currently use their existing researched workflows rather than this Groq drafting feature.

Data boundary. Separate identity fields and uploaded documents are excluded from Groq payloads. Recognizable CNIC, mobile and email patterns are masked, and known identity/reference values are additionally masked during drafting. Free text can still contain names or other identifying details. The user-facing notice explains that complaint text, requested relief and reference extracts leave the app for Groq when AI is enabled.

Failure behavior. Missing credentials disable AI selection. Connection, access, quota and invalid-output failures retain the standard workflow and show safe messages without exposing credentials or upstream complaint content. AI is called on explicit actions, not every page rerun. Broader Urdu accuracy, quota behavior and live drafting remain evaluation tasks.

## 8 Legal knowledge and source governance

Each supported route should have a structured record containing institution/provider, category, territory, complaint type, first forum, eligible escalation, exclusions, legal instrument/version, section or clause, source URL, page reference when applicable, filing endpoint, recipient role, required evidence, form constraints, review date, reviewer and confidence/research status.

Legal deadline records additionally require the triggering event, start-date evidence, calendar versus working-day rule, extensions, limitation/condonation rules and amendment dates. Until these are verified, the product must use personal follow-up reminders only.

The publication process shall be: discover official material → record provenance/version → extract and inspect → assess jurisdiction and amendments → review legal/procedural interpretation → publish → monitor → correct or withdraw. Operator terms and unofficial datasets may assist research but cannot replace binding law or current official procedures.

Proposed operating policy: check active complaint links monthly, review high-use legal/procedural routes quarterly, and conduct an immediate review after a known amendment or material complaint-channel change. Assign reviewers before treating these intervals as an operational commitment.

## 9 Data, privacy and non-functional requirements

### Data model and retention

Separate private case data from the public knowledge corpus and aggregate analytics. A case may contain identity/contact fields, narrative, provider, region, stage, references, attachments, reviewed OCR values, sources used, generated documents and filing-record provenance. Knowledge records must never contain a citizen's uploaded documents by default.

Currently private cases and uploads remain in Streamlit session memory; ending the session can lose the records. Optional analytics uses local SQLite aggregates and is not guaranteed to survive a Cloud rebuild. Production needs an approved retention policy, user-visible deletion controls, access isolation and durable storage before long-term case tracking can be promised.

### Public-pilot requirements

- Protect private data in transit and at rest wherever retained; exclude it from routine logs and analytics.

- Authorize administrators and isolate each citizen's case access. Do not expose shared ingestion controls as an unrestricted public admin function.

- Validate upload size/type and handle unreadable, malicious or oversized files without crashing or executing embedded content.

- Treat document and retrieved web text as untrusted data, including any instructions embedded in it.

- Provide keyboard-accessible controls, meaningful labels, mobile layouts and readable Urdu/English text. Target WCAG 2.2 AA review for principal journeys.

- Preserve guidance when an external portal is unavailable; label the failure and offer only sourced alternatives.

- Keep deployment secrets out of GitHub. The current workflow must continue to operate without an OpenAI API key.

- Document backup, recovery, retention and incident-response responsibilities before storing durable private cases.

Proposed performance targets, to be benchmarked rather than assumed: guidance selection within 2 seconds and a text-only petition within 10 seconds at the 95th percentile, excluding cold starts and external portals. OCR must show progress and recoverable failure. Hosting capacity and concurrency targets require measured pilot demand.

### AI operating requirements

Keep AI optional and preserve guidance and petition preparation when credentials are absent or Groq is unavailable. Use server-side secrets, bounded request duration, validated structured output and a clear error state. Never silently switch providers or send additional files. Any future change in provider, data sharing or autonomous filing requires revised user-facing disclosure and acceptance criteria.

## 10 Evaluation and release acceptance

The Groq integration baseline passed 199 automated tests. All seven AI integration tests passed after the connection fix in revision fff4e06. A synthetic Jazz billing complaint on the hosted app received a live Groq explanation and selected Jazz. Live petition drafting has not yet been separately verified. These checks do not establish legal certification, comprehensive security testing or multilingual accuracy.

| Measure | Proposed pilot acceptance target |
| --- | --- |
| Named-provider routing | At least 95% correct on a reviewer-labelled English/Urdu/Roman Urdu test set; uncertain cases ask for confirmation |
| Critical jurisdiction safety | Zero known invalid automatic escalations in the approved release test set |
| Legal citation integrity | Every generated provision has a traceable source; zero fabricated citations in the reviewed release sample |
| Filing-link accuracy | Every route labelled verified resolves to the intended institution and stated destination type at release check |
| Optional-document behavior | Petition preparation succeeds without uploads when required identity and workflow inputs are valid |
| Privacy | No identity, narrative or attachment content in aggregate records or ordinary application logs |
| Draft/submission distinction | No test can mark a case officially filed solely by generating a PDF or opening a portal |
| Language and export quality | All representative approved Urdu/English PDF cases are readable and unclipped |
| Citizen task completion | Proposed target: 80% of pilot participants identify the correct first channel and prepare usable content without facilitator correction |

Build a labelled evaluation set spanning provider-first complaints, ambiguous providers, regional mismatches, missing references, pending court matters, formal appeals, banking exclusions, mobile-wallet versus telecom complaints, PEMRA content versus service issues, unsupported offence elements and uncertain RTI territories. Record failures by language and sector; an overall score must not hide a weak Urdu or provincial subset.

Track completion of guidance, draft preparation and self-reported filing separately. A resolution-rate claim requires reliable outcome data that the current app does not possess.

## 11 Delivery plan and dependencies

| Stage | Deliverable | Exit condition |
| --- | --- | --- |
| Demonstration baseline — delivered | Current Streamlit app, department guidance, preparation outputs, FIR and RTI journeys | Running deployment and regression checks; gaps disclosed |
| Knowledge completion | Issue-specific law, recipients and complaint mechanisms for prioritized routes | Legal/research reviewers approve route records and source conflicts |
| Public-pilot hardening | Administrator authorization, privacy controls, accessibility, safe uploads and reliability | Security/privacy review and approved pilot acceptance results |
| Filing assistance expansion | More verified field guides and improved multilingual routing | Maintained form records and successful citizen usability evaluation |
| Integrated service — conditional | Approved autofill/dispatch and authentic tracking integrations | Partner permission, user consent, secure operation and acknowledgment reconciliation |

Dependencies include access to official law and complaint information, legal reviewers, language/OCR testing resources, hosting capacity, a privacy/retention decision and any future channel partnership. There is no committed timeline or budget in this PRD; estimate these after staffing and pilot scope are approved.

## 12 Risks and unresolved decisions

| Risk or decision | Required response |
| --- | --- |
| Laws, procedures and URLs change | Version sources; monitor links; surface review dates and withdrawal status |
| All entries appear equally verified | Use separate badges for directory, researched guidance, verified recipient and issue-specific provisions |
| OCR or language interpretation changes facts | Require user review and allow correction; measure each language separately |
| Identity information is collected earlier than necessary | Keep browsing anonymous; confirm the product-owner requirement for identity on all grievance petitions and treatment of expired/lifetime CNICs |
| Session loss or ephemeral hosting | Explain export and loss behavior; add durable cases only after privacy and retention design |
| User mistakes draft for official filing | Persistent not-submitted labels and separate acknowledgment provenance |
| Broad provincial entry lacks an exact office | Ask for district/provider or disclose uncertainty; do not manufacture a recipient |
| RTI operational-channel gaps | Prioritize Punjab, Sindh and Balochistan endpoint verification and territorial-law review |
| Audio reinstatement pressure | Keep disabled until a defined Urdu transcription evaluation and user-review flow pass |

Product-owner decisions still needed: initial public-pilot audience and sectors; legal-review ownership; acceptable research freshness; production hosting and operating budget; retention period and account model; whether future audio or automated filing is worth its operational cost. These decisions do not block use of the current demonstration but do block claims of production readiness.

## 13 Reference and change-control notes

This PRD is based on the product owner's instructions, the latest saved team information and the implementation inspected at revision fff4e06, particularly app.py, grievance/catalog.py, grievance/sector_research.py, grievance/guidance.py, grievance/knowledge.py, grievance/legal.py, grievance/agents.py, grievance/identity.py, grievance/rti.py, grievance/storage.py and grievance/llm.py.

The linked [PRD overview](https://en.wikipedia.org/wiki/Product_requirements_document) was consulted for document context. Product-specific requirements and priorities in this document come from this project's needs, not that reference. Legal facts remain attached to the official sources in the application's individual guides; this document does not replace those guides or independently certify their legal completeness.

Changes to mandatory identity fields, sector coverage, source verification policy, submission behavior, legal deadline calculations or private-data retention should update this PRD and its acceptance criteria before implementation is described as complete.
