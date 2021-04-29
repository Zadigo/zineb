## Welcome Zineb homepage

Zineb is a lightweight tool solution for simple and efficient web scrapping and crawling built around BeautifulSoup and Pandas. It's main purpose is to help __quickly structure your data in order to be used as fast as possible in data science or machine learning projects.__

# Understanding how Zineb works

Zineb gets your custom spider, creates a set of ``HTTPRequest`` objects for each url, sends the requests and caches a BeautifulSoup object of the page within an ``HTMLResponse`` class of that request.

Most of your interactions with the HTML page will be done through the ``HTMLResponse`` class.

When the spider starts crawling the page, each response and request in past through the start function:

```
def start(self, response, **kwargs):
     request = kwargs.get('request')
     images = response.images
```

# Getting started

## Creating a project

To create a project do `python -m zineb startproject <project name>` which will create a directory which will have the following structure.

.myproject
|
|--media
|
|-- models
      |-- base.py
|
|-- __init__.py
|
|-- manage.py
|
|-- settings.py
|
|-- spiders.py

Once the project folder is created, all your interractions with Zineb will be made trough the management commands that are executed through `python manage.py` from your project's directory.

The models directory allows you to place the elements that will help structure the data that you have scrapped from from the internet.

The `manage.py` file will allow you to run all the required commands from your project.

Finally, the spiders module will contain all the spiders for your project.

## Configuring your project

On startup, Zineb implements a set of basic settings (`zineb.settings.base`) that will get overrided by the values that you would have defined in your `settings.py` located in your project.

You can read more about this in the [settings section of this file](#Settings).

## Creating a spider

Creating a spider is extremely easy and requires a set of starting urls that can be used to scrap one or many HTML pages.

```
class Celebrities(Zineb):
    start_urls = ['http://example.com']

    def start(self, response, request=None, soup=None, **kwargs):
        # Do something here
```

Once the Celibrities class is called, each request is passed through the `start` method. In other words the `zineb.http.responses.HTMLResponse`,  `zineb.http.request.HTTPRequest` and the `BeautifulSoup` HTML page object are sent through the function.

You are not required to use all these parameters at once. They're just for convinience.

In which case, you can also write the start method as so if you only need one of these.

```
def start(self, response, **kwargs):
  # Do something here
```

Other objects can be passes through the function such as the models that you have created but also the settings of the application etc.

### Adding meta options

Meta options allows you to customize certain very specific behaviours [not found in the `settings.py` file] related to the spider.

```
 class Celerities(Zineb):
    start_urls = ['http://example.com']
  
     class Meta:
         domains = []
```

#### Domains

This option limits a spider to a very specific set of domains.

#### Verbose name

This option writter as `verbose_name` will specific a different name to your spider.

## Running commands

#### Start

Triggers the execution of all the spiders present in the given the project. This command will be the main one that you will be using to execute your project.

#### Shell

Start a iPython shell on which you can test various elements on the HTML page.

When the shell is started, the `zineb.http.HTTPRequest`, the `zineb.response.HTMLResponse`, and the BeautifulSoup instance of the page are all injected in the shell.

Extractors are passed using aliases:

* `links`: LinkExtractor
* `images`: ImageExtractor
* `multilinks`: MultiLinkExtractor
* `tables`: TableExtractor


The extractors are also all passed within the shell in addition to the project settings.

In that regards, the shell becomes a interesting place where you can test various querying on an HTML page before using it in your project. For example, using the shell with http://example.com.

We can get a simple url :

```
IPython 7.19.0

In [1]: response.find("a")
Out[1]: <a href="https://www.iana.org/domains/example">More information...</a>
```

We can find all urls on the page:

```
IPython 7.19.0

In [2]: extractor = links()
In [3]: extractor.resolve(response)
In [4]: str(extrator)
Out [4]: [Link(url=https://www.iana.org/domains/example, valid=True)]

In [5]: response.links
Out [5]: [Link(url=https://www.iana.org/domains/example, valid=True)]
```

Or simply get the page title:

```
IPython 7.19.0

In [6]: response.page_title
Out [6]: 'Example Domain'
```

Remember that in addition to the custom functions created for the class, all the rest called on `zineb.response.HTMLResponse` are BeautifulSoup functions (find, find_all, find_next...)

## Queries on the page

Like said previously, the majority of your interactions with the HTML page will be done through the `HTMLResponse` object or `zineb.http.responses.HTMLResponse` class.

This class will implement some very basic general functionnalities that you can use through the course of your project. To illustrate this, let's create a basic Zineb HTTP response from a request:

```
from zineb.http.requests import HTTPRequest

request = HTTPRequest("http://example.com")
```

Requests, when created a not sent [or resolved] automatically if the `_send` function is not called. In that case, they are marked as being unresolved ex. `HTTPRequest("http://example.co", resolved=False)`.

Once the `_send` method is called, by using the `html_page` attribute or calling any BeautifulSoup function on the class, you can do all the classic querying on the page e.g. find, find_all...

```
request._send()

request.html_response

    -> Zineb HTMLResponse object

request.html_response.html_page

    -> BeautifulSoup object

request.find("a")

    -> BeautifulSoup Tag
```

If you do not know about BeautifulSoup please read [the documentation here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

For instance, suppose you have a spider and want to get the first link present on the http://example.com page. That's what you would so:

```
from zineb.app import Zineb

class MySpider(Zineb):
    start_urls = ["http://example.com"]

    def start(self, response=None, request=None, soup=None, **kwargs):
        link = response.find("a")

        # Or, you can also use this tehnic through
        # the request object
        link = request.html_response.find("a")

        # Or you can directly use the soup
        # object as so
        link = soup.find("a")
```

In order to understand what the `Link`, `Image` and `Table` objects represents, please read the [following section]() of this page.

Zineb HTTPRequest objects are better explained in the following section.

### Getting all the links

```
request.html_response.links

    -> [Link(url=http://example.com valid=True)]
```

### Getting all the images

```
request.html_response.images

    -> [Image(url=https://example.com/1.jpg")]
```

### Getting all the tables

```
request.html_response.tables

    -> [Table(url=https://example.com/1")]
```

### Getting all the text

Finally you can retrieve all the text of the web page at once.

```
request.html_response.text

    -> '\n\n\nExample Domain\n\n\n\n\n\n\n\nExample Domain\nThis domain is for use in   illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\nMore information...\n\n\n\n'
```
