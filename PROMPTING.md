1
The Key Fact: Each Worker Is Its Own Process
Remember from earlier: each Gunicorn worker is a separate process.

A process is like its own little world inside your computer. It has:

Its own memory

Its own variables

Its own copy of your Python code

Two processes cannot see each other's variables. Ever. This is by design — it's how operating systems keep programs from stepping on each other.
you mean each process has a complete copy of my flask application?

2
So on modern Python, import app can succeed without __init__.py — as long as project/ is on sys.path.
how to know if it's in the sys.path

3
f the f-string is inside a SQL query but only interpolates a hardcoded value chosen from a whitelist (like a fixed column name chosen by an if/else), that's a lower-severity finding — a code smell but not exploitable — and should be noted.
if a variable comes from user input directly does this approach make the programm faster?
4
tell me what to do like i know nothing about postman
5
there are 5 type of request data handler in flask, get_json from react apps, and .form for getting from forms, what about the others
6
i mean i already have the schema, how to extract it's code