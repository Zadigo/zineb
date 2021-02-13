# Introduction

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
         options: []
```

# Doing queries

Like said previously, the majority of your interactions with the HTML page will be done through the ``HTMLResponse`` object.

This class implements some basic functionnalities that you can use through the course of your project.

Let's create a basic HTTP response:

```
from zineb.http.requests import HTTPRequest

request = HTTPRequest('http://example.co' resolved=False)
```

Requests, when created a not sent [or resolved] automatically the `_send` function is called. In that case, they are marked as being unresolved.

```
request._send()
request.html_response.html_page

    -> BeautifulSoup object
```

By using the `html_page` attribute, you can do all the classic querying that you would do with BeautifulSoup e.g. find, findall...

## Basic implementations

The `request.html_response` attribute provides some very basic functionalities that we will be reviewing below.

These three elements are generally the most common items retrieved when doing web scraping.

### Getting all the links

```
request.html_response.links

    -> [Link(url='http://example.com')]
```

In order to understand what the ``Link`` object represents, please read the [following section]() of this page.

### Getting all the images

```
request.html_response.images

    -> [Image(url='https://example.com/1.jpg')]
```

### Getting all the tables

```
request.html_response.tables

    -> [Table(url='https://example.com/1')]
```

# Models

Models are a simple way to structure your scrapped data before saving them to a file. The Model class is built around Panda's excellent DataFrame class.

## Creating a custom Model

In order to create a model, subclass the Model object from `zineb.models.Model` and then add fields to it. For example:

```
from zineb.models.datastructure import Model
from zineb.models.fields import CharField

class Player(Model):
    name = CharField()
```

### Using the custom model

On its own, a model does nothing. In order to make it work, you have to add values to it and then resolve the fields.

You can add values in multiple ways. The first, and easiest way to add values is through the `add_value` method:

```
player.add_value('name', 'Kendall Jenner')
```

Once a value is added to the field, a series of checks and validations are run on the value.

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

#### Checks

Checks make sure that the value that was passed respects the constraints that were implemented as a keyword arguments on the field class. There are five basic checks:

- Maximum length
- Uniqueness
- Nullity
- Defaultness
- Validity (validators)

The maximum length check ensures that the value does not exceed a certain length.

The nullity check makes sure that the value is not null and that if a default is provided, that null value be replaced by the latter.

The defaultness provides a default value for null or none existing ones.

And, finally, the validity checks are a set of extra validation checks that can be passed to ensure value correctness.

For instance, suppose you want only values that do not exceed a certain length:

```
name = CharField(max_length=50)
```

Or suppose you want a default value for fields that are empty or blank:

```
name = CharField(default='Kylie Jenner')
```

#### Validators

__Validators__ validate the value itself. For instance, making sure that an URL is indeed an url or that an email follows the expected pattern that you would expect from an email.

Suppose you want only values that would be `Kendall Jenner`:

```
def check_name(value):
    if value == "Kylie Jenner":
        return None
    return value

name = CharField(validators=[check_name])
```


Zineb comes with a default set of validators. But you can also create yours and pass it to the field:

```
from zineb.models.datastructure import Model
from models.fields import CharField

def custom_validator(value):
    if value == 'Kendall Jenner':
        return 'Kylie Jenner'
    return value

class Player(Model):
    name = CharField(validators=[custom_validator])
```

You can also create validators that match a specific regex pattern using the `regex_compiler` decorator:

```
from zineb.models.datastructure import Model
from zineb.models.fields import CharField
from zineb.models.validators import regex_compiler

@regex_compiler(r'\d+')
def custom_validator(value):
    if value > 10:
        return value
    return 0

class Player(Model):
    age = IntegerField(validators=[custom_validator])
```

It is important to understand that the result of the regex compiler is reinjected into your custom validator on which you can then do various other checks.

#### Field resolution

Once the field tries to resolve the value, it will run __checks__ if any and will __validate__ the value before storing it.

In order to get the complete structured data, you need to call `resolve_values`:

```
player.add_value("name", "Kendall Jenner")
player.resolve_values()

    -> pandas.DataFrame
```

This returns a DataFrame object.

You can also call the `save` method to create a JSON file:

```
player.save(commit=True)

    -> JSON File
```

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

## Pipelines

Pipelines are a great way to send chained requests to the internet or treat a set of responses by processing them afterwards through a set of functions of your choice.

Pipelines are perfect for downloading images for example.

### HTTPPipeline

This pipeline takes a set of urls, creates HTTPResquests for each of them and then sends them to the internet.

````
from zineb.http.pipelines import Pipeline
from zineb.utils.general import download_image

def some_function(response):
pass

HTTPPipeline([https://example.com], [download_image])
````

Each function should be able to accept an HTTP Response object.

You can also pass additional parameters to your functions by doing the following:

```
HTTPPipeline([https://example.com], [download_image], parameters={'extra': False})
```

In this specific case, your function should accept an `extra` parameter which result would be False.


# Utilities

## Link reconciliation

Most of times, when you retrieve links from a page, they are returned as relative paths. The ``urljoin`` method reconciles the url of the visited page with that path.

```
<a href="/kendall-jenner">Kendall Jenner</a>

# Now we want to reconcile the relative path from this link to
# the main url that we are visiting e.g. https://example.com

request.urljoin("/kendall-jenner")

-> https://example.com/kendall-jenner
```
