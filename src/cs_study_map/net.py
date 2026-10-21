"""Keep credentials on the explicitly configured endpoint."""

import urllib.request


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def open_without_redirects(request, timeout):
    # Redirects can replay credentials or a billable inference body elsewhere.
    return urllib.request.build_opener(RejectRedirects()).open(request, timeout=timeout)
