# Resume evidence integrity — 2026-10-28

One preregistered deterministic correction at baseline `9a4ca6cca99c52b8d87c800e8057cffd421ab01c`. An editable resume file could previously replace a retained excerpt with absent text while its source hash still matched. Resume now checks retained chunk identity, exact text, offsets, line references, query score, uniqueness and result bounds before mutation.

The frozen author-created cases improved from 7/15 to 15/15: eight malformed-evidence cases now reject, six valid normalized outputs remain byte-equivalent, and the source-preservation check passes. The native suite passed 51 tests with seven live/integration skips and five existing configuration warnings. These cases establish this regression boundary only; they are not statistically held-out usefulness evidence. User-editable jobs are not cryptographically authenticated. No provider call was made, no new PDF/OCR support is implied, and no source file or frozen Data artifact changed.
