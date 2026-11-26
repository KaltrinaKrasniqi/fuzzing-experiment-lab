Eksperimenti 2 — Zbulimi i një gabimi logjik me Atheris

Rregulli i pikëve

Funksioni merr numrin e artikujve (0 deri në 255). Çdo artikull jep
një pikë dhe çdo grup i plotë prej tre artikujsh jep një pikë bonus.
Për n artikuj, rezultati është n + ⌊n/3⌋. Versioni fillestar përdor
kushtin n > 3, ndaj humb bonusin kur ka saktësisht tre artikuj.
Versioni i korrigjuar shton n // 3 për të gjithë domenin e testuar.

Kushti i saktësisë dhe zbulimi

Funksioni referencë ecën nëpër pozicionet e artikujve, shton nga një
pikë për secilin dhe shton bonusin në çdo pozicion shumëfish të tre.
Për çdo hyrje të Atheris, testi merr bajtin e parë si numrin e
artikujve dhe interpreton hyrjen boshe si zero. Kontrolli kërkon që
rezultati i funksionit të jetë i barabartë me rezultatin e referencës.
Kur ato ndryshojnë, harness-i ngre OracleMismatch me hyrjen dhe të
dyja vlerat. Vetë funksioni fillestar kthen normalisht një numër.

Ekzekutimi i regjistruar

Ubuntu 24.04 në WSL, Python 3.12.3, Atheris 3.1.0, seed 1, pa korpus
fillestar, hyrje deri në një bajt dhe kufi prej 10 000 ekzekutimesh për
version. Versioni fillestar raportoi mospërputhjen pas 429 ekzekutimesh
(1.200009 s). Artefakti përmban bajtin 0x03. Në riprodhim me këtë bajt,
versioni fillestar ktheu 3 pikë, referenca priste 4 dhe versioni i
korrigjuar ktheu 4. Versioni i korrigjuar përfundoi 10 000 ekzekutime
pa mospërputhje (2.323744 s). Kohët matin proceset e fuzzing-ut,
përfshirë nisjen e tyre.

JSON-i për dashboard-in ndodhet në dosjen prind. Referencat në JSON
tregojnë dy log-et origjinale, artefaktin dhe logun e riprodhimit.
Për ta përsëritur në një mjedis lokal Linux me Atheris 3.1.0, nga
dosja e projektit ekzekuto: python3 -B experiment_2/run_experiment.py
Çdo nisje ruan log-et në një nën-dosje të re dhe përditëson JSON-in.
