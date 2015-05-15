import flickr_api
from datetime import date, timedelta
import os.path
import shutil
import time

'''
PI Host 192.168.0.4
'''

TOKEN_FILE = 'token_file'
SIX_MONTHS = 182  # in days
PATH = 'photos'
DOWNLOADS = 'downloads'
# Follow Flickr instructions to get api key and secret
# Follow directions here to
# generate a OAUTH token
# https://github.com/alexis-mignon/python-flickr-api/wiki/Tutorial
flickr_api.set_auth_handler(TOKEN_FILE)
user = flickr_api.test.login()

today = date.today()

start = today - timedelta(SIX_MONTHS)

print 'Getting photos taken after', start.isoformat()
w = flickr_api.Walker(flickr_api.Photo.search,
                      user=user,
                      min_taken_date=start.isoformat())

# Download into downloads folder, if download fails
# photos folder stays in place and downloads is deleted
# if download succeeds, download folder is moved to photos

#delete a stray downloads dir if it exists
if os.path.isdir(DOWNLOADS):
    shutil.rmtree(DOWNLOADS)
os.makedirs(DOWNLOADS)

print "Attempting to download", len(w), "photos..."
i = 1
try:
    for p in w:
        attempt = 1
        while attempt <= 5:
            try:
                p.save(os.path.join(DOWNLOADS, "%04d.jpg" % (i,)), size_label='Original')
                if attempt > 1:
                    print 'Success after failure'
                i = i+1
                break
            except Exception as e:
                print "Retrying after error", e
                attempt = attempt + 1
                time.sleep(1)

        if (i % 25) == 0:
            print "Downloaded", i, "photos..."
except Exception as e:
    print 'Error getting photos', e

if i > 10:
    if os.path.isdir(PATH):
        shutil.rmtree(PATH)
    shutil.move(DOWNLOADS, PATH)
else:
    shutil.rmtree(DOWNLOADS)

print 'Finished downloading', i, 'photos.'
