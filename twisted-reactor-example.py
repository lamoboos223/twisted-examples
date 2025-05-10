from twisted.internet import reactor
import logging


logging.basicConfig(level=logging.DEBUG)

def task1():
    logging.debug("Executing task1 (scheduling delayed work)")
    reactor.callLater(3, finish_task1)

def finish_task1():
    logging.debug("Finished task1 after 3 seconds")

def task2():
    logging.debug("Executing task2")

def task3():
    logging.debug("Executing task3")

reactor.callWhenRunning(task1)
reactor.callWhenRunning(task2)
task3()
reactor.run()

