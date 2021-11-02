from zineb.html_parser.builders import BaseBuilder
from zineb.html_parser.soup import Soup

HTML = """
<html>
    <head>
        <link type="text/css" href="http://example.com/example.css" />
    </head>
    <!-- Some comment -->
    <body id="some-value">
        <main>
            <button class="btn btn-lg" data-toggle="something">Press me</button>
            <p class="h1">Some value</p>
        </main>
    </body>
</html>
"""



# builder = BaseBuilder()
# builder.start_iteration(HTML)
# builder.finalize()
# tag = builder.html_tree[1]
# print(builder.html_tree)
# print(builder.html_tree[1].contents)


soup = Soup(HTML)
t = soup.builer.html_tree[1]
print(t.contents)
