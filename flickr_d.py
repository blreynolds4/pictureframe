from datetime import date, timedelta, datetime
import flickrapi
import requests
import os
import logging
import shutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
lh = logging.FileHandler('flickr_download.log', mode='w')
lh.setLevel(logging.DEBUG)
lh.setFormatter(formatter)
logger.addHandler(lh)


PATH = 'photos'
DOWNLOADS = 'downloads'
THREE_MONTHS = 91

# "GET /?oauth_token=72157676847105361-61b14e34f1f033d5&oauth_verifier=5b4ac02ff1efddfc HTTP/1.1"


def getUrl(size, sizes):
    '''
    Get the url from the list of urls by size.
    '''
    for s in sizes:
        if size == s['label']:
            return s['source']

    # if size not found, use the last size object
    return sizes[-1]['source']


def main(key, secret, user, since):
    logger.info("Starting photo download %s", datetime.now().isoformat())
    logger.info('Getting photos taken after %s', since.isoformat())

    flickr = flickrapi.FlickrAPI(key, secret, format='parsed-json')

    i = 1
    page = 1
    while True:
        photos = flickr.photos.search(user_id=user,
                                      min_taken_date=since.isoformat(),
                                      page=page,
                                      per_page=100)
        max_page = photos['photos']['pages']
        page = photos['photos']['page']
        logger.info("Downloading page %d of %s pictures...", page, photos['photos']['total'])
        for p in photos['photos']['photo']:
            p_info = flickr.photos.getSizes(photo_id=p['id'], format='parsed-json')
            url = getUrl("Original", p_info['sizes']['size'])
            r = requests.get(url)
            filename = os.path.join(DOWNLOADS, "photo_%04d.jpg" % i)

            logger.debug("Downloading image %s to %s", url, filename)
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=512):
                    fd.write(chunk)
            i = i + 1

        # get the next page
        if page >= max_page:
            break
        else:
            page = page + 1

    if os.path.isdir(PATH):
        shutil.rmtree(PATH)
    shutil.move(DOWNLOADS, PATH)

    logger.info('Finished downloading %d photos at %s.', i-1, datetime.now().isoformat())


if __name__ == "__main__":
    api_key = os.getenv("FLICKR_API_KEY")
    api_secret = os.getenv("FLICKR_SECRET")
    user_id = os.getenv("FLICKR_USER")
    window = os.getenv("PICTURE_WINDOW", THREE_MONTHS)

    # remove old downloads
    if os.path.isdir(DOWNLOADS):
        shutil.rmtree(DOWNLOADS)
    os.makedirs(DOWNLOADS)

    today = date.today()
    start = today - timedelta(window)

    main(api_key, api_secret, user_id, start)
