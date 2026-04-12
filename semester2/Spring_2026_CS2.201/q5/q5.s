.section .text
.global main

main:
    # Save return address and saved registers
    addi sp, sp, -48
    sd ra, 40(sp)
    sd s0, 32(sp)      # s0 = fd
    sd s1, 24(sp)      # s1 = length
    sd s2, 16(sp)      # s2 = left pointer (offset)
    sd s3, 8(sp)       # s3 = right pointer (offset)
    
    # Construct filename "input.txt" on stack to avoid .data section
    # 'i'=105, 'n'=110, 'p'=112, 'u'=117, 't'=116, '.'=46, 't'=116, 'x'=120, 't'=116, \0=0
    li t0, 105
    sb t0, -10(sp)
    li t0, 110
    sb t0, -9(sp)
    li t0, 112
    sb t0, -8(sp)
    li t0, 117
    sb t0, -7(sp)
    li t0, 116
    sb t0, -6(sp)
    li t0, 46
    sb t0, -5(sp)
    li t0, 116
    sb t0, -4(sp)
    li t0, 120
    sb t0, -3(sp)
    li t0, 116
    sb t0, -2(sp)
    li t0, 0
    sb t0, -1(sp)
    
    # Open file "input.txt"
    # openat(AT_FDCWD, filename, O_RDONLY, 0)
    li a0, -100        # AT_FDCWD = -100
    addi a1, sp, -10   # pointer to "input.txt"
    li a2, 0           # O_RDONLY = 0
    li a3, 0
    li a7, 56          # openat syscall
    ecall
    
    mv s0, a0          # s0 = fd
    bltz s0, fail      # if fd < 0, fail
    
    # Get file length using lseek
    # lseek(fd, 0, SEEK_END)
    mv a0, s0
    li a1, 0           # offset = 0
    li a2, 2           # SEEK_END = 2
    li a7, 62          # lseek syscall
    ecall
    
    mv s1, a0          # s1 = length
    
    # Handle edge cases: empty file or 1 character
    li t0, 1
    ble s1, t0, is_pal
    
    # Check if the last character is a newline and skip it if so
    # lseek(fd, length - 1, SEEK_SET)
    mv a0, s0
    addi a1, s1, -1    # offset = length - 1
    li a2, 0           # SEEK_SET = 0
    li a7, 62          # lseek
    ecall
    
    # read(fd, buf, 1)
    mv a0, s0
    addi a1, sp, -1    # use stack as 1-byte buffer
    li a2, 1
    li a7, 63          # read syscall
    ecall
    
    lb t0, -1(sp)
    li t1, 10          # ASCII newline = 10
    
    addi s3, s1, -1    # Default right pointer = length - 1
    bne t0, t1, no_newline
    addi s3, s3, -1    # Skip newline character
    addi s1, s1, -1    # Adjust length
    
no_newline:
    li s2, 0           # left pointer = 0
    
    # Re-check length after skipping newline
    li t0, 1
    ble s1, t0, is_pal
    
check_loop:
    bge s2, s3, is_pal # If pointers meet or cross, it's a palindrome
    
    # Read character at 'left'
    # lseek(fd, left, SEEK_SET)
    mv a0, s0
    mv a1, s2
    li a2, 0
    li a7, 62
    ecall
    
    # read(fd, buf, 1)
    mv a0, s0
    addi a1, sp, -1
    li a2, 1
    li a7, 63
    ecall
    lb s4, -1(sp)      # s4 = left character
    
    # Read character at 'right'
    # lseek(fd, right, SEEK_SET)
    mv a0, s0
    mv a1, s3
    li a2, 0
    li a7, 62
    ecall
    
    # read(fd, buf, 1)
    mv a0, s0
    addi a1, sp, -1
    li a2, 1
    li a7, 63
    ecall
    lb s5, -1(sp)      # s5 = right character
    
    # Compare characters
    bne s4, s5, not_pal
    
    addi s2, s2, 1     # left++
    addi s3, s3, -1    # right--
    j check_loop
    
is_pal:
    # Print "Yes\n"
    li t0, 89          # 'Y'
    sb t0, -4(sp)
    li t0, 101         # 'e'
    sb t0, -3(sp)
    li t0, 115         # 's'
    sb t0, -2(sp)
    li t0, 10          # '\n'
    sb t0, -1(sp)
    
    li a0, 1           # stdout
    addi a1, sp, -4
    li a2, 4
    li a7, 64          # write syscall
    ecall
    j cleanup
    
not_pal:
    # Print "No\n"
    li t0, 78          # 'N'
    sb t0, -3(sp)
    li t0, 111         # 'o'
    sb t0, -2(sp)
    li t0, 10          # '\n'
    sb t0, -1(sp)
    
    li a0, 1           # stdout
    addi a1, sp, -3
    li a2, 3
    li a7, 64          # write syscall
    ecall
    j cleanup
    
fail:
    # If file open fails, we just exit silently or could return an error code.
    # Here we just proceed to cleanup.
    
cleanup:
    # Close file if it was opened
    bltz s0, finish
    mv a0, s0
    li a7, 57          # close syscall
    ecall
    
finish:
    # Restore registers and return
    ld ra, 40(sp)
    ld s0, 32(sp)
    ld s1, 24(sp)
    ld s2, 16(sp)
    ld s3, 8(sp)
    addi sp, sp, 48
    li a0, 0
    ret
