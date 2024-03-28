# ./data/ui/meson.build: Gtk UI Resources Build Targets

bp_comp = find_program('blueprint-compiler', required: true)

ui_targets = custom_target(
  'blueprints',
  command: [bp_comp, 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
  input: files(
    'shortcuts.blp',
    'window.blp',
    'menu.blp',
  ),
  output: '.',
  install: false,
)