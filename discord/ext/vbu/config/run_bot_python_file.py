#!/usr/bin/env python
import voxelbotutils.__main__
parser = voxelbotutils.__main__.get_default_program_arguments()
args = parser.parse_args(['run-bot', '.'])
voxelbotutils.runner.run_bot(args)
