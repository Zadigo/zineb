NORMAL_HTML = """
<html>
    <body>
        <a id="test">Question</a>
        <a href="http://example.com">
            <span>Height</span>
            <span>173cm</span>
        </a>
        <a class="google">Test</a>
        <div>
            <span id="1">Fast</span>
        </div>
    </body>
</html>
"""


INLINE_HTML = """<html><span>Amazing</span><span>Amazing2</span></html>"""


NONE_FORMATTED_HTML = """
<html>
<head>
<title>Page title</title>
<link href="http://example.com" />
</head>
<body>
Some text
</body>
</html>
"""


# s = """<html><head><link href="http://example.com"/></head></html>"""


# s = """<html><head><title>Something</title></head></html>"""


COMMENT_HTML = """<html><body><!-- My comment --><span>Something</span></body></html>"""


TABLE_HTML = """<html><body><table id="my-table"><tbody><tr><td>1</td><td>2</td></tr></tbody></table></body></html>"""


SIBLINGS_HTML = """
<html>
    <body>
        <div>
            <span>1</span>
        </div>
        
        <div>
            <span>2</span>
        </div>
    </body>
</html>
"""


SIMPLE_HTML = """
<html>
    <body>
        <span id="1">1</span>
        <span id="2">2</span>
    </body>
</html>
"""


IMAGE_HTML = """
<html>
    <body>
        <img src="kendall.jpg">
        <div>
            <img src="kylie.jpg">
        </div>
    </body>
</html>
"""
