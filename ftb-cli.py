#!/usr/bin/env python3
# The MIT License (MIT)
# 
# Copyright (c) 2017 Rick Rongen>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# With Hhelp of:
#   https://stackoverflow.com/a/34503421
#   https://forum.feed-the-beast.com/threads/server-api.121687/#post-1441327
import requests
from lxml import etree
from optparse import OptionParser
from zipfile import ZipFile
import os
import sys

base_download_url = 'http://ftb.cursecdn.com/FTB2/modpacks/%(dir)s/%(version)s/%(pack)s'

class ModPack:
    def __init__(self, pack):
            self.author = optlist(pack.attrib,'author',None)
            self.curseProjectId = optlist(pack.attrib,'curseProjectId',None)
            self.description = optlist(pack.attrib,'description',None)
            self.dir = optlist(pack.attrib,'dir',None)  # TODO check
            self.image = optlist(pack.attrib,'image', None)
            self.logo = optlist(pack.attrib,'logo',None)
            self.mcVersion = optlist(pack.attrib,'mcVersion',None)
            self.minJRE = optlist(pack.attrib,'minJRE', '0')
            self.mods = optlist(pack.attrib,'mods',None)  # TODO to list
            self.name = optlist(pack.attrib,'name',None)
            self.oldVersions = optlist(pack.attrib,'oldVersions', '').split(';')
            self.repoVersion = optlist(pack.attrib,'repoVersion', None)
            self.serverPack = optlist(pack.attrib,'serverPack', None)
            self.url = optlist(pack.attrib,'url',None)
            self.version = optlist(pack.attrib,'version',None)
            

def optlist(the_list, key, default):
    return the_list[key] if key in the_list else default



def get_modpacks():
    response = requests.get('http://ftb.cursecdn.com/FTB2/static/modpacks.xml')
    parsed = etree.XML(response.text)
    packs = []
    for pack in parsed:
        packs.append(ModPack(pack))
    return packs

def download_pack(local, directory, version, pack):
    url = base_download_url % {'dir': directory, 'version': version, 'pack': pack}
    print('Getting %s storing to %s' % (url, local))
    response = requests.get(url, stream=True)
    with open(local, 'wb') as f:
        for chunk in response.iter_content(1024*1024*4):  # In chunks of 4 kilobyte
            sys.stdout.write('.')
            sys.stdout.flush()
            f.write(chunk)
            f.flush()

        sys.stdout.write('\n')
        print('Download done!')

def extract_zip(zippath):
    with ZipFile(zippath) as zf:
        zf.extractall()
    

def main():
    parser = OptionParser()
    parser.add_option('-p', '--pack', dest='pack', help='The FTB Pack to use, copy the name from the FTB site')
    parser.add_option('-v', '--version', dest='version', help='The version of the pac, leave empty for LATEST', default='LATEST')
    parser.add_option('-e', '--no-extract', dest='extract', action='store_false', default=True, help='Do not extract the zip file')
    parser.add_option('-d', '--delete', dest='delete', action='store_true', default=False, help='Delete the zipfile afterwards')
    parser.add_option('-c', '--client', dest='client', action='store_true', default=False, help='Download the client version instead of the server version')
    (options, args) = parser.parse_args()

    if not options.pack:
        print('--pack is required, type -h for help!')
        exit(-1)
    
    packs = get_modpacks()
    
    pack = [pack for pack in packs if pack.name == options.pack]
    if len(pack) == 0:
        print('Pack %s not found!' % options.pack)
        exit(-1)
    pack = pack[0]

    if options.version == 'LATEST':
        version = pack.version
    else:
        version = [version for version in pack.oldVersions if version == options.version]
        if len(version) == 0:
            print("Version %s not found for %s!" % (options.version, options.pack))
            exit(-1)
        version = version[0]
    version = version.replace('.','_')

    dlpack = pack.url if options.client else pack.serverPack

    print('Starting download of %s version %s' % (pack.name, version))

    #download_pack(dlpack, pack.dir, version, dlpack)

    if options.extract:
        print('Extracting %s' % dlpack)
        extract_zip(dlpack)
        if options.delete:
            print('Deleting %s' % dlpack)
            os.remove(dlpack)


if __name__ == '__main__':
    main()
