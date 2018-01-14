#!/bin/sh

xgettext -L glade --output=po/ezadb.pot $(find ./ezadb/gui -name "*.ui")
xgettext --join-existing --language=Python --keyword=_ --output=po/ezadb.pot --from-code=UTF-8 `find ./ezadb/gui -name "*.py"`