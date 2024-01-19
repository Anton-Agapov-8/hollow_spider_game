$fn = 80;
x = -10;
color("orange"){
rotate([0, 5, 150]){
difference(){
translate([x, 0, 0]){
intersection(){
cube([50, 20, 20]);
translate([0, 10, 5]){
rotate([0, 90, 0]){
cylinder(50, 10, 10, $fn=7);}}
}}
translate([x - 0.001, 0, -0.001]){
intersection(){
cube([50, 20, 20]);
translate([0, 10, 5]){
rotate([0, 90, 0]){
cylinder(50, 8, 8);}}
}}
}
intersection(){
translate([x - 1, 0, 10]){
cube([1, 20, 1]);}

translate([x-1, 10, 5]){
rotate([0, 90, 0]){
cylinder(50, 10, 10, $fn=7);}}
}
intersection(){
translate([x - 1, 0, 7]){
cube([1, 20, 1]);}

translate([x-1, 10, 5]){
rotate([0, 90, 0]){
cylinder(50, 10, 10, $fn=7);}}
}

translate([0, 5, 0]){
    rotate([0, 75, 0]){
cube([30, 10, 10]);}}

intersection(){
cube([50, 20, 20]);
translate([0, 10, 5]){
rotate([0, 90, 0]){
cylinder(50, 8, 8);}}
}
}
}