press_review
============

A press review app that help to organize and summarize your press review. This app is not useful for a production service. However, I use it mannually to organize and create summaries and to return a LibreOffice document.

## Requirements ##

Press Review is developed on a Ubuntu system running:
   * [Python](http://python.org) 2.7
   * [Django](http://djangoproject.com) 1.5
   * [Goose-extractor](https://pypi.python.org/pypi/goose-extractor/)
   * [Textblob](https://pypi.python.org/pypi/textblob/0.8.4)
   * [Nltk](https://pypi.python.org/pypi/nltk/2.0.4)
   * [ots](https://pypi.python.org/pypi/ots)


## Installing it ##

To enable `press_review` in your project you need to add it to `INSTALLED_APPS` in your projects `settings.py` file::

    INSTALLED_APPS = (
            ...
                    'press_review',
                            ...
    )

## Basic use ##

    Install this app, go to admin interface and enjoy. The .odt files are saved on the root path.

## Getting Involved ##

Open Source projects can always use more help. Fixing a problem, documenting a feature, adding translation in your language. If you have some time to spare and like to help us, here are the places to do so:

- GitHub: https://github.com/pepourquier/press_review

## Documentation ##

For the moment, there is no good documentation for this app.

## Next features ##
    
   * Write tests
   * Write documentation
   * Add an RSS aggregator
   * A lot of things

## Credits and License ##

Pierre-Emmanuel Pourquier create this. 

This program is free software: you can redistribute it and/or modify it under
the terms of either the MIT License. See the file `COPYING.md` for details.

All dependencies and requirements also are under the terms of an open source licence.
