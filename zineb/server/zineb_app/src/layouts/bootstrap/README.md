# Bootstrap for Vue
## Form
### Checkbox
```html
<base-checkbox id="dark-mode" :is-switch="true" label="Dark mode" @update:initial="toggleDarkMode" />
```

#### switch

### select

```html
<base-select :items="['A', 'B', 'C']" />
```

## Pagination

```html
<base-pagination :pages="4" />
```

## Dropdown

A dropdown menu represents a container to be used as a menu

```html
<dropdown-menu :show="show" animation="slideup">
    <dropdown-item-input link-name="Example input" />
    <dropdown-item link-name="Link 1" :active="true" />
    <dropdown-item-header link-name="Example header" />
    <dropdown-item link-name="Link 3" />
    <dropdown-item-divider />
    <dropdown-item link-name="Link 4" />
    <dropdown-item link-name="Link 5" icon="table" />
</dropdown-menu>
```

A dropdown menu needs to wrapped in order to benefit from the drop functionnalities

```html
<dropdown-button id="drop-1" v-slot="{show}">
    <dropdown-menu :show="show" animation="slide">
        <dropdown-item-input link-name="Example input" />
    </dropdown-menu>
</dropdown-button>
```

## Modal

```html
<base-modal-vue id="..." :show="..." non-invasive scrollable centered static-backdrop position="top-right" size="sm" @close="...">
    <p>...</p>
</base-modal-vue>
```

### Attributes

* `show`: true, false
* `non-invasive`: true, false
* `scrollable`: true, false
* `centered`: true, false
* `position`: top-right, top-left, bottom-right, bottom-left
* `size`: sm, md, lg, xl, fullscreen

### Events

* `@close`

## Offcanvas

```html
<base-offcanvas id="..." :show="..." allow-scroll position="..." @close="...">
    ...
</base-offcanvas>
```

### Attributes

* `show`: true, false
* `allow-scroll`: true, false
* `position`: top, bottom, start, end

### Events

* `@close`

## Dynmamic table

An advanced data table to filter, sort and manipulate data efficiently.

```html
<dynamic-table id="table1" :headers="['firstname', 'lastname', 'age']" :items="table" />
```

The `items` attribute receive data structured as below:

```json
[
    {
        "id": 1,
        "firstname": "Kendall",
        "lastname": "Jenner",
        "age": 35
    }
]
```


### Attributes

- `position` : top, bottom, start, end
- `static-backdrop` : true, false
- `allow-scroll` : true, false
- `show` : true, false
- `id`

### Emits

- @close


## List Groups

```html
<base-list-group>
    <base-list-group-item-action v-for="(item, i) in []" :key="i">
        {{ item.text }}
    </base-list-group-item-action>
</base-list-group>
```

If you wish to handle the items that were selected for future manipluation, you must pass the list of items to the `base-list-group` and then use the `handleSelection` function.

```html
<base-list-group v-slot="{ listGroupItems, handleSelection }" :items="items">
    <base-list-group-item-action v-for="(item, i) in listGroupItems" :key="i" @click="handleSelection(i, item)">
        {{ item.text }}
    </base-list-group-item-action>
</base-list-group>
```
