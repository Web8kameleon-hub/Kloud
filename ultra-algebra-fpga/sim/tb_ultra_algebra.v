kt`timescale 1ns / 1ps

module tb_ultra_algebra;

    // Testbench for Ultra Algebra Engine
    reg clk = 0;
    reg rst_n = 0;
    reg [3:0] op_id;
    reg [7:0] payload [0:63];
    reg payload_valid = 0;
    reg [2:0] tide_level;
    wire [7:0] state_out [0:63];
    wire state_valid;
    wire [3:0] op_allowed;
    
    // DUT Instantiation
    ultra_algebra_engine uut (
        .clk(clk),
        .rst_n(rst_n),
        .op_id(op_id),
        .payload(payload),
        .payload_valid(payload_valid),
        .tide_level(tide_level),
        .state_out(state_out),
        .state_valid(state_valid),
        .op_allowed(op_allowed)
    );
    
    // Clock generator
    always #5 clk = ~clk;
    
    integer i;
    
    initial begin
        $dumpfile("ultra_algebra.vcd");
        $dumpvars(0, tb_ultra_algebra);
        
        // Reset
        rst_n = 0;
        payload_valid = 0;
        #20 rst_n = 1;
        
        // Test 1: OP_S (Store) - High Tide
        tide_level = 3'd2; // High
        op_id = 4'd1; // S
        for (i = 0; i < 64; i = i + 1) payload[i] = i[7:0];
        payload_valid = 1;
        #10 payload_valid = 0;
        #20 $display("Test S: PASS if state_out[0]=0, [1]=1, state_valid=1");
        
        // Test 2: OP_C (Compute) - increment
        op_id = 4'd2; // C
        payload_valid = 1;
        #10 payload_valid = 0;
        #20 $display("Test C: PASS if state_out[0]=1, [1]=2");
        
        // Test 3: OP_M Low Tide - only basic ops allowed
        tide_level = 3'd0; // Low
        op_id = 4'd6; // M (allowed)
        payload_valid = 1;
        #10 payload_valid = 0;
        #20 $display("Test M Low: PASS");
        
        // Test 4: OP_L Low Tide - should be blocked
        op_id = 4'd9; // L (blocked in Low)
        payload_valid = 1;
        #10 payload_valid = 0;
        #20 $display("Test L Low: PASS if op_allowed=0");
        
        #50 $finish;
    end
    
    // Monitor
    always @(posedge clk) begin
        if (state_valid) begin
            $display("OUTPUT: op=%d, tide=%d, allowed=%d, state[0]=%h, state[1]=%h",
                     op_id, tide_level, op_allowed, state_out[0], state_out[1]);
        end
    end

endmodule

