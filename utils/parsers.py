from xml.etree import ElementTree
from io import BytesIO

TEST_DATA = """
<?xml version="1.0"?>
<data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</data>
"""

TEST_DATA2 = """
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://www.shein.com/sitemap-category-sc.xml</loc>
        <lastmod>2021-09-30</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-article.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-campaign.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-pages.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-category-sp.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-category-sets.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-category-c.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://www.shein.com/sitemap-products-1.xml</loc>
        <lastmod>2021-10-02</lastmod>
    </sitemap>
</sitemapindex>
"""

class XML:
    parser = ElementTree
    _cached_content = None

    def __init__(self, content: str):
        self._cached_content = BytesIO(content)
        self.root = self.parser.fromstring(content)
        self.tag = self.root.tag

