# -*- coding: utf-8 -*-
import logging
import sys
import re
import quopri
import base64
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log(msg):
    logging.info(msg)


def main():
    args = sys.argv
    if len(args) != 2:
        print("Usage: extract.py <mht file>")
        return
    mht = sys.argv[1]
    log('Extract multi-part of "%s" ...' % mht)
    # open file
    with open(mht, 'r') as f:
        for line in f.readlines():
            processline(line)


# global variables

boundary = ""
state = 'none'  # none, start-head, head-end
body = ""
content_type = ''
content_encoding = ''
content_location = ''


def processline(line):
    global state
    global body

    getboundary(line)
    sep = '------=%s' % boundary
    sep_end = '------=%s--' % boundary
    # print('sep: %s' % sep)
    line_stripped = line.strip()
    if line_stripped == sep or line_stripped == sep_end:
        state = 'start-head'
        log('status: %s' % state)
        # to save block
        save_block()
        # reset contentXXX and body
        reset_content()
        return

    if state == 'start-head':
        if line.strip() == '':
            state = 'head-end'
            return
        else:
            read_header(line)
            return

    if state == 'head-end':
        body = body + line


def save_block():
    decoded_body = ''
    if body == '':
        return
    else:
        # decode
        if content_encoding == 'quoted-printable':
            decoded_body = quopri.decodestring(body)
        if content_encoding == 'base64':
            decoded_body = base64.b64decode(body)
        log('will save file "%s", encoding=%s' % (content_location, content_encoding))
        # save to file
        save_file(decoded_body)


def save_file(decoded_body):
    # empty then return
    if not content_location:
        return
    # remove file://
    location = re.sub('file://', '', content_location)
    # remove C: driver path
    location = re.sub(r'\\?\w:', '', location)
    dirname, filename = os.path.split(location)
    subdir = os.path.relpath('./'+dirname)

    # mkdir at reverse second dir
    try:
        os.makedirs(subdir)
    except OSError:
        pass
    relative_file_name = os.path.join(subdir, filename)
    with open(relative_file_name, 'w') as f:
        log('saved file: %s' % relative_file_name)
        f.writelines(decoded_body)


def reset_content():
    global body
    global content_type
    global content_location
    global content_encoding
    body = ''
    content_type = ''
    content_encoding = ''
    content_location = ''


def read_header(line):
    log('readHeader: %s' % line.strip())
    global content_type
    global content_location
    global content_encoding
    # parse contentType...
    matcher = re.match('Content-Location:(.*)', line, flags=re.IGNORECASE)
    if matcher:
        # extract location
        content_location = matcher.group(1).strip()

    matcher = re.match('Content-Transfer-Encoding:(.*)', line, flags=re.IGNORECASE)
    if matcher:
        # extract encoding
        content_encoding = matcher.group(1).strip()

    matcher = re.match('Content-Type:(.*)', line, flags=re.IGNORECASE)
    if matcher:
        # extract type
        content_type = matcher.group(1).strip()


def getboundary(line):
    global boundary  # set global variable

    matcher = re.match(r'Content-Type: multipart/related; boundary="----=(.*)"', str(line))
    if matcher:
        boundary = matcher.group(1)


if __name__ == '__main__':
    main()