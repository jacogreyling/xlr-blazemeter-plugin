#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import json
import sys
import urllib2
import ssl
import time
import base64

# Call URL with proper error handling
def callUrl(verb, url):
    data = {}
    base64string = base64.encodestring('%s:%s' % (keyId, secret)).replace('\n', '')
    context = ssl._create_unverified_context()

    try:
        if verb == 'post':
            request = urllib2.Request(url, data)
        elif verb == 'get':
            request = urllib2.Request(url)
        else:
            print 'HTTP verb error!\n'
            print 'Reason: Only POST and GET verbs supported.\n'
            sys.exit(201)

        request.add_header("Authorization", "Basic %s" % base64string)            
        response = urllib2.urlopen(request, context=context)
        output = json.loads(response.read())

        return output
    # Catch all exceptions
    except urllib2.HTTPError as error:
        print 'HTTP %s error!\n' % error.code
        print 'Reason: %s (URL: %s)\n' % (error.msg, url)
        sys.exit(202)
    except urllib2.URLError as error:
        print 'Network error!\n'
        print 'Reason: %s\n' % error.reason
        sys.exit(203)
    except ValueError as error:
        print 'JSON parsing error!\n'
        print 'Reason: %s\n' % error.message
        sys.exit(204)
    except Exception as error:
        print 'Uncaught error!\n'
        print 'Reason: %s\n' % error
        sys.exit(205)

# Initialize variables
base_url = server.get('url').strip('/')
app_url = ''
data = ''
master = ''
project = ''
account = ''

# Make sure all the required paramaters are set
if not base_url.strip():
    print 'Input error!\n'
    print 'Reason: Server configuration url undefined\n'
    sys.exit(101)

if not keyId.strip():
    print 'Input error!\n'
    print 'Reason: Parameter keyId undefined\n'
    sys.exit(102)

if not secret.strip():
    print 'Input error!\n'
    print 'Reason: Parameter secret undefined\n'
    sys.exit(103)

if not test.strip():
    print 'Input error!\n'
    print 'Reason: Parameter test undefined\n'
    sys.exit(104)

if not pollingInterval:
    print 'Input error!\n'
    print 'Reason: Parameter pollingInterval undefined\n'
    sys.exit(104)

# Start the test
start_test_url = '%s/tests/%s/start' % (base_url, test)
print 'Starting BlazeMeter test\n'
data = callUrl('post', start_test_url)
session = data.get('result').get('sessionsId')[0]

# Monitor the progress of the session
print 'The following session id has been created for this test run: %s\n' % session
session_status_url = '%s/sessions/%s/status' % (base_url, session)
count = 1
while True:
    print 'Checking to see if the test is complete: retry #%d\n' % count
    data = callUrl('get', session_status_url)
    if data.get('result').get('status') == "ENDED":
        if 'errors' in data.get('result') and data.get('result').get('errors'):
            error = data.get('result').get('errors')[0]
            print 'Session %s error!\n' % error.get('code')
            print 'Reason: %s\n' % error.get('message')
            sys.exit(301)
        else:
            break
    count += 1   
    time.sleep(pollingInterval)

# Retrieve the master id from the session
session_url = '%s/sessions/%s' % (base_url, session)
print 'Retrieving the report id in order to lookup the test results report\n'
data = callUrl('get', session_url)
master = data.get('result').get('masterId')
project = data.get('result').get('projectId')

# Retrieve the various elements to build a url in order to view the reports
account_url = '%s/accounts' % base_url
print 'Retrieving account information so we can generate a test report summary URL\n'
data = callUrl('get', account_url)
result = data.get('result')[0]
if result and 'id' in result:
    account = result.get('id')
    app_url = result.get('appUrl')
    print 'Test report summary URL: %s/app/#/accounts/%s/workspaces/%s/projects/%s/masters/%s/summary\n' % (app_url, account, workspace, project, master)

# Review the test report
master_url = '%s/masters/%s' % (base_url, master)
data = callUrl('get', master_url)
if 'passed' in data.get('result') and data.get('result').get('passed') == False:
    print 'BlazeMeter test %s failed!\n' % test
    print '```'
    print json.dumps(data)
    print '```'
    sys.exit(1)

# Print output
print 'BlazeMeter test %s completed successfully\n' % test
print '```'
print json.dumps(data)
print '```'
sys.exit(0)
