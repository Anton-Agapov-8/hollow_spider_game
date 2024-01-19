$fn=50;
module leg(koeff, end){
step = end/4;
i = 0;
rotate([0, 180, -90]){
for (x=[0:step*2:end]){
i=i+1;
r = 48;
g = 48;
b = 48;

color([r/255, g/255, b/255]){
hull(){
translate([x*koeff, 0, x*x*koeff]){
sphere(5);}
translate([(x+step)*koeff, 0, (x+step)*(x+step)*koeff]){
sphere(5);}}}
}
for (x=[step:step*2:end]){
i=i+1;
r = 128;
g = 128;
b = 128;
color([r/255, g/255, b/255]){
hull(){
translate([x*koeff, 0, x*x*koeff]){
sphere(5);}
translate([(x+step)*koeff, 0, (x+step)*(x+step)*koeff]){
sphere(5);}}}
}

}
}

r = 50;
g = 50;
b = 50;

ax = 0;
ay = 0;
az = 0;
translate([0, 0, 50]){
rotate([ax, ay, az]){
translate([0, 0, 75]){
color([r/255, g/255, b/255]){
scale([0.6, 0.6, 1]){
sphere(100);}}
translate([0, 0, 100]){
color([r/255, g/255, b/255]){
scale([0.6, 0.6, 1]){
sphere(30);}}}

color([r/255, g/255, b/255]){
translate([0, 0, 130]){
rotate([0, 90, 0]){
rotate_extrude(angle=160){
    translate([10, 0, 0]){
    circle(2);}}
rotate_extrude(angle=-160){
    translate([10, 0, 0]){
    circle(2);}}
}}}

color("black"){
translate([0, -40, 75]){
    sphere(5);}
translate([0, -48, 60]){
    sphere(5);}
translate([0, 40, 75]){
    sphere(5);}
translate([0, 48, 60]){
    sphere(5);}

translate([0, -40, -75]){
    sphere(5);}
translate([0, -28, -90]){
    sphere(5);}
translate([0, 40, -75]){
    sphere(5);}
translate([0, 28, -90]){
    sphere(5);}
}
}}
}

translate([0, 28, 35]){
leg(1.5, 4);}
translate([0, -28, 35]){
rotate([0, 0, 180]){
leg(1.5, 4);}}

translate([0, 40, 50]){
leg(2.1, 4);}
translate([0, -40, 50]){
rotate([0, 0, 180]){
leg(2.1, 4);}}


translate([0, 50, 185]){
leg(20, 1.6);}
translate([0, -50, 185]){
rotate([0, 0, 180]){
leg(20, 1.6);}}

translate([0, 40, 200]){
leg(60, 0.9);}
translate([0, -40, 200]){
rotate([0, 0, 180]){
leg(60, 0.9);
}}