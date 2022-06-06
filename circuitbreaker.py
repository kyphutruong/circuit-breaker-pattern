import time
import random


class InvalidMethod(Exception):
    pass


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, http_client, error_threshold, time_window):
        self.http_client = http_client
        self.error_threshold = error_threshold
        self.time_window = time_window


        # Http client settings
        self._methods = {
            "get": lambda url: self.http_client.get(url),
            "post": lambda url: self.http_client.post(url)
        }

        self._status_code = lambda resp: resp.status_code()
        self._empty_response = lambda: None



        # Circuit Specific
        self.__lastRequest = 0
        self.__errorCount = 0

        # Backup for recursion mechanism
        self.prev_method = None
        self.prev_url = None


    def isOpen(self):
        return (self.__errorCount >= self.error_threshold) and (time.time() - self.__lastRequest < self.time_window)

    def isHalfOpen(self):
        return (self.__errorCount >= self.error_threshold) and (time.time() - self.__lastRequest >= self.time_window)

    def isClosed(self):
        return self.__errorCount < self.error_threshold


    def clearState(self):
        self.__lastRequest = 0
        self.__errorCount = 0


    def do_request(self, method, url):
        # make method case-insensitive
        method = method.lower()

        # check if method is valid
        if method in self._methods:


            # if circuit is open throw exception
            if self.isOpen():
                raise CircuitOpenError("CircuitBreaker is open")


            # make a backup of the previous options
            self.prev_method = method
            self.prev_url = url


            # try to send an http_request
            try:
                resp = self._methods[method](url)
                if self._status_code(resp) == 200:
                    self.clearState()
                    return resp
            except Exception:
                pass


            # update errorCount and lastRequest ONLY when an actual request failed
            self.__errorCount += 1
            self.__lastRequest = time.time()
            return self._empty_response()
        else:
            raise InvalidMethod(f"Invalid method selected: {method}\nPlease select one of the following: {list(self._methods.keys())}")




# Testing Classes

class FakeResponse():
    def __init__(self, status_code = 404, empty = False):
        self._status_code = status_code
        self.empty = empty

    def isEmpty(self):
        return self.empty

    def status_code(self):
        return self._status_code


class FakeHttpClient():
    state = 0 # 0 = random, 1 = fail, 2 = succeed
    def randomizeReturn(self):
        print("Sending Request")
        if self.state == 0:
            r = random.randint(0, 2)
        elif self.state == 1:
            r = random.randint(1, 2)
        else: # self.state == 2
            r = 0

            
        
        if r == 0:
            return FakeResponse(200, False)
        elif r == 1:
            return FakeResponse(404, False)
        else: # r == 2
            raise TimeoutError()
    
    def get(self, url):
        return self.randomizeReturn()

    def post(self, url):
        return self.randomizeReturn()



def testBreaker(breaker):
    url = "https://wetransfer.com"
    method = random.choice(["get","post"])
    resp = breaker.do_request(method, url)
    print(method, url, resp.status_code())
    print('Breaker: lastRequest =', time.time() - breaker._CircuitBreaker__lastRequest, 'errorCount =', breaker._CircuitBreaker__errorCount)
    print('Breaker Open State?', breaker.isOpen(), '\n\n')
    return resp


# Testing Classes stop here


# Test Case
if __name__ == "__main__":
    # TODO: Instantiate and configure stub_client
    stub_client = FakeHttpClient()
    x = 5 # error_threshold
    y = 4 # time_window

    breaker = CircuitBreaker(stub_client, x, y)
    breaker._empty_response = lambda: FakeResponse(empty = True)
    breaker._methods = {
        "get": lambda url: breaker.http_client.get(url),
        "post": lambda url: breaker.http_client.post(url)
    }

    # TODO:
    # 
    # Loop N number of times to simulate consecutive requests.
    # Demonstrate that the circuit opens after some number of
    # failures.

    # 3 succesful requests
    stub_client.state = 2
    for i in range(3):
        testBreaker(breaker)

    # 5 errors
    stub_client.state = 1
    for i in range(5):
        testBreaker(breaker)


    try:
        testBreaker(breaker)
    except:
        print("Exception thrown")

    
    # Then, wait a while, you may sleep ().
    print(f"Waiting for {y} seconds")
    time.sleep(y)
    print(f"Open: {breaker.isOpen()}, HalfOpen: {breaker.isHalfOpen()}, Closed: {breaker.isClosed()}")
    
    # Demonstrate that the circuit has closed and that requests to the
    # stub client flow freely.
    stub_client.state = 2
    for i in range(10):
        try:
            resp = testBreaker(breaker)
            print(f"StatusCode: {resp._status_code}, Empty?: {resp.empty}")
        except Exception as err:
            print('Exception thrown')
        stub_client.state = 0
