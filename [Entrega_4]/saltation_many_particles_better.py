
from matplotlib.pylab import *
import random
#unidades base SI (m, kg, s)

_m = 1.
_kg = 1.
_s = 1.
_mm = 1e-3*_m
_cm = 1e-2*_m
_gr = 1e-3*_kg
_in = 2.54 *_cm 

#masa de una particula 
g = 9.81 *_m/_s**2 #gravedad
d = 1*_mm #diametro 
rho_agua = 1000.*_kg/(_m**3)
rho_particula = 2650.*_kg/(_m**3)

dt = 0.001*_s  #paso de tiempo
tmax = 0.5*_s #tiempo maximo de simulacion
ti = 0.*_s  #tiempo actual
print tmax/dt
Nparticulas = 3

x0 = 10*d*rand(Nparticulas)
y0 = 3*d*rand(Nparticulas) + d

vx0 = rand(Nparticulas)/2
vy0 = rand(Nparticulas)/2

A = pi*(d/2)**2
V = (4./3.)*pi*(d/2)**3
m = rho_particula*V

W = array([0, -m*g])
#fB = array([0, rho_agua*V*g])

t = arange(0,tmax,dt)
Nt = len(t)

norm = lambda v: sqrt(dot(v,v))

Cd = 0.47 #para una particula
Cm = 0.5
CL = 0.2
Rp = 73.
R = (rho_particula/rho_agua -1)
alpha = 1/(1 + R + Cm)

ihat = array ([1,0]) #vectores unitarios
jhat = array ([0,1])

ustar = 0.14
def velocity_field(x):
	z = x[1] /d
	if z > 1./30:
		uf = ustar*log (30.*z)/0.41
	else :
		uf = 0 
	return array ([uf,0])	

vfx = velocity_field([0,4*d])[0]
k_penal = 100*0.5*Cd*rho_agua*A*norm(vfx)**2/(1*_mm) 
def particula(z,t):
	zp = zeros (4*Nparticulas)
	
	for i in range (Nparticulas):
		di = d
		xi = z[4*i:(4*i+2)]
		vi = z[4*i+2:(4*i+4)]
		vf = velocity_field(xi) #evaluo la velocidad del flujo en la posicion de la particula 
		vf_top = norm (velocity_field(xi + (di/2) *jhat)) #evaluo velocidad del flujo arriba
		vf_bot = norm (velocity_field(xi - (di/2) *jhat)) #evaluo velocidad de flujo abajo 
		vrel = vf - vi #se calcula velocidad relativa
		fD = (0.5*Cd*alpha*rho_agua*norm(vrel)*A)*vrel #coeficiente de drag 
		fL = (0.5*CL*alpha*rho_agua*(vf_top**2 - vf_bot**2)*A)*jhat #fuerza lift 

		Fi = W + fD + fL

		if xi [1] < 0: #evaluo el choque con el piso 
			Fi[1]+= -k_penal*xi[1]

		zp[4*i:(4*i+2)] = vi
		zp[4*i+2:(4*i+4)] = Fi / m 
	
	for i in range (Nparticulas):
		xi = z[4*i:(4*i+2)] #calculo posicion de particula i 
		for j in range (Nparticulas):
			if i > j :
				xj = z[4*j : (4 * j+2)] #posicion de particula j 
				rij = xj - xi #vector diferencia entre posiciones i j 
				if norm (rij) < d: 
					delta = d - norm (rij)	
					nij = rij / norm (rij) #vector unitario q apunta de i hacia j 
					Fj = k_penal*delta*nij
					Fi = -k_penal*delta*nij
					zp [4*i+2:(4*i+4)] += Fi/m	
					zp [4*j+2:(4*j+4)] += Fj/m

	return zp 

from scipy.integrate import odeint
z0 = zeros (4*Nparticulas)
z0[0::4] = x0 
z0[1::4] = y0
z0[2::4] = vx0 
z0[3::4] = vy0

print "integrando"
z = odeint (particula, z0, t)
print "fin"

fig = figure ()
ax = gca() #linea suelo
for i in range(Nparticulas):
	xi = z[:, 4*i]
	yi = z[:, 4*i+1]
	col = rand(4)
	for j in range(int(tmax/dt)): 
		if j%6 == 0: 
			circle = plt.Circle((xi[j], yi[j]), d/2, color ='r', clip_on=True)
		ax.add_artist(circle)	
		
	#plot (xi[0], yi[0], "o", color ="r")
	plot (xi,yi,"--.", color=col)
	#for x, y in zip(xi, yi):
	#	ax.add_artist(Circle(xy=(x,y),radius=d/2, color = col, alpha=0.7))

ax.axhline(d/2,color="k",linestyle="--")

show ()

