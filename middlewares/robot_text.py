from zineb.utils.conversion import transform_to_unicode
from urllib.robotparser import RobotFileParser

class RobotText:
    text = ''
    parser = RobotFileParser()

    def __init__(self):
        pass

    def __call__(self, sender, url):
        self.parser.set_url(url)
        self.parser.read()
        self.parser.site_maps()
        self.text = transform_to_unicode('')


r = RobotFileParser()
r.set_url('https://www.prettylittlething.us/robots.txt')
# r.set_url('http://www.musi-cal.com/robots.txt')
r.read()
c = r.can_fetch('*', 'https://www.prettylittlething.us/')
print(c)
