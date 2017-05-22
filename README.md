# tt
## Introduction
`tt` (time-track) is a mysql- or sqlite-based program to keep track of time (for consultants, etc.) using Python commmands. It is a general -- and very simple -- time tracking program. A database has the following values:

* `date`: Should entered as 'mm/dd/yyyy' (as a string).
* `start`: The time one starts working; recorded as HH:MM. So, `8:15` would represent 8:15am and `17:45` would represent 5:45pm.
* `end`: The time one ends working; recorded as HH:MM (see above).
* `project`: A string (up to 8 characters long) for identify the project to charge against.

### Configuration file
There is a configuration file that is expected called `config.cfg` (see `config.cfg.example`) that takes care of specificing some values that might be unlikely to change very often (host, database, table). These are set __only__ if not set at the command line with the Python scripts.

### Environmental variables
In the `__init__` file, there are three environmental variables to be set. Two pertain to mysql use, so if your flavor of database is sqlite, these can be ignored. The third, `TT_PATH` represents the path to your clone of `tt` and is used for correctly reading the `config.cfg` file.

## Use
### Initializing the time-tracking database
To set up a time-tracking database, one must have mysql (currently 5.7.17) or sqlite3 installed locally on their machine. Then, using the `create.py` script, set up the database with a database name and table. A user can add additional tables into the same named database. Each time a table is initialized, a test entry is created. Usage is as follows:

For mysql:
```
$ python create.py -d my-time-db -t my-time-table -e mysql
```

For sqlite:
```
$ python create.py -d my-time-db -t my-time-table -e sqlite
```

### Adding entries
The `add.py` script is called to open or close an entry in the database.

To open an entry:
```
$ python add.py -t 9 -d '01/01/2017' -p gen
```

Where the `-t` or `--time` entry expects an integer or float. These entries should be something like `9` (for 9am), `9:15` (for 9:15am), `9:32` (for 9:32am), or `9:45` (for 9:45am). Note, the system expects a 24-hour clock, so 1:30pm would be entered as `13:30`.

The `-d` or `--date` entry expects a string date of the format `mm/dd/yyyy`. The `-p` or `--project` entry expects a string of no more than eight (8) characters. This is short-hand for the project that is being billed.

To close an entry:
```
$ python add.py -t 10:30 --close_entry
```

The `-t` or `--time` entry is as described above. The `-c` or `--close_entry` is a flag for the fact that the last entry should be closed, closing it with the time indicated in the command.

Note, the program will not let you open a time entry while another is closed; the command will abort and a warning that you need to close the earlier entry will be issued to the terminal.

Optionally, you can specify a database host, database name, and database table, if you need something that differs from your `config.cfg` setup. If none are specified at the command-line, then the defaults in the `config.cfg` file will be used.

### Analyzing entries
One can analyze time entries for a particular day or sequential range of days, both in table and graphical form.

To analyze time in table form (for a single day):
```
$ python analyze.py -d 01/01/2017 -a table
```

This command will summarize all time by project for 01 January 2017. It would look something like:
```
date        project
2017-01-01  proj1       01:00
            proj2       02:45
            gen         04:15
```

To analyze time in table form for a range of days:
```
$ python analyze.py -d 01/01/2017 01/03/2017 -a table
```

It would look something like:
```
date        project
2017-01-01  proj1       01:00
            proj2       02:45
            gen         04:15
2017-01-02  proj2       03:30
            proj3       02:45
            gen         03:00
2017-01-03  proj1       03:00
            proj2       04:15
            proj3       00:30
```

To analyze time in graphical form:
```
$ python analyze.py -d 01/01/2017 01/03/2017 -a graph
```

This will product an ASCII plot in the terminal over the range of days specified. This requires having `gnuplot` installed.

Finally, `python analyze.py -d 01/01/2017 01/03/2017 -a all` will produce both tabular and graphical output.

## Dependencies
This program requires a number of dependencies. First, `mysql` (or `sqlite3`) and `gnuplot` are external dependencies that are needed for proper functioning. Second, within Python, `pymysql` (or `sqlite3`) and `pandas` are dependencies.

## Symbolically linking the file for use in any directory
It may be cumbersome to type out the path name to `add` and `analyze` time data, so one option is symlinking those files for use across your system. This can be accomplished by:

1. Symbolically linking the file: `ln -s add.py /usr/local/bin/add`
2. Making it executable: `chmod +x /usr/local/bin/add`

This should allow the following command, for example, from any directory:

```
$ add -t 9 -d '01/01/2017' -p gen
```

## Conclusion
This is a basic, but functional, time tracking program. Feel free to submit PRs if you have features to add. If there are questions, contact Matt Hoover at matthew.a.hoover at gmail.com.
