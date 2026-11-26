<p align="center">
  <img src="up_emblem_cover_crop.png" alt="University of Prishtina emblem" width="130">
</p>

# Fuzzing Experiment Lab

This repository contains a **small educational fuzzing case study** prepared for the course **Software Design and Analysis**.
It connects:

- **Paper A**: the general fuzzing model and taxonomy by **Manès et al.**
- **Paper B**: the practical developer challenges during fuzzing reported by **Nourry et al.**
- **Our lab**: four controlled experiments implemented in Python and C++

The goal is **not** to benchmark Python vs. C++, and **not** to reproduce the original papers in full.
Instead, the project demonstrates how fuzzing can automatically generate inputs, reveal failures, replay them, and verify a corrected version.

---

## Project scope

We use four intentionally simplified targets:

| Experiment | Language | Tool | Main detection mechanism | Purpose |
|---|---|---|---|---|
| 1 | Python | Atheris | Unexpected exception | Demonstrates failure caused by missing validation |
| 2 | Python | Atheris | Reference oracle mismatch | Demonstrates detection of logically incorrect output |
| 3 | C++ | libFuzzer + ASan | Heap buffer overflow | Demonstrates memory-safety detection |
| 4 | C++ | libFuzzer + LSan | Memory leak | Demonstrates leak detection |

These examples are deliberately small and academic, so the focus stays on the **fuzzing workflow**, not on industrial-scale performance.

---

## How this relates to the two papers

### Paper A — Manès et al.
Paper A provides the **technical model** of fuzzing:

- preprocess / configure
- schedule
- input generation
- input evaluation
- configuration update

Our implementation does **not** build a new fuzzing engine from scratch.  
Instead, it uses **Atheris** and **libFuzzer** as the execution engines, while our code defines the targets, harnesses, oracles, and replay logic.

### Paper B — Nourry et al.
Paper B studies the **human and practical side** of fuzzing and reports challenges such as:

- **F15**: generating appropriate inputs
- **F16**: configuration effort
- **F14**: reproducing failures
- **F18**: diagnostics and understanding reports

Our laboratory experiments are used to **illustrate** these challenges conceptually:

- Experiments 1 and 2 show how input structure and correctness checks matter.
- Experiments 3 and 4 show why configuration, replay, and diagnostics are important.

So, the connection is:

**Paper A explains the fuzzing model** → **our lab demonstrates it in a controlled way** → **Paper B explains the practical difficulties developers face when applying it**.

---

## Folder structure

```text
Experiment/
├── .streamlit/                 # Streamlit configuration
├── app.py                      # Main interactive dashboard
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── up_emblem_cover_crop.png   # University of Prishtina emblem
├── Eksperimenti 3.json        # Recorded results for experiment 3
├── Eksperimenti 4.json        # Recorded results for experiment 4
├── experiment_1/              # Python / Atheris target 1
├── experiment_2/              # Python / Atheris target 2
├── experiment_3/              # C++ / libFuzzer + ASan target 3
├── experiment_4/              # C++ / libFuzzer + LSan target 4
├── scripts/                   # Helper scripts for running and validation
├── tests/                     # Smoke test(s) for the UI logic
├── archive_previous_results/  # Older archived evidence from earlier versions
└── preview.py                 # Optional helper preview script
```

### What are the `run-...` folders?
Folders such as `run-zu3wk8iv` or `run-ey4cep61` are **automatically created run directories**.
They store artifacts from one fuzzing execution, for example:

- generated corpora
- crash files
- replay logs
- buggy/fixed execution logs
- temporary binaries

They are useful as **evidence** for the recorded run.  
If a JSON result file points to logs or artifacts inside such a folder, that folder should be kept.

---

## Requirements

### Python
- Python 3.10+ recommended
- `pip`
- Streamlit
- pandas
- Atheris (for Python fuzzing)

### C++ experiments
- Linux or WSL Ubuntu recommended
- `clang++`
- libFuzzer support in Clang
- AddressSanitizer / LeakSanitizer

---

## Installation

From the `Experiment` directory:

### On Linux / WSL Ubuntu
```bash
sudo apt update
sudo apt install -y clang python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install atheris
```

### On Windows
You can run the **Streamlit dashboard** in Windows Python, but the **C++ fuzzing experiments** are best executed in **WSL Ubuntu** because they require `clang++` and sanitizer support.

---

## Running the project

### 1. Run the dashboard
From the `Experiment` directory:

```bash
python -m streamlit run app.py
```

Then open the local URL shown in the terminal.

### 2. Run the experiments manually

#### Python targets
```bash
python experiment_1/run_experiment.py
python experiment_2/run_experiment.py
```

#### C++ targets
```bash
python experiment_3/run_experiment.py
python experiment_4/run_experiment.py
```

### 3. Deterministic checks
```bash
python scripts/deterministic_checks.py
```

---

## About the recorded JSON files

The files:

- `Eksperimenti 3.json`
- `Eksperimenti 4.json`

contain the currently recorded verified results for the C++ experiments.

If Experiments 1 and 2 are not yet shown as complete in the UI, that means a fresh Atheris fuzzing campaign has not been recorded yet in the current environment.
This is normal if Atheris is not installed or was not run locally.

---

## Important interpretation notes

- This project is a **teaching demonstration**, not an industrial benchmark.
- Run counts should **not** be used to compare Python vs. C++ or one fuzzer against another.
- A successful fixed run does **not** prove that the program is fully correct.
- The experiments are intentionally small in order to clearly show the mechanism of fuzzing, detection, replay, and verification.

---

## Main references

[1] V. J. M. Manès, H. Han, C. Han, S. K. Cha, M. Egele, E. J. Schwartz, and M. Woo,  
*The Art, Science, and Engineering of Fuzzing: A Survey*, IEEE Transactions on Software Engineering, vol. 47, no. 11, pp. 2312–2331, 2021.  
DOI: 10.1109/TSE.2019.2946563

[2] O. Nourry, Y. Kashiwa, B. Lin, G. Bavota, M. Lanza, and Y. Kamei,  
*The Human Side of Fuzzing: Challenges Faced by Developers During Fuzzing Activities*, ACM Transactions on Software Engineering and Methodology, vol. 33, no. 1, art. 14, 2024 (online 2023).  
DOI: 10.1145/3611668

---

## Credits

**Prepared by:** Kaltrina Krasniqi  
**Course:** Software Design and Analysis  
**Instructor:** Prof. Ass. Dr. Dhuratë Hyseni  
**Institution:** Faculty of Electrical and Computer Engineering, Master, University of Prishtina
