Eksperimenti 4 — Memory leak

Ekzekutimi (Ubuntu/WSL me clang++):
  python3 experiment_4/run_experiment.py

Kjo përdor libFuzzer për gjenerimin e hyrjeve dhe AddressSanitizer/LeakSanitizer
për diagnostikimin e gabimeve të memories. Testohen vetëm funksione lokale
sintetike të krijuara për laboratorin. Shih JSON-in dhe log-et për metrikat.

Versioni buggy përmban një defekt demonstrues. Versioni fixed e trajton atë.
Ritestimi 10000 herë nuk provon mungesën e të gjitha defekteve.
