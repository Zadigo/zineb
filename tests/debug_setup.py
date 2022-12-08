import os

import zineb

# Helps debug the setup function by using tests.testproject in
# tests folder

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject')

zineb.setup()
