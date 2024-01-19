$fn = 50;
h = 150;
color("GRAY"){
translate([0, 0, 200]){
rotate([0, -90, 0]){
scale([1, 1, 0.5]){
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
}}}
translate([0, 0, 120]){
rotate([90, 90, 0]){
rotate_extrude(angle=180){
    translate([80, 0, 0]){
    circle(25);}}}
}
translate([-40, 0, 40]){
rotate([0, 90, 0]){
cylinder(40, 30, 25);}}
translate([-160, 0, 40]){
rotate([0, 90, 0]){
cylinder(120, 30, 30);}}

hull(){
translate([-160, 0, 40]){
rotate([0, 90, 0]){
cylinder(0.001, 30, 30);}}
translate([-200, 0, 30]){
scale([1, 2, 1]){
sphere(10);}}
}
r = 8;
end = 100;
step = end/3;
delta_left = -40; //-40
delta_right = 40; //40
for (x=[0:step:end]){
hull(){
translate([-50 - x, -25, 40]){
sphere(r);}
translate([-50 - x + delta_left/2, -50, 70]){
sphere(r);}
}
hull(){
translate([-50 - x + delta_left/2, -50, 70]){
sphere(r);}
translate([-50 - x + delta_left, -70, 0]){
sphere(r);}
}
hull(){
translate([-50 - x, 25, 40]){
sphere(r);}
translate([-50 - x + delta_right/2, 50, 70]){
sphere(r);}
}
hull(){
translate([-50 - x + delta_right/2, 50, 70]){
sphere(r);}
translate([-50 - x + delta_right, 70, 0]){
sphere(r);}
}
}
}

color("red"){
translate([-180, -10, 50]){
sphere(5);}}
color("red"){
translate([-180, 10, 50]){
sphere(5);}}

translate([-10, 0, 200]){
color("red"){
    cube([5, 50, 5], true);
}}
translate([-30, 0, 200]){
color("red"){
    cube([5, 50, 5], true);
}}
translate([-50, 0, 200]){
color("red"){
    cube([5, 50, 5], true);
}}