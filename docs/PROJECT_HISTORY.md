# Project history

The scoring workflow originated in the operational needs of the **Torneio Brasileiro de Debates do Ensino Médio (TBDEM)**, Brazil's national high-school debate championship.

A preliminary tournament-specific workflow was used during TBDEM 2024. In 2025, the ranking logic was reconstructed into a Python/pandas pipeline that handled team results, individual speaker averages, reply speeches, eligibility rules, and iron/double-speech cases.

The present repository formalizes and extends that work into a reusable software project. The current version adds:

- explicit data schemas;
- English and Portuguese column normalization;
- validation before ranking;
- format-specific scoring modules;
- a British Parliamentary/WUDC implementation;
- a browser-based interface;
- command-line tooling;
- standardized Excel exports;
- tests and continuous integration;
- documented scoring assumptions and sources.

The historical TBDEM reconstruction is retained in `legacy/tbdem_2025_reconstruction.py` as a compact reference point for how the original scoring pipeline evolved into the current architecture.
