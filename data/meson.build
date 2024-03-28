# ./data/meson.build: Gtk Application Resources Build Targets

subdir('icons')


##
# Linux
if host_machine.system() == 'linux'
  configure_file(
    input: '_app.desktop.in.in',
    output: f'@appid@.desktop.in',
    configuration: conf,
    install: false,
  )

  desktop_file = i18n.merge_file(
    input: '@appid@.desktop.in',
    output: f'@appid@.desktop',
    type: 'desktop',
    po_dir: '../po',
    install_dir: join_paths(get_option('datadir'), 'applications'),
    install_tag: 'resources',
    install: true,
  )

  desktop_utils = find_program('desktop-file-validate', required: false)
  if desktop_utils.found()
    test('Validate desktop file', 
      desktop_utils,
      args: [desktop_file]
    )
  endif
endif  # Linux


subdir('ui')


##
# AppStream metadata
# https://www.freedesktop.org/software/appstream/docs/chap-Metadata.html
configure_file(
  input: '_app.metainfo.xml.in.in',
  output: f'@appid@.metainfo.xml.in',
  configuration: conf,
  install: false,
)

appstream_file = i18n.merge_file(
  input: f'@appid@.metainfo.xml.in',
  output: f'@appid@.metainfo.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif


##
# gresources compilation
configure_file(
  input: '_app.gresource.xml.in',
  output: f'@appname@.gresource.xml',
  configuration: conf,
  install: false,
)

gnome.compile_resources(
  appname,
  join_paths(meson.current_build_dir(), f'@appname@.gresource.xml'),
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  dependencies: ui_targets,
  install_dir: appdatadir,
  install: true,
)

##
# gschemas compilation
configure_file(
  input: '_app.gschema.xml.in',
  output: f'@appid@.gschema.xml',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif
