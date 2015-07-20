from django.core.urlresolvers import reverse
import inspect

def skip_test(self):
    pass

def chapter7(test):
    #If it is using goto (Chapter 16), test would fail, thus must skip it
    try:
        reverse('goto')
        print "Chapter 7 - Skipped: " + test.__name__
        return skip_test
    except:
        return test

def chapter8(test):

    #If it has login functionality tests would fail, thus must skip it
    try:
        # Chapter 9 login functionality
        reverse('login')
        print "Chapter 8 - Skipped: " + test.__name__
        return skip_test
    except:
        try:
            # Chapter 12 login functionality
            reverse('auth_login')
            print "Chapter 8 - Skipped: " + test.__name__
            return skip_test
        except:
            return test

def chapter9(test):
    #If it has login functionality from chapter 12 tests would fail, thus must skip it
    try:
        reverse('auth_login')
        print "Chapter 9 - Skipped: " + test.__name__
        return skip_test
    except:
        return test

def chapter10(test):
    #If it has login functionality from chapter 12 tests would fail, thus must skip it
    try:
        reverse('auth_login')
        print "Chapter 10 - Skipped: " + test.__name__
        return skip_test
    except:
        return test

def chapter15(test):
    # If mapping to url search exists, then run chapter 15 tests
    try:
        reverse('search')
        return test
    except:
        # Else if running chapter 16 tests, search mapping should be decommissioned
        print "Chapter 15 - Skipped: " + test.__name__
        return skip_test
