Security note
=============

TODO: add some kind of automated support to avoid CSFR (https://en.wikipedia.org/wiki/Cross-site_request_forgery)

One of the common security flaws of web apps is Cross Site Request Forgery.

Either:
- provide auth-creditentials on each request

Or make a double token check:
- provide a HTTP-Only cookie containing your session ID (to prove your're authenticated and prevent XSS, done by Canister)
- and provide an additional token as parameter or in a "X-Csrf-Token" header (to prove it comes from your Browser and prevent CSFR, must be done client side through javascript)

...however, the issue is that this method requires client side stuff in the page (through hidden fields, request parameters or setting specific headers through javascript)

Alternatively, the Referer Header can be checked.
How does this prevent CSRF?
- if the request doesn't come from the browser, the cookie/session-id is unknown
- if it comes from the browser, we can ensure it comes from the site itself
 
...however, the issue in case is that the header is sometimes removed (because of a privacy proxy or plugin, but I think it's pretty seldom)


