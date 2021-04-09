# Versions

## Version 1.0.0-alpha

**ISSUES**

* The middlewares do not load properly or do not load at all
* The settings in `zineb.settings.Settings` loads twice [once in the `zineb.settings__init__` when the project has started and a second time when...]. Technically, we would want to load the settings once when everything is set and then be able to lazily use these settings in the rest of the program without forcing that first initial preload in the \_\_init\_\_.
* The settings file does not include almost anything from the user's settings file which thus prevents a correct pointing towards the directories of the project
* When loading the project's spiders module, something calls the .save() method on the Model class
