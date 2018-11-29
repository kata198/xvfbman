Xvfbman
=======

A python module focusing on managing Xvfb sessions / ensuring DISPLAY through a simple interface.


Why?
----

Xvfb is the X11 Virtual Frame Buffer, and basically implements a display without a monitor, just in memory.

This is useful for testing ( such as in conjunction with selenium ), profiling, or other automation task.


How
---

The xvfbman module provides an interface to start and manage Xvfb sessions, as well as providing a common interface your application can use to ensure a DISPLAY is set (either a real display or start a managed Xvfb which will be closed on exit).


**Ensuring DISPLAY**

A common usage would be for your application to use DISPLAY if already set or to start an Xvfb session otherwise.

This can be accomplished via the *ensureDisplayPresent* and *registerAtExitCleanup*.


*ensureDisplayPresent* will check if DISPLAY environment variable is set, and if not it will start an Xvfb session and set DISPLAY environment variable to match.


*registerAtExitCleanup* Will register an "atexit" handler which will ensure that all Xvfb sessions we opened (if any) will be closed.


    # Returns True if we setup an Xvfb, False if DISPLAY already set
    if ensureDisplayPresent():

        # If we setup an Xvfb, register the cleanup function
        registerAtExitCleanup()



**Starting Xvfb Sessions**

You can start Xvfb instances on-demand via *startXvfb* or *startXvfbRange*


*startXvfb* takes an argument, serverNum, which specifies the server ( e.x. serverNum=50 would be DISPLAY :50.0 ). You can also override the default value for "screenStr" ( 1280x720x24 ) to specify a different resolution and depth.


*startXvfbRange* takes two arguments, startServerNum and lastServerNum, as well as optional screenStr, and tries to start a server on every server number / display number in that inclusive range. If the display number is already in use, it moves onto the next one.

This will return the server num that ended up being used.


Use this function if your app can have multiple instances running, or for any condition where there would be contention over server numbers.


    try:
        # Start an Xvfb anywhere from :50 to :99 and return the one used
        serverNum = startXvfbRange(50, 99)
    except KeyError:
        # All servers 50-99 were in use
        raise
    except OSError:
        # Other error occured preventing Xvfb from working properly
        #  (Exception message will contain the output)



**Stopping Xvfb Session**

You can stop Xvfb instances via *stopXvfb* or *stopAllManagedXvfbs*


*stopXvfb* Takes a server number (integer) as an argument, and will stop the managed Xvfb running on that display.


*stopAllManagedXvfbs* Will stop ALL the Xvfb sessions being managed by the process


**Utility Functions**


*isUsingXvfb* - Tests if we are managing Xvfb sessions. Default / None for an argument will test if we have _any_ sessions managed, or passing an integer will check on a specific server num.


*getDisplayStrForServerNum* - Will convert a server number into a DISPLAY string (for use in DISPLAY env var, for example)



Full PyDoc
----------

Can be found at  http://htmlpreview.github.io/?https://github.com/kata198/xvfbman/blob/master/doc/xvfbman.html?vers=1.0.0 .


