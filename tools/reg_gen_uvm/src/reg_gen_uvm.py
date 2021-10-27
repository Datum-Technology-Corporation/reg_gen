#! /usr/bin/python3 
# * use filename as block name
# * foreach over each row
#     * if register doesn't exist in dictionary
#         * create register class
#     * add to each register template sections
# * foreach over each register in dictionary
#     * write out register class to file
#     * add to each block template sections
# * write out block class to file
# * hand-assembled ral top


import typedefs
import templates
import re
import csv
import jinja2
import tarfile
from jinja2 import Template
from enum import Enum
import os
import sys

project_name = sys.argv[1]

def gen_block(gen_block_name, gen_block_offset):
    row_count = 0
    
    cfg = typedefs.Configuration(project_name, 32, typedefs.uvm_endianness_enum.UVM_LITTLE_ENDIAN, sys.argv[3], "// \n// Copyright 2021 ???.\n// ")
    block = typedefs.RegisterBlock(gen_block_name, gen_block_offset)
    
    with open(cfg.filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
    
        for row in csv_reader:
            if row_count > 0:
                raw_offset   = row[0].lower()
                raw_reg_name = row[1].lower().strip()
                access_type  = row[2].upper().strip()
                field_size   = row[3].strip()
                field_lsb    = row[4].strip()
                field_name   = row[5].lower().strip()
                raw_reset    = row[6].lower().strip()
                comments     = row[7].strip()
                
                vector_regex_results = re.match(templates.pattern_symbol_vector, raw_reg_name)
                if vector_regex_results:
                    reg_name  = vector_regex_results.group(1)
                    reg_size  = vector_regex_results.group(2)
                    is_vector = 1
                else:
                    reg_name  = raw_reg_name
                    reg_size  = 1
                    is_vector = 0
                
                hex_regex_results = re.match(templates.pattern_symbol_hex, raw_offset)
                if hex_regex_results:
                    offset = hex_regex_results.group(1)
                else:
                    exit("Invalid offset for field " + gen_block_name + "." + reg_name + "." + field_name + ": '" + raw_offset + "'")
                
                
                if reg_name not in block.registers:
                    block.registers[reg_name] = typedefs.Register(reg_name, block.name, offset, row[3], is_vector, reg_size)
                current_register = block.registers[reg_name]
                
                lsb = field_lsb
                msb = lsb + field_size
                size = field_size
                
                hex_regex_results = re.match(templates.pattern_symbol_hex, raw_reset)
                if hex_regex_results:
                    reset_value = int(hex_regex_results.group(1), 16)
                else:
                    exit("Invalid reset value for field " + gen_block_name + "." + reg_name + "." + field_name + ": '" + raw_reset + "'")
                    
                current_register.fields[field_name] = typedefs.RegisterField(field_name, size, lsb, msb, reset_value, access_type, comments, reg=current_register)
                current_field = current_register.fields[field_name]
            
            row_count += 1
    
    reg_text = ""
    for reg in block.registers:
        current_reg = block.registers[reg]
        reg_text = current_reg.render(cfg)
        reg_filename = templates.template_sub_reg_filename.render(
            project_name=cfg.project_name,
            block_name=gen_block_name,
            name=current_reg.name
        )
        
        directory = "../out/"
        if not os.path.exists(directory):
            os.mkdir(directory)
        reg_file = open(sys.argv[4] + "/" + reg_filename, "w")
        reg_file.write(reg_text)
        reg_file.close()
    
    block_text = block.render(cfg, reg_text)
    block_filename = templates.template_sub_block_filename.render(
        name=cfg.project_name
    )
    block_file = open(sys.argv[4] + "/" + block_filename, "w")
    block_file.write(block_text)
    block_file.close()


# gen_block(gen_block_name, gen_block_offset)
gen_block(sys.argv[1], sys.argv[2])
# 
# with tarfile.open("./out/" + project_name + "_ral.tgz", "w:gz") as tar:
#     tar.add("./out/", arcname=os.path.basename("./out/"))

