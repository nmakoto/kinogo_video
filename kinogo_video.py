#!/usr/bin/env python3
# encoding:utf-8:
#
# Generate html page with only player based on kinogo.net site information
#

import re
import base64
import urllib.request as ur

from argparse import ArgumentParser


class KinoGo(object):
    def __init__(self):
        self._site_url = None
        self._param_file = None
        self._param_st = None
        self._param_comment = None
        self._file = None

        if not self.parse_args():
            return

        if not self._site_url:
            return

        if not self._get_page():
            return

        if not self._file:
            name = self.url_to_name(self._site_url)
            if not name:
                name = 'output'
            self._file = name + '.html'

        self._gen_page()


    @staticmethod
    def url_to_name(url):
        name = re.sub(r'.*/(.*?)\.htm.?$', r'\1', url)
        if name == url:
            return None
        return name

    def parse_args(self):
        ap = ArgumentParser(description='KinoGo.net video page grabber')
        ap.add_argument('--url', action='store', type=str, help='site url to parse (required)')
        ap.add_argument('--out', action='store', type=str, help='output html page')

        args = ap.parse_args()
        if args.url:
            self._site_url = args.url

        if args.out:
            self._file = args.out

        if not args.url:
            ap.print_help()
            return False

        return True

    def _get_page(self):
        try:
            req = ur.Request(self._site_url)
            req.add_header("User-Agent", "Mozilla")
            f = ur.urlopen(req)
            data = f.read().decode('cp1251')
            coded_block = re.search(
                r'<script type="text/javascript">document\.write\(Base64\.decode\(\'(.*?)\'\)\);</script>',
                data
            )
            if not coded_block:
                return False

            block = base64.b64decode(coded_block.group(1).encode())
            params = re.search(
                r'flashvars.*?comment=(.*?)&amp;.*?st=(.*?)&amp;.*?file=(.*?)&amp;',
                block.decode())

            if not params:
                return False

            self._param_comment = params.group(1)
            self._param_st = params.group(2)
            self._param_file = params.group(3)
            return True

        except (ur.URLError, ValueError) as ex:
            print("Error: {}".format(ex))

        return False

    def _gen_page(self):
        flashvars = 'comment={}&amp;st={}&amp;file={}'.format(
            self._param_comment,
            self._param_st,
            self._param_file)
        data = '''<!DOCTYPE html5>
<html lang="ru-RU">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style>
.dark {
    background-color: #000;
}

.playerbox {
    display: block;
}

.player {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 1200px;
    height: 820px;
    margin-left: -600px;
    margin-top: -410px;
}
</style>
</head>
<body class="dark">
<div class="playerbox">
<object class="player" type="application/x-shockwave-flash" data="http://kinogo.net/templates/kinogo/player/player.swf">
    <param name="bgcolor" value="#000000">
    <param name="wmode" value="transparent">
    <param name="allowFullscreen" value="true">
    <param name="allowScriptAccess" value="always">
    <param name="movie" value="http://kinogo.net/templates/kinogo/player/player.swf">
    <param name="flashvars" value="''' + flashvars + '''">
</object>
</div>
</body>
</html>
'''
        f = open(self._file, mode='w+', encoding='utf-8')
        f.write(data)
        f.close()


def main():
    KinoGo()


if __name__ == '__main__':
    main()
