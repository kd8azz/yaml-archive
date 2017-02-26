#!/usr/bin/env python

# Copyright Raoul Wols 2017
# Modified from original by Rene Rivera 2016 of github.com/boostorg/release-tools
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import sys
import inspect
import optparse
import os
import string
import time
import subprocess
import codecs
import shutil
import threading
import site
import tarfile
import multiprocessing
import urllib

class SystemCallError(Exception):
    def __init__(self, command, result):
        self.command = command
        self.result = result
    def __str__(self, *args, **kwargs):
        return "'%s' ==> %s"%("' '".join(self.command), self.result)

class utils:
    
    call_stats = []
    
    @staticmethod
    def call(*command, **kargs):
        utils.log( "%s> '%s'"%(os.getcwd(), "' '".join(command)) )
        t = time.time()
        result = subprocess.call(command, **kargs)
        t = time.time()-t
        if result != 0:
            print "Failed: '%s' ERROR = %s"%("' '".join(command), result)
        utils.call_stats.append((t,os.getcwd(),command,result))
        utils.log( "%s> '%s' execution time %s seconds"%(os.getcwd(), "' '".join(command), t) )
        return result
    
    @staticmethod
    def print_call_stats():
        utils.log("================================================================================")
        for j in sorted(utils.call_stats, reverse=True):
            utils.log("{:>12.4f}\t{}> {} ==> {}".format(*j))
        utils.log("================================================================================")
    
    @staticmethod
    def check_call(*command, **kargs):
        cwd = os.getcwd()
        result = utils.call(*command, **kargs)
        if result != 0:
            raise(SystemCallError([cwd].extend(command), result))
    
    @staticmethod
    def makedirs( path ):
        if not os.path.exists( path ):
            os.makedirs( path )
    
    @staticmethod
    def log_level():
        frames = inspect.stack()
        level = 0
        for i in frames[ 3: ]:
            if i[0].f_locals.has_key( '__log__' ):
                level = level + i[0].f_locals[ '__log__' ]
        return level
    
    @staticmethod
    def log( message ):
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stderr.write( '# ' + '    ' * utils.log_level() +  message + '\n' )
        sys.stderr.flush()

    @staticmethod
    def rmtree(path):
        if os.path.exists( path ):
            #~ shutil.rmtree( unicode( path ) )
            if sys.platform == 'win32':
                os.system( 'del /f /s /q "%s" >nul 2>&1' % path )
                shutil.rmtree( unicode( path ) )
            else:
                os.system( 'rm -f -r "%s"' % path )

    @staticmethod
    def retry( f, max_attempts=5, sleep_secs=10 ):
        for attempts in range( max_attempts, -1, -1 ):
            try:
                return f()
            except Exception, msg:
                utils.log( '%s failed with message "%s"' % ( f.__name__, msg ) )
                if attempts == 0:
                    utils.log( 'Giving up.' )
                    raise

                utils.log( 'Retrying (%d more attempts).' % attempts )
                time.sleep( sleep_secs )

    @staticmethod
    def web_get( source_url, destination_file, proxy = None ):
        import urllib

        proxies = None
        if proxy is not None:
            proxies = {
                'https' : proxy,
                'http' : proxy
                }

        src = urllib.urlopen( source_url, proxies = proxies )

        f = open( destination_file, 'wb' )
        while True:
            data = src.read( 16*1024 )
            if len( data ) == 0: break
            f.write( data )

        f.close()
        src.close()

    @staticmethod
    def unpack_archive( archive_path ):
        utils.log( 'Unpacking archive ("%s")...' % archive_path )
        tar = tarfile.TarFile(archive_path)
        tar.extractall()
        tar.close()

        # if extension in ( ".tar.gz", ".tar.bz2" ):
        #     import tarfile
        #     import stat


        #     mode = os.path.splitext( extension )[1][1:]
        #     tar = tarfile.open( archive_path, 'r:%s' % mode )
        #     for tarinfo in tar:
        #         tar.extract( tarinfo )
        #         if sys.platform == 'win32' and not tarinfo.isdir():
        #             # workaround what appears to be a Win32-specific bug in 'tarfile'
        #             # (modification times for extracted files are not set properly)
        #             f = os.path.join( os.curdir, tarinfo.name )
        #             os.chmod( f, stat.S_IWRITE )
        #             os.utime( f, ( tarinfo.mtime, tarinfo.mtime ) )
        #     tar.close()
        # elif extension in ( ".zip" ):
        #     import zipfile

        #     z = zipfile.ZipFile( archive_path, 'r', zipfile.ZIP_DEFLATED )
        #     for f in z.infolist():
        #         destination_file_path = os.path.join( os.curdir, f.filename )
        #         if destination_file_path[-1] == "/": # directory
        #             if not os.path.exists( destination_file_path  ):
        #                 os.makedirs( destination_file_path  )
        #         else: # file
        #             result = open( destination_file_path, 'wb' )
        #             result.write( z.read( f.filename ) )
        #             result.close()
        #     z.close()
        # else:
        #     raise Exception('Do not know how to unpack archives with extension \"%s\"' % extension)
    
    @staticmethod
    def build_boost_libs(variant, link, jobs, with_libraries=[]):
        variant = 'variant={}'.format(variant)
        link = 'link={}'.format(link)
        jobs = '-j{}'.format(str(jobs))
        if os.name == 'nt': # windows
            utils.check_call('bootstrap.bat')
            if len(with_libraries) == 0:
                utils.check_call('./b2', '-d0', '-q', link, jobs)
            else:
                for i, lib in enumerate(with_libraries):
                    with_libraries[i] = '--with-' + lib
                utils.check_call('./b2', '-d0', '-q', variant, link, jobs, *with_libraries)
        else: # assume unix-like
            if len(with_libraries) == 0:
                utils.check_call('./bootstrap.sh')
            else:
                libs = '--with-libraries=' + ','.join(with_libraries)
                utils.check_call('./bootstrap.sh', libs)
            utils.check_call('./b2', '-d0', '-q', variant, link, jobs)

    @staticmethod
    def make_file(filename, *text):
        f = codecs.open( filename, 'w', 'utf-8' )
        f.write( string.join( text, '\n' ) )
        f.close()
    
    @staticmethod
    def mem_info():
        if sys.platform == "darwin":
            utils.call("top","-l","1","-s","0","-n","0")
        elif sys.platform.startswith("linux"):
            utils.call("free","-m","-l")

class parallel_call(threading.Thread):
    
    def __init__(self, *command, **kargs):
        super(parallel_call,self).__init__()
        self.command = command
        self.command_kargs = kargs
        self.start()
    
    def run(self):
        self.result = utils.call(*self.command, **self.command_kargs)
    
    def join(self):
        super(parallel_call,self).join()
        if self.result != 0:
            raise(SystemCallError(self.command, self.result))

class script_common(object):
    '''
    Main script to run continuous integration.
    '''

    def __init__(self, ci_klass, **kargs):
        self.ci = ci_klass(self)

        opt = optparse.OptionParser(
            usage="%prog [options] [commands]")

        #~ Debug Options:
        opt.add_option( '--debug-level',
            help="debugging level; controls the amount of debugging output printed",
            type='int' )
        opt.add_option( '-j',
            help="maximum number of parallel jobs to use for building with b2",
            type='int', dest='jobs')
        opt.add_option('--branch')
        opt.add_option('--commit')
        kargs = self.init(opt,kargs)
        kargs = self.ci.init(opt, kargs)
        branch = kargs.get('branch',None)
        commit = kargs.get('commit',None)
        actions = kargs.get('actions',None)
        root_dir = kargs.get('root_dir',None)

        #~ Defaults
        self.debug_level = 0
        self.jobs = multiprocessing.cpu_count()
        self.branch = branch
        self.commit = commit
        ( _opt_, self.actions ) = opt.parse_args(None,self)
        if not self.actions or self.actions == []:
            if actions:
                self.actions = actions
            else:
                self.actions = [ 'info' ]
        if not root_dir:
            self.root_dir = os.getcwd()
        else:
            self.root_dir = root_dir
        self.build_dir = os.path.join(os.path.dirname(self.root_dir), "build")
        self.home_dir = os.path.expanduser('~')

        try:
            self.start()
            self.command_info()
            self.main()
            utils.print_call_stats()
        except:
            utils.print_call_stats()
            raise
    
    def init(self, opt, kargs):
        return kargs
    
    def start(self):
        pass

    def main(self):
        for action in self.actions:
            action_m = "command_"+action.replace('-','_')
            if hasattr(self,action_m):
                utils.log( "### %s.."%(action) )
                if os.path.exists(self.root_dir):
                    os.chdir(self.root_dir)
                getattr(self,action_m)()
    
    def __getattr__(self, attr):
        if attr.startswith('command_'):
            ci_command = getattr(self.ci, attr)
            if ci_command:
                def call(*args, **kwargs):
                    return ci_command(*args, **kwargs)
                return call
        return self.__dict__[attr]

    # Common test commands in the order they should be executed..
    
    def command_info(self):
        if self.ci and hasattr(self.ci,'command_info'):
            self.ci.command_info()
    
    def command_install(self):
        utils.makedirs(self.build_dir)
        os.chdir(self.build_dir)
        if self.ci and hasattr(self.ci,'command_install'):
            self.ci.command_install()
    
    def command_before_build(self):
        if self.ci and hasattr(self.ci,'command_before_build'):
            self.ci.command_before_build()

    def command_build(self):
        if self.ci and hasattr(self.ci,'command_build'):
            self.ci.command_build()

    def command_after_success(self):
        if self.ci and hasattr(self.ci,'command_after_success'):
            self.ci.command_after_success()

class ci_cli():
    '''
    This version of the script provides a way to do manual building. It sets up
    additional environment and adds fetching of the git repos that would
    normally be done by the CI system.
    
    The common way to use this variant is to invoke something like:
    
        mkdir boost-ci
        cd boost-ci
        python path-to/ci_boost_<script>.py --branch=develop
    
    Status: In working order.
    '''
    
    def __init__(self,script):
        self.script = script
    
    def init(self, opt, kargs):
        kargs['actions'] = [
            'clone',
            'install',
            'before_build',
            'build',
            ]
        return kargs
    
    def command_clone(self):
        '''
        This clone mimicks the way Travis-CI clones a project's repo. So far
        Travis-CI is the most limiting in the sense of only fetching partial
        history of the repo.
        '''

class ci_travis(object):
    '''
    This variant build releases in the context of the Travis-CI service.
    
    Status: In working order.
    '''
    
    def __init__(self,script):
        self.script = script
    
    def init(self, opt, kargs):
        kargs['root_dir'] = os.getenv("TRAVIS_BUILD_DIR")
        kargs['branch'] = os.getenv("TRAVIS_BRANCH")
        kargs['commit'] = os.getenv("TRAVIS_COMMIT")
        return kargs

    # Travis-CI commands in the order they are executed. We need
    # these to forward to our common commands, if they are different.
    
    def command_before_install(self):
        pass
    
    def command_install(self):
        pass

    def command_before_script(self):
        self.script.command_before_build()

    def command_script(self):
        self.script.command_build()

    def command_after_success(self):
        pass

    def command_after_failure(self):
        pass

    def command_before_deploy(self):
        pass

    def command_after_deploy(self):
        pass

    def command_after_script(self):
        pass

class ci_circleci(object):
    '''
    This variant build releases in the context of the CircleCI service.
    
    Status: Untested.
    '''
    
    def __init__(self,script):
        self.script = script
    
    def init(self, opt, kargs):
        kargs['root_dir'] = os.path.join(os.getenv("HOME"),os.getenv("CIRCLE_PROJECT_REPONAME"))
        kargs['branch'] = os.getenv("CIRCLE_BRANCH")
        kargs['commit'] = os.getenv("CIRCLE_SHA1")
        return kargs
    
    def command_machine_post(self):
        # Apt update for the pckages installs we'll do later.
        utils.check_call('sudo','apt-get','-qq','update')
        # Need PyYAML to read Travis yaml in a later step.
        utils.check_call("pip","install","--user","PyYAML")
    
    def command_checkout_post(self):
        os.chdir(self.script.root_dir)
        utils.check_call("git","submodule","update","--quiet","--init","--recursive")
    
    def command_dependencies_pre(self):
        # Read in .travis.yml for list of packages to install
        # as CircleCI doesn't have a convenient apt install method.
        import yaml
        utils.check_call('sudo','-E','apt-get','-yqq','update')
        utils.check_call('sudo','apt-get','-yqq','purge','texlive*')
        with open(os.path.join(self.script.root_dir,'.travis.yml')) as yml:
            travis_yml = yaml.load(yml)
            utils.check_call('sudo','apt-get','-yqq',
                '--no-install-suggests','--no-install-recommends','--force-yes','install',
                *travis_yml['addons']['apt']['packages'])
    
    def command_dependencies_override(self):
        self.script.command_install()
    
    def command_dependencies_post(self):
        pass
    
    def command_database_pre(self):
        pass
    
    def command_database_override(self):
        pass
    
    def command_database_post(self):
        pass
    
    def command_test_pre(self):
        self.script.command_before_build()
    
    def command_test_override(self):
        # CircleCI runs all the test subsets. So in order to avoid
        # running the after_success we do it here as the build step
        # will halt accordingly.
        self.script.command_build()
        self.script.command_after_success()
    
    def command_test_post(self):
        pass

class ci_appveyor(object):
    
    def __init__(self,script):
        self.script = script
    
    def init(self, opt, kargs):
        kargs['root_dir'] = os.getenv("APPVEYOR_BUILD_FOLDER")
        kargs['branch'] = os.getenv("APPVEYOR_REPO_BRANCH")
        kargs['commit'] = os.getenv("APPVEYOR_REPO_COMMIT")
        return kargs
    
    # Appveyor commands in the order they are executed. We need
    # these to forward to our common commands, if they are different.
    
    def command_install(self):
        pass
    
    def command_before_build(self):
        os.chdir(self.script.root_dir)
        utils.check_call("git","submodule","update","--quiet","--init","--recursive")
    
    def command_build_script(self):
        self.script.command_build()
    
    def command_after_build(self):
        pass
    
    def command_before_test(self):
        pass
    
    def command_test_script(self):
        pass
    
    def command_after_test(self):
        pass
    
    def command_on_success(self):
        self.script.command_after_success()
    
    def command_on_failure(self):
        pass
    
    def command_on_finish(self):
        pass

class script(script_common):
    '''
    Main script to build/test
    '''

    def __init__(self, ci_klass, **kargs):
        os.environ["PATH"] += os.pathsep + os.path.join(site.getuserbase(), 'bin')
        utils.log("PATH = %s"%(os.environ["PATH"]))
        script_common.__init__(self, ci_klass, **kargs)
        
    def init(self, opt, kargs):
        kargs = super(script,self).init(opt,kargs)
        return kargs
        
    def start(self):
        super(script,self).start()
        self.boost_version_major = 1
        self.boost_version_minor = int(os.getenv('BOOST_VERSION_MINOR', 60))
        self.build_shared_libs = os.getenv('BUILD_SHARED_LIBS', 'ON')
        self.cmake_build_type = os.getenv('CMAKE_BUILD_TYPE', 'Debug')
        self.boost_version_patch = 0
        self.boost_version = '{0}.{1}.{2}'.format(self.boost_version_major, self.boost_version_minor, self.boost_version_patch)
        self.boost_version_underscores = self.boost_version.replace('.','_')
        self.boost_dir = os.path.join(self.build_dir, 'boost_{}'.format(self.boost_version_underscores))
    
    def command_info(self):
        super(script, self).command_info()
    
    def command_install(self):
        super(script,self).command_install()
        print('Changing directory to {}'.format(self.build_dir))
        os.chdir(self.build_dir)
        boost_tar_file = 'boost_{0}_{1}_{2}.tar.bz2'.format(self.boost_version_major, self.boost_version_minor, self.boost_version_patch)
        boost_url_prefix = 'https://downloads.sourceforge.net/project/boost/boost'
        url = boost_url_prefix + '/' + self.boost_version + '/' + boost_tar_file
        print('Downloading {}'.format(url))
        utils.web_get(url, boost_tar_file)
        print('Unpacking {}'.format(boost_tar_file))
        utils.unpack_archive(boost_tar_file)
        print('Changing directory to {}'.format(self.boost_dir))
        os.chdir(self.boost_dir)
        link = 'shared' if self.build_shared_libs == 'ON' else 'static'
        variant = 'debug' if self.cmake_build_type == 'Debug' else 'release'
        utils.build_boost_libs(variant, link, self.jobs, ['system', 'serialization', 'test'])

    def command_before_build(self):
        super(script,self).command_before_build()

    def command_build(self):
        super(script,self).command_build()
        print('Changing directory to {}'.format(self.build_dir))
        os.chdir(self.build_dir)

        utils.check_call('cmake', 
            self.root_dir, '-DCMAKE_SYSTEM_INCLUDE_PATH={}'.format(self.boost_dir), 
            '-DCMAKE_SYSTEM_LIBRARY_PATH={}'.format(self.boost_dir + '/stage/lib'), 
            '-DBUILD_SHARED_LIBS={}'.format(self.build_shared_libs),
            '-DCMAKE_BUILD_TYPE={}'.format(self.cmake_build_type))

        utils.check_call('cmake', '--build', '.')
        utils.check_call('ctest', '--output-on-failure')

    def command_after_success(self):
        super(script,self).command_after_success()

def main(script_klass):
    if os.getenv('TRAVIS', False):
        script_klass(ci_travis)
    elif os.getenv('CIRCLECI', False):
        script_klass(ci_circleci)
    elif os.getenv('APPVEYOR', False):
        script_klass(ci_appveyor)
    else:
        script_klass(ci_cli)

main(script)
