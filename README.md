# Circuit Breaker Pattern
## Solution
Solution is in [circuitbreaker.py](https://github.com/kyphutruong/circuit-breaker-pattern/blob/main/circuitbreaker.py)

## Documentation
Exception InvalidMethod is thrown/raised when an invalid method is specified in CircuitBreaker.do_request function

Exception CircuitOpenError is thrown/raised when the error_threshold is surpassed and the last error
occurred before passing "CircuitBreaker.time_window" seconds

CircuitBreaker._methods can be used to add/modify/delete http methods
It is mainly used as Http_Client interface so the class can be used with all http clients (and custom ones too)

CircuitBreaker._status_code is another lambda for getting the response code from the client's response
it is again used for compatibility between multiple clients

CircuitBreaker._empty_response is a variable that is returned when the request was unsuccessful
it can also be used for recursion, retry sending the request, the reason it is a lambda is because it's easier
to modify

To update "methods", modify "status_code" action, enable retries when a request fails you can do something like:

    if __name__ == "__main__":
        # initialize object
        breaker = CircuitBreaker(client_of_choice, error_threshold, time_window)

        # update methods
        breaker._methods = {"get": lambda url: breaker.http_client.get(url), "post": lambda url: breaker.http_client.post(url)}

        # modify status_code
        breaker._status_code = lambda response: response.status_code()

        # enable retries
        breaker._empty_response = lambda: breaker.do_request(breaker.prev_method, breaker.prev_url)

        # modify return value on failed attempts (when errorCounter doesn't surpass error_threshold)
        # to return None
        breaker._empty_response = lambda: None

CircuitBreaker.isOpen/isHalfOpen/isClosed are used to check the state of the circuit, they all return boolean typed values.

CircuitBreaker.clearState restores the breaker's state to Closed (forcefully)

CircuitBreaker.do_request is a function that, with a method and a url, sends an http request using the http_client
if the circuit is Open then an exception is raised


NOTE: CircuitBreaker assumes that a request succeeds ONLY if it's response status_code is 200
'''

## References
https://martinfowler.com/bliki/CircuitBreaker.html

https://bhaveshpraveen.medium.com/implementing-circuit-breaker-pattern-from-scratch-in-python-714100cdf90b

https://github.com/fabfuel/circuitbreaker
