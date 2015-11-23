__author__ = 'Andrew'


def f():
    a = 10
    if a > 5:
        b = 10
    print b


def g():
    lambda_list = []
    for i in xrange(3):
        my_lambda = lambda x: x + i
        lambda_list.append(my_lambda)
    print lambda_list[0](10)
    print my_lambda(10)

# f()
g()