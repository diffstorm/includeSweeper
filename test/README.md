# Test Project for includeSweeper Script

This is a test project designed to demonstrate and validate the functionality of the includeSweeper script. The includeSweeper script is used to identify and remove redundant include statements in C/C++ projects.

```bash
$ python src/includeSweeper.py --path "test/" --cmd "make"
Checking initial compilation...
Processing files...
Directory: /home/includeSweeper/test

Redundant Includes:
+----+-----------+-----------------+--------+
|    | Include   | File            |   Line |
+====+===========+=================+========+
|  0 | utils.h   | src/utils.c     |      1 |
+----+-----------+-----------------+--------+
|  1 | stdint.h  | src/utils.c     |      2 |
+----+-----------+-----------------+--------+
|  2 | limits.h  | src/utils.c     |      3 |
+----+-----------+-----------------+--------+
|  3 | stdlib.h  | src/main.c      |      4 |
+----+-----------+-----------------+--------+
|  4 | stdint.h  | src/main.c      |      5 |
+----+-----------+-----------------+--------+
|  5 | time.h    | src/main.c      |      6 |
+----+-----------+-----------------+--------+
|  6 | time.h    | include/utils.h |      5 |
+----+-----------+-----------------+--------+
|  7 | string.h  | include/utils.h |      6 |
+----+-----------+-----------------+--------+
```