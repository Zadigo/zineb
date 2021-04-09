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

# Getting started

All your interractions with Zineb will be made trough the management commands that are executed through `python manage.py` from your project's directory.

## Creating a project

To create a project do `python manage.py startproject <project name>` which will create a directory which will have the following structure.

The models directory allows you to place the elements that will help structure the data that you have scrapped from from the internet.

The `manage.py` file will allow you to run all the required commands from your project.

Finally, the spiders module will contain all the spiders for your project.

## Configuring your project

On startup, Zineb implements a set of basic settings (`zineb.settings.base`) that will get overrided by the values that you would have defined in your `settings.py` located in your project.

You can readd more about this in the [settings section of this file](#Settings).

## Creating a spider

Creating a spider is extremely easy and requires a set of starting urls that can be used to scrap one or many HTML pages.

```
class Celebrities(Zineb):
    start_urls = ['http://example.com']

    def start(self, response, request=None, soup=None, **kwargs):
        # Do something here


```

Once the Celibrities class is called, each request is passed through the `start` method. In other words the `zineb.response.HTTPResponse`,  `zineb.request.HTTPRequest` and the `BeautifulSoup` HTML page object and sent through the function.

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

Start a iPython shell on which you can test various elements on the HTML page, the HTTP request

## Queries on the page

Like said previously, the majority of your interactions with the HTML page will be done through the ``HTMLResponse`` object or the `zineb.http.responses.HTMLResponse` class.

This class will implement some very basic general functionnalities that you can use through the course of your project. To illustrate this, let's create a basic Zineb HTTP response:

```
from zineb.http.requests import HTTPRequest

request = HTTPRequest("http://example.co")
```

Requests, when created a not sent [or resolved] automatically if the `_send` function is not called. In that case, they are marked as being unresolved ex. `HTTPRequest("http://example.co", resolved=False)`.

Once the `_send` method is called, by using the By using the `html_page` attribute or calling any BeautifulSoup function on the class, you can do all the classic querying on the page e.g. find, findall...

```
request._send()
request.html_response.html_page

    -> BeautifulSoup object

request.html_response.find("a")
    -> BeautifulSoup Tag 

```

If you do not know about BeautifulSoup please read [the documentation here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

For instance, suppose you have a spider and want to get the first link present on the http://example.com page. That's what you would so:

```mermaid
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

### Getting all the links

```
request.html_response.links

    -> [Link(url='http://example.com')]
```

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

### Getting all the text

Finally you can retrieve all the text of the web page at once.

# Models

Models are a simple way to structure your scrapped data before saving them to a file. The Model class is built around Panda's excellent DataFrame class in order to simplify as a much as possible the fact of dealing with your data.

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

You can add values to your model in two main ways.

#### Adding a free custom value

The first method consists of adding values through the `add_value` method. This method does not rely on the BeautifulSoup HTML page object which means that values can be added freely.

```
player.add_value('name', 'Kendall Jenner')
```

#### Adding an expression based value

Addind expression based values requires a BeautifulSoup HTML page object. You can add one value at a time or multiple values.

````
player.add_expression("name", "a#kendall__text", many=True)
````

By using the `many` parameter, you can add the all the tags with a specific name and/or attributes to your model at once.

Here is a list of expressions that you can use for this field:


| expression | interpretation | tag |
| - | - | - |
| a.kendall | Link with class kendall | <a class="kendall"> |
| a#kendall | Lind with ID Kendall | <a id="kendall"> |

By default, if a pseudo is not provided, `__text` pseudo is appended in order to always retrieve the inner text element of the tag.

## Meta options

By adding a Meta to your model, you can pass custom behaviours.

* Ordering
* Indexing

### Indexes

### Ordering

## Fields

Fields are a very simple way to passing HTML data to your model in a very structured way. Zineb comes with number of preset fields that you can use out of the box:

- CharField
- TextField
- NameField
- EmailField
- UrlField
- ImageField
- IntegerField
- DecimalField
- DateField
- AgeField
- FunctionField
- ArrayField
- CommaSeparatedField

### How fields work

Once the field is called via the `resolve` function on each field which in turns calls the `super().resolve` function of the `Field` super class, the value is stored.

By default, the resolve function will do the following things.

First, it will run all cleaning functions on the value for example by stripping tags like "<" or ">" by using the `w3lib.html.remove_tags` library.

Second, a `deep_clean` method will be called on the value which takes out any spaces using `w3lib.html.strip_html5_whitespace`, remove escape characters with the `w3lib.html.replace_escape_chars` function and finally reconstruct the value to ensure that any none-detected white space be eliminated.

Finally, all validators (default and custom created) are called on the value. The final value is then returned within the model class.

### CharField

The CharField represents the normal character element on an HTML page. You constrain the length.

### TextField

The text field is longer allows you to add paragraphs of text.

### NameField

The name field allows to implement names in your model. The `title` method is called on the string in order to represent the value correctly e.g. Kendall Jenner.

### EmailField

The email field represents emails. The default validator, `validators.validate_email`, is automatically called on the resolve function fo the class in order to ensure that that the value is indeed an email.

### UrlField

The url field is specific for urls. Just like the email field, the default validator, `validators.validate_url` is called in order to validate the url.

### ImageField

The image field holds the url of an image exactly like the UrlField with the sole difference that you can download the image directly when the field is evaluated.

```
class MyModel(Model):
    avatar = ImageField(download=True, download_to="/this/path")
```

### IntegerField

### DecimalField

### DateField

The date field allows you to pass dates to your model. In order to use this field, you have to pass a date format so that the field can know how to resolve the value.

```
class MyModel(Model):
    date = DateField("%d-%m-%Y")
```

### AgeField

The age field works likes the DateField but instead of returning the date, it will return the difference between the date and the current date which is an age.

### FunctionField

The function field is a special field that you can use when you have a set of functions to run on the value before returning the final result. For example, let's say you have this value `Kendall J. Jenner` and you want to run a specific function that takes out the middle letter on every incoming values:

```
def strip_middle_letter(value):
    return

class MyModel(Model):
    name = FunctionField(strip_middle_letter, output_field=CharField(), )
```

Every time the resolve function will be called on this field, the methods provided will be passed on the value.

An output field is not compulsory but if not provided, each value will be returned as a character.

### ArrayField

An array field will store an array of values that are all evalutated to an output field that you would have specified.

### CommaSeperatedField

### Creating your own field

You an also create a custom field by suclassing `zineb.models.fields.Field`. When doing so, your custom field has to provide a `resolve` function in order to determine how the value should be treated. For example:

```
class MyCustomField(Field):
    def resolve(self, value):
        initial_result = super().resolve(value)
```

If you want to use the custom cleaning functionalities on your resolve function before running yours, make sure to call super.

## Validators

Validators make sure that the value that was passed respects the constraints that were implemented as a keyword arguments on the field class. There are five basic validations:

- Maximum length
- Uniqueness
- Nullity
- Defaultness
- Validity (validators)

### Maximum or Minimum length

The maximum length check ensures that the value does not exceed a certain length using `zineb.models.validators.max_length_validator` or `zineb.models.validators.min_length_validator` which are encapsulated and used within the `zineb.models.validators.MinLengthValidator` or `zineb.models.validators.MaxLengthValidator` class.

### Nullity

The nullity validation ensures that the value is not null and that if a default is provided, that null value be replaced by the latter. It uses `zineb.models.validators.validate_is_not_null`.

The defaultness provides a default value for null or none existing ones.

### Practical examples

For instance, suppose you want only values that do not exceed a certain length:

```
name = CharField(max_length=50)
```

Or suppose you want a default value for fields that are empty or blank:

```
name = CharField(default='Kylie Jenner')
```

Remember that validators will validate the value itself for example by making sure that an URL is indeed an url or that an email follows the expected pattern that you would expect from an email.

Suppose you want only values that would be `Kendall Jenner`. Then you could create a custom validator that would do the following:

```
def check_name(value):
    if value == "Kylie Jenner":
        return None
    return value

name = CharField(validators=[check_name])
```

You can also create validators that match a specific regex pattern using the `zineb.models.validators.regex_compiler` decorator:

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

In order to get the complete structured data, you need to call `resolve_values` which will return a `pandas.DataFrame` object:

```
player.add_value("name", "Kendall Jenner")
player.resolve_values()

    -> pandas.DataFrame
```

Practically though, you'll be using the `save` method which also calls the `resolve_values` under the hood:

```
player.save(commit=True, filename=None, **kwargs)

    -> pandas.DataFrame or new file
```

By calling the save method, you'll be able to store the data directly to a JSON or CSV file.

# Extractors

Extractors are utilities that facilitates extracting certain specific pieces of data from a web page such as links, images [...] quickly. They are very handy in that regards.

## LinkExtractor

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

## TableExtractor

Extract all the rows from the first table that is matched on the HTML page.

* `class_name` - intercept a table with a specific class name
* `has_headers` - specify if the table has headers in order to ignore it in the final data
* `filter_empty_rows` - ignore any rows that do not have a values
* `processors` - a set of functions to run on the data once it is all extracted

## ImageExtractor

Extract all the images on the HTML page.

You can filter down the images that you get by using a specific set of parameters:

* `unique` - return only a unique et set of urls
* `as_type` - only return images having a specific extension
* `url_must_contain` - only return images which contains a specific string
* `match_height` - only return images that match as specific height
* `match_width` - only return images that match a specific width

## TextExtractor

Extract all the text on an HTML page.

First, the text is retrieved as a raw value then tokenized and vectorized using `nltk.tokenize.PunktSentenceTokenizer` and `nltk.tokenize.WordPunctTokenizer`.

To know more about NLKT, [please read the following documentation](https://www.nltk.org/).

# Signals

Signals are a very simple yet efficient way for you to run functions during the lifecycle of your project when certain events occur at very specific moments.

Internally signals are sent on the following events:

- When the registry is populated
- Before the spider starts
- After the spider has started
- Before an HTTP request is sent
- Before and HTTP request is sent
- Before the model downloads anything
- After the model has downloaded something

### Creating a custom signal

To create custom signal, you need to mark a method as being a receiver for any incoming signals. For example, if you want to create a signal to intercept one of the events above, you should do:

```
from zineb.signals import receiver

@receiver(tag="Signal Name")
def my_custom_signal(sender, **kwargs):
    pass
```

The signals function has to be able to accept a `sender` object and additional parameters such as the current url or the current HTML page.

You custom signals do not have to return anything.

# Pipelines

Pipelines are a great way to send chained requests to the internet or treat a set of responses by processing them afterwards through a set of functions of your choice.

Some Pipeplines are also perfect for donwloading images.

## ResponsesPipeline

The response pipepline allows you to chain a group of responses and treat all of them at once through a function:

```
from zineb.http.pipelines import ResponsesPipeline

pipeline = ResponsesPipeline([response1, response2], [function1, function2])
pipeline.results
    -> list
```

It comes with three main parameters:

* `responses` - which corresponds to a list of HTMLResponses
* `functions` - a list of functions to pass each individual response and additional parameters
* `paramaters` - a set of additional parameters to pass to the functions

The best way to use the ResponsesPipeline is within the functions of your custom spider:

```

class MySpider(Zineb):
   start_urls = ["https://example.com"]

   def start(self, response, soup=None, **kwargs):
       extractor = LinksExtractor()
       extractor.resolve(soup)
       responses = request.follow_all(*list(extractor))
       ResponsesPipeline(responses, [self.do_something_here])

   def do_something_here(self, response, soup=None, **kwargs):
       # Continue parsing data here

```

**N.B.** Each function is executed sequentially. So, the final result will come from the final function of the list

## HTTPPipeline

This pipeline takes a set of urls, creates HTTPResquests for each of them and then sends them to the internet.

If you provided a set of functions, it will pass each request through them.

````
from zineb.http.pipelines import HTTPPipeline
from zineb.utils.general import download_image

HTTPPipeline([https://example.com], [download_image])
````

Each function should be able to accept an HTTP Response object.

You can also pass additional parameters to your functions by doing the following:

```
HTTPPipeline([https://example.com], [download_image], parameters={'extra': False})
```

In this specific case, your function should accept an `extra` parameter which result would be False.

## Callback

The Callback class allows you to run a callback function once each url is processed and passed through the main start function of your spider.

The `__call__` method is triggerd on the instance in order to resolve the function to use.

```
class Spider(Zineb):
    start_urls = ["https://example.com"]

    def start(self, response, **kwargs):
        request = kwargs.get("request")
        model = MyModel()
        return Callback(request.follow, self.another_function, model=model)

    def another_function(self, response, **kwargs):
        model = kwargs.get("model")
        model.add_value("name", "Kendall Jenner")
        model.save()
```

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

# Settings

This section will talk about all the available settings that are available for your project and how to use them for web scrapping.

**DOMAINS**

You can restrict your project to use only to a specific set of domains.

```
DOMAINS = [
    "example.com"
]
```

**ENSURE_HTTPS**

Enforce that every link in your project is a secured HTTPS link.

**MIDDLEWARES**

Middlewares are functions/classes that are executed before the main the main logic of your spider is executed. Middlewares implement extra functionnalities to a given project.

```
MIDDLEWARES = [
    "zineb.middlewares.handlers.Handler",
    "project.middlewares.MyMiddleware"
]
```

**PROJECT_PATH**

This variable stores the absolute path for your project

**PROXIES**

Use a set of proxies within your project. When a request in sent, a random proxy is selected and implemented with the request.

```
PROXIES = [
    ("http", "127.0.0.1"),
    ("https", "127.0.0.1")
]
```

**SPIDERS**

In order to run your spiders, every created spider should be registered here. The name of the class should serve as the name of the spider to be used.

```
SPIDERS = [
    "MySpider"
]
```

**USER_AGENTS**

A user agent is a characteristic string that lets servers and network peers identify the application, operating system, vendor, and/or version of the requesting [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent). You can add a list of user agents to use within your project with this constant.
