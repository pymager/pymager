from twisted.web import http
from twisted.web2 import static

class RequestHandler(http.Request):
    pages = {
        '/': '<h1>Home</h1>Home page',
        '/test': '<h1>Test</h1>Test page',
        }
    def process(self):
        import time
        time.sleep(10)
        if self.pages.has_key(self.path):
            self.write(self.pages[self.path])
        else:
            self.setResponseCode(http.NOT_FOUND)
            self.write("<h1>Not Found</h1>Sorry, no such page.")
        self.finish( )
class MyHttp(http.HTTPChannel):
    requestFactory = RequestHandler
class MyHttpFactory(http.HTTPFactory):
    protocol = MyHttp