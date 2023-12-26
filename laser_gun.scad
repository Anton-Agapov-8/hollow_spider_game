$fn = 50;
h = 150;
color("GRAY"){
cylinder(h, 25, 25);
translate([0, 0, h + 100]){
rotate([0, 180, 0]){
scale([50/4, 50/4, 50/4]){
hull(){
for (x=[4:-1:0]){
translate([0, 0, x*2]){
    sphere(sqrt(x));}}}}}}
translate([0, 0, h]){
    difference(){
    sphere(40);
    translate([0, 0, 40]){
    cube(80, true);}
    }
}
}