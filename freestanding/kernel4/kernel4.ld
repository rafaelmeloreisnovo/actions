ENTRY(kernel4_entry)

SECTIONS
{
  . = 0x00010000;

  .text : ALIGN(16)
  {
    KEEP(*(.text.kernel4_entry))
    *(.text .text.*)
  }

  .rodata : ALIGN(16)
  {
    *(.rodata .rodata.*)
  }

  .data : ALIGN(16)
  {
    *(.data .data.*)
  }

  .bss (NOLOAD) : ALIGN(16)
  {
    *(.bss .bss.*)
    *(COMMON)
  }

  /DISCARD/ :
  {
    *(.comment)
    *(.note*)
    *(.eh_frame*)
    *(.gnu*)
  }
}
