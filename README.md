scheduler
==========

`attachment` is a project to manage schedules, making decisions for the user.


Events
------

To create a new event, simply create a new file with the event name as
filename. The contents dictate the time and duration of the event, for example:
`every day from 11:30 am to 12:30 pm'.

*scheduler* automatically notifies you when an event starts.


Tasks
-----

Tasks are very similar to events, but they don't specify start and end times,
only duration and due date. The basic format is:

`write example task.txt`

`15 minutes due next Friday`

When running, *scheduler* automatically finds a time slot for this task and
notifies you when it's time to start it.


Natural Language
---------

*scheduler* supports many natural language constructs.

Event examples:

- `every weekday except Friday from 2 pm to 6 pm`
- `next Tuesday 21:00 to 22:00`
- `March 23 from 11 pm to 2 am`


Task examples:

- `15 minutes due next Friday`
- `2 hours due March 23`
- `30 seconds due tomorrow`
