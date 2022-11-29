#!/usr/bin/env python3

import sys
import logging

from argparse import ArgumentParser
from parser.openapi import OpenAPIParser
from parser.preprocessing import Preprocessor

logger = logging.getLogger(__name__)

def execute(args):
    import os

    if not os.path.exists(args.output):
        logger.exception('[EXCEPTION] Output is not given or not exist')
        return
    
    object_files = []
    link_files = []

    import shutil

    for root, dirs, files in os.walk(args.output):
        for f in files:
            os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    
    for file in os.listdir(args.input):

        if not os.path.isfile(os.path.join(args.input, file)):
            continue

        spec_json = os.fsdecode(file)
    
        if spec_json.endswith(".json"):
            logger.info(f'[INFO] About to process {spec_json}')
            processor = Preprocessor(os.path.join(args.input, spec_json), args.output)
            parser = OpenAPIParser(spec_json, processor.fix(), args.output, args.debug)

            try:
                parser.convert_objects(False)
            except Exception as ex:
                logger.exception(f'[EXCEPTION] Failure {ex}')
                continue

            try:
                parser.convert_links(False)
            except Exception as ex:
                logger.exception(f'[EXCEPTION] Failure {ex}')
                continue

            objectfile_renamed = os.path.join(args.output, f'objects-{spec_json}.csv')
            linkfile_renamed = os.path.join(args.output, f'links-{spec_json}.csv')

            os.rename(os.path.join(args.output, 'objects.csv'), objectfile_renamed)
            os.rename(os.path.join(args.output, 'links.csv'), linkfile_renamed)
            object_files.append(objectfile_renamed)
            link_files.append(linkfile_renamed)

            logger.info(f'[INFO] {objectfile_renamed} and {linkfile_renamed} created')
    
    '''
    merge object files
    TODO: robustness 1) header check 2) column matching 3) consider to use pandas
    '''
    object_files_merged = open(os.path.join(args.output, 'objects.csv'), 'a')
    header = ''
    header_set = False

    for object_file in object_files:
        csv_in = open(object_file)
        for line in csv_in:
            if not header_set:
                header = line
                header_set = True
            else:
                if line.startswith(header):
                    continue
            object_files_merged.write(line)
    
        csv_in.close()
        logger.info(f'[... MERGED {object_file} ...]')

    object_files_merged.close()

    '''
    merge link files
    TODO: robustness 1) header check 2) column matching 3) consider to use pandas
    '''
    object_links_merged = open(os.path.join(args.output, 'links.csv'), 'a')
    header = ''
    header_set = False

    for link_file in link_files:
        csv_in = open(link_file)
        for line in csv_in:
            if not header_set:
                header = line
                header_set = True
            else:
                if line.startswith(header):
                    continue
            object_links_merged.write(line)
    
        csv_in.close()
        logger.info(f'[... MERGED {link_file} ...]')

    object_links_merged.close()

    parser.zip_metadata()

def _parse_args(argv):
    parser = ArgumentParser()
    parser.add_argument('--input', default=None, type=str, help='directory where openapi spec json files are stored')
    parser.add_argument('--output', default=None, type=str, help='directory to save objects.csv and links.csv')
    parser.add_argument('--debug', default=False, type=bool, help='debug option. for example create additional spec validation file')
    parser.set_defaults(func=execute)

    args = parser.parse_args(argv[1:])
    return args

def _main(argv):
    args = _parse_args(argv)
    args.func(args)
    return 0

if __name__ == '__main__':

    """
    for release build
    """
    import sys, os
    os.environ["PATH"] += os.pathsep + os.path.join(os.getcwd())

    """
    logging
    """
    logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    sys.exit(_main(sys.argv))

