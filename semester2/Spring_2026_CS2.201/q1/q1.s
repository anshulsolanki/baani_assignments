.section .text
.global make_node
.global insert
.global get
.global getAtMost

# struct Node {
#    int val;          // offset 0
#    // 4 bytes padding
#    struct Node* left;  // offset 8
#    struct Node* right; // offset 16
# }; // total size = 24 bytes

# struct Node* make_node(int val);
# Returns a pointer to a struct with the given value and left and right pointers set to NULL.
make_node:
    # Save return address and saved registers
    addi sp, sp, -16
    sd ra, 8(sp)
    sd s0, 0(sp)
    
    mv s0, a0          # Save val in s0
    
    li a0, 24          # Size of struct Node
    call malloc        # Call C malloc to allocate memory
    
    # Check if malloc failed
    beqz a0, make_node_fail
    
    sw s0, 0(a0)       # node->val = val
    sd zero, 8(a0)     # node->left = NULL
    sd zero, 16(a0)    # node->right = NULL
    
make_node_fail:
    # Restore registers and return
    ld ra, 8(sp)
    ld s0, 0(sp)
    addi sp, sp, 16
    ret


# struct Node* insert(struct Node* root, int val);
# insert a node with value val into the tree with the given root. Return the root.
insert:
    # Save return address and saved registers
    addi sp, sp, -32
    sd ra, 24(sp)
    sd s0, 16(sp)
    sd s1, 8(sp)
    
    mv s0, a0          # s0 = root
    mv s1, a1          # s1 = val
    
    # If root == NULL, create a new node
    bnez s0, insert_not_null
    
    mv a0, s1
    call make_node
    j insert_done      # Return the new node as root
    
insert_not_null:
    lw t0, 0(s0)       # t0 = root->val
    blt s1, t0, insert_left
    bgt s1, t0, insert_right
    # If equal, do nothing (or just return root)
    j insert_done_root
    
insert_left:
    ld a0, 8(s0)       # a0 = root->left
    mv a1, s1
    call insert
    sd a0, 8(s0)       # root->left = insert(...)
    j insert_done_root
    
insert_right:
    ld a0, 16(s0)      # a0 = root->right
    mv a1, s1
    call insert
    sd a0, 16(s0)      # root->right = insert(...)
    j insert_done_root
    
insert_done_root:
    mv a0, s0          # Return the original root
    
insert_done:
    # Restore registers and return
    ld ra, 24(sp)
    ld s0, 16(sp)
    ld s1, 8(sp)
    addi sp, sp, 32
    ret


# struct Node* get(struct Node* root, int val);
# Return a pointer to a node with value val in the tree. Return NULL if no such node exists.
get:
    # Iterative implementation
get_loop:
    beqz a0, get_not_found # If root == NULL, not found
    lw t0, 0(a0)       # t0 = current->val
    beq a1, t0, get_found  # If val == current->val, found
    blt a1, t0, get_go_left # If val < current->val, go left
    
    # Go right
    ld a0, 16(a0)
    j get_loop
    
get_go_left:
    ld a0, 8(a0)
    j get_loop
    
get_found:
    # a0 already contains the pointer to the node
    ret
    
get_not_found:
    li a0, 0           # Return NULL
    ret


# int getAtMost(int val, struct Node* root);
# Return the greatest value present in the tree which is <= val. Return -1 if no such node exists.
getAtMost:
    # a0 = val, a1 = root
    li t0, -1          # best so far = -1
    
getAtMost_loop:
    beqz a1, getAtMost_done # If current == NULL, done
    lw t1, 0(a1)       # t1 = current->val
    
    beq a0, t1, getAtMost_equal # If val == current->val, exact match
    blt a0, t1, getAtMost_go_left # If val < current->val, must go left
    
    # current->val < val. This is a candidate.
    mv t0, t1          # Update best so far
    ld a1, 16(a1)      # Go right to find a larger value that is still <= val
    j getAtMost_loop
    
getAtMost_go_left:
    # current->val > val. Cannot be an answer. Go left.
    ld a1, 8(a1)
    j getAtMost_loop
    
getAtMost_equal:
    mv t0, t1          # Exact match is the best possible
    j getAtMost_done
    
getAtMost_done:
    mv a0, t0          # Return the best value found
    ret
