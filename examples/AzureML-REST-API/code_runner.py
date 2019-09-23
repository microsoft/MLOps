import sys
import os
import subprocess


def run_command(program_and_args, # ['python', 'foo.py', '3']
                working_dir=None, # Defaults to current directory
                env=None):

    if working_dir is None:
        working_dir = os.getcwd()

    output = ""
    process = subprocess.Popen(program_and_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=working_dir, shell=False, env=env)
    for line in process.stdout:
        line = line.decode("utf-8").rstrip()
        if line and line.strip():
            # Stream the output
            sys.stdout.write(line)
            sys.stdout.write('\n')
            # Save it for later too
            output += line
            output += '\n'

    process.communicate()
    retcode = process.poll()

    if retcode:
        raise subprocess.CalledProcessError(retcode, process.args, output=output, stderr=process.stderr)

    return retcode, output


if __name__ == "__main__":
    ret, _ = run_command(sys.argv[1:])
