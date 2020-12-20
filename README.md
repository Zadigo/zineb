## Introduction

Zineb is a lightweight tool solution for simple and efficient web scrapping built around BeautifulSoup -; and whose main purpose is to help __quickly structure your data in order for you to use it at fast as possible for data science or machine learning projects.__

## Understanding how Zineb works

Zineb gets your custom spider, creates a set of ``HTTPRequest`` objects for each url, sends the requests and caches a BeautifulSoup object of the page within an ``HTMLResponse`` class.

Most of your interactions with the HTML page will be done through the ``HTMLResponse`` class.

## Creating a spider

Creating a spider is extremely easy and requires a set of starting urls that can be used to scrap an HTML page.

```
class Celerities(Zineb):
    start_urls = ['http://example.com']
```

### Adding meta options to the spider

```
class Celerities(Zineb):
    start_urls = ['http://example.com']

    class Meta:
        ordering = None
        options = None
```

## Doing basic querying on the page

Like said previously, the majority of your interactions with the HTML page will be done through the ``HTMLResponse`` object.

This class implements some basic functionnalities that you can use through the course of your project.

To explain, these, let's create a basic HTTP response:

```
from zineb.http.requests import HTTPRequest

request = HTTPRequest('http://example.co' resolved=False)
```

Requests, when created a not sent automatically until you call the `_send` function. Unsent requests are marked as unresolved.

```
request._send()
request.html_response.html_page

    -> BeautifulSoup object
```

### Basic implementations

The `request.http_response.html_response` provides some very basic functionalities such as __getting all the links__ from a page:

```
request.html_response.links

    -> [Link(url='http://example.com')]
```

In order to understand what the ``Link`` object represents, please read the following section of this page.

You can also get all the images:

```
request.html_response.images

    -> [Image(url='https://example.com/1.jpg')]
```

Or, all the tables:

```
request.html_response.tables

    -> [Table(url='https://example.com/1')]
```

These three elements are generally the most common items retrieved when doing web scraping.



Finally, most of times, when you retrieve links from a page, they are returned as relative paths. The ``urljoin`` method reconciles the url of the visited page with that path.

```
<a href="/kendall-jenner">Kendall Jenner</a>

# Now we want to reconcile the relative path from this link to
# the main url that we are visiting e.g. https://example.com

request.urljoin("/kendall-jenner")

-> https://example.com/kendall-jenner
```

## Models

Models are simple way that you can use to structure data in your project.

### Creating and using a model

Creating a model is very simple. You have to subclass the Model object from `zineb.models.Model` and then add fields from `zineb.models.fields` to it. Here is a basic example:

```
from models.fields import CharField
from zineb.models.datastructure import Model

class Player(Model):
    name = CharField()

```

On its own, a model does nothing. In order to make it work, you have to call it, add values to it and then resolve the fields.

You can add values in multiple ways. The first, and easiest way to add values is through the `add_value`.

```
player = Player()
player.add_value('name', 'Kendall Jenner')
```



method consits of passing a query expression that will then automatically resolve in getting the elements from the given page.

What this `p__text` expression says, is __get me all the text elemnts from p tags in the document__ for structuring.

At this stage, the field, expressions have been resolved and each respective field contains the result of what the expression has parsed.

In order to get the complete structured data, you need to call `resolve_values`:

```
player.resolve_values()

-> pandas.DataFrame
```

As you can see, this returns a DataFrame object on which you do additional things.

You can also call the `save` method to create a JSON file:

```
player.save()

-> JSON File
```

### Fields

Fields are a very simple way to passing HTML data to your model in a very structured way. Zineb comes with number of preset fields that you can use out of the box:

    - CharField
    - UrlField
    - ImageField
    - TextField
    - DateField
    - AgeField
    - Function
    - SmartField

You an also create a custom field by suclassing the `Field` class. When doing so, your custom field has to provide a `resolve` function in order to determine how the value coming to that field should be treated.

### Expressions

Remember that Zineb is built around BeautifulSoup. In that regards, all the expressions that work with BeatifulSoup are also valid with within your spider.

Ultimately, the only thing that changes __is the attribute__ at the end of the expression.

Expression | Description
--- | ---
a__text | Get the text of all a tags
--- | ---
a___text__contains:Kendall | Get all tag elements whose a tag contains kendall
--- | ---
a___text__eq:Kendall | Get all tag elements whose a tag text is exactly Kendall


__NOTE:__ Remember that these expessions are only exclusive to models and and models are tools for you to use if your sole purpose is to intelligently structure your data from a scrapped page. 

## Signals

Signals are a very simple yet efficient way for you to run functions during the lifecycle of your project. You can run many types of signals:

    - Before the spider starts
    - After the spider has started
    - Before the spider downloads anything
    - while the spider generates data

### Creating a signal

```
from zineb.signals import register

@register(sender, receiver)
def my_custom_signal(sender, **kwargs):
    pass
```

The signals function has to be able to accept an instance object and additional parameters such as the current url or the current HTML page.

This instance element represents the spider object on which you will be able to run a set of options.

You custom signals do not have to return anything.


# Extractors

Extractors a utilities that facilitates extracting certain specific pieces of data from a web page e.g. links, images [...] They are very handly when you need to quickly get these objects for further processing.

```
extractor = LinkExtractor()
extractor.finalize(response.html_response)

    -> [Link(url=http://example.com, valid=True)]
```

There might be times where the extracted links are relative paths. This can cause an issue for running additional requests. In which case, use the `base_url` parameter:

```
extractor = LinkExtractor(base_url=http://example.com)
extractor.finalize(response.html_response)

# Instead of returning this result:

    -> [Link(url=/relative/path, valid=False)]

# You will get:

    -> [Link(url=http://example.com/relative/path, valid=True)]
```

NOTE: By definition, a relative path is not a valid link hence the valid set to False.

Some extractors such the LinkExtractor are iterable. It is perfectly possible to do the following:

```
for link in extractor:
    ...
```

Or, you an also use the result used by finalize:

```
links = extractor.finalize(response.html_response)

for link in links:
    ...
```


## Configuring your spider

Your spiders get configured on initialization through your ``settings.conf`` file.
