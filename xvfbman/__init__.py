'''
    Copyright (c) 2018 - Timothy Savannah, All Rights Reserved

    Licensed under terms of GNU Lesser General Purpose License (LGPL) Version 2.1
    
    Distribution should contain a full copy of this license as LICENSE, or check
      https://raw.githubusercontent.com/kata198/xvfbman/master/LICENSE

    xvfbman - Manages Xvfb sessions
'''

#import copy
import os
import signal
import subprocess
#import sys
import time

from tempfile import NamedTemporaryFile

__version__ = '1.0.0'
__version_tuple__ = ('1', '0', '0', '')

__all__ = ('startXvfb', 'startXvfbRange', 'stopXvfb', 'stopAllManagedXvfbs',
            'getDisplayStrForServerNum', 'isUsingXvfb', 'ensureDisplayPresent',
            'registerAtExitCleanup', 
)

# xvfbPipes - The xvfb pipes, keyed by serverNum <int>
global xvfbPipes
xvfbPipes = {}


# xvfbOutputFiles - A write file to /dev/null which will be used for
#             stdout/stderr to each session
global xvfbOutputFiles
xvfbOutputFiles = {}

# DEFAULT_SCREEN_STR - The default screen config for Xvfb screen 0
DEFAULT_SCREEN_STR = '1280x720x24'

def isUsingXvfb(serverNum=None):
    '''
        isUsingXvfb - Test if we are using Xvfb,
        
            optionally at a specific server number

                @param serverNum <None/int> Default None - If None, tests if

                    we have ANY Xvfb sessions managed.

                  If an int, tests at a specific server number

                 
                 @return <bool> - True if we are managing Xvfb, otherwise False
    '''
    global xvfbPipes

    if serverNum is None:
        return bool( xvfbPipes )

    return bool( int(serverNum) in xvfbPipes )


def getDisplayStrForServerNum(serverNum):
    '''
        getDisplayStrForServerNum - Gets the DISPLAY string for a given

            server number

                @param serverNum <int> - Server number


                @return <str> - The DISPLAY string that references the given session
    '''
    return ':' + str(serverNum) + '.0'


def startXvfb(serverNum, screenStr=DEFAULT_SCREEN_STR):
    '''
        startXvfb - Starts a managed Xvfb session at a given server num

            @param serverNum <int> - Server number

            @param screenStr <str> Default '1280x720x24' - 
                
                Screen configuration for this Xvfb


            @return True

            @raises -
                      ValueError - We are already managing an Xvfb on #serverNum

                      KeyError - Failed to start Xvfb on #serverNum because #serverNum
                                    already in use

                      OSError  - Failed to start Xvfb on #serverNum for reason
                                    other than #serverNum in use

                                 Exception str will contain exit code and output

    '''

    global xvfbPipes
    global xvfbOutputFiles

    serverNum = int(serverNum)

    if isUsingXvfb(serverNum):
        raise ValueError('Tried to start Xvfb on server num %d, but one is already open.' %(serverNum, ))

    # Lock this serverNum
    xvfbPipes[serverNum] = None

    serverNumStr = ':' + str(serverNum)

    xvfbOutputFile = NamedTemporaryFile(mode='w')

    xvfbOutputFiles[serverNum] = xvfbOutputFile

    try:
        xvfbPipe = xvfbPipes[serverNum] = subprocess.Popen(['/usr/bin/Xvfb', serverNumStr, '-screen', '0', screenStr], shell=False, stdout=xvfbOutputFile, stderr=xvfbOutputFile)
    except Exception as exc:
        # Cleanup and unlock if we failed to launch subprocess
        del xvfbOutputFiles[serverNum]
        try:
            xvfbOutputFile.close()
        except:
            pass

        del xvfbPipes[serverNum]

        # Raise exception as OSError
        raise OSError('Got exception trying to start Xvfb on %s. %s:  %s' %(serverNumStr, str(type(exc)), str(exc)) )

    
    # Wait for up to 3 seconds for the Xvfb program to crash
    for i in range(3 * 2):
        time.sleep(.5)

        exitCode = xvfbPipe.poll()
        if exitCode is not None:
            
            try:
                xvfbPipe.wait()
            except:
                pass

            xvfbOutputFile.flush()
            try:
                with open(xvfbOutputFile.name, 'rt') as f:
                    xvfbOutput = f.read()
            except:
                xvfbOutput = 'ERROR: Could not read output file "%s"' %(xvfbOutputFile.name, )

            del xvfbOutputFiles[serverNum]
            try:
                xvfbOutputFile.close()
            except:
                pass

            # Unlock last
            del xvfbPipes[serverNum]

            if 'Server is already active for display' in xvfbOutput:
                exceptionStr = 'Failed to start Xvfb on %d. Exit code %d. Server is already active for display %s' %(serverNum, exitCode, getDisplayStrForServerNum(serverNum) )
                raise KeyError(exceptionStr)
            else:
                exceptionStr = 'Failed to start Xvfb on %d. Exit code %d. Output:\n%s' %(serverNum, exitCode, xvfbOutput)
                raise OSError(exceptionStr)

    return True


def startXvfbRange(startTryNum, lastTryNum, screenStr=DEFAULT_SCREEN_STR):
    '''
        startXvfbRange - Try to start an Xvfb using a range of possible

            server numbers. Use this if multiple instances of Xvfb sessions could
             be running.

               @param startTryNum <int> - The first server num to attempt

               @param lastTryNum <int> - The last server num to attempt

               @param screenStr <str> Default '1280x720x24' - The screen configuration to use


               @return <int> - The server num we succeded on starting a
                
                     Xvfb session.


               @raises -
                            KeyError - Could not start an Xvfb session on any
                                        server num in range because all were
                                        in use.

                            OSError  - Could not start an Xvfb session because
                                         Xvfb crashed for a reason other than
                                         another session is active on serverNum
    '''
    for tryServerNum in range(startTryNum, lastTryNum + 1, 1):
        
        # If we are already managing this number, skip
        if isUsingXvfb(tryServerNum):
            continue

        try:
            startXvfb(tryServerNum, screenStr)
        except ValueError:
            # Race condition catch
            continue
        except KeyError:
            # Already a session active on this address
            continue
        except OSError:
            # A real problem starting Xvfb, raise
            raise


        # If we got here, we have successfully started Xvfb
        return tryServerNum

    # If we got here, we've exhausted all server numbers and all are active
    raise KeyError('Failed to start an Xvfb session on any server num in range %d --> %d inclusive. All were in use.' %(startTryNum, lastTryNum) )



def stopXvfb(serverNum):
    '''
        stopXvfb - Stops a managed Xvfb session on a given server number

            @param serverNum <int> - The server number


            @return <bool> - True on success, 
                        False if there was no managed session on #serverNum
    '''
    global xvfbPipes
    global xvfbOutputFiles

    serverNum = int(serverNum)

    if not isUsingXvfb(serverNum):
        return False

    # Use .get to cover race condition, consider None a valid option
    #   so use 'x' as the miss default
    xvfbPipe = xvfbPipes.get(serverNum, 'x')
    if xvfbPipe == 'x':
        return False

    if xvfbPipe is None:

        # Placeholder value, so sleep up to past what startXvfb would
        #   take, and if still placeholder clear, otherwise we have
        #   the pipe to stop.
        didFindPipe = False

        for i in range(4 * 2):
            time.sleep(.5)

            xvfbPipe = xvfbPipes.get(serverNum, 'x')
            if xvfbPipe is None:
                continue
            if xvfbPipe == 'x':
                return False

            # At this point, the pipe has been set
            didFindPipe = True
            break

        if didFindPipe is False:
            # Still a placeholder, startXvfb must have failed in a bad way.
            #  Cleanup the mess
            if serverNum in xvfbOutputFiles:
                try:
                    xvfbOutputFiles[serverNum].close()
                except:
                    pass
                try:
                    del xvfbOutputFiles[serverNum]
                except:
                    pass

            # And unset the "None" placeholder entry
            del xvfbPipes[serverNum]

            # I guess True? Since we did clean up a failed entry
            return True

    # end if xvfbPipe is None

    # Send terminate signal
    try:
        xvfbPipe.terminate()
    except:
        try:
            os.kill(xvfbPipe.pid, signal.SIGTERM)
        except:
            pass
    
    isDone = False
    # Wait up to 3 seconds to terminate cleanly
    for i in range(3 * 4):

        time.sleep(.25)

        if xvfbPipe.poll() is not None:
            isDone = True
            break

    if not isDone:
        # If we are still alive, send the kill
        try:
            xvfbPipe.kill()
        except:
            pass
        
        time.sleep(.05)
        if xvfbPipe.poll() is not None:
            try:
                os.kill(xvfbPipe.pid, signal.SIGKILL)
            except:
                pass

    # At this point, should be dead or processing SIGKILL
    try:
        xvfbPipe.wait()
    except:
        pass

    
    # Now can close the associated output files
    xvfbOutputFiles[serverNum].close()
    del xvfbOutputFiles[serverNum]

    # And delete the pipe
    del xvfbPipes[serverNum]

    return True


def stopAllManagedXvfbs():
    '''
        stopAllManagedXvfbs - Stops all Xvfb's managed by this process

            @return <int> - The number of Xvfb's stopped
    '''
    global xvfbPipes

    # Make a copy as this will be changing
    serverNums = list( xvfbPipes.keys() )

    for serverNum in serverNums:
        stopXvfb(serverNum)


    return len(serverNums)


def ensureDisplayPresent(xvfbStartNum=50, xvfbLastNum=99, screenStr=DEFAULT_SCREEN_STR):
    '''
        ensureDisplayPresent - Ensure we have either DISPLAY env var set,

            or we attempt to start an Xvfb session via startXvfbRange

                @param xvfbStartNum <int> Default 50 - If DISPLAY is not set,
                    
                    try to start Xvfb from here to #xvfbLastNum inclusive

                @param xvfbLastNum <int> Default 99 - If DISPLAY is not set,

                    try to start Xvfb from #xvfbStartNum to here inclusive

                @param screenStr <str> Default DEFAULT_SCREEN_STR - If DISPLAY

                    is not set, try to start Xvfb using this screen configuration


                NOTE: This will set the environment variable 'DISPLAY' if not already set


                @return <bool> - True if we did setup an Xvfb and set DISPLAY,

                    False if we use existing DISPLAY
    '''

    curDisplay = os.environ.get('DISPLAY', '')

    if not curDisplay:
        
        serverNum = startXvfbRange(xvfbStartNum, xvfbLastNum, screenStr)
        os.environ['DISPLAY'] = getDisplayStrForServerNum(serverNum)
        
        return True

    return False


def registerAtExitCleanup():
    '''
        registerAtExitCleanup - Register an "at exit" handler which will
            
            cleanup/close any Xvfb sessions we are managing
    '''
    import atexit
    atexit.register( stopAllManagedXvfbs )


#vim: set ts=4 sw=4 st=4 expandtab :
