# PRODUCT

## Users And Operators

- Primary users: internal MTG security, compliance, and service delivery operators using CISO Assistant as the GRC system of record.
- Customer-facing roles: vCISO, account, and audit-support users who need to explain customer coverage, gaps, and evidence without exposing unrelated customer data.
- Service-provider role: MTG acts as an MSP. One service provider domain represents controls MTG operates for customers. MTG internal domains remain separate because internal controls and customer-applied controls can differ.
- Integrations: Bifrost provides technical evidence, workflow execution, and near-real-time verification signals. CISO Assistant stores the compliance record, review state, and reporting surface.

## Core Workflows

- Domain hierarchy: create and maintain provider, internal, and customer domain folders. The hierarchy must make parent-child relationships obvious and keep customer domains under the service provider boundary when they inherit MSP coverage.
- MSP control assertions: map one provider-operated applied control to one or more customer domains, including verification source, summary, payload, and current coverage state.
- Compliance assessment work: assess frameworks, requirements, applied controls, evidence, risks, exceptions, and findings. Users must be able to see when a customer requirement is covered locally versus inherited from provider-operated coverage.
- Evidence review: operators need fast paths from a scored or covered requirement to the underlying assertion, technical evidence, and last verification reference.
- First screen must make clear: where the user is, which domain/scope they are working in, what state is inherited versus local, and what action is available next.
- Repeated actions: filter, search, edit, view, bulk import/export, inspect hierarchy, reconcile technical signals, and explain control coverage.

## Product Tone

- Should feel: operational, trustworthy, dense but readable, audit-ready, and built for repeated use by people with real tickets and meetings.
- Should not feel: like a marketing landing page, generic AI SaaS, a decorative dashboard, or an onboarding demo that hides the actual work.
- Copy style: direct labels, concrete domain language, short helper text only where it prevents mistakes. Avoid educational blocks where controls, filters, hierarchy, or status indicators can communicate the same thing.

## Trust And Risk

- Sensitive data: customer boundaries, compliance evidence, security findings, vulnerabilities, risk decisions, authentication settings, and MSP verification payloads.
- Failure states: stale evidence, expired assertions, missing customer hierarchy, broken inheritance, hidden fields due to role permissions, failed imports, failed verification sync, and background API errors.
- Recovery expectations: users need visible error states, retry paths, clear validation messages, and audit-safe mutation flows. Destructive or broad actions should be explicit and reversible where possible.
- Evidence users need: status, result, source, last verified time, customer domains covered, provider control, related requirement/reference control, and whether a result was inherited or locally asserted.

## Anti-References

- Avoid these UI patterns: cards inside cards, hero sections in app workflows, decorative gradients, oversized empty-state illustrations, long explanatory panels, and layout that makes tables fight with onboarding copy.
- Avoid these words or tones: vague "seamless", "powerful", "AI-driven", "unlock", or "single pane of glass" language.
- Avoid these product assumptions: CISO Assistant is not a PSA, ticketing system, endpoint manager, or Bifrost replacement. Bifrost proves and updates signals; CISO Assistant records, reviews, and reports them.
