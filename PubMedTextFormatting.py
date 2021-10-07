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

import pubmed_parser as pmp
from tqdm import tqdm


class PubMedTextFormatting:

    def __init__(self, pubmed_path, output_filename, abstract_min_length = 30, recursive = False):
        self.pubmed_path = pubmed_path
        self.recursive = recursive
        self.output_filename = output_filename
        self.abstract_min_length = abstract_min_length


    # This puts one article per line
    def merge(self):
        print('PubMed path:', self.pubmed_path)

        with open(self.output_filename, mode='w', newline='\n') as ofile:
            for filename in tqdm(glob.glob(self.pubmed_path + '/*.xml', recursive=self.recursive)):
                dicts_out = pmp.parse_medline_xml(filename)
                for dict_out in dicts_out:
                    if not dict_out['abstract']:
                        continue
                    try:
                        for line in dict_out['abstract'].splitlines():
                            if len(line) < self.abstract_min_length:
                                continue
                            ofile.write(line.strip() + " ")
                        ofile.write("\n\n")
                    except:
                        ofile.write("\n\n")
                        continue


def main(args):
    formatter = PubMedTextFormatting(args.dataset_path,args.output_filename,args.abstract_min_length,True)
    formatter.merge()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pubmed Abstract parser')
    parser.add_argument(
        '--dataset_path',
        type=str,
        help="Specify the dataset path where xml files are available",
        )
    parser.add_argument(
        '--output_filename',
        type=str,
        help="Specify the output filename"
        )
    parser.add_argument(
        '--abstract_min_length',
        type=int,
        default=30,
        help='Specify the minimum length of abstracts line, length less than this will be skipped'
        )
    args = parser.parse_args()
    main(args)
