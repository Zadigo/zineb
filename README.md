![logo](https://imgur.com/VVkf96x)

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

## Creating a project

To create a project do `python -m zineb start_project <project name>` which will create a directory which will have the following structure.

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

This option writer as `verbose_name` will specific a different name to your spider.

## Running commands

#### Start

Triggers the execution of all the spiders present in the given the project.

#### Shell

Start a iPython shell on which you can test various elements on the HTML page.

When the shell is started, the `zineb.http.HTTPRequest`, the `zineb.response.HTMLResponse`, and the BeautifulSoup instance of the page are injected.

Extractors are passed using aliases:

* `links`: LinkExtractor
* `images`: ImageExtractor
* `multilinks`: MultiLinkExtractor
* `tables`: TableExtractor

The extractors are also all passed within the shell in addition to the project settings.

In that regards, the shell becomes a interesting place where you can test various querying before using it in your project. For example, using the shell with `http://example.com`.

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

Remember that in addition to the custom functions created for the class, all the rest called on `zineb.response.HTMLResponse` are BeautifulSoup ones (find, find_all, find_next, next_sibling...)

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

## FileCrawler

There might be situations where you might have a set of HTML files in your project directory that you want to crawl. Zineb provides a Spider for such event.

__NOTE:__ Ensure that the directory to use is within your project.

```
class Spider(FileCrawler):
    start_files = ["media/folder/myfile.html"]
```

You might have thousands of files and certainly might not want to reference each file one by one. You can then also use a utility function `collect_files`.

```
from zineb.utils.iterator import collect_files

class Spider(FileCrawler):
    start_files = collect_files("media/folder")
```

Read more on `collect_files` [here](#-File-collection).

# Models

Models are a simple way to structure your scrapped data before saving them to a file.

## Creating a custom Model

In order to create a model, subclass the Model object from `zineb.models.Model` and then add fields to it. For example:

```
from zineb.models.datastructure import Model
from zineb.models import fields

class Player(Model):
    name = fields.CharField()
    date_of_birth = fields.DateField()
    height = fields.IntegerField()
```

### Using the custom model

On its own, a model does nothing. In order to make it work, you have to add values to it and then resolve the fields.

#### Adding a free custom value

The first method consists of adding values through the `add_value` method. This method does not rely on the BeautifulSoup HTML page object which means that values can be added freely.

```
player.add_value('name', 'Kendall Jenner')
```

#### Adding a value based on an expression

Addind expression based values requires a BeautifulSoup HTML page object. You can add one value at a time.

````
player.add_using_expression(''name', 'a', attrs={'class': 'title'})
````

#### Add case based values

If you want to add a value to the model based on certain conditions, use `add_case` in combination wih an expression class.

For instance, suppose you are scrapping a fashion website and for certain prices, let's say 25 you want to replace them by 25.5.

```
from zineb.models.expressions import When

my_model.add_case(25, When('price__eq=25', 25.5))
```

#### Adding multiple values with expressions

#### Adding calculated values

If you wish to operate a calculation on a field before passing to your model, you can use expression classes in combination with the `add_calculated_value`.

```
from zineb.models.expressions import Add

my_model.add_calculatd_value('price', Add(25, 5))
```

#### Adding related values

In cases where you want to add a value to your model based on the last inserted value, this function serves exactly this purpose. Suppose you are retrieving date of births on a website and want to automatically derive the person's age based on that model field:

```
class MyModel(Model):
    date_of_birth = fields.DateField("%d-%M-%Y")
    age = fields.AgeField("%Y-%M-%d")
```

Without the `add_related_value` this is what you would do:

```
model.add_value("date_of_birth", value)
model.add_value("age", value)
```

However, with the `add_related_value` you can automatically insert the age value in the model based on the returned value from the date of birth:

```
model.add_related_value("date_of_birth", "age", value)
```

This will insert date of birth based on the DateField and then insert another on the AgeField.

## Meta options

By adding a Meta to your model, you can pass custom behaviours.

* Ordering
* Constraints

### Constraints

### Ordering

Order your data in a specific way based on certain fields before saving your model.

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
- CommaSeparatedField
- ListField
- BooleanField

### How fields work

Each fields comes with a  `resolve` function when called stores the resulting value within itself.

By default, the resolve function will do the following things.

First, it will run all cleaning functions on the original value for example by stripping tags like "<" or ">" which normalizes the value before additional processing.

Second, a `deep_clean` method is run on the result by taking out out any useless spaces, removing escape characters and finally reconstructing the value to ensure that any none-detected white space be eliminated.

Finally, all the registered validators (default and custom) are called on the final value.

### CharField

The CharField represents the normal character element on an HTML page.

`CharField(max_length=None, null=None, default=None, validators=[])`

### TextField

The text field is longer which allows you then to add paragraphs of text.

`TextField(max_length=None, null=None, default=None, validators=[])`

### NameField

The name field allows you to implement capitalized text in your model. The `title` method is called on the string in order to represent the value correctly e.g. Kendall Jenner.

`NameField(max_length=None, null=None, default=None, validators=[])`

### EmailField

The email field represents emails. The default validator, `validators.validate_email`, is automatically called on the resolve function fo the class in order to ensure that that the value is indeed an email.

- `limit_to_domains`: Check if email corresponds to the list of specified domains

`EmailField(limit_to_domains=[], max_length=None, null=None, default=None, validators=[])`

### UrlField

The url field is specific for urls. Just like the email field, the default validator, `validators.validate_url` is called in order to validate the url.

### ImageField

The image field holds the url of an image exactly like the UrlField with the sole difference that you can download the image directly when the field is evaluated.

- `download`: Download the image to your media folder while the scrapping is performed
- `as_thumnail`: Download image as a thumbnail
- `download_to`: Download image to a specific path

```
class MyModel(Model):
    avatar = ImageField(download=True, download_to="/this/path")
```

### IntegerField

This field allows you to pass an integer into your model.

- `default`: Default value if None
- `max_value`: Implements a maximum value constraint
- `min_value`: Implements a minimum value constraint

### DecimalField

This field allows you to pass a float value into your model.

- `default`: Default value if None
- `max_value`: Implements a maximum value constraint
- `min_value`: Implements a minimum value constraint

### DateField

The date field allows you to pass dates to your model. In order to use this field, you have to pass a date format so that the field can know how to resolve the value.

- `date_format`: Indicates how to parse the incoming data value
- `default`: Default value if None
- `tz_info`: Timezone information

```
class MyModel(Model):
    date = DateField("%d-%m-%Y")
```

### AgeField

The age field works likes the DateField but instead of returning the date, it will return the difference between the date and the current date which corresponds to the age.

- `date_format`: Indicates how to parse the incoming data value
- `default`: Default value if None
- `tz_info`: Timezone information

### FunctionField

The function field is a special field that you can use when you have a set of functions to run on the value before returning the final result. For example, let's say you have this value `Kendall J. Jenner` and you want to run a specific function that takes out the middle letter on every incoming values:

```
def strip_middle_letter(value):
    # Do something here
    return value

class MyModel(Model):
    name = FunctionField(strip_middle_letter, output_field=CharField())
```

Every time the resolve function will be called on this field, the methods provided will be passed on the value sequentially. Each method should return the new value.

An output field is not compulsory but if not provided, each value will be returned as a character.

### ListField

An array field will store an array of values that are all evalutated to an output field that you would have specified.

__N.B.__ Note that the value of an ArrayField is implemented as is in the final DataFrame. Make sure you are using this field correctly in order to avoid unwanted results.

### CommaSeperatedField

Create a comma separated field in your model.

__N.B.__ Note that the value of a CommaSeperatedField is implemented as is in the final DataFrame. Make sure you are using this field correctly in order to avoid unwanted results.

### RegexField

Parse an element within a given value using a regex expression before storing it in your model.

```
RegexField(r'(\d+)(?<=\€)')
```

### BooleanField

Adds a boolean based value to your model. Uses classic boolean represenations such as `on, off, 1, 0, True, true, False or false` to resolve the value.

### Creating your own field

You an also create a custom field by suclassing `zineb.models.fields.Field`. When doing so, your custom field has to provide a `resolve` function in order to determine how the value should be parsed.

```
class MyCustomField(Field):
    def resolve(self, value):
        initial_result = super().resolve(value)

        # Rest of your code here
```

__NOTE:__ If you want to use the cleaning functionalities from the super class in your own resolve function, make sure to call super beforehand as indicated above.

## Validators [initial validators]

Validators make sure that the value that was passed respects the constraints that were implemented as a keyword arguments on the field class. There are five basic validations that could possibly run if you specify a constraint for them:

- Maximum length (`max_length`)
- Nullity (`null`)
- Defaultness (`default`)
- Validity (`validators`)

### Maximum or Minimum length

The maximum or minimum length check ensures that the value does not exceed a certain length using `validators.max_length_validator` or `validators.min_length_validator`.

### Nullity

The nullity validation ensures that the value is not null and that if a default is provided, that null value be replaced by the latter. It uses `validators.validate_is_not_null`.

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

__NOTE:__ It is important to understand that the result of the regex compiler is reinjected into your custom validator on which you can then do various other checks.

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

## Expressions

Expressions a built-in functions that can modify the incoming value in some kind of way before storing to your model.

### Math

Run a calculation such as addition, substraction, division or multiplication on the value.

```
from zineb.models.expressions import Add

player.add_calculated_field('height', Add(175, 5))

-> {'height': [180]}
```

### ExtractYear, ExtractDate, ExtractDay

From a date string, extract the year, the date or the day.

```
from zineb.models.expressions import ExtractYear

player.add_value('competition_year', ExtractYear('11-1-2021'))

-> {'competition_year': [2021]}
```

# Extractors

Extractors are utilities that facilitates extracting certain specific pieces of data from a web page such as links, images [...] quickly.

Some extractors can be used in various manners. First, with a context processor:

```
extractor = LinkExtractor()
with extractor:
    # Do something here
```

Second, in an interation process:

```
for link in extractor:
    # Do something here
```

Finally, with `next`:

```
next(extractor)
```

You can also check if an extractor has a specific value and even concatenate some of them together:

```
# Contains
if x in extractor:
    # Do something here

# Addition
concatenated_extractors = extractor1 + extractor2
```

## LinkExtractor

* `url_must_contain` - only keep urls that contain a specific string
* `unique` - return a unique set of urls (no duplicates)
* `base_url` - reconcile a domain to a path
* `only_valid_links` - only keep links (Link) that are marked as valid

```
extractor = LinkExtractor()
extractor.finalize(response.html_response)

    -> [Link(url=http://example.com, valid=True)]
```

There might be times where the extracted links are relative paths. This can cause an issue for running additional requests. In which case, use the `base_url` parameter:

```
extractor = LinkExtractor(base_url=http://example.com)
extractor.finalize(response.html_response)

# Instead of getting this result which would also
# be marked as a none valid link

    -> [Link(url=/relative/path, valid=False)]

# You will get the following with the full url link

    -> [Link(url=http://example.com/relative/path, valid=True)]
```

NOTE: By definition, a relative path is not a valid link hence the valid set to False.

## MultiLinkExtractor

A `MultiLinkExtractor` works exactly like the `LinkExtractor` with the only difference being that it also identifies and collects emails that are contained within the HTML page.

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

# Zineb special wrappers

# HTTPRequest

Zineb uses a special built-in HTTPRequest class which wraps the following for better cohesion:

* The `requests.Request` response class
* The `bs4.BeautifulSoup` object

In general, you will not need to interact with this class that much because it's just an interface for implement additional functionnalities especially to the Request class.

* `follow`: create a new instance of the class whose resposne will be the one of a new url
* `follow_all`: create new instances of the class who responses will tbe the ones of the new urls
* `urljoin`: join a path the domain

# HTMLResponse

It wraps the BeautifulSoup object in order to implement some small additional functionalities:

* `page_title`: return the page's title
* `links`: return all the links of the page
* `images`: return all the images of the page
* `tables`: return all the tables of the page

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

## Creating a custom signal

To create custom signal, you need to mark a method as being a receiver for any incoming signals. For example, if you want to create a signal to intercept one of the events above, you should do:

```
from zineb.signals import receiver

@receiver(tag="Signal Name")
def my_custom_signal(sender, **kwargs):
    pass
```

The signals function has to be able to accept a `sender` object and additional parameters such as the current url or the current HTML page.

You custom signals do not have to return anything.

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

## File collection

Collect files within a specific directory using `collect_files`. Collect files also takes an additional function that can be used to filter or alter the final results.

# Settings

This section will talk about all the available settings that are available for your project and how to use them for web scrapping.

**PROJECT_PATH**

Represents the current path for your project. This setting is not be changed.

**SPIDERS**

In order for your spider to be executed, every created spider should be registered here. The name of the class should serve as the name of the spider to be used.

```
SPIDERS = [
    "MySpider"
]
```

**DOMAINS**

You can restrict your project to use only to a specific set of domains by ensuring that no request is sent if it matches one of the domains within this list.

```
DOMAINS = [
    "example.com"
]
```

**ENSURE_HTTPS**

Enforce that every link in your project is a secured HTTPS link. This setting is set to False by default.

**MIDDLEWARES**

Middlewares are functions/classes that are executed when a signal is sent from any part of the project. Middlewares implement extra functionnalities without affecting the core parts of the project. They can then be disabled safely if you do not need them.

```
MIDDLEWARES = [
    "zineb.middlewares.handlers.Handler",
    "myproject.middlewares.MyMiddleware"
]
```

The main Zineb middlewares are the following:

* zineb.middlewares.referer.Referer
* zineb.middlewares.handlers.Handler
* zineb.middlewares.automation.Automation
* zineb.middlewares.history.History
* zineb.middlewares.statistics.GeneralStatistics
* zineb.middlewares.wireframe.WireFrame

**USER_AGENTS**

A user agent is a characteristic string that lets servers and network peers identify the application, operating system, vendor, and/or version of the requesting [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent).

Implement additional sets of user agents to your projects in addition to those that were already created.

**RANDOMIZE_USER_AGENTS**

Specifies whether to use one user agent for every request or to randomize user agents on every request. This setting is set to to False by default.

**DEFAULT_REQUEST_HEADERS**

Specify additional default headers to use for each requests.

The default initial headers are:

* `Accept-Language` - en
* `Accept` - text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
* Referrer - None

**PROXIES**

Use a set of proxies for each request. When a request in sent, a random proxy is selected and implemented with the request.

```
PROXIES = [
    ("http", "127.0.0.1"),
    ("https", "127.0.0.1")
]
```

**RETRY**

Specifies the retry policy. This is set to False by default. In other words, the request silently fails and never retries.

**RETRY_TIMES**

Specificies the amount of times the the request is sent before eventually failing.

**RETRY_HTTP_CODES**

Indicates which status codes should trigger a retry. By default, the following codes: 500, 502, 503, 504, 522, 524, 408 and 429 will trigger it.

###### TIME_ZONE
