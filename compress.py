#!/usr/bin/env python3

# as the opcode table printed by ./dacli is very large, compress it directly

# group by identical opcode strings and then by the form of the arguments
# (basically all argument characters ignoring values of any embedded numbers),
# then for each opcode-string and argument-form, only keep a representative
# selection of the lines (those which vary in a single bit from a prototype)

import sys

instructions = {}
for line in sys.stdin:
  line = line.rstrip()
  if len(line) and line[:8] != 'opcodes ':
    fields = line.split('\t')
    opcode = int(fields[0], 16)
    mnemonic = fields[1]
    arguments = '' if len(fields) < 3 else fields[2]

    i = 0
    while i < len(arguments):
      if arguments[i] == ' ':
        arguments = arguments[:i] + '_' + arguments[i + 1:]
      elif arguments[i:i + 2] == ', ':
        arguments = arguments[:i + 1] + arguments[i + 2:]
      elif arguments[i:i + 2] == '0x':
        j = i + 2
        while j < len(arguments) and arguments[j] in '0123456789abcdef':
          j += 1
        arguments = arguments[:i] + 'X' + arguments[j:]
      elif arguments[i] in '0123456789':
        j = i + 1
        while j < len(arguments) and arguments[j] in '0123456789':
          j += 1
        arguments = arguments[:i] + 'N' + arguments[j:]
      i += 1

    if (mnemonic, arguments) not in instructions:
      instructions[(mnemonic, arguments)] = []
    instructions[(mnemonic, arguments)].append((opcode, line))

for (mnemonic, arguments), instructions1 in sorted(instructions.items()):
  opcode_min = 0xffffffff
  opcode_max = 0
  for opcode, _ in instructions1:
    opcode_min &= opcode
    opcode_max |= opcode
  operand_bits = opcode_min ^ opcode_max
  print(
    'opcodes',
    mnemonic,
    arguments,
    hex(opcode_min),
    hex(operand_bits ^ 0xffffffff)
  )
  opcodes = {opcode_min}
  for i in range(0x20):
    opcodes.add(opcode_min | ((1 << i) & operand_bits))
  for opcode, line in sorted(instructions1):
    if opcode in opcodes:
      print(line)
  print()
