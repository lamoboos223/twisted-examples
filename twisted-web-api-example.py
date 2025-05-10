from twisted.web import server, resource
from twisted.internet import reactor, threads, defer
import json
import time

# Simple GET endpoint
class HelloResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"Content-Type", b"application/json")
        return json.dumps({"message": "Hello, world!"}).encode("utf-8")

# Simple POST endpoint
class EchoResource(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        try:
            content = request.content.read()
            data = json.loads(content.decode("utf-8"))
            response = {"you_sent": data}
        except Exception as e:
            response = {"error": str(e)}

        request.setHeader(b"Content-Type", b"application/json")
        return json.dumps(response).encode("utf-8")

# Simulate a blocking operation in a thread pool (GOOD)
def long_blocking_task():
    time.sleep(10)
    return {"result": "This took a while."}

class HeavyResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"Content-Type", b"application/json")
        d = threads.deferToThread(long_blocking_task)

        def write_response(result):
            request.write(json.dumps(result).encode("utf-8"))
            request.finish()

        def handle_error(failure):
            request.setResponseCode(500)
            request.write(json.dumps({"error": str(failure)}).encode("utf-8"))
            request.finish()

        d.addCallbacks(write_response, handle_error)
        return server.NOT_DONE_YET

# Simulate a blocking operation on the main thread (BAD)
class BlockedResource(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        request.setHeader(b"Content-Type", b"application/json")

        # BAD: This will block the main reactor thread
        time.sleep(10)

        return json.dumps({"result": "Blocked the event loop!"}).encode("utf-8")

# Main site with endpoints
class RootResource(resource.Resource):
    def __init__(self):
        super().__init__()
        self.putChild(b"hello", HelloResource())
        self.putChild(b"echo", EchoResource())
        self.putChild(b"heavy", HeavyResource())   # Good async version
        self.putChild(b"blocked", BlockedResource())  # Bad blocking version

# Start the Twisted server
site = server.Site(RootResource())
reactor.listenTCP(8080, site)
print("Server started at http://localhost:8080")
reactor.run()
