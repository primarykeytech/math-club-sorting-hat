# The Sorting Hat (TM)

A tiny command-line program that randomly places students listed one per line in a text file into balanced groups.

## Use

As shown in `sample_students.txt`, create a file like `students.txt`:

```text
Ada Lovelace
Grace Hopper
Katherine Johnson
Alan Turing
```

Run the program from this folder:

```powershell
python sorting_hat.py students.txt 2
```

The last argument is the number of groups. The program skips blank lines, shuffles names, and keeps the group sizes as equal as possible. To get the same result again, provide a seed:

```powershell
python sorting_hat.py students.txt 2 --seed 42
```

## Test

```powershell
python -m unittest -v
```
