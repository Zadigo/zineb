![logo](https://imgur.com/VVkf96x)

# Introduction

Zineb is a lightweight tool solution for simple and efficient web scrapping and crawling built around BeautifulSoup. It's main purpose is to help __structure your data efficiently in order to be used in data science or machine learning projects.__

# Understanding how Zineb works

Zineb works within a project and then proceeds to create a set of ``HTTPRequest`` objects for each url. The response is cached in an `HTTPREsponse` proxy in which the `BeautifulSoup` object of the page is stored.

Most of your interactions with the HTML page will be done through the `HTMLResponse` class.

When the spider starts crawling the page, each response and request in past through the start function:

```python
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

The models directory allows you to place the elements that will help structure the scrapped data.

Finally, the spiders module will contain all the spiders for your project.

## Configuring your project

On startup, Zineb implements a set of basic settings (`zineb.settings.base`) that will get overrided by the values that you would have defined in your local `settings.py` project.

You can read more about this in the [settings section of this file](#Settings).

## Creating a spider

Creating a spider is extremely easy with `python -m zineb startproject myproject` and requires a set of starting urls that can be used to scrap one or many HTML pages.

```python
class Celebrities(Zineb):
    start_urls = ['http://example.com']

    def start(self, response, request=None, soup=None, **kwargs):
        # Do something here
```

Once the Celibrities class is called, each request is passed through the `start` method. In other words the `zineb.http.responses.HTMLResponse`,  `zineb.http.request.HTTPRequest` and the `BeautifulSoup`.

You are not required to use all these parameters at once. They're just for convinience. You can also write the start method as so if you only need one of these.

```python
def start(self, response, **kwargs):
    # Do something here
```

Other objects can be passes through the function such as the models that you have created but also the settings of the application etc.

### Adding meta options

Meta options allows you to customize certain very specific behaviours [not found in the `settings.py` file] related to the spider.

```python
 class Celerities(Zineb):
    start_urls = ['http://example.com']
  
     class Meta:
         domains = []
```

#### Domains

This option limits a spider to a very specific set of domains.

#### Verbose name

This option will specify a different name to your spider.

## Running commands

### Start

Triggers the execution of all the spiders present in the given the project.

### Shell

Start a iPython shell on which you can test various elements on the HTML page.

When the shell is started, the `zineb.http.HTTPRequest`, the `zineb.response.HTMLResponse`, and the BeautifulSoup instance of the page are injected.

Extractors are passed using aliases:

* `links`: LinkExtractor
* `images`: ImageExtractor
* `multilinks`: MultiLinkExtractor
* `tables`: TableExtractor

The interractive shell becomes a interesting place where you can test various querying before using it in your original project. For example, we can get a simple url :

```python
IPython 7.19.0

In [1]: response.find("a")
Out[1]: <a href="https://www.iana.org/domains/example">More information...</a>
```

We can find all urls on the page:

```python
IPython 7.19.0

In [2]: extractor = links()
In [3]: extractor.resolve(response)
In [4]: str(extrator)
Out [4]: [Link(url=https://www.iana.org/domains/example, valid=True)]

In [5]: response.links
Out [5]: [Link(url=https://www.iana.org/domains/example, valid=True)]
```

Or simply get the page title:

```python
IPython 7.19.0

In [6]: response.page_title
Out [6]: 'Example Domain'
```

Remember that in addition to the custom functions created for the class, all the rest called on `zineb.response.HTMLResponse` are BeautifulSoup ones (find, find_all, find_next, next_sibling...)

## Queries on the page

Like said previously, the majority of your interactions with the HTML page will be done through the `HTMLResponse` object or `zineb.http.responses.HTMLResponse` class.

This class will implement some very basic general functionnalities that you can use through the course of your project. To illustrate this, let's create a basic Zineb HTTP response from a request:

```python
from zineb.http.requests import HTTPRequest

request = HTTPRequest("http://example.com")
```

Requests, when created a not sent [or resolved] automatically if the `_send` function is not called. In that case, they are marked as being unresolved.

Once the `_send` method is called, by using the `html_page` attribute or calling any BeautifulSoup function on the class, you can do all the classic querying on the page e.g. find, find_all...

```python
request._send()

request.html_response
# -> Zineb HTMLResponse object

request.html_response.html_page
# -> BeautifulSoup object

request.find("a")
# -> BeautifulSoup Tag
```

If you do not know about BeautifulSoup please read [the documentation here](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

For instance, suppose you have a spider and want to get the first link present on http://example.com. That's what you would so:

```python
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

```python
request.html_response.links
# -> [Link(url=http://example.com valid=True)]
```

### Getting all the images

```python
request.html_response.images
# -> [Image(url=https://example.com/1.jpg")]
```

### Getting all the tables

```python
request.html_response.tables
# -> [Table(url=https://example.com/1")]
```

### Getting all the text

Finally you can retrieve all the text of the web page at once.

```python
>> request.html_response.text

>> '\n\n\nExample Domain\n\n\n\n\n\n\n\nExample Domain\nThis domain is for use in   illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.\nMore information...\n\n\n\n'
```

## FileCrawler

There might be situations where you might have a set of HTML files in your project directory that you want to crawl. Zineb provides a Spider for such event.

__NOTE:__ Ensure that the directory to use is within your project.

```python
class Spider(FileCrawler):
    start_files = ["media/folder/myfile.html"]
```

You might have thousands of files and certainly might not want to reference each file one by one. You can then also use a utility function `collect_files`.

```python
from zineb.utils.iterator import collect_files

class Spider(FileCrawler):
    start_files = collect_files("media/folder")
```

Read more on `collect_files` [here](#-File-collection).

# Models

Models are a simple way to structure your scrapped data before eventually saving them to a file (generally JSON or CSV). The Model class is an interface to an internal container called `SmartDict` that actually does contain the data and fields which purpose is to clean and normalize the incoming values.

By using models, you are then assured to have clean usable data for data analysis.

## Creating a custom Model

In order to create a model, subclass the Model object from `zineb.models.Model` and then add fields to it:

```python
from zineb.models import fields
from zineb.models.datastructure import Model

class Player(Model):
    name = fields.CharField()
    date_of_birth = fields.DateField()
    height = fields.IntegerField()
```

On its own however, a model does nothing. In order to make it work, you have to add values to it and then resolve the fields [or data]. There are multiple ways to do this.

Adding a new value generally requires two main parameters: _the name of the field to use and the incoming data to be added._

## Adding values to the model

Each model gets instantiated with a underlying container that does the heavy work of storing and aggregating the data. The default container is called `SmartDict`.

### Understanding SmartDict

The `SmartDict` container ensures that each row is well balanced with the same amount of fields when values are added.

For instance, if your model has two fields `name` and `surname`, suppose you add `name` but not `surname`, the final result should be `{"name": ['Kendall'], "surname": [None]}` which in return will be saved as `[{"name": "Kendall", "surname": null}]`.

In the same manner, if you supply values for both fields your final result would be `{"name": ['Kendall'], "surname": ["Jenner"]}` which in return will be saved as `[{"name": "Kendall", "surname": "Jenner"}]`.

In other words, whichever fields are supplied, the final result will always be a well balanced list of dictionnaries with no missing fields.

__deprecated__
This class does the following process:

* Before the data is added, it runs any field constraint present on the model
* It then adds the value to the existing container via the `update` function
* Finally, once `execute_save` is called, it applies any sorting specified on the fields in the `Meta` class of the model and returns the corresponding data

### Adding a free custom value

The first method consists of using `add_value`.

```python
player.add_value('name', 'Kendall Jenner')
```

### Adding a value based on an expression

Addind expression based values requires a BeautifulSoup HTML page object. You can add one value at a time.

````python
player.add_using_expression('name', 'a', attrs={'class': 'title'})
````

### Add case based values

When you want to add a value to the model based on certain conditions, use `add_case` in combination wih a function class.

For instance, suppose you are scrapping a fashion website and for certain prices, let's say 25 you want to replace them by 25.5 you can do the following:

```python
from zineb.models.expressions import When

my_model.add_case(25, When(25, 25.5))
```

### Adding calculated values

If you wish to operate a calculation on a field before passing the data to your model, you can use math function classes in combination with the `add_calculated_value`.

```python
from zineb.models.expressions import Add

my_model.add_calculatd_value('price', 25, Add(5))
```

You can also run multiple arithmetic operations on on the field:

```python
my_model.add_calculatd_value('price', 25, Add(5), Substract(1))
```

## Saving the model

You can save the data within a model by calling the `save` method. It takes the following arguments:

* `filename`
* `commit`

The save method does the following things in order:

* Call `full_clean` in order to apply general modifications to the final data
* `full_clean` then calls the `clean` method to apply any custom user modifications to be applied on the resulting data
* Finally, save the data to a file if commit or return the elements as list

## Meta options

By adding a Meta to your model, you can pass custom behaviours.

* Ordering
* Template model
* Constraints

### Template model

If a model's only purpose is to implement additional fields to a child model, use the `template_model` option to indicate this state.

```python
class TemplateModel(Model):
    name = fields.CharField()

    class Meta:
        template_model = True


class MainModel(TemplateModel):
    surname = fields.CharField()
```

This technique is useful when you need to implement common fields to multiple models at a time.

### Ordering

Order your data in a specific way based on certain fields before saving your model.

### Constraints

You an ensure that the data on your model is unique using the `UniqueConstraint` class. These constraint check is done before the data is saved by skipping the saving process if a similar value was found.

```python
class UserModel(Model):
    name = fields.CharField()
    email = fields.EmailField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name'], name='unique_name')
        ]
```

Multiple fields can be constrained creating a unique together directive. In the example below, both name and email have to be unique in order to be saved.

```python
class UserModel(Model):
    name = fields.CharField()
    email = fields.EmailField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'email'], name='unique_name')
        ]
```

You can also implement a constraint function on the fields:

```python
class UserModel(Model):
    name = fields.CharField()
    email = fields.EmailField()

    class Meta:
        constraints = [
            UniqueConstraint(fields=['name', 'email'], name='unique_name', condition=lambda x: x != 'Kendall')
        ]
```

## Fields

Fields are the main entrypoint for passing a raw value from the internet to the underlying `SmartDict` container of your model. They guarantee cleanliness and consistency.

Zineb comes with number of preset fields that you can use out of the box:

* CharField
* TextField
* NameField
* EmailField
* UrlField
* ImageField
* IntegerField
* DecimalField
* DateField
* AgeField
* CommaSeparatedField
* ListField
* BooleanField
* Value
* RelatedModelField

### How they work

Each fields comes with a `resolve` function which gets called by the model. 

When a value comes a from the internet, it is first encapsulated in a `Value` proxy field that runs cleaning functions on the data in order to normalize it as much a possible. It is then passed unto the field object which runs respsectively `resolve`, `_simple_resolve` then `_to_python_object`, if necessary, and finally `_run_validation` before being store in the model.

### Accessing data from the field instance

You can access the data of a declared field directly on the model by calling the field's name.

```python
class PlayerModel(Model):
	name = fields.CharField()
	surname = fields.CharField()

model = PlayerModel()
model.add_value('name': 'Shelly-Ann')
model.add_value('surname', 'Fraiser')

# -> model.name -> ["Shelly-Ann"]
# -> model.surname -> ["Fraiser"]
```

By calling `model.name` you will receive an array containing all the values that were registered in the data container e.g. `["Shelly-Ann"]`. Each field has a descriptor `FieldDescriptor`.

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

* `limit_to_domains`: Check if email corresponds to the list of specified domains

`EmailField(limit_to_domains=[], max_length=None, null=None, default=None, validators=[])`

### UrlField

The url field is specific for urls. Just like the email field, the default validator, `validators.validate_url` is called in order to validate the url.

### ImageField

The image field holds the url of an image exactly like the UrlField with the sole difference that you can download the image directly when the field is evaluated.

* `download`: Download the image to your media folder while the scrapping is performed
* `as_thumnail`: Download image as a thumbnail
* `download_to`: Download image to a specific path

```python
class MyModel(Model):
    avatar = ImageField(download=True, download_to="/this/path")
```

### IntegerField

This field allows you to pass an integer into your model.

* `default`: Default value if None
* `max_value`: Implements a maximum value constraint
* `min_value`: Implements a minimum value constraint

### DecimalField

This field allows you to pass a float value into your model.

* `default`: Default value if None
* `max_value`: Implements a maximum value constraint
* `min_value`: Implements a minimum value constraint

### DateField

The date field allows you to pass dates to your model. This field uses a preset of custom date formats to identify the structure of a date incoming value. For instance `%d-%m-%Y` will be able to resolve `1-1-2021`.

* `date_format`: Additional format that can be used to parse the incoming value
* `default`: Default value if None

```python
class MyModel(Model):
    date = DateField("%d-%m-%Y")
```

Generally speaking, most date formats are covered so you wouldn't need to implement a generally used format.

### AgeField

The age field works likes the DateField but instead of returning the date, it will return the difference between the date and the current date which corresponds to a person's age.

* `date_format`: Indicates how to parse the incoming data value
* `default`: Default value if None

### ListField

An array field will store an array of values that are all evalutated to an output field that you would have specified.

__N.B.__ Note that the value of an ArrayField is implemented as is in the final DataFrame. Make sure you are using this field correctly in order to avoid unwanted results.

### CommaSeperatedField

Create a comma separated field in your model.

__N.B.__ Note that the value of a CommaSeperatedField is implemented as is in the final DataFrame. Make sure you are using this field correctly in order to avoid unwanted results.

### RegexField

Parse an element within a given value using a regex expression before storing it in your model.

```python
RegexField(r'(\d+)(?<=\€)')
```

### BooleanField

Adds a boolean based value to your model. Uses classic boolean represenations such as `on, off, 1, 0, True, true, False or false` to resolve the value.

### RelatedModelField

This field allows you to create a direct relationship with any existing models of your project. Suppose you have the given models:

```python
from zineb.models.datastructure import Model
from zineb.models import fields

class Tournament(Model):
    location = fields.CharField()


class Player(Model):
    full_name = fields.CharField()

```

You might be tempted when scrapping your data to instantiate both models like this:

```python
class MySpider(Spider):
    def start(self, soup, **kwargs):
        player = Player()
        tournament = Tournament()
        
        player.add_value('full_name', 'Roland Garros')
        tournament.add_value('location', 'Paris')
```

This creates a lot of code and is not necessarily the most efficient way. The `RelatedModelField` resolves this problem by creating a forward and backward relationship between two different models.

The above technique can then be simplified the code below:

```python
from zineb.models.datastructure import Model
from zineb.models import fields

class Tournament(Model):
    location = fields.CharField()


class Player(Model):
    full_name = fields.CharField()
    tournament = fields.RelatedModelField(Tournament)
```

Which would then allow us to do the following:

```python
class MySpider(Spider):
    def start(self, soup, **kwargs):
        player = Player()
        
        player.add_value('full_name', 'Roland Garros')
        player.tournament.add_value('location', 'Paris')

        player.save(commit=False)   
```

It does not keep track of the individual relationship between the main model and the related model. In other words, all data from the main model will receive the same data from the related model contrarily to a database foreign key.

This is ideal for creating nested data within your model.

The resulting data would be:

```json
[
    {
        "id": 1,
        "full_name": "Roland Garros",
        "tournament": [
            {
                "id": 1,
                "location": "Paris"
            },
            {
                "id": 2,
                "location": "New-York"
            }
        ]
    }
]
```

If you want to keep track of the relationship between an item between two models use the `foreign_key` flag. The result would then be:

```json
[
    {
        "id": 1,
        "full_name": "Roland Garros",
        "tournament": {
            "id": 1,
            "location": "Paris"
        }
    }
]
```

Finally you can also keep track of multiple related values by using the `multiple` flag:

```json
[
    {
        "id": 1,
        "full_name": "Roland Garros",
        "tournament": [
            {
                "id": 1,
                "location": "Paris"
            },
            {
                "id": 5,
                "location": "France"
            }
        ]
    }
]
```

### Creating your own field

You an also create a custom field by suclassing `zineb.models.fields.Field`. When doing so, your custom field has to provide a `resolve` function in order to determine how the value should be parsed and a `_to_python_object` function in order to know under which python type the data should be represented (str, int...).

```python
class MyCustomField(Field):
    _dtype = str

    def _to_python_object(self, clean_value):
        # Code here

    def resolve(self, value):
        initial_result = super().resolve(value)

        # Rest of your code here
```

## Validators [initial validators]

Validators make sure that the value that was passed respects the constraints that were implemented as a keyword arguments on the field class. There are five basic validations that could possibly run if they are specified.

* Maximum length (`max_length`)
* Nullity (`null`)
* Defaultness (`default`)
* Validity (`validators`)

### Maximum or Minimum length

The maximum or minimum length check ensures that the value does not exceed a certain length using `validators.max_length_validator` or `validators.min_length_validator`.

### Nullity

The nullity validation ensures that the value is not null and that if a default is provided, that null value be replaced by the latter. It uses `validators.validate_is_not_null`.

### Practical examples

For instance, suppose you want only values that do not exceed a certain length:

```python
name = CharField(max_length=50)
```

Or suppose you want a default value for fields that are empty or blank:

```python
name = CharField(default='Kylie Jenner')
```

Remember that validators will validate the value itself for example by making sure that an URL is indeed an url or that an email follows the expected pattern that you would expect from an email.

Suppose you want only values that would be `Kendall Jenner`. Then you could create a custom validator that would do the following:

```python
def check_name(value):
    if value == "Kylie Jenner":
        raise ValidationError(...)

name = CharField(validators=[check_name])
```

You can also create validators that match a specific regex pattern using the `zineb.models.validators.regex_compiler` decorator:

```python
from zineb.models.datastructure import Model
from zineb.models.fields import CharField
from zineb.exceptions import ValidationError
from zineb.models.validators import regex_compiler

@regex_compiler(r'\d+')
def custom_validator(clean_value):
    if value > 10:
        raise ValidationError(...)

class Player(Model):
    age = IntegerField(validators=[custom_validator])
```

__NOTE:__ The result of the regex compiler is reinjected into your custom validator on which you can then do your own custom checks.

__NOTE:__ Validators are not expected to return any result and will also raise a blocking error 

#### Field resolution

In order to get the complete structured data, you need to call `save` which will return the values as list stored into the `SmartDict` container.

```python
player.add_value("name", "Kendall Jenner")
player.save()

# -> List
```

## Functions

Functions a built-in elements that can modify the incoming value in some kind of way before sending it to the `SmartDict` container through your model.

### Add, Substract, Divide, Multiply

Allows you to run an arithmetic operation on an incoming value.

```python
from zineb.models.functions import Add, Substract, Divide, Multiply

player.add_calculated_value('height', 175, Add(5))
player.add_calculated_value('height', 175, Substract(5))
player.add_calculated_value('height', 175, Divide(1))
player.add_calculated_value('height', 175, Multiply(1))

# -> {'height': [180]}
# -> {'height': [170]}
# -> {'height': [175]}
# -> {'height': [175]}
```

### ExtractYear, ExtractMonth, ExtractDay

From a string that contains a date, extract the year, the date or the day.

```python
from zineb.models.functions import ExtractYear

player.add_value('competition_year', ExtractYear('11-1-2021'))
player.add_value('competition_month', ExtractMonth('11-1-2021'))
player.add_value('competition_day', ExtractDay('11-1-2021'))

# -> {'competition_year': [2021]}
# -> {'competition_month': [11]}
# -> {'competition_day': [1]}
```

### When

Allows you to conditionally implement a value in the model if it respects a set of conditions.

```python
from zineb.models.functions import When

player.add_value('age', When(21, 25, else_condition=None))
```

__NOTE__: If no value is provided to the `else_condition`, the incoming value is considered to be the default one to implement in the model.

### Smallest, Greatestt

From a set of incoming data, pick the smallest or the greatest from the list. This requires that all values are of the same type or an error will be raised.

```python
from zineb.models.functions import Smallest, Greatest

player.add_value('name', Smallest('Kendall', 'Kylie', 'Hailey'))
player.add_value('revenue', Greatest(12000, 5000, 156000))
```

# Zineb special wrappers

# HTTPRequest

Zineb uses a special built-in HTTPRequest proxy class that wraps the following classes:

* The `requests.Request` response class
* The `bs4.BeautifulSoup` object

In general, you will not need to interact with this class because it's just an interface for implementing additional functionnalities to the above classes.

* `follow`: create a new instance of the class whose response will be one created from the url to follow
* `follow_all`: create new instances of the class who responses will be ones created from the urls to follow
* `urljoin`: join a domain to a given path

# HTMLResponse

It wraps the BeautifulSoup object in order to implement some small additional functionalities:

* `page_title`: return the page's title
* `links`: return all the links of the page
* `images`: return all the images of the page
* `tables`: return all the tables of the page

# Utilities

## Link reconciliation

Most of times, when you retrieve links from a page, they are returned as relative paths. The ``urljoin`` method reconciles the url of the visited page with that path.

```python
# <a href="/kendall-jenner">Kendall Jenner</a>

# Now we want to reconcile the relative path from this link to
# the main url that we are visiting e.g. https://example.com

request.urljoin("/kendall-jenner")

# -> https://example.com/kendall-jenner
```

## File collection

Collect files within a specific directory using `collect_files`. Collect files also takes an additional function that can be used to filter or alter the final results.

# Settings

This section will talk about all the available settings for your project and how they should be used.

## PROJECT_PATH

Represents the current path for your project. This setting is not to be changed.

## SPIDERS

In order for your spiders to be executed, they should be registered here. The name of the spider class serves as the name of the spider to be run.

```python
SPIDERS = [
    "MySpider"
]
```

## DOMAINS

You can restrict your project to use only to a specific set of domains by ensuring that no request is sent if it matches one of the domains within this list.

```python
DOMAINS = [
    "example.com"
]
```

## ENSURE_HTTPS

Enforce that every link in your project is a secured HTTPS link. This setting is set to False by default.

## USER_AGENTS

A user agent is a characteristic string that lets servers and network peers identify the application, operating system, vendor, and/or version of the requesting [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent).

Implement additional sets of user agents to your projects in addition to those that were already created.

## RANDOMIZE_USER_AGENTS

Specifies whether to use one user agent for every request or to randomize user agents on every request. This setting is set to to False by default.

## DEFAULT_REQUEST_HEADERS

Specify additional default headers to use for each requests.

The default initial headers are:

* `Accept-Language` - en
* `Accept` - text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
* `Referrer` - None

## PROXIES

Allows every request to be sent via a proxy. A random proxy is selected and implemented within each request.

`PROXIES` accepts a list of tuples implemeting a loc e.g. http, https and the IP address to bee used.

```python
PROXIES = [
    ("http", "127.0.0.1"),
    ("https", "127.0.0.1")
]
```

## RETRY

Specifies the retry policy. This is set to False by default. In other words, the request silently fails and never retries.

## RETRY_TIMES

Specificies the amount of times the the request is sent before eventually failing.

## RETRY_HTTP_CODES

Indicates which status codes should trigger a retry. By default, the following codes: 500, 502, 503, 504, 522, 524, 408 and 429 will trigger it.

## TIME_ZONE

Indicates which timezone to use when manipulating dates and times in the application. The default is `America/Chicago`.
