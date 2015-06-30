import random
import string

# create a random string
def get_random_string():
    return (''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32)))

