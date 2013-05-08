Install
-------

Setup your virtualenv if desired.
````
git clone https://github.com/aptivate/commcare-api-wrapper.git
cd commcare-api-wrapper
pip install .
````

Usage
-----
This is intended for use by developers to see how we accessed the commcareapi,
feel free to take whatever is useful.

The information you will need to supply to access your commcare data from the 
api is as follows:
* domain: is the project space or name. it is in the url when you login to your
  commcarehq project e.g. https://www.commcarehq.org/a/testapi/ the domain is
  testapi
* app_id: this is a build id of an actual build of your app - its a little
  tricky to find and works with the unsupported piece of the API that we use to
get pieces out that we need. Go to your application in your project and find 
the Deploy section. You should see multiple versions that you have built over
time. Click on the Deploy button and a pop-up will appear with options like
"Preview in emulator", "Download to Java Phone." Look at the "Preview in
emulator" mode link and after /emulator/ you will find a 32-character key, that
is the app_id.
* user: user to login with - needs permission to access data from the app
* password: password from above app

You can also use it directly from the commandline using the dump-api-fixtures
script.
````
usage: dump_api_fixtures.py [-h] -u U -p P -d D {case,form} ...

positional arguments:
  {case,form}
    case       list cases or get case
    form       get form

optional arguments:
  -h, --help   show this help message and exit
  -u U         username (eg. "user@example.org")
  -p P         password
  -d D         domain 
````
If you just use case, then you will get a list of all cases, if you provide a
case_id or a form_id you will get just that information.

Tests
-----
To run the tests you will need to install py.test, and have a commcarehq
instance for certain tests.

````
pip install pytest
cd tests
py.test
````
By default this will run all the local tests, in addition there are apitests
that actually connect to commcarehq and test the api is still working as
expected. To run these tests, copy the credentials.json.example file and make a
file credentials.json

    {
        "domain": "",
        "app_id": "",
        "user": "",
        "password": ""
    }
This needs to be filled in with the information as described in usage above.

Credits & License
-----------------
All files unless further specified, copyright Aptivate (2013) with the following
License:

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

xform.py

Taken from https://github.com/dimagi/commcare-hq/blob/master/corehq/apps/app_manager/xform.py

with the following license:

    Copyright (c) 2009-2012, Dimagi Inc., and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
        * Neither the name of CommCare HQ, CommTrack, CommConnect, or Dimagi, nor
        the
        names of its contributors, may be used to endorse or promote products
        derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL DIMAGI INC. BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
