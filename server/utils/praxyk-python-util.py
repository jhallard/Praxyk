#!/usr/bin/env python

import praxyk

if __name__ == "__main__":
    praxyk_int = praxyk.return_int()
    praxyk_string = praxyk.return_string()
    praxyk_double = praxyk.return_double()
    praxyk_char = praxyk.return_char()

    print("praxyk_int = {0}".format(praxyk_int))
    print("praxyk_string = {0}".format(praxyk_string))
    print("praxyk_double = {0}".format(praxyk_double))
    print("praxyk_char = {0}".format(praxyk_char))
