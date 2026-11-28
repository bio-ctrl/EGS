module orcus_candidate(x0, x1, x2, y);
  input x0, x1, x2;
  output y;
  wire n2;
  wire n4;
  wire n5;
  wire n6;
  assign n2 = (x1 | x0);
  assign n4 = (x1 & x0);
  assign n5 = (x2 | n4);
  assign n6 = (n2 & n5);
  assign y = n6;
endmodule
