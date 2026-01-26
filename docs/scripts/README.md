Scripts
====

### Running these scripts
The python environment here is managed by `uv`.

Run the scripts with e.g.:

```
uv run scripts/0-create_dicoms.py
```

### Getting Help
Each script comes with help output, e.g.

```
$ uv run scripts/0-create_dicoms.py -h
usage: 0-create_dicoms.py [-h] [--dry-run]

Create DICOM files from TIFFs

options:
  -h, --help  show this help message and exit
  --dry-run   Don't write any files; just print what would be done instead
```

<details>
<summary> For developers: How to read code </summary>
In general, the script files here follow a common structure:

```
"""
docstring
"""
...helper functions...

def main():
   ...do stuff...

if __name__ == "__main__":
    ...parse args...
    main(args)

```

It's quite hard to figure out what's going on if you read these
files top-to-bottom, since the helper functions are implementation details and
aren't as important for the functionality as the rest of it.

If you're planning to make some changes to the source code,
you'll first want to read it to make sense of it and figure out
what to change.
I'd suggest reading the code in this order:
 1. Docstring (gives an overall summary of what the script does)
 2. Argparsing (tells you what options the script takes)
 3. main function (gives the highest level flow of execution)
 4. helper functions, if you need to

This is a sensible way to read things because the code effectively executes bottom-to-top (first argparsing, then `main`, which then calls the helper functions).

</details>