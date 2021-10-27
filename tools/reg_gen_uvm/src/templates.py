#! /usr/bin/python3 
import re
import jinja2
from jinja2 import Template


template_ral_filename = Template("uvme_{{ project_name }}_{{ name }}_reg_block.sv")

template_sub_block_filename = Template("uvme_{{ name }}_reg_block.sv")

template_sub_reg_filename = Template("uvme_{{ project_name }}_{{ name }}_reg.sv")

template_sub_block_declaration       = Template("  rand uvme_{{ project_name }}_{{ name }}_reg_block_c  {{ name }};")

template_sub_block_declaration_array = Template("  rand uvme_{{ project_name }}_{{ name }}_reg_block_c  {{ name }}[{{ size }}];")

template_sub_reg_declaration         = Template("  rand uvme_{{ project_name }}_{{ name }}_reg_c  {{ name }};")

template_sub_reg_declaration_array   = Template("  rand uvme_{{ project_name }}_{{ name }}_reg_c  {{ name }}[{{ size }}];")

#template_sub_block_creation = Template("{{ name }} = uvme_{{ project_name }}_{{ name }}_reg_block_c::type_id::create(\"{{ name }}\");\
#    {{ name }}.configure(this);\
#    {{ name }}.build();")

#template_sub_block_creation_array = Template("foreach ({{ name }}[ii]) begin\
#      {{ name }}[ii] = uvme_{{ project_name }}_{{ name }}_reg_block_c::type_id::create($sformatf(\"{{ name }}[%0d]\", ii));\
#      {{ name }}[ii].configure(this);\
#      {{ name }}[ii].build();\
#    end")

template_field_macro = Template("      `uvm_field_object({{ name  }}, UVM_DEFAULT)")

template_sub_reg_creation = Template("   {{ name }} = uvme_{{ project_name }}_{{ name }}_reg_c::type_id::create(\"{{ name }}\");\n\
   {{ name }}.configure(this);\n\
   {{ name }}.build();\n\
   ")

template_sub_reg_creation_array = Template("   foreach ({{ name }}[ii]) begin\n\
      {{ name }}[ii] = uvme_{{ project_name }}_{{ name }}_reg_c::type_id::create($sformatf(\"{{ name }}[%0d]\", ii));\n\
      {{ name }}[ii].configure(this);\n\
      {{ name }}[ii].build();\n\
   end\n\n")

template_sub_reg_map       = Template("   default_map.add_reg(\n\
      .rg    ({{ name }}),\n\
      .offset(32'h{{ offset }}),\n\
      .rights(\"RW\")\n\
   );")

template_sub_reg_map_array = Template("  foreach ({{ name }}[ii]) begin\n\
      default_map.add_reg(\n\
         .rg    ({{ name }}[ii]),\n\
         .offset(32'h{{ offset }} + ii*{{ num_bytes }}),\n\
         .rights(\"RW\")\n\
      );\n\
   end")

template_field_declaration = Template("   rand uvml_ral_reg_field_c  {{ name }}; ///< {{ comments }}")

template_field_creation = Template("   {{ name }} = uvml_ral_reg_field_c::type_id::create(\"{{ name }}\");\n\
   {{ name }}.configure(\n\
      .parent                 (this),\n\
      .size                   (   {{ size }}),\n\
      .lsb_pos                (   {{ lsb }}),\n\
      .access                 (\"{{ access_type }}\"),\n\
      .volatile               (   0),\n\
      .reset                  (   {{ reset_value }}),\n\
      .has_reset              (   1),\n\
      .is_rand                (   1),\n\
      .individually_accessible(   1)\n\
   );\n")

template_sv_include_ral = Template("`include \"uvme_{{ project_name }}_{{ name }}_ral.sv\"")

template_sv_include_reg_block = Template("`include \"uvme_{{ project_name }}_{{ name }}_reg_block.sv\"")

template_sv_include_reg = Template("`include \"uvme_{{ project_name }}_{{ block_name }}_{{ name }}_reg.sv\"")


pattern_symbol_vector     = re.compile("^(\w+)\[(\d+)\]$")
pattern_symbol_single_bit = re.compile("^\[(\d+)\]$")
pattern_symbol_range      = re.compile("^\[(\d+)\:(\d+)\]$")
pattern_symbol_hex        = re.compile("^0x((?:\d|a|b|c|d|e|f)+)$")
