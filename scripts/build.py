#!/usr/bin/env python3
#
# Build Lambda function with no binary dependencies
#
import contextlib
import distutils.dir_util
import os
import shutil
import subprocess
import sys
import tempfile


# -- helpers

@contextlib.contextmanager
def environ(**env):
    """Set the environment variables

    Temporarily set environment variables inside the context manager and
    fully restore previous environment afterwards
    """
    original_env = {key: os.getenv(key) for key in env}
    os.environ.update(env)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value


@contextlib.contextmanager
def cd(path):
    """Set the working directory

    Temporarily set the working directory inside the context manager and
    reset it to the previous working directory afterwards
    """
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


# -- main functions

def build_venv(workdir):
    # make project dir in workdir
    venv_dir = os.path.join(workdir, "venv")

    # make virtualenv with pip in workdir
    python_create_venv = [sys.executable, '-m', 'venv', venv_dir]
    subprocess.check_call(python_create_venv)
    return venv_dir


def install_requirements(venv_dir, project_dirname, requirements_file):
    if requirements_file != 'none':
        python_bindir = os.path.join(venv_dir, "bin")
        python_exe = os.path.join(python_bindir, os.path.basename(sys.executable))
        with cd(os.path.join(venv_dir, "..")):
            with environ(VIRTUAL_ENV=venv_dir,
                         PATH=python_bindir + os.pathsep + os.environ.get("PATH")):
                # install from requirements into project dir
                pip_install_requirements = [python_exe, '-m', 'pip', 'install', '-t', project_dirname, '-qqq',
                                            '-r', requirements_file]
                subprocess.check_call(pip_install_requirements)


def make_zipfile(venv_dir, project_dirname, tf_project_path, tf_lib_path, tf_output_filepath):
    with cd(os.path.join(venv_dir, "..")):
        # Copy scripts from terraform module variables into project dir
        if tf_lib_path != 'null':
            distutils.dir_util.copy_tree(tf_lib_path, project_dirname)
        distutils.dir_util.copy_tree(tf_project_path, project_dirname)

        # Create zip archive
        archive_name = os.path.splitext(tf_output_filepath)[0]
        with cd(project_dirname):
            shutil.make_archive(archive_name, "zip")


def main(args):
    with tempfile.TemporaryDirectory() as workdir:

        tf_requirements_file = os.environ.get('REQUIREMENTS_FILE', 'none')
        tf_project_path = os.environ.get('PROJECT_PATH')
        tf_lib_path = os.environ.get('LIB_PATH', 'none')
        tf_output_filepath = os.environ.get('OUTPUT_FILEPATH')

        project_dirname = "project"
        project_dir = os.path.join(workdir, project_dirname)
        os.mkdir(project_dir)

        venv_dir = build_venv(workdir)
        install_requirements(venv_dir, project_dirname, tf_requirements_file)
        make_zipfile(venv_dir, project_dirname, tf_project_path, tf_lib_path, tf_output_filepath)


if __name__ == "__main__":
    main(sys.argv)
