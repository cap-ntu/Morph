

def divide(x, y):
    try:
        if y == 0:
            return 5
        result = x / y
    except ZeroDivisionError:
        print "division by zero!"
    else:
        print "result is", result
    finally:
        print "executing finally clause"
        return 7
