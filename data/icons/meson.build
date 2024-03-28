# ./data/icons/meson.build: Applications Icons Build Targets

build_icons = find_program(files('build-aux/buildicons.py'), required: true)

icons_dir = custom_target(
  'icons',
  command: [build_icons, '@INPUT@', appid, '@OUTPUT@'],
  input: 'template.svg',
  output: ['icons'],
  build_by_default: true,
  install: false,
)

if host_machine.system() == 'linux'
  install_icons_dir = join_paths(get_option('datadir'), 'icons')
endif

install_subdir(
  icons_dir.full_path(),
  strip_directory: true,
  install_dir: install_icons_dir,
  install_tag: 'resources',
)
