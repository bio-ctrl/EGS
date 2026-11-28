module orcus_candidate(x0, x1, x2, y);
  input x0, x1, x2;
  output y;
  wire n3;
  wire n4;
  wire n5;
  assign n3 = (x2 ^ x1);
  assign n4 = ~(x0 & n3);
  assign n5 = ~(x2 ^ n4);
  assign y = n5;
endmodule
