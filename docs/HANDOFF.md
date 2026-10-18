# Manual handoff

The local demonstration is implemented and available in English. Issue #17 still
requires provider credentials and human judgment. Running the demonstration
without an API key requires no additional manual implementation.

## Complete the live evaluation for #17

1. Copy `.env.example` to `.env` and configure your Gemini key and a model with
   Structured Outputs available in your account. Keep the credentials private.
2. Read [the protocol](EVALUATION_PROTOCOL.md), then run:

   ```sh
   python evaluate_affinity.py --live --repeats 3 --output artifacts/affinity-live.json
   ```

   This makes up to 36 billable calls: 6 queries × 2 variants × 3 repetitions.
   The empty-selection case can skip a JEV call. Avoid repeated live runs.
3. Inspect call status, truncation, available token counts and p50/p95 by variant.
   Record the model's verified tariff and its date before calculating costs.
   Null cost means unmeasured; a failed call is not evidence of savings.
4. Review each explanation claim and evidence ID. Record reviewer, date,
   supported/unsupported/inconclusive classification and reason. Check ordering,
   requirements and claims beyond the supplied evidence. Explanations should be
   in English for both variants.
5. Annotate an independent set of real queries before evaluating external
   relevance. Review national versus regional or de facto official-language
   status, current validity and national aggregation. The historical snapshot
   does not substitute for this review.
6. Save the reviewed report in `docs/evaluations/`, update the remaining items in
   #17, and close it once that evidence is available. There is currently no
   measured claim of monetary savings or external ranking superiority.

## Demonstration and publication

- Run `python -m streamlit run src/app.py`, confirm the criteria, then check hover,
  zoom, country search, VAT/PSE entries, JSON export and a narrow screen layout.
  The browser needs CDN geometry while recording. Microstates remain searchable.
- Follow [the English video script and post draft](PORTFOLIO.md). Review the final
  wording and framing before publishing.
- Hosting is optional. A Streamlit-compatible host needs `src/app.py`, Python
  3.12+ and `requirements.txt`. Keep API keys in the host's secret manager, allow
  the map CDN and verify quotas. The demonstration works without credentials.
- Integration targets `develop`. Promotion to `main` and a public deployment can
  follow the hosting decision and release review.
