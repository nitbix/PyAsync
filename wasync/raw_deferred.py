import core
import threading

class Raw_Deferred:
    """A unit of computation that runs in the background, which immediately returns a 
    promise that will be fulfilled at a later time."""
  
    def __init__(self,function=None):
        self.function = function
        self.callbacks = []
        self.result = None
        self.determination = threading.Event()
        self.blockers = []
        self.exc_info = None

    def determine(self,val):
        """In the normal flow, realise the value of the promise"""
        self.result = val
        self.determination.set()

    def determine_exception(self,exc_info):
        """Something threw an exception in the code thunk. This does not mean wasync is
        broken, but rather that the code running inside it threw."""
        self.result = None
        self.exc_info = exc_info
        self.determination.set()

    def is_determined(self):
        return self.determination.is_set()

    def is_blocked(self):
        if len(self.blockers) == 0:
            return False
        else:
            blocked = False
            for b in self.blockers:
                if isinstance(b,Raw_Deferred):
                    if b.is_blocked():
                        blocked = True

    def add_callback_f(self,f):
        raise Exception("deprecated")

    def add_callback(self,d,scheduler):
        """Hang a callback onto this deferred"""
        if not isinstance(d, Raw_Deferred):
            raise Exception("new usage model requires Raw_Deferred callbacks")
        if self.determination.is_set():
            #all other callbacks have been already scheduled
            scheduler.submit_job(d)
        else:
            self.callbacks.append(d)

    def add_blocker(self,d):
        self.blockers.append(d)
        
    def peek_opt(self):
        if not self.determination.is_set():
            return None
        else:
            if self.exc_info is None:
                return self.result
            else:
                raise (self.exc_info[0], self.exc_info[1], self.exc_info[2])

    def await(self):
        self.determination.wait()
        if self.exc_info is None:
            return self.result
        else:
            raise (self.exc_info[0], self.exc_info[1], self.exc_info[2])

    def await_result(self):
        return self.await()

    def bind(self,f):
        return core.bind(self,f)

    def chain(self,f):
        return core.chain(self,f)
