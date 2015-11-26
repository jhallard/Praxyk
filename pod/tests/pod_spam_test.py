#!/usr/bin/env python

import sys
import traceback
import inspect
import praxyk
def spam_test1():
    import praxyk
    from praxyk import spam
    try:
        print "ham1 result = "
        print praxyk.bayes_spam("/home/nikita/testdata/ham1")
        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

def spam_test2():
    import praxyk
    from praxyk import spam
    try:
        print "spam1 result = "
        print praxyk.bayes_spam("/home/nikita/testdata/spam1")
        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

def spam_test3():
    import praxyk
    try:
        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

if __name__ == "__main__":
    successful = spam_test1() and spam_test2() and spam_test3()
    sys.exit(0 if successful else 1)
