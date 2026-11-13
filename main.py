import numpy as np
import math as m
import matplotlib.pyplot as plt
from matplotlib import animation

plt.rcParams['animation.ffmpeg_path'] = r'C:\\FFmpeg\bin\ffmpeg.exe'

#==================================================
# Take off modelling 
# by Kaique Fernandes 
#==================================================

#==================================================
# 0. Functions defitions
#==================================================

def lift_ht(velocity):
    return 0.5*rho_air*h_stab_surface*c_lht*velocity**2

def lift(velocity):
    return 0.5*rho_air*wing_surface*cl*velocity**2

def drag(velocity):
    return 0.5*rho_air*wing_surface*cd*velocity**2

def main_gear_reaction(nlg_reaction, lift, rear_lift):
    return weight + rear_lift - lift - nlg_reaction

def nose_gear_reaction(lift, speed, rear_lift):
    
    # pitch moment
    M = 0.5 * rho_air * (speed**2) * wing_surface * 1.5 * (-0.05)

    # nose gear
    Rn = (total_thrust * z_h + (weight + rear_lift - lift) * (mlg_x_pos + mu*z_cg) + lift*lift_center_x_pos - rear_lift * rear_lift_pos  - M) / (mlg_x_pos + nlg_x_pos)

    return Rn

def x_acc(fx):
    return fx/mass

def lift_distribution(lift):
    '''
    Calculates lift distribution at span L(y)

    Parameters: 
    ----------
    lift: total lift generated
    '''
    b = np.linspace(-wing_span/2, wing_span/2, wing_span_resolution)

    L_y = 4 * lift/(m.pi*wing_span) * np.sqrt(1 - (2*b/wing_span)**2)

    return L_y

#==================================================
# 1. Inputs
#==================================================
gravity = 9.81 # m/s2
mass = 600  # kg
weight = mass*gravity # N 
wing_span = 7 # m
nlg_x_pos = 1.07 # m
mlg_x_pos = 0.39 # m
lift_center_x_pos = 0.21 # m
z_cg = 0.82 # m
z_h = 0.18 # m
rear_lift_pos = 3.05 # m

mu = 0.05 # -
wing_surface = 10.22 # m2
h_stab_surface = 2.3 # m2
rho_air = 1.21 # kg/m3
cl = 0.5 # -
cd = 0.03 # -
c_lht = 0.825


wing_span_resolution = 100 # Wingspan points to lift calculation 
time_step = 0.01 # s
total_time = 25 # s
total_thrust = 1800 # N # thrust is constant

#==================================================
# 2. Simulation setup
#==================================================

n = int(total_time/time_step) # total steps
simulation_time = np.linspace(0, total_time, n)
f_lift = [0] # lift list
f_lift_rear = [0] # lift list
f_drag = [0] # drag list
dvdt = [0] # logitudinal acceleration list
x_speed = [0] # logitudinal speed list
f_nose = [0] # nose gear reaction force
f_main = [0] # main gears reaction force
lift_y = [np.zeros(wing_span_resolution)]# 

f_nose[0] = nose_gear_reaction(0, 0, 0) # nose gear reaction force at t = 0 
f_main[0] = main_gear_reaction(f_nose[0], 0, 0) # main gear reaction force at t = 0 

for iteration in range(1, n):

    f_drag.append(drag(x_speed[iteration-1]))
    f_lift.append(lift(x_speed[iteration-1]))
    f_lift_rear.append(lift_ht(x_speed[iteration-1]))

    f_nose.append(nose_gear_reaction(f_lift[iteration], 
                                     x_speed[iteration-1],
                                     f_lift_rear[iteration]))
    
    f_main.append(main_gear_reaction(f_nose[iteration], 
                                     f_lift[iteration],
                                     f_lift_rear[iteration]))

    lift_y.append(lift_distribution(f_lift[iteration]))

    x_force = (total_thrust - f_drag[iteration] - mu*(f_nose[iteration] + f_main[iteration]))
    dvdt = x_acc(x_force)

    x_speed.append((x_speed[iteration-1] + dvdt*time_step))

    if f_nose[iteration] < 0:
        print(f"V_rotate has been achieved at time {simulation_time[iteration]}")
        break   

#==================================================
# 3. Plotting Results
#==================================================

fig, (ax1, ax2) = plt.subplots(2, figsize=(7, 7))
plt.subplots_adjust(left=0.15,
                    bottom=0.1, 
                    right=0.95, 
                    top=0.95, 
                    wspace=0.4, 
                    hspace=0.4)


# forces Plot settings
line1, = ax1.plot([], [], lw=2, label='Nose Gear')
line2, = ax1.plot([], [], lw=2, label='Main Gear')
line3, = ax1.plot([], [], lw=2, label='Lift')
ax1.title.set_text('Load x Time')
ax1.set_xlabel('Speed [knots]')
ax1.set_ylabel('Force [N]')
ax1.set_xlim(0, 65)
ax1.set_ylim(0, weight)
ax1.legend()

# lift distribution Plot settings
line4, = ax2.plot([], [], lw=2, label='Lift Distribution')
ax2.title.set_text('Lift load distribution')
ax2.set_xlabel('Wingspan position [m]')
ax2.set_ylabel('Lift Force [N]')
ax2.set_xlim(-wing_span/2 - 0.5, wing_span/2 + 0.5)
ax2.set_ylim(0, weight/10)
ax2.invert_yaxis()

# Direct plot due to debugging purposes
#ax1.plot(x_speed, f_nose, x_speed, f_main, x_speed, f_lift)

#ax2.plot(np.linspace(-wing_span/2, wing_span/2, 100), lift_y[3])

# Initialize data lists
speed_to_plot = []
f_nose_to_plot, f_main_to_plot, lift_to_plot = [], [], []
lift_dist_y = []

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])

    return line1, line2, line3, line4

def draw_graph(i):
    '''
    Update the graph every time step 

    '''
    speed_to_plot.append(x_speed[i]*1.94384)
    f_nose_to_plot.append(f_nose[i])
    f_main_to_plot.append(f_main[i])
    lift_to_plot.append(f_lift[i])
    lift_dist_y = lift_y[i]

    line1.set_xdata(speed_to_plot)
    line1.set_ydata(f_nose_to_plot)
    
    line2.set_xdata(speed_to_plot)
    line2.set_ydata(f_main_to_plot)

    line3.set_xdata(speed_to_plot)
    line3.set_ydata(lift_to_plot)

    line4.set_xdata(np.linspace(-wing_span/2,
                                wing_span/2,
                                100))
    line4.set_ydata(lift_dist_y)    

    return line1, line2, line3, line4

anim = animation.FuncAnimation(fig, draw_graph, frames=len(simulation_time), init_func=init, interval=18, repeat=False)  

#plt.show()

# saves the animation in our desktop
writervideo = animation.FFMpegWriter(fps=60)  
anim.save('TakeOff_lift.mp4', writer=writervideo)


