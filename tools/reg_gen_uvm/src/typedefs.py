#! /usr/bin/python3 
import re
import templates
import jinja2
from jinja2 import Template
from enum import Enum



REG_BLOCK_TEMPLATE_FILE         = "reg_block.j2"
REG_TEMPLATE_FILE               = "reg.j2"

templateLoader                  = jinja2.FileSystemLoader(searchpath="../templates")
templateEnv                     = jinja2.Environment(loader=templateLoader)    
templateRegBlock                = templateEnv.get_template(REG_BLOCK_TEMPLATE_FILE)
templateReg                     = templateEnv.get_template(REG_TEMPLATE_FILE      )


class uvm_endianness_enum(Enum):
    UVM_LITTLE_ENDIAN = 0
    UVM_BIG_ENDIAN    = 1


# Global Configuration.
class Configuration:
    """Root of register data model"""

    def __init__(self, name, bit_width, endianness, filename, copyright_header):
        self.project_name             = name
        self.register_bit_width       = bit_width
        self.endianness               = endianness
        self.filename                 = filename
        self.copyright_header         = copyright_header


class RegisterBlock:
    """Model of a register block"""

    def __init__(self, name, offset):
        self.name      = name
        self.offset    = offset
        self.blocks    = {}
        self.registers = {}

    
    def render(self, cfg, regs):
        return templateRegBlock.render(
            copyright_header=cfg.copyright_header,
            project_name=cfg.project_name,
            project_name_uppercase=cfg.project_name.upper(),
            name=self.name.lower(),
            includes=self.render_reg_includes(cfg),
            name_uppercase=self.name.upper(),
            base_address=self.offset,
            register_bit_width=int(cfg.register_bit_width/8),
            endianness=cfg.endianness.name,
            reg_declarations=self.render_reg_declarations(cfg),
            reg_creations=self.render_reg_creations(cfg),
            reg_add_to_map=self.render_reg_add_to_map(cfg),
            field_macros=self.render_reg_macros(cfg)
        )
    
    #def render_block_declarations(self, cfg):
    #    text = ""
    #    for block in self.blocks:
    #        text += block.render_block_declaration(cfg)
    #    return text
    #
    #def render_block_uvm_macros(self, cfg):
    #    text = ""
    #    for block in self.blocks:
    #        text += block.render_uvm_macro(cfg)
    #    return text
    #
    #def render_block_creations(self, cfg):
    #    text = ""
    #    for block in self.blocks:
    #        text += block.render_block_creation(cfg)
    #    return text
    #
    #def render_block_declaration(self, cfg):
    #    return templates.template_sub_block_declaration.render(project_name=cfg.project_name, name=self.name)
    #
    #def render_block_uvm_macro(self, cfg):
    #    return templates.template_uvm_field_macro.render(name=self.name)
    #
    #def render_block_creation(self, cfg):
    #    return templates.template_sub_block_creation.render(project_name=cfg.project_name, name=self.name)
    
    def render_reg_includes(self, cfg):
        text = ""
        for reg in self.registers:
            text += self.registers[reg].render_include(cfg) + "\n"
        return text
    
    def render_reg_declarations(self, cfg):
        text = ""
        for reg in self.registers:
            text += self.registers[reg].render_declaration(cfg) + "\n"
        return text
    
    def render_reg_creations(self, cfg):
        text = ""
        for reg in self.registers:
            text += self.registers[reg].render_creation(cfg, self.name) + "\n"
        return text
    
    def render_reg_add_to_map(self, cfg):
        text = ""
        for reg in self.registers:
            text += self.registers[reg].render_add_to_map(cfg) + "\n"
        return text
    
    def render_reg_macros(self, cfg):
        text = ""
        for reg in self.registers:
            text += templates.template_field_macro.render(name=self.registers[reg].name) + "\n"
        return text


class Register:
    """Model of a register"""

    def __init__(self, name, block_name, offset, access_type, is_vector, reg_size):
        self.name        = name.lower()
        self.block_name  = block_name.lower()
        self.offset      = offset
        self.access_type = access_type
        self.is_vector   = is_vector
        self.reg_size    = reg_size
        self.fields      = {}


    def render(self, cfg):
        return templateReg.render(
            copyright_header       = cfg.copyright_header,
            project_name           = cfg.project_name,
            project_name_uppercase = cfg.project_name.upper(),
            name                   = self.name,
            block_name             = self.block_name,
            block_name_uppercase   = self.block_name.upper(),
            name_uppercase         = self.name.upper(),
            register_bit_width     = cfg.register_bit_width,
            field_declarations     = self.render_field_declarations(cfg),
            field_creations        = self.render_field_creations(cfg),
            field_macros           = self.render_field_macros(cfg)
        )

    def render_include(self, cfg):
        reg_filename = templates.template_sub_reg_filename.render(project_name=cfg.project_name, block_name=self.block_name, name=self.name)
        return "`include \"" + reg_filename + "\""
    
    def render_declaration(self, cfg):
        if self.is_vector:
            return templates.template_sub_reg_declaration_array.render(project_name=cfg.project_name, block_name=self.block_name, name=self.name, size=self.reg_size)
        else:
            return templates.template_sub_reg_declaration.render(project_name=cfg.project_name, block_name=self.block_name, name=self.name)
    
    def render_creation(self, cfg, block_name):
        if self.is_vector:
            return templates.template_sub_reg_creation_array.render(project_name=cfg.project_name, block_name=self.block_name, name=self.name)
        else:
            return templates.template_sub_reg_creation.render(project_name=cfg.project_name, block_name=self.block_name, name=self.name)
    
    def render_add_to_map(self, cfg):
        if self.is_vector:
            return templates.template_sub_reg_map_array.render(name=self.name, offset=self.offset, access_type=self.access_type, num_bytes=int(cfg.register_bit_width/8))
        else:
            return templates.template_sub_reg_map.render(name=self.name, offset=self.offset, access_type=self.access_type)

    def render_field_declarations(self, cfg):
        text = ""
        for field in self.fields:
            text += self.fields[field].render_declaration(cfg) + "\n"
        return text
    
    def render_field_creations(self, cfg):
        text = ""
        for field in self.fields:
            text += self.fields[field].render_creation(cfg) + "\n"
        return text
    
    def render_field_macros(self, cfg):
        text = ""
        for field in self.fields:
            text += templates.template_field_macro.render(name=self.fields[field].name) + "\n"
        return text



class RegisterField:
    """Model of a register field"""

    def __init__(self, name, size, lsb, msb, reset_value, access_type, comments, reg):
        self.name        = name
        self.size        = size
        self.lsb         = lsb
        self.msb         = msb
        self.reset_value = reset_value
        self.access_type = access_type
        self.comments    = comments
        self.reg         = reg
    
    def render_declaration(self, cfg):
        return templates.template_field_declaration.render(name=self.name, comments=self.comments)
    
    def render_creation(self, cfg):
        return templates.template_field_creation.render(name=self.name, size=self.size, lsb=self.lsb, msb=self.msb, access_type=self.access_type, reset_value=self.reset_value)
    


