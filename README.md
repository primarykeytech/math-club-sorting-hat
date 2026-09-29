# The Sorting Hat (TM)

A small Python app that randomly places students listed one per line in a text file into balanced groups. It includes both a desktop interface and a command-line mode.

**Disclosure**: An LLM assisted in the development of this app, but it was not 
entirely vibe coded.  

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

## Desktop app

Launch the graphical sorting experience with:

```powershell
python sorting_hat_app.py
```

Choose the student text file, enter the number of groups, and select **Start sorting**. The top-hat entry screen transitions to a results view, reveals each assignment with a short delay, and displays up to three group columns across.

The desktop app uses the included `magical_background.png` artwork as a decorative backdrop behind the readable content panels.
It opens fullscreen by default for projection; press `Esc` to leave fullscreen.

## Test

```powershell
python -m unittest -v
```
