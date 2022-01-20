# XXXX

xxx is a modern HTML parser with which you can query anything on a given page.

## Getting started

```python
from zineb.html_parser.parsers import Extactor

extractor = Extractor()
extractor.resolve(html_page_as_string)
```

XXX uses Python's default `html.HTMLParser` to read  each lines of the HTML page. Before sending the string to the parser, the page is formatted to a standard format using `lxml.html_from_string`.

Once the string is processed, each html tag on the page is converted into a Python object which will then be used to
run all the queries on the page.

## Querying objects on the page

XXX interfaces the queries via a `Manager` class which provides a set of default functions. The `Manager` class can be subclassed and additional custom functions can be added as we'll see later on.

### Manager API

Consider that the Manager API deals with queries at the very top level on the html page.

#### Get title

Returns the title of the current page.

```python
extractor.manager.get_title
-> Example Website
```

#### Links

Returns all the links present on the current page. Returns a (#QuerySet)[QuerySet].

```python
extractor.manager.links

# QuerySet([<a>, <a>])
```

#### Tables

Returns all the tables present on the current page. Returns a (#QuerySet)[QuerySet].

```python
extractor.manager.tables

# QuerySet([<table>, <table>])
```

#### Find

Returns a specific tag on the page. Returns an (#HTMLTag)[HTMLTag].

```python
extractor.manager.find('a')

# Tag -> <a>
```

#### Find all

Returns a specific tag on the page. Returns a (#QuerySet)[QuerySet].

```python
extractor.manager.find_all('a')

# QuerySet([<a>, <a>])
```

#### Save

Saves the html page to a file.

```python
extractor.manager.save('myfile')
```

#### Live update

Fetches a newer version of the html page using a url or a string.

```python
extractor.manager.live_update(url='http://example.com')
```

### QuerySet API

Certain functions will return a list of tags that are aggregated under `QuerySet`. This implements additional querying functionnalities but also allows for the original html data to stay untouched. Each query generates a new queryset with sub data that can be queried.

The queries on QuerySet allows to deal with aggregation of multiple tags.

Consider this example:

```python
queryset.find_all('a').find_all('a', attrs={'id': 'test'}).exclude('a', attrs={'id': 'test2'})
```

Each element of the chain returns a new `QuerySet` copy on which we can run additional queries. This can be done until we reach the tag level or that the queryset is empty.

Note that every time a new `QuerySet` is created, the data that the next element of the chain will use to filter tags will be the result of the previous query stored in the previously created one.

#### First

Returns the first item of the queryset. Returns a Tag.

```python
tags = extractor.manager.find_all('a')
tags.first

# Tag -> <a>
```

#### Last

Returns the last item of the queryset. Returns a Tag.

```python
tags = extractor.manager.find_all('a')
tags.last

# Tag -> <a>
```

#### Count

Returns the number of items in the queryset.

```python
tags = extractor.manager.find_all('a')
tags.count()

# int -> 1
```

#### Save

Saves the queryset to a file.

```python
tags = extractor.manager.find_all('a')
tags.save('myfile')
```

#### Find

Find an element within the queryset.

```python
tags = extractor.manager.find_all('a')
tag = tags.find('a')

# Tag -> <a>
```

#### Find all

Find all the elements within the queryset.

```python
queryset = extractor.manager.find_all('a')
tags = queryset.find_all('a')

# QuerySet([<a>, <a>])
```

#### Exclude

Return items that do not contain a given or certain attributes.

```python
queryset = extractor.manager.find_all('a')
tags = queryset.exclude('a', attrs={'id': 'test'})

# QuerySet([<a>, <a>])
```

#### Distinct

Return elements that have a very disting attribute.

```python
queryset = extractor.manager.find_all('a')
tags = queryset.distinct('a', attrs={'id': 'test'})

# QuerySet([<a>, <a>])
```

#### Values

Return the data or value contained within each tag of the queryset.

```python
queryset = extractor.manager.find_all('a')
tags = queryset.values()

# List -> ['Click', 'Press', ...]
```

#### Values list

Returns the data or any attributes value contained within each tag of the queryset. You can specify which attributes to return specifically.

```python
queryset = extractor.manager.find_all('a')
tags = queryset.values('id', 'string')

# List -> [[('id', 'test'), ('data', 'Click)], ...]
```

#### Dates

Returns the date within an html tag as Python objects. If no date can be parsed, None will be stored in the return values.

```python
queryset = extractor.manager.find_all('div')
tags = queryset.dates('datetime')

# List -> [datetime.datetime(1, 1, 2000), ...]
```

#### Union

Concatenate two querysets into a third new queryset.

```python
q1 = extractor.manager.find_all('div')
q2 = extractor.lmanager.find_all('a')
q3 = q1.union(q2)

# QuerySet([<div>, <a>])
```

#### Exists

Checks if there are elements in the queryset.

```python
queryset = extractor.manager.find_all('div')
if queryset.exists():
    # Do something

# True or False
```

#### Contains

Checks if an element exists wihin the queryset.

```python
queryset = extractor.manager.find_all('div')
if queryset.contains('div'):
    # Do something

# True or False
```

#### Explain

Displays in verbose text what the queryset is composed of.

```python
queryset = extractor.manager.find_all('div')
queryset.explain()

# name: 'div', tag: <div>, ...
```

#### Generator

Defers the resolution of the new query.

```python
queryset = extractor.manager.find_all('div')
result = queryset.generator('a', attrs={'id': 'test'})

for item in result:
    # Do something

# Generator
```

#### Update

Update all the attribute list of the items within the queryset.

```python
queryset = extractor.manager.find_all('div')
result = queryset.update('a', 'id', 'test2')
```

### BaseTag API

Tags also provide additional query functionnalities for the children within them. Therefore calling one of these functions will only query the child elements of the tag.

#### Children

Returns all the children of a tag.

```python
tag = extractor.manager.find('div')
tag.children

# String
```

#### Find

Find a child element within the tag.

```python
tag = extractor.manager.find('div')
tag.find('a')

# Tag -> <a>
```

#### Find all

Find all child element within the tag by a specific name or attribute.

```python
tag = extractor.manager.find('div')
tag.find_all('a')

# QuerySet([<a>, <a>])
```

## Navigating the DOM

At the tag level, you can navigate the DOM very easily using these functions.

#### Previous element

Get the element directly before the current tag.

```python
tag = extractor.manager.find('div')
new_tag = tag.previous_element

# Tag
```

#### Next element

Get the element directly after the current tag.

```python
tag = extractor.manager.find('div')
new_tag = tag.next_element

# Tag
```

#### Contents

Get all the content within the tag.

```python
tag = extractor.manager.find('div')
result = tag.contents

# List
```

#### Get attribute

Get the attribute of a given tag.

```python
tag = extractor.manager.find('div')
queryset = tag.get_attr('div')

# String
```

#### Get previous

Get the previous element before the current tag by name.

```python
tag = extractor.manager.find('div')
queryset = tag.get_previous('div')

# Tag -> <div>
```

#### Get next

Get the next element before the current tag by name.

```python
tag = extractor.manager.find('div')
queryset = tag.get_next('div')

# Tag -> <div>
```

#### Get all previous

Get the all the previous elements before the current tag by name.

```python
tag = extractor.manager.find('div')
queryset = tag.get_all_previous('div')

# QuerySet([<div>, <div>])
```

#### Get all next

Get the all the next elements after the current tag by name.

```python
tag = extractor.manager.find('div')
queryset = tag.get_all_next('div')

# QuerySet([<div>, <a>])
```

#### Get parent

Get the parent of the current tag.

```python
tag = extractor.manager.find('div')
queryset = tag.get_parent

# QuerySet([<div>, <a>])
```

#### Get previous sibling

Get the previous sibling of the current tag.

```python
tag = extractor.manager.find('div')
queryset = tag.get_previous_sibling('div')

# Tag -> <div>
```

#### Get next sibling

Get the next sibling of the current tag.

```python
tag = extractor.manager.find('div')
queryset = tag.get_next_sibling('div')

# Tag -> <div>
```

#### String

Get the content of a given tag.

```python
tag = extractor.manager.find('div')
tag.string

# String
```
