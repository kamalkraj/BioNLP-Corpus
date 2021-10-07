# Copyright (c) 2019 NVIDIA CORPORATION. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import glob
import gzip
import os
import shutil
import urllib.request


class PubMedDownloader:

    def __init__(self, subset, save_path):
        
        self.subset = subset
        # Modifying self.save_path in two steps to handle creation of subdirectories
        self.save_path = save_path + '/'

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.save_path = self.save_path + '/' + subset

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.download_urls = {
            'baseline' : 'ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/',
            'daily_update' : 'ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/',
            'fulltext' : 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/',
            'open_access' : 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/'
        }


    def download(self,keep_extracted_only):
        print('subset:', self.subset)
        url = self.download_urls[self.subset]
        self.download_files(url)
        self.extract_files(keep_extracted_only)


    def download_files(self, url):
        url = self.download_urls[self.subset]
        output = os.popen('curl ' + url).read()

        if self.subset == 'fulltext' or self.subset == 'open_access':
            line_split = 'comm_use' if self.subset == 'fulltext' else 'non_comm_use'
            for line in output.splitlines():
                if line[-10:] == 'xml.tar.gz' and \
                        line.split(' ')[-1].split('.')[0] == line_split:
                    file = os.path.join(self.save_path, line.split(' ')[-1])
                    if not os.path.isfile(file):
                        print('Downloading', file)
                        response = urllib.request.urlopen(url + line.split(' ')[-1])
                        with open(file, "wb") as handle:
                            handle.write(response.read())

        elif self.subset == 'baseline' or self.subset == 'daily_update':
            for line in output.splitlines():
                if line[-3:] == '.gz':
                    file = os.path.join(self.save_path, line.split(' ')[-1])
                    if not os.path.isfile(file):
                        print('Downloading', file)
                        response = urllib.request.urlopen(url + line.split(' ')[-1])
                        with open(file, "wb") as handle:
                            handle.write(response.read())
        else:
            assert False, 'Invalid PubMed dataset/subset specified.'

    def extract_files(self,keep_extracted_only):
        if self.subset == 'baseline' or self.subset == 'daily_update':
            files = glob.glob(self.save_path + '/*.xml.gz')
        elif self.subset == 'fulltext' or self.subset == 'open_access':
            files = glob.glob(self.save_path + '/*.gz')        

        for file in files:
            print('file:', file)
            if self.subset == 'baseline' or self.subset == 'daily_update':
                input = gzip.GzipFile(file, mode='rb')
                s = input.read()
                input.close()

                out = open(file[:-3], mode='wb')
                out.write(s)
                out.close()
            elif self.subset == 'fulltext' or self.subset == 'open_access':
                shutil.unpack_archive(file)

            if os.path.isfile(file) and keep_extracted_only:
                os.remove(file)

def main(args):
    downloader = PubMedDownloader(args.dataset,args.path)
    if args.action == "download_extract":
        downloader.download(args.keep_extracted_only)
    elif args.action == "download":
        print('subset:', downloader.subset)
        url = downloader.download_urls[downloader.subset]
        downloader.download_files(url)
    elif args.action == "extract":
        downloader.extract_files(args.keep_extracted_only)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pubmed Downloader')
    parser.add_argument(
        '--dataset',
        type=str,
        help="Specify the dataset to download",
        choices={'baseline','daily_update','fulltext','open_access'}
        )
    parser.add_argument(
        '--action',
        type=str,
        help='Specify the action you want the app to take. download, download and extract',
        choices={'download','extract','download_extract'}
        )
    parser.add_argument(
        '--path',
        type=str,
        help='Specify the path to store the downloaded data'
        )
    parser.add_argument(
        '--keep_extracted_only',
        help='remove gz files after extraction',
        default=False, 
        action='store_true')
    args = parser.parse_args()
    main(args)
