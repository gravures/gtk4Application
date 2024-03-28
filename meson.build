# ./meson.build: Top Project Build File

project(
  run_command('build-aux/readtoml.py', 'project/name', check: true).stdout(), 
  'c', 'cython',
          version: run_command('build-aux/readtoml.py', 'project/version', check: true).stdout(),
    meson_version: '>= 0.64.0',
  default_options: [ 'warning_level=2',
                     'werror=false',
                     'buildtype=debugoptimized',
                   ],
)

##
# Print summaries
summary(
  {
    'bindir': get_option('bindir'),
    'libdir': get_option('libdir'),
    'datadir': get_option('datadir'),
  }, 
  section: 'Directories'
)

##
# Meson modules
i18n  = import('i18n')
gnome = import('gnome')
pymod = import('python')


##
# Python Installation 
# https://mesonbuild.com/Python-module.html
python = pymod.find_installation(required: true, pure: false)

##
# Project Dependecies
# https://mesonbuild.com/Reference-manual_functions.html#dependency
python_dependency = python.dependency(embed: false, required: true)
dependency('glib-2.0', allow_fallback: false, required: true)
dependency('gtk4', version: '>= 4.5.0', allow_fallback: false, required: true)
dependency('libadwaita-1', version: '>= 1.2', allow_fallback: false, required: true)
dependency('pygobject-3.0', version: '>= 3.42.0', allow_fallback: false, required: true)

##
# Application Properties
appdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir  = python.get_install_dir()
appbundle  = run_command('build-aux/readtoml.py', 'tool/gnome/bundle', check: true).stdout()
appname    = run_command('build-aux/readtoml.py', 'tool/gnome/appname', check: true).stdout()
appid      = appbundle + '.' + appname  # com.example.MyApp
approot    = '/' + appid.replace('.', '/')  # /com/example/MyApp

##
# Install configuration data
conf = configuration_data()
conf.set('VERSION',      meson.project_version())
conf.set('APP_NAME',     meson.project_name())
conf.set('APP_ID',       appid)
conf.set('APP_ROOT',     approot)
conf.set('BUILD_TYPE',   get_option('buildtype'))

conf.set('local_build', 'False')
conf.set('INSTALL_DIR',  moduledir)
conf.set('APP_DATA_DIR', appdatadir)
conf.set('SCHEMAS_DIR',  appdatadir)
conf.set('LOCALE_DIR',   join_paths(get_option('prefix'), get_option('localedir')))


##
# Local install configuration data
local_conf = configuration_data()
local_conf.set('VERSION',     meson.project_version())
local_conf.set('APP_NAME',    meson.project_name())
local_conf.set('APP_ID',      appid)
local_conf.set('APP_ROOT',    approot)
local_conf.set('BUILD_TYPE',  get_option('buildtype'))

local_conf.set('local_build', 'True')
local_conf.set('INSTALL_DIR',  join_paths(meson.current_source_dir(), 'src'))
local_conf.set('APP_DATA_DIR', join_paths(meson.current_build_dir(), 'data'))
local_conf.set('SCHEMAS_DIR',  join_paths(meson.current_build_dir(), get_option('datadir')))
local_conf.set('LOCALE_DIR',   join_paths(get_option('prefix'), get_option('datadir'), 'locale'))


##
# Build Sub-Directories
subdir('data')
subdir('src')
subdir('po')
# subdir('docs')

##
#
gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
