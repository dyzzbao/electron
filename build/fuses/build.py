#!/usr/bin/env python3

import json
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

SENTINEL = "dL7pKGdnNz796PbbjQWNKmHXBZaB9tsX"

TEMPLATE_H = """
#ifndef ELECTRON_FUSES_H_
#define ELECTRON_FUSES_H_

#if defined(WIN32)
#define FUSE_EXPORT __declspec(dllexport)
#else
#define FUSE_EXPORT __attribute__((visibility("default")))
#endif

namespace electron {

namespace fuses {

extern const volatile char kFuseWire[];

{getters}

}  // namespace fuses

}  // namespace electron

#endif  // ELECTRON_FUSES_H_
"""

TEMPLATE_CC = """
#include "electron/fuses.h"

namespace electron {

namespace fuses {

const volatile char kFuseWire[] = "{sentinel}{fuse_version}{initial_config}";

{getters}

}

}
"""

with open(os.path.join(dir_path, "fuses.json"), 'r') as f:
  fuse_defaults = json.load(f)

fuse_version = fuse_defaults['_version']
del fuse_defaults['_version']
del fuse_defaults['_schema']
del fuse_defaults['_comment']

if fuse_version >= pow(2, 8):
  raise Exception("Fuse version can not exceed one byte in size")

fuses = fuse_defaults.keys()

initial_config = ""
getters_h = ""
getters_cc = ""
index = len(SENTINEL) + 1
for fuse in fuses:
  index += 1
  initial_config += fuse_defaults[fuse]
  name = ''.join(word.title() for word in fuse.split('_'))
  getters_h += "bool Is{name}Enabled();\n".replace("{name}", name)
  getters_cc += """
FUSE_EXPORT bool Is{name}Enabled() {
  return kFuseWire[{index}] == '1';
}
""".replace("{name}", name).replace("{index}", str(index))

header = TEMPLATE_H.replace("{getters}", getters_h.strip())
impl = TEMPLATE_CC.replace("{sentinel}", SENTINEL).replace("{fuse_version}", chr(fuse_version) + chr(len(fuses))).replace("{initial_config}", initial_config).replace("{getters}", getters_cc.strip())

with open(sys.argv[1], 'w') as f:
  f.write(header)

with open(sys.argv[2], 'w') as f:
  f.write(impl)
