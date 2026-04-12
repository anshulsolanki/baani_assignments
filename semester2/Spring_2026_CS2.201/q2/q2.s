.section .text
.global main

# Helper function to convert string to integer (positive only)
# a0 = pointer to null-terminated string
# returns integer in a0
atoi:
    li t0, 0           # result = 0
    li t1, 10          # multiplier = 10
atoi_loop:
    lb t2, 0(a0)
    beqz t2, atoi_done # null terminator
    
    addi t2, t2, -48   # convert ASCII to integer
    bltz t2, atoi_done # stop if not a digit
    
    mul t0, t0, t1
    add t0, t0, t2
    addi a0, a0, 1
    j atoi_loop
atoi_done:
    mv a0, t0
    ret

# Helper function to print a number to stdout
# a0 = number to print
print_number:
    addi sp, sp, -32
    sd s0, 24(sp)
    sd s1, 16(sp)
    
    mv s0, a0          # s0 = number
    li s1, 0           # digit counter
    
    # Special case for -1
    li t0, -1
    bne s0, t0, not_minus_one
    li t0, 49          # ASCII '1'
    sb t0, 0(sp)
    li t0, 45          # ASCII '-'
    sb t0, 1(sp)
    li s1, 2
    j print_out
    
not_minus_one:
    # Special case for 0
    bnez s0, get_digits
    li t0, 48          # ASCII '0'
    sb t0, 0(sp)
    li s1, 1
    j print_out
    
get_digits:
    beqz s0, print_out
    li t2, 10
    rem t1, s0, t2
    div s0, s0, t2
    addi t1, t1, 48    # convert to ASCII
    add t0, sp, s1
    sb t1, 0(t0)
    addi s1, s1, 1
    j get_digits
    
print_out:
    # print digits in reverse order (most significant first)
    beqz s1, done_printing
    addi s1, s1, -1
    add t0, sp, s1
    
    li a0, 1           # 1 = stdout
    mv a1, t0          # address of character
    li a2, 1           # length
    li a7, 64          # write syscall
    ecall
    j print_out
    
done_printing:
    ld s0, 24(sp)
    ld s1, 16(sp)
    addi sp, sp, 32
    ret

main:
    # Save return address and saved registers
    addi sp, sp, -48
    sd ra, 40(sp)
    sd s0, 32(sp)
    sd s1, 24(sp)
    sd s2, 16(sp)
    sd s3, 8(sp)
    sd s4, 0(sp)
    
    mv s0, a0          # s0 = argc
    mv s1, a1          # s1 = argv
    
    # If argc <= 1, exit (no elements to process)
    li t0, 1
    ble s0, t0, exit_success
    
    addi s2, s0, -1    # s2 = n (number of elements)
    
    # Allocate space on stack for:
    # 1. input array (n * 8 bytes)
    # 2. result array (n * 8 bytes)
    # 3. stack for algorithm (n * 8 bytes)
    # Total = 24 * n bytes
    
    li t0, 24
    mul t0, t0, s2
    sub sp, sp, t0     # allocate space
    
    # Pointers to the allocated spaces
    mv s3, sp          # s3 = input array
    slli t1, s2, 3     # t1 = n * 8
    add s4, s3, t1     # s4 = result array
    
    # Parse command line arguments and store in input array
    li s5, 0           # i = 0
parse_loop:
    beq s5, s2, parse_done
    
    addi t0, s5, 1     # argv index = i + 1
    slli t0, t0, 3     # pointer offset
    add t0, s1, t0
    ld a0, 0(t0)       # a0 = argv[i+1] (string)
    
    call atoi
    
    slli t0, s5, 3     # array offset
    add t0, s3, t0
    sd a0, 0(t0)       # store in input array
    
    addi s5, s5, 1
    j parse_loop
    
parse_done:
    # Initialize result array to -1
    li s5, 0
init_result_loop:
    beq s5, s2, init_result_done
    slli t0, s5, 3
    add t0, s4, t0
    li t1, -1
    sd t1, 0(t0)
    addi s5, s5, 1
    j init_result_loop
    
init_result_done:
    # Next Greater Element Algorithm
    # We use the third part of allocated space as stack
    slli t1, s2, 3
    add s6, s4, t1     # s6 = algorithm stack base
    mv s7, s6          # s7 = algorithm stack top (empty)
    
    addi s5, s2, -1    # s5 = i = n - 1 (start from right)
    
algo_loop:
    bltz s5, algo_done
    
    # while (!stack.empty() && arr[stack.top()] <= arr[i]) stack.pop()
while_loop:
    beq s7, s6, while_done # stack empty
    
    ld t0, -8(s7)      # t0 = stack.top() (index)
    
    slli t1, t0, 3
    add t1, s3, t1
    ld t1, 0(t1)       # t1 = arr[stack.top()]
    
    slli t2, s5, 3
    add t2, s3, t2
    ld t2, 0(t2)       # t2 = arr[i]
    
    bgt t1, t2, while_done # if arr[stack.top()] > arr[i], stop popping
    
    addi s7, s7, -8    # stack.pop()
    j while_loop
    
while_done:
    # if (!stack.empty()) result[i] = stack.top()
    beq s7, s6, stack_empty
    
    ld t0, -8(s7)      # t0 = stack.top()
    slli t1, s5, 3
    add t1, s4, t1
    sd t0, 0(t1)       # result[i] = stack.top()
    
stack_empty:
    # stack.push(i)
    sd s5, 0(s7)
    addi s7, s7, 8
    
    addi s5, s5, -1    # i--
    j algo_loop
    
algo_done:
    # Print results
    li s5, 0
print_result_loop:
    beq s5, s2, print_result_done
    
    slli t0, s5, 3
    add t0, s4, t0
    ld a0, 0(t0)       # a0 = result[i]
    
    call print_number
    
    # Print space between numbers, except after the last one
    addi t0, s5, 1
    beq t0, s2, no_space
    
    li t1, 32          # ASCII space
    sb t1, -1(sp)
    li a0, 1           # stdout
    addi a1, sp, -1    # address of space
    li a2, 1           # length
    li a7, 64          # write syscall
    ecall
    
no_space:
    addi s5, s5, 1
    j print_result_loop
    
print_result_done:
    # Print newline at the end
    li t1, 10          # ASCII newline
    sb t1, -1(sp)
    li a0, 1           # stdout
    addi a1, sp, -1    # address of newline
    li a2, 1           # length
    li a7, 64          # write syscall
    ecall
    
    # Restore stack pointer from allocation
    li t0, 24
    mul t0, t0, s2
    add sp, sp, t0
    
exit_success:
    # Restore registers and return
    ld ra, 40(sp)
    ld s0, 32(sp)
    ld s1, 24(sp)
    ld s2, 16(sp)
    ld s3, 8(sp)
    ld s4, 0(sp)
    addi sp, sp, 48
    li a0, 0
    ret
