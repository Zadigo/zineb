from zineb.html_parser.builders import BaseBuilder


# HTML = """
# <html>
#     <head>
#         <link type="text/css" href="http://example.com/example.css" />
#     </head>
#     <!-- Some comment -->
#     <body id="some-value">
#         <main>
#             <button class="btn btn-lg" data-toggle="something">Press me</button>
#             <p class="h1">Some value</p>
#         </main>
#     </body>
# </html>
# """

# HTML = """
# <html>
#     <p>test</p>
#     <p>test</p>
# </html>
# """

HTML = """
<html>
    <div id="title">
        <div>
            <img src="http://example.com">
        </div>
    </div>
</html>
"""


builder = BaseBuilder()
builder.start_iteration(HTML)
builder.finalize()
print(builder)
