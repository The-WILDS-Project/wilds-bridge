# LDT broker XML schemas

Vendored from [LowellObservatory/ligmos](https://github.com/LowellObservatory/ligmos/tree/master/ligmos/schemas),
`ligmos/schemas/` and `ligmos/schemas/xmlsamples/`.

- **Commit:** `5e7cf9e48627708fc32e3a8696086fa6f7b1fb42` (2025-09-16)
- **Fetched:** 2026-10-19

Only the telescope/instrument topics are vendored; the `lig.*` site and weather-station
schemas are not. Files are unmodified — refresh by re-downloading at a newer commit and
updating the hash above.

## Not covered upstream

- `wrs.loisTelemetry` — sample XML exists, but no XSD.
- `TCSTcsStatusSV` v1.9 — only `@1_0` and `@1_8` exist; tanagra was publishing v1.9 on 2026-04-29.
- TCS command topics (`TCSTcsCommandSV`, `NewScienceTargetSV`) — schema "TBD" per the
  DCT Science Instrument Software Interface (v78, `docs/`).
- `AOS.AOSSubDataSV.*` focus commands — plain single-value messages, no schema by design.
