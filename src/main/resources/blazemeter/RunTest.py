#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import json
import sys
import requests
import time

# Call URL with proper error handling
def callUrl(verb, url):
    try:
        if verb == 'post':
            response = requests.post(url, auth=(id, secret))
        elif verb == 'get':
            response = requests.get(url, auth=(id, secret))
        else:
            print 'HTTP verb error!'
            print 'Reason: Only POST and GET verbs supported.'
            sys.exit(201)

        # Check to see if the request was successful
        output = response.json()
        if output.get('error'):
            print 'HTTP %s error!' % output.get('error').get('code')
            print 'Reason: %s' % output.get('error').get('message')
            sys.exit(202)

        return output

    # Catch all exceptions
    except requests.HTTPError as error:
        print 'HTTP %s error!' % error.response.status_code
        print 'Reason: %s' % error.message
        sys.exit(203)
    except requests.RequestException as error:
        print 'Network error!'
        print 'Reason: %s' % error.message
        sys.exit(204)
    except ValueError as error:
        print 'JSON parsing error!'
        print 'Reason: %s' % error.message
        sys.exit(205)
    except Exception as error:
        print 'Uncaught error!'
        print 'Reason: %s' % error
        sys.exit(206)

# Initialize variables
base_url = server.get('url')
data = ''
master = ''

# Make sure all the required paramaters are set
if not base_url.strip():
    print 'Input error!'
    print 'Reason: Server configuration url undefined\n'
    sys.exit(101)

if not id.strip():
    print 'Input error!'
    print 'Reason: Parameter id undefined\n'
    sys.exit(102)

if not secret.strip():
    print 'Input error!'
    print 'Reason: Parameter id undefined\n'
    sys.exit(103)

if not test.strip():
    print 'Input error!'
    print 'Reason: Parameter test undefined\n'
    sys.exit(104)

# Start the test
start_test_url = '%s/tests/%s/start' % (base_url, test)
data = callUrl('post', start_test_url)
session = data.get('result').get('sessionsId')[0]

# Monitor the progress of the session
session_status_url = '%s/sessions/%s/status' % (base_url, session)
while True:
    data = callUrl('get', session_status_url)
    if data.get('result').get('status') == "ENDED":
        if 'errors' in data.get('result') and data.get('result').get('errors'):
            print 'Session %s error!' % data.get('result').get('errors').get('code')
            print 'Reason: %s' % data.get('result').get('errors').get('message')
            sys.exit(301)
        else:
            break
    time.sleep(30)

# Retrieve the master id from the session
session_url = '%s/sessions/%s' % (base_url, session)
data = callUrl('get', session_url)
master = data.get('result').get('masterId')

# Review the test report
master_url = '%s/masters/%s' % (base_url, master)
data = callUrl('get', master_url)
if 'passed' in data.get('result') and data.get('result').get('passed') == False:
    print 'BlazeMeter test %s failed!' % test
    print '```'
    print json.dumps(data)
    print '```'
    sys.exit(1)

# Print output
print 'BlazeMeter test %s completed successfully' % test
print '```'
print json.dumps(data)
print '```'
sys.exit(0)
