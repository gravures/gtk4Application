# ./src/meson.build: Applications Codes Build Targets

##
# Customs helper commandes
python_build = find_program(files('/build-aux/pythonbuild.py'), required: true)
no_compiler  = find_program(files('/build-aux/nocompiler.py'), required: true)


##
#
configure_file(
  input: meson.project_name() + '.in',
  output: 'local-' + meson.project_name(),
  configuration: local_conf,
  install: false
)

configure_file(
  input:  meson.project_name() + '.in',
  output: meson.project_name(),
  configuration: conf,
  install_dir: get_option('bindir'),
  install: true
)


##
# Python build target
py_files = []
foreach f : run_command(python_build, 'src', check:true).stdout().splitlines() 
  py_files += files(f)
endforeach

custom_target(
  'python_lib',
  command: [no_compiler, '@INPUT@'],
  capture: true,
  input: py_files,
  output: [],
  build_by_default: true,
  install_dir: moduledir,
  install_tag: 'python-runtime',
  install: true
)


##
# Meson dev run target
launcher = join_paths(
  meson.project_build_root(), 
  meson.project_name(), 
  'local-' + meson.project_name()
)
run_target('run', command: [launcher])




