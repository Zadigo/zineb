TEST_DATE_FORMATS = ['1987-1-1', '1.1.1987', '1-1-1987', '1/1/1987',
                'Oct 1, 1987', '1-1-02', '02-1-1', '1.1.02']

HTML_TAGS = [
    ('<p>See: &#39;&eacute; is an apostrophe followed by e acute</p>', 'See: &#39;&eacute; is an apostrophe followed by e acute'),
    ('<p>See: &#x27;&eacute; is an apostrophe followed by e acute</p>', 'See: &#x27;&eacute; is an apostrophe followed by e acute'),
    ('<adf>a', 'a'),
    ('</adf>a', 'a'),
    ('<asdf><asdf>e', 'e'),
    ('hi, <f x', 'hi, <f x'),
    ('234<235, right?', '234<235, right?'),
    ('a4<a5 right?', 'a4<a5 right?'),
    ('b7>b2!', 'b7>b2!'),
    ('</fe', '</fe'),
    ('<x>b<y>', 'b'),
    ('a<p onclick="alert(\'<test>\')">b</p>c', 'abc'),
    ('a<p a >b</p>c', 'abc'),
    ('d<a:b c:d>e</p>f', 'def'),
    ('<strong>foo</strong><a href="http://example.com">bar</a>', 'foobar'),
    # caused infinite loop on Pythons not patched with
    # https://bugs.python.org/issue20288
    ('&gotcha&#;<>', '&gotcha&#;<>'),
    ('<sc<!-- -->ript>test<<!-- -->/script>', 'ript>test'),
    ('<script>alert()</script>&h', 'alert()h'),
    ('><!' + ('&' * 16000) + 'D', '><!' + ('&' * 16000) + 'D'),
    ('X<<<<br>br>br>br>X', 'XX'),
]
