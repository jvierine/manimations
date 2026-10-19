"""Click-controlled derivation of meteor-head RCS, with archived numerical data.

conda run -n base python -m meteor_rcs.prepare_assets
conda run -n base manim-slides render -r 1920,1080 --fps 30 meteor_head_rcs.py MeteorHeadRCS
Plot provenance is kept in code comments and HDF5 metadata only.
"""
from pathlib import Path
import json

import h5py
import numpy as np
from manim import *
from manim_slides import Slide
from planck_to_ktb import Text

ROOT = Path(__file__).resolve().parent/'meteor_rcs'
BG, FG, MUTED = '#FFFFFF', '#172333', '#596779'
BLUE, GOLD, GREEN, RED = '#245774', '#9B4825', '#267369', '#B33C3C'


def boost_photon(direction, speed_over_c):
    """Photon direction and energy ratio after a Lorentz boost along +x.

    Used only for the explanatory diagram. Its deliberately enlarged v/c
    makes aberration and Doppler shifts visible; it is not an orbital speed.
    """
    direction=np.asarray(direction,dtype=float)
    gamma=1/np.sqrt(1-speed_over_c**2)
    factor=1+speed_over_c*direction[0]
    return np.array([(direction[0]+speed_over_c)/factor,
                     direction[1]/(gamma*factor),direction[2]/(gamma*factor)]),gamma*factor


class MeteorHeadRCS(Slide):
    skip_reversing = True

    def setup(self):
        self.camera.background_color = ManimColor(BG)
        MathTex.set_default(color=FG)
        self._slide_started = False
        self._clear_pending = False
        with h5py.File(ROOT/'data.h5') as f:
            self.sample = dict(f.attrs)
            self.production, self.q, self.nstar = f['example/production_q_nstar'][:]

    def clear_slide(self):
        self._clear_pending = True

    def _flush_pending_clear(self):
        if self._clear_pending:
            removable = list(self.mobjects)
            self.play(*[FadeOut(m) for m in removable], run_time=.3)
            self._clear_pending = False

    def start_slide(self, title, note):
        if self._slide_started:
            # The preceding segment ends on its complete frame. Cleanup occurs
            # only after the presenter advances, inside the incoming segment.
            self.next_slide(title, notes=note)
            self._flush_pending_clear()
        else:
            self._slide_started = True
            self.next_slide(title, notes=note)
        heading = Text(title, font_size=40, color=FG)
        if heading.width > 13:
            heading.scale_to_fit_width(13)
        heading.to_edge(UP, buff=.28)
        self.play(FadeIn(heading), run_time=.4)

    def finish(self):
        self.wait(.6)
        self.clear_slide()

    def equation(self, tex, size=37, color=FG):
        item = MathTex(tex, font_size=size, color=color)
        if item.width > 12.5:
            item.scale_to_fit_width(12.5)
        return item

    def stack(self, *items, buff=.38):
        group = VGroup(*items).arrange(DOWN, buff=buff).move_to(ORIGIN)
        if group.height > 5.2:
            group.scale_to_fit_height(5.2)
        for item in items:
            self.play(FadeIn(item, shift=.1*UP), run_time=.5)
        return group

    def prose(self, text, size=27, color=MUTED):
        item = Text(text, font_size=size, color=color)
        if item.width > 12.4:
            item.scale_to_fit_width(12.4)
        return item

    def paper_links(self, references):
        """Render scientific citations and record their clickable web bounds."""
        links=[]
        for label,url,item in references:
            links.append(dict(label=label,url=url,
                x=.5+item.get_left()[0]/config.frame_width,
                y=.5-item.get_top()[1]/config.frame_height,
                width=item.width/config.frame_width,height=item.height/config.frame_height))
        self._base_slide_config.notes+='\n<!-- paper-links: '+json.dumps(links)+' -->'

    def citation(self, label, url):
        text=self.prose(label,18,BLUE).move_to([0,-3.78,0])
        self.play(FadeIn(text),run_time=.25)
        self.paper_links([(label,url,text)])

    def image(self, name, width=9.5):
        return ImageMobject(ROOT/'assets'/name).set(width=width)

    def construct(self):
        self.story_release()
        self.story_pr_drag()
        self.solar_radiation_pressure()
        self.story_orbits()
        self.story_final_laps()
        self.story_entry()
        self.story_evaporation()
        self.story_collision()
        self.story_cloud()
        self.opening()
        self.geometry()
        self.grain_geometry()
        self.atmospheric_heating()
        self.free_molecular_drag()
        self.cooling_terms()
        self.energy()
        self.mass_loss()
        self.trajectory_equations()
        self.trajectory()
        self.ionization()
        self.line_density()
        self.source_terms()
        self.do_parameters()
        self.collision_length()
        self.collision_frames()
        self.velocity_dependence()
        self.mean_free_path_coordinates()
        self.normalization()
        self.normalization_meaning()
        self.density()
        self.shape_terms()
        self.density_3d()
        self.worked_example()
        self.mesh()
        self.plasma_response()
        self.maxwell()
        self.response_animation()
        self.far_field()
        self.rcs()
        self.polarization()
        self.limits()
        self.convergence()
        self.detection()
        self.inference()
        self.references()
        # No cleanup: the completed references remain on the final slide.

    def grain(self, center=ORIGIN, scale=.4):
        angles=np.linspace(0,TAU,10,endpoint=False)
        radii=np.array([1,.8,1.05,.85,1,.75,1,.9,1,.8])*scale
        return Polygon(*[np.array([r*np.cos(t),r*np.sin(t),0])+center for r,t in zip(radii,angles)],
                       color=GOLD,fill_opacity=1,stroke_width=1.5)

    def story_release(self):
        # Source: 55P story: juha.no/55p | comet identity: NASA Science, 55P/Tempel--Tuttle
        self.start_slide('A tiny grain leaves comet 55P/Tempel--Tuttle',
            'Follow one illustrative 100-micrometre grain. It is shed from the parent of the Leonid stream. '
            'The grain and comet are greatly enlarged for visibility.')
        rng=np.random.default_rng(55)
        stars=VGroup(*[Dot([rng.uniform(-6,6),rng.uniform(-2.8,2.7),0],radius=.012,color=MUTED,fill_opacity=.5) for _ in range(60)])
        nucleus=self.grain(np.array([-3.7,.3,0]),.7).set_color('#BFC8CC')
        tail=VGroup(*[Line([-4,.3,0],[-6.2,.3+dy,0],stroke_width=12,stroke_opacity=.1,color=BLUE) for dy in [-.9,-.4,.3,.8]])
        grain=self.grain(np.array([-3,.3,0]),.18)
        self.play(FadeIn(stars),FadeIn(tail),FadeIn(nucleus))
        dust=VGroup(*[Dot([-3.4,.3,0],radius=.035,color=GOLD) for _ in range(12)])
        self.add(dust,grain)
        self.play(*[d.animate.shift(RIGHT*rng.uniform(1,4)+UP*rng.uniform(-.7,.7)) for d in dust],
                  grain.animate.move_to([1.7,.9,0]),run_time=2.3)
        label=self.equation(r'D\simeq100\ \mu\mathrm m',42,GOLD).move_to([3.4,1.7,0])
        self.play(Write(label),GrowArrow(Arrow(label.get_bottom(),grain.get_top(),color=GOLD,buff=.1)))
        self.play(FadeIn(self.prose('A small piece of cometary material begins an independent orbit.',29,FG).shift(DOWN*2.2)))
        self.finish()

    @staticmethod
    def kepler_position(mean_anomaly,a,e):
        mean_anomaly=(mean_anomaly+PI)%TAU-PI
        eccentric=np.asarray(mean_anomaly,dtype=float).copy()
        for _ in range(15):
            eccentric-=(eccentric-e*np.sin(eccentric)-mean_anomaly)/(1-e*np.cos(eccentric))
        return np.array([a*(np.cos(eccentric)-e),a*np.sqrt(1-e*e)*np.sin(eccentric),np.zeros_like(eccentric)])

    def radiation_wave(self, start, end, color, wavelength=.26):
        """Code-native wavy photon arrow; no imported artwork or plot backend."""
        start,end=np.asarray(start),np.asarray(end)
        direction=(end-start)/np.linalg.norm(end-start)
        normal=np.array([-direction[1],direction[0],0])
        t=np.linspace(0,1,100)
        points=start+t[:,None]*(end-start)
        points+=.055*np.sin(2*PI*t*np.linalg.norm(end-start)/wavelength)[:,None]*np.sin(PI*t)[:,None]*normal
        wave=VMobject(color=color,stroke_width=2.6).set_points_as_corners(points)
        tip=Arrow(end-.22*direction,end,buff=0,color=color,stroke_width=2.6,
                  max_tip_length_to_length_ratio=.65)
        return VGroup(wave,tip)

    def story_pr_drag(self):
        # Source: Fitzpatrick, Effect of solar radiation on interplanetary dust
        # grains, Eqs. 10.160--10.178:
        # https://farside.ph.utexas.edu/teaching/celestial/Celestial/node95.html
        # Original two-frame schematic inspired by the user's reference image.
        # Absorbing spherical grain, thermal steady state, locally tangential
        # velocity. Isotropic emission is assumed in the instantaneous grain
        # frame. A toy v/c=0.30 exaggerates the directional effects.
        self.start_slide('Poynting--Robertson drag',
            'P-R means Poynting-Robertson. Compare the same radiation in two frames. '
            'In the grain frame sunlight is aberrated, while thermal emission is isotropic. '
            'In the Sun frame sunlight is radial and the moving grain emits radiation carrying net forward momentum. '
            'The recoil opposes tangential motion. The diagram exaggerates v/c; '
            'an actual meteor grain is highly nonrelativistic. This is distinct from a thermal-lag Yarkovsky force.')
        panels=VGroup(*[Rectangle(width=6.25,height=4.65,color=MUTED,stroke_width=1.2).move_to([x,.15,0]) for x in [-3.3,3.3]])
        self.play(Create(panels),run_time=.5)
        incoming=VGroup();emission=VGroup();grains=VGroup();labels=VGroup()
        for x,beta,title,caption in [
            (-3.3,0.,'(a) Grain rest frame','Thermal emission is isotropic.'),
            (3.3,.30,'(b) Sun rest frame','Emission carries forward momentum.'),
        ]:
            center=np.array([x,-.5,0])
            grain=Circle(.43,color=FG,fill_color='#D5DADD',fill_opacity=1,stroke_width=1.7).move_to(center)
            grains.add(grain)
            labels.add(self.prose(title,25,FG).move_to([x,2.12,0]),
                self.prose('Sunlight',20,GOLD).move_to([x+1.55,1.52,0]),
                self.prose(caption,22,FG).move_to([x,-1.99,0]))
            for offset in [-.48,-.16,.16,.48]:
                end=np.array([x+offset,.18,0])
                start=end+np.array([.43 if beta==0 else 0,1.52,0])
                incoming.add(self.radiation_wave(start,end,GOLD))
            for direction in [RIGHT,LEFT,UP,DOWN]:
                transformed,energy=boost_photon(direction,beta)
                normal=np.array([-transformed[1],transformed[0],0])
                for offset in [-.09,.09]:
                    start=center+.48*transformed+offset*normal
                    end=center+1.34*transformed+offset*normal
                    emission.add(self.radiation_wave(start,end,RED,wavelength=.27/energy))
            if beta:
                # A faint previous position identifies the moving grain;
                # motion and force arrows are separate from photon arrows.
                ghost=Circle(.43,color=MUTED,stroke_opacity=.25,fill_opacity=.05).move_to(center-.14*RIGHT)
                self.add(ghost)
                arrow=Arrow(center-.27*RIGHT,center+.27*RIGHT,buff=0,color=FG,stroke_width=2.5)
                grains.add(arrow)
                labels.add(self.equation(r'\mathbf v',23).next_to(arrow,UP,buff=.05))
            else:
                labels.add(self.equation(r'\mathbf v^{\prime}=0',20).move_to(center))
        self.play(FadeIn(grains),FadeIn(labels),run_time=.5)
        self.play(LaggedStart(*[Create(ray) for ray in incoming],lag_ratio=.06),run_time=1.1)
        self.play(LaggedStart(*[Create(ray) for ray in emission],lag_ratio=.025),run_time=1.6)
        force=self.equation(r'\mathbf F_{\rm drag}=-\frac{P_{\rm abs}}{c^2}\,\mathbf v_{t}',36,BLUE).move_to([-3.0,-2.77,0])
        meaning=VGroup(self.equation(r'P_{\rm abs}:\ \text{absorbed solar power [W]}',21,MUTED),
            self.equation(r'\mathbf v_t:\ \text{tangential grain velocity [m/s]}',21,MUTED),
            self.equation(r'c:\ \text{speed of light [m/s]};\quad\mathbf F_{\rm drag}:\ \text{tangential force [N]}',21,MUTED)).arrange(DOWN,buff=.14).move_to([3.0,-2.87,0])
        self.play(Write(force),FadeIn(meaning))
        self.play(FadeIn(self.prose('Tangential recoil removes angular momentum; aberration is exaggerated.',20).shift(DOWN*3.52)))
        self.citation('Burns, Lamy and Soter (1979)','https://doi.org/10.1016/0019-1035(79)90050-2')
        self.finish()

    def solar_radiation_pressure(self):
        # Source: Burns, Lamy & Soter (1979), doi:10.1016/0019-1035(79)90050-2.
        # Solar-spectrum-averaged Q_pr includes absorption and scattering.
        # beta_rad is distinct from the later Si ionization efficiency beta_Si.
        self.start_slide('Sunlight pushes outward and brakes orbital motion',
            'Radiation pressure is the leading radial force. Poynting--Robertson drag is its much smaller '
            'velocity-dependent component. The force arrows are schematic and not to scale. For a sphere, '
            'radiation pressure scales with projected area and gravity with mass. The inverse-radius scaling '
            'only holds while the radiation-pressure efficiency Q_pr remains comparable.')
        center=np.array([-3.1,1.25,0])
        sun=Dot([-5.8,1.25,0],radius=.18,color=GOLD)
        grain=self.grain(center,.17)
        self.play(FadeIn(sun),FadeIn(grain))
        self.add(self.prose('Sun',23,GOLD).next_to(sun,DOWN,buff=.2))
        pressure=Arrow(center+.22*RIGHT,center+1.75*RIGHT,buff=0,color=GOLD)
        gravity=Arrow(center+.22*LEFT,center+1.75*LEFT,buff=0,color=FG)
        velocity=Arrow(center+.22*UP,center+1.25*UP,buff=0,color=BLUE)
        drag=Arrow(center+.22*DOWN,center+.95*DOWN,buff=0,color=RED)
        self.play(GrowArrow(pressure),GrowArrow(gravity),GrowArrow(velocity),GrowArrow(drag))
        self.add(self.equation(r'F_{\rm rad}',25,GOLD).next_to(pressure,UP,buff=.15),
            self.equation(r'F_g',25).next_to(gravity,DOWN,buff=.15),
            self.equation(r'v_t',25,BLUE).next_to(velocity,LEFT,buff=.15),
            self.prose('P--R drag',22,RED).next_to(drag,RIGHT,buff=.18))
        force_ratio=self.term_definitions([
            r'F_{\rm rad}\propto Q_{\rm pr}a^2,\qquad F_g\propto\rho_Ma^3',
            r'\frac{|F_{\mathrm{PR},t}|}{F_{\rm rad}}=\frac{v_t}{c}\ll1'],[3.,1.4,0],32,6.2)
        self.play(Write(force_ratio))
        ratio=self.equation(r'\boxed{\beta_{\rm rad}\equiv\frac{F_{\rm rad}}{F_g}='
            r'\frac{3L_\odot Q_{\rm pr}}{16\pi c\mu_\odot\rho_Ma}}',39,GOLD).shift(DOWN*.8)
        self.play(Write(ratio))
        defs=self.term_definitions([
            r'a:\ \text{grain radius [m]};\quad\rho_M:\ \text{bulk density [kg/m}^3\text{]}',
            r'L_\odot:\ \text{solar luminosity [W]};\quad\mu_\odot:\ \text{solar gravity parameter [m}^3\mathrm{s}^{-2}\text{]}',
            r'Q_{\rm pr}:\ \text{solar radiation-pressure efficiency [dimensionless]};\quad c:\ \text{speed of light [m/s]}'],[0,-2.3,0],23,12.4)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('Smaller radius increases the force ratio when optical efficiency stays comparable.',25).shift(DOWN*3.28)))
        self.citation('Burns, Lamy and Soter (1979)','https://doi.org/10.1016/0019-1035(79)90050-2')
        self.finish()

        self.start_slide('When does radiation pressure eject the grain?',
            'Neglect ejection velocity, P--R drag and planetary perturbations at the instant of release. '
            'The grain inherits the parent velocity, while radial radiation pressure changes its effective '
            'solar gravity to mu_sun times one minus beta_rad. For constant beta_rad the displayed specific '
            'orbital energy determines whether the grain is bound. A circular parent gives the familiar '
            'one-half threshold; an eccentric comet has a release-position-dependent threshold. '
            'Q_pr is size- and composition-dependent, and can fall for grains much smaller than optical wavelengths.')
        sun=Dot([-4.8,1.1,0],radius=.18,color=GOLD)
        grain=self.grain(np.array([-2.1,1.1,0]),.16)
        radius=DoubleArrow([-4.65,.45,0],[-2.25,.45,0],buff=0,color=MUTED)
        velocity=Arrow([-2.1,1.35,0],[-2.1,2.35,0],buff=0,color=BLUE)
        self.play(FadeIn(sun),FadeIn(grain),GrowArrow(radius),GrowArrow(velocity))
        self.add(self.prose('Sun',23,GOLD).next_to(sun,LEFT,buff=.22),
            self.equation(r'r_{\rm rel}',27).next_to(radius,DOWN,buff=.14),
            self.equation(r'v_{\rm rel}',27,BLUE).next_to(velocity,RIGHT,buff=.18))
        self.play(FadeIn(self.prose('Same release velocity; weaker inward force.',24).move_to([-3.6,-.45,0])))
        energy=self.term_definitions([
            r'\mu_{\rm eff}=\mu_\odot(1-\beta_{\rm rad})',
            r'\mathcal E=\frac{v_{\rm rel}^2}{2}-\frac{\mu_{\rm eff}}{r_{\rm rel}}',
            r'\mathcal E=\mu_\odot\!\left(\frac{\beta_{\rm rad}}{r_{\rm rel}}-\frac{1}{2a_p}\right)'],[3.1,1.2,0],33,6.1)
        for row in energy:self.play(Write(row))
        escape=self.equation(r'\mathcal E\geq0\quad\Longleftrightarrow\quad\beta_{\rm rad}\geq\frac{r_{\rm rel}}{2a_p}'
            r'\qquad\left[\text{circular parent: }\beta_{\rm rad}\geq\tfrac12\right]',34,GOLD).shift(DOWN*1.2)
        self.play(Write(escape))
        defs=self.term_definitions([
            r'a_p:\ \text{parent semimajor axis [m]};\quad r_{\rm rel}:\ \text{distance from Sun at release [m]}',
            r'v_{\rm rel}:\ \text{inherited speed [m/s]};\quad\mathcal E:\ \text{specific orbital energy [J/kg]}',
            r'\mu_{\rm eff}:\ \text{effective gravity parameter [m}^3\mathrm{s}^{-2}\text{]};\quad\beta_{\rm rad}:\ \text{radiation/gravity force ratio}'],[0,-2.35,0],23,12.4)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('At very small sizes optical coupling can weaken: blowout is material dependent.',24,RED).shift(DOWN*3.3)))
        self.citation('Burns, Lamy and Soter (1979)','https://doi.org/10.1016/0019-1035(79)90050-2')
        self.finish()

    def story_orbits(self):
        # Source: Evolution data: juha.no/55p | Fitzpatrick P--R equations and Jupiter-averaged
        # perturbations
        self.start_slide('Sunlight and Jupiter reshape the orbit',
            'Reuse the actual orbit-averaged Jupiter-plus-Poynting--Robertson track from the 55P demo. '
            'This long-term secular illustration suppresses individual close encounters and does not predict an Earth impact. '
            'Its m/A=0.1 kg/m2 corresponds to a 100-micrometre sphere at density 1500 kg/m3; later thermal examples use a different stony material.')
        with h5py.File(ROOT/'inputs.h5') as f:
            g=f['orbit_55p'];orbit={k:g[k][:] for k in g}
        indices=[0,75,150,225]
        def points(index):
            node,inc,arg=[orbit[k][index] for k in ['longitude_ascending_node_rad','inclination_rad','argument_perihelion_rad']]
            rz=lambda a:np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
            rx=np.array([[1,0,0],[0,np.cos(inc),-np.sin(inc)],[0,np.sin(inc),np.cos(inc)]])
            xyz=(rz(node)@rx@rz(arg)@self.kepler_position(np.linspace(0,TAU,400),orbit['a_au'][index],orbit['eccentricity'][index])).T
            return np.column_stack([xyz[:,0],.85*xyz[:,1]+.4*xyz[:,2],np.zeros(len(xyz))])*.32+np.array([-1.,.1,0])
        sun=Dot([-1,.1,0],radius=.12,color=GOLD)
        earth=Circle(.32,color=BLUE,stroke_width=1.5).move_to(sun)
        jupiter=Ellipse(width=2*.32*5.2044,height=2*.32*5.2044*.85,color=MUTED,stroke_width=1.5).move_to(sun)
        curve=VMobject(color=GREEN).set_points_as_corners(points(0))
        self.play(FadeIn(sun),Create(earth),Create(jupiter),Create(curve))
        self.add(self.prose('Sun',20,GOLD).next_to(sun,DOWN),self.prose('Jupiter orbit',22).move_to([1.9,1.9,0]))
        label=self.prose('Orbit at release',25,GREEN).move_to([3.8,-1.9,0]);self.add(label)
        for i in indices[1:]:
            next_curve=VMobject(color=GREEN).set_points_as_corners(points(i))
            next_label=self.prose('Later secular orbit',25,GREEN).move_to(label)
            self.play(Transform(curve,next_curve),Transform(label,next_label),run_time=1.1)
        self.play(FadeIn(self.prose('Poynting--Robertson drag removes angular momentum; Jupiter perturbs the orbit.',25,FG).shift(DOWN*2.8)))
        self.finish()

    def story_final_laps(self):
        # Source: Encounter animation: meteor_head_rcs.py | illustrative geometry, not an impact
        # ephemeris
        self.start_slide('Many orbits later: the final few laps',
            'An illustrative Earth-crossing Kepler ellipse, not a selected trajectory from the secular model. '
            'The encounter phase is chosen to meet Earth. The dust is retrograde; Earth is prograde. '
            'Earlier orbital evolution is compressed into the preceding slide.')
        origin=np.array([1.,.1,0]);scale=1.35;a=2.2;e=1-1/a
        phase=ValueTracker(0)
        path=VMobject(color=GREEN).set_points_as_corners((self.kepler_position(np.linspace(0,TAU,400),a,e)*scale).T+origin)
        earth_path=Circle(scale,color=BLUE,stroke_width=1.5).move_to(origin)
        sun=Dot(origin,radius=.13,color=GOLD)
        dust=always_redraw(lambda:Dot(origin+scale*self.kepler_position(-phase.get_value(),a,e),radius=.055,color=GOLD))
        earth=always_redraw(lambda:Dot(origin+scale*np.array([np.cos((phase.get_value()-6*PI)*a**1.5),np.sin((phase.get_value()-6*PI)*a**1.5),0]),radius=.12,color=BLUE))
        self.play(Create(path),Create(earth_path),FadeIn(sun));self.add(dust,earth)
        meteoroid_label=self.prose('Meteoroid',25,GREEN).next_to(path,LEFT,buff=.4).set_y(1.5)
        self.add(meteoroid_label,self.prose('Earth',25,BLUE).move_to([3.2,-1.2,0]))
        self.play(phase.animate.set_value(6*PI),run_time=5.,rate_func=linear)
        dust.clear_updaters();earth.clear_updaters()
        self.play(Flash(dust.get_center(),color=GOLD,flash_radius=.35))
        self.play(FadeIn(self.prose('At the right place and time, the grain meets Earth.',31,FG).shift(DOWN*2.6)))
        self.finish()

    def story_entry(self):
        # Source: Entry physics: Vondrak et al. (2008), doi:10.5194/acp-8-7015-2008, with
        # corrigendum
        self.start_slide('The first atmospheric impacts',
            'Sputtering ejects surface atoms through nonthermal impacts, while collision heating grows as the particle '
            'encounters denser gas. These processes overlap; the cartoon emphasizes the onset sequence.')
        earth=Circle(5,color=BLUE,fill_opacity=.16).move_to([0,-6.2,0])
        atmosphere=Circle(6,color=BLUE,stroke_opacity=.2,fill_opacity=.07).move_to(earth)
        rng=np.random.default_rng(103)
        gas=VGroup(*[Dot([rng.uniform(-5,5),rng.uniform(-1.0,1.2),0],radius=.035,color=BLUE) for _ in range(55)])
        grain=self.grain(np.array([-3.2,2.2,0]),.15)
        self.add(earth,atmosphere,gas,grain)
        self.play(grain.animate.move_to([-2,1.,0]),run_time=1.1)
        sputter=VGroup(*[Dot(grain.get_center(),radius=.025,color=GOLD) for _ in range(6)])
        self.add(sputter)
        self.play(*[d.animate.shift(np.array([rng.uniform(-.5,.8),rng.uniform(.2,.8),0])) for d in sputter],
                  grain.animate.move_to([-.3,-.2,0]).set_color(RED),run_time=1.5)
        self.add(self.prose('Rare impacts sputter surface atoms.',26,GOLD).move_to([2.5,2,0]),
                 self.prose('More impacts heat the grain.',26,RED).move_to([2.8,1.35,0]))
        self.play(FadeIn(self.prose('The numerical example later includes thermal evaporation; sputtering is context here.',23).shift(DOWN*2.7)))
        self.finish()

    def story_evaporation(self):
        # Source: Langmuir evaporation: Hill et al. (2005); Vondrak et al. (2008), with corrigendum
        self.start_slide('A hot surface undergoes Langmuir evaporation',
            'Zoom into the grain rest frame. The hot surface emits neutral atoms with thermal velocity relative to the grain. '
            'Vapor pressure grows strongly with temperature; the full thermal model balances heating, radiation and latent heat.')
        grain=self.grain(np.array([-1.5,0,0]),.8).set_color(RED)
        initial=grain.copy().set_fill(opacity=0).set_stroke(MUTED,width=1.5,opacity=.45)
        self.add(initial)
        self.play(FadeIn(grain),FadeIn(self.prose('Grain rest frame',25).move_to([-4,2,0])))
        directions=np.linspace(-PI,PI,16,endpoint=False)
        for pulse in range(3):
            radius=.8*.92**pulse
            atoms=VGroup(*[Dot(grain.get_center()+radius*np.array([np.cos(a),np.sin(a),0]),radius=.045,color=GOLD) for a in directions])
            self.add(atoms)
            self.play(*[atom.animate.shift(1.05*np.array([np.cos(a),np.sin(a),0])).set_opacity(.45) for atom,a in zip(atoms,directions)],
                      grain.animate.scale(.92),run_time=1.15)
        self.add(self.prose('Initial size',22).move_to([-1.5,-1.28,0]))
        self.play(FadeIn(self.prose('Hot solid or melt',28,RED).move_to([3,1,0])),
                  FadeIn(self.prose('Neutral vapour',28,GOLD).move_to([3,.2,0])))
        self.play(Write(self.equation(r'm\downarrow\quad\Longrightarrow\quad D_{\rm grain}\propto m^{1/3}\downarrow',36,RED).move_to([2.5,-1.2,0])))
        self.play(FadeIn(self.equation(r'm:\ \text{mass};\quad D_{\rm grain}:\ \text{diameter}\quad\text{(fixed bulk density)}',21,MUTED).scale_to_fit_width(5.8).move_to([2.5,-1.82,0])))
        self.play(FadeIn(self.prose('Atoms carry mass away; the remaining grain becomes smaller.',29,FG).shift(DOWN*2.5)))
        self.finish()

    def story_collision(self):
        # Source: Hyperthermal impact ionization: Jones (1997); Dimant--Oppenheim Part 1 (2017)
        self.start_slide('The vapour retains the meteoroid\'s large bulk speed',
            'In the atmosphere frame a newly emitted atom has the grain velocity plus its much smaller thermal velocity. '
            'An energetic collision can produce an ion and an electron; not every encounter ionizes.')
        grain=self.grain(np.array([-4,-.45,0]),.23)
        atom=Dot([-3.6,.8,0],radius=.07,color=GOLD)
        molecule=VGroup(Dot([1.1,.8,0],radius=.09,color=BLUE),Dot([1.28,.8,0],radius=.09,color=BLUE))
        self.add(grain,atom,molecule)
        self.add(self.prose('Atmosphere frame',24).move_to([-3,2.15,0]))
        self.play(GrowArrow(Arrow([-4,-1.2,0],[-2.2,-1.2,0],color=GOLD,buff=0)),
                  Write(self.equation(r'\mathbf v_{\rm atom}=\mathbf v_{\rm grain}+\mathbf v_{\rm thermal}',34).shift(DOWN*2.35)))
        self.play(grain.animate.shift(RIGHT*4.7),atom.animate.move_to([1.1,.8,0]),run_time=1.7,rate_func=linear)
        self.play(Flash([1.1,.8,0],color=GOLD))
        ion=Circle(.09,color=RED,fill_opacity=.5).move_to(atom)
        electron=Dot(atom.get_center(),radius=.045,color=GREEN)
        self.play(ReplacementTransform(atom,ion),FadeIn(electron),run_time=.4)
        self.play(electron.animate.shift(UP*.8+RIGHT),run_time=.6)
        self.add(self.prose('Ion',25,RED).next_to(ion,DOWN),self.prose('Electron',25,GREEN).next_to(electron,RIGHT))
        self.finish()

    def story_cloud(self):
        # Source: actual 433-element layout from meteor/cal/maarsy_antenna_positions.txt,
        # preserved with source hash in meteor_rcs/maarsy_array.h5. Perspective
        # schematic of an antenna array, not a photograph or beam calculation.
        self.start_slide('A radar sees the plasma surrounding the grain',
            'The ion/electron cloud is much larger than the solid particle. A high-power large-aperture radar probes the '
            'induced plasma current, provided the echo exceeds its detection threshold. The cloud drawing is schematic; '
            'its quantitative kinetic shape is derived later. D_eff is an effective projected diameter of the scattering '
            'region, not a sharp plasma boundary, FDTD cutoff, or a value inferred from this cartoon. '
            'It depends on radar wavelength, plasma response, polarization and viewing direction.')
        rng=np.random.default_rng(2017)
        center=np.array([-2.,.35,0])
        grain=Dot(center,radius=.035,color=GOLD)
        electrons=VGroup(*[Dot(center+np.array([rng.normal(.45,.75),rng.normal(0,.55),0]),radius=.018,color=GREEN,fill_opacity=.6) for _ in range(140)])
        with h5py.File(ROOT/'maarsy_array.h5') as f:
            positions=f['east_north_m'][:]
        radar=VGroup()
        for east,north in positions:
            p=np.array([4+.034*east+.012*north,-1+.018*north,0])
            top=p+UP*.075
            radar.add(Line(p,top,color=MUTED,stroke_width=.8),
                Line(top+np.array([-.043,-.016,0]),top+np.array([.043,.016,0]),color=FG,stroke_width=1.1),
                Line(top+np.array([-.018,.024,0]),top+np.array([.018,-.024,0]),color=BLUE,stroke_width=1.1))
        self.play(FadeIn(grain),LaggedStart(*[FadeIn(p) for p in electrons],lag_ratio=.006),FadeIn(radar))
        beam=Polygon([4,-.6,0],[-3.6,1.9,0],[-3.6,-1.1,0],color=BLUE,fill_opacity=.05,stroke_width=1)
        self.play(FadeIn(beam))
        self.play(GrowArrow(Arrow([3.4,-.7,0],[-.5,.1,0],color=BLUE)),
                  GrowArrow(Arrow([-.4,.5,0],[3.4,-.3,0],color=GOLD)))
        self.add(self.prose('MAARSY phased array',25,FG).move_to([4,-2.15,0]),self.prose('Incident wave',23,BLUE).move_to([1.6,1.5,0]),
                 self.prose('Head echo',23,GOLD).move_to([1.7,.7,0]))
        diameter=DoubleArrow([-4.4,-1.05,0],[-4.4,1.65,0],buff=0,color=GREEN,stroke_width=2.5)
        self.play(GrowArrow(diameter),Write(self.equation(r'D_{\rm eff}',31,GREEN).next_to(diameter,LEFT)))
        self.play(Write(self.equation(r'D_{\rm grain}\sim100\ \mu\mathrm m\qquad\ll\qquad D_{\rm eff}',35,GREEN).shift(DOWN*2.65)))
        self.play(FadeIn(self.equation(r'D_{\rm eff}:\ \text{effective diameter of the radar-scattering region}',24,MUTED).shift(DOWN*3.18)))
        self.finish()

    def opening(self):
        # Source: Independent Rust FDTD implementation: github.com/jvierine/fdtd
        self.start_slide('What sets the echo, and what can we infer?',
            'Derive every interface from the thermal grain model to a polarized far-field radar cross section.')
        subtitle = self.prose('How does the grain create plasma, and how does that plasma scatter?', 29, FG).shift(UP*1.65)
        self.play(FadeIn(subtitle))
        labels = [('Ablation',r'-\dot m',GOLD),('Ionization',r'\dot N_e,\ q',GREEN),
                  ('Plasma shape',r'n_e(\mathbf r)',BLUE),('Maxwell solver',r'\sigma_{\rm rx}',RED)]
        boxes=[]
        for x,(name,symbol,color) in zip([-4.8,-1.6,1.6,4.8],labels):
            box=RoundedRectangle(width=2.8,height=1.55,corner_radius=.12,color=color)
            content=VGroup(Text(name,font_size=25,color=FG),MathTex(symbol,font_size=37,color=color)).arrange(DOWN,buff=.25)
            block=VGroup(box,content).move_to([x,0,0]);boxes.append(block)
            self.play(FadeIn(block),run_time=.4)
            if len(boxes)>1:self.play(GrowArrow(Arrow(boxes[-2].get_right(),block.get_left(),buff=.04,color=MUTED)),run_time=.3)
        self.play(FadeIn(self.prose('Forward: predict the echo. Inverse: constrain the grain from the echo.',28).shift(DOWN*1.7)))
        self.finish()

    def geometry(self):
        # Source: Geometry conventions: fdtd/examples/ablation_head_rcs.py and maarsy_rcs.py
        self.start_slide('Define the grain, atmosphere, and radar',
            'The ablation trajectory and the local electromagnetic scattering calculation use different frames. '
            'The DO axial coordinate is positive behind the meteor. Radar aspect is a separate rotation.')
        grain=Circle(.22,color=GOLD,fill_opacity=1).move_to(LEFT*2)
        tail=VGroup(*[Dot([-.9+.37*j,.35*np.sin(j),0],radius=.035,color=GREEN) for j in range(12)])
        velocity=Arrow([-2.3,1.1,0],[-4.6,1.1,0],color=GOLD,buff=0)
        axis=Arrow([-2,-.9,0],[3,-.9,0],color=FG,buff=0)
        self.play(FadeIn(grain),LaggedStart(*[FadeIn(d) for d in tail],lag_ratio=.08),GrowArrow(velocity),GrowArrow(axis))
        self.add(MathTex(r'\mathbf v',color=GOLD,font_size=35).next_to(velocity,UP),
                 MathTex(r'z_{\rm DO}>0\quad\text{behind}',font_size=30).next_to(axis,DOWN))
        definitions=self.equation(r'h:\ \text{altitude [m]};\quad v:\ \text{speed [m/s]};\quad m:\ \text{mass [kg]};\quad T_M:\ \text{grain temperature [K]}',27).shift(UP*2)
        frequency=self.equation(r'f_0=53.5\ \mathrm{MHz},\quad \lambda_0=c/f_0=5.60\ \mathrm m',29).shift(DOWN*2.35)
        self.play(Write(definitions),Write(frequency));self.finish()

    def term_definitions(self, entries, position, size=23, width=6.):
        rows=VGroup(*[self.equation(tex,size,MUTED) for tex in entries]).arrange(DOWN,buff=.22,aligned_edge=LEFT)
        if rows.width>width:rows.scale_to_fit_width(width)
        return rows.move_to(position)

    def grain_geometry(self):
        # Spherical isothermal approximation; A always denotes projected area.
        self.start_slide('Mass sets the radius and the intercepted area',
            'Assume a spherical grain with constant bulk density. Its projected area intercepts atmospheric particles. '
            'The whole surface, four times this area, radiates and evaporates.')
        grain=Circle(.95,color=RED,fill_opacity=.12).move_to([-3.2,.2,0])
        radius=Arrow(grain.get_center(),grain.get_center()+.95*RIGHT,buff=0,color=RED)
        self.play(Create(grain),GrowArrow(radius))
        self.add(self.equation(r'a',30,RED).next_to(radius,UP))
        first=MathTex('m','=',r'\rho_M',r'\frac{4\pi}{3}','a^3',font_size=39,color=FG).move_to([-3.2,1.95,0])
        self.play(Write(first));self.play(Indicate(grain,color=RED))
        solved=self.equation(r'a=\left(\frac{3m}{4\pi\rho_M}\right)^{1/3}',39,RED).move_to(first)
        self.play(TransformMatchingTex(first,solved))
        disk=Circle(.95,color=GOLD,fill_opacity=.2).move_to([3.2,.2,0])
        self.play(TransformFromCopy(grain,disk))
        self.play(Write(self.equation(r'A=\pi a^2',39,GOLD).move_to([3.2,1.95,0])))
        self.play(FadeIn(self.prose('Projected area',27,GOLD).move_to([3.2,-1.1,0])))
        definitions=self.term_definitions([
            r'm:\ \text{grain mass [kg]}',r'\rho_M:\ \text{grain bulk density [kg/m}^3\text{]}',
            r'a:\ \text{grain radius [m]}'],[-3.2,-2.25,0],24)
        area=self.term_definitions([r'A:\ \text{projected area [m}^2\text{]}',
            r'4A=4\pi a^2:\ \text{whole surface area [m}^2\text{]}'],[3.2,-2.25,0],24)
        self.play(FadeIn(definitions),FadeIn(area))
        self.finish()

    def atmospheric_heating(self):
        # Source: kinetic-energy flux and the Hill / MetAblate thermal model.
        # Lambda is defined with the displayed factor 1/2; Gamma in the drag
        # equation below uses F_drag=Gamma*rho_A*A*v^2 with no factor 1/2.
        self.start_slide('Atmospheric collisions supply the heating power',
            'In the grain frame the atmosphere streams into projected area A at speed v. '
            'Mass intercepted per second is rho_A v A. Each kilogram brings v squared over two joules. '
            'Lambda is the effective heat-transfer coefficient in this convention; the remaining energy need not heat the grain.')
        grain=Circle(.55,color=RED,fill_opacity=.15).move_to([3.1,1.35,0])
        tube=Rectangle(width=6.2,height=1.1,color=BLUE,fill_opacity=.035,stroke_width=1).move_to([-.55,1.35,0])
        area=Ellipse(width=.3,height=1.1,color=GOLD).move_to([2.55,1.35,0])
        gas=VGroup(*[Dot([-3.7+.4*(j%4),1.05+.2*(j//4),0],radius=.045,color=BLUE) for j in range(12)])
        velocity=Arrow([-2.7,2.23,0],[.2,2.23,0],color=BLUE,buff=0)
        self.play(FadeIn(tube),Create(grain),Create(area),FadeIn(gas),GrowArrow(velocity))
        self.add(self.equation(r'v',27,BLUE).next_to(velocity,UP,buff=.05),self.equation(r'A',28,GOLD).next_to(area,UP))
        flux=self.equation(r'\dot M_{\rm air}=\rho_AvA\quad[\mathrm{kg\,s^{-1}}]',34,BLUE).move_to([0,.15,0])
        self.play(gas.animate.shift(RIGHT*5.8),Write(flux),run_time=1.25)
        energy=self.equation(r'\text{Kinetic energy per intercepted kilogram: }\frac{v^2}{2}\quad[\mathrm{J\,kg^{-1}}]',29).move_to([0,-.7,0])
        self.play(Write(energy))
        power=self.equation(r'\boxed{P_{\rm heat}=\Lambda(\rho_AvA)\frac{v^2}{2}=\frac12\Lambda A\rho_Av^3}\quad[\mathrm W]',38,GOLD).move_to([0,-1.7,0])
        self.play(TransformFromCopy(flux,power),Indicate(grain,color=GOLD))
        definitions=self.term_definitions([
            r'\rho_A:\ \text{atmospheric mass density [kg/m}^3\text{]};\quad v:\ \text{relative speed [m/s]}',
            r'A:\ \text{projected area [m}^2\text{]};\quad\Lambda:\ \text{heat-transfer coefficient [dimensionless]}'],[0,-2.75,0],24,12.4)
        self.play(FadeIn(definitions))
        self.finish()

    def free_molecular_drag(self):
        # Source: Bariselli et al. (2020), doi:10.1093/mnras/stz3559;
        # Loth et al. (2021), doi:10.2514/1.J060153, free-molecular sphere limit.
        # The archived model uses Gamma*rho*A*v^2, not 1/2*Gamma*rho*A*v^2.
        self.start_slide('A small grain meets individual atmospheric molecules',
            'Knudsen number compares the undisturbed air--air mean free path to grain diameter. '
            'In free molecular flow, molecules usually reach the grain without colliding with another gas '
            'molecule over the grain scale. Use molecular momentum and energy transfer, rather than a continuum '
            'sphere drag coefficient. A dense ablation vapour can invalidate the unshielded-grain approximation. '
            'This air--air mean free path is distinct from the ablated-neutral collision lengths in the DO model.')
        grain=Circle(.22,color=RED,fill_opacity=.16).move_to([-3.,1.,0])
        diameter=DoubleArrow([-3.22,.48,0],[-2.78,.48,0],buff=0,color=RED,
                             max_tip_length_to_length_ratio=.2)
        gas=VGroup(*[Dot([-5.7+.25*(j%3),.4+.5*(j//3),0],radius=.04,color=BLUE) for j in range(9)])
        tracks=VGroup(*[Line([-5.8,y,0],[-3.4,y,0],color=BLUE,stroke_opacity=.25) for y in [.4,1.,1.6]])
        self.play(Create(grain),Create(tracks),FadeIn(gas),GrowArrow(diameter))
        self.add(self.equation(r'D=2a',26,RED).next_to(diameter,DOWN,buff=.15),
            self.prose('Individual molecular impacts',25,BLUE).move_to([-3.8,2.25,0]))
        self.play(gas.animate.shift(RIGHT*1.9),Indicate(grain,color=GOLD),run_time=1.1)
        kn=self.equation(r'\mathrm{Kn}=\frac{\lambda_{nn}}{D}\gg1',43,BLUE).move_to([3.1,1.55,0])
        speed=self.equation(r's\equiv\frac{v}{\sqrt{2k_BT_A/m_A}}\gg1',36,GOLD).move_to([3.1,.25,0])
        self.play(Write(kn),Write(speed))
        defs=self.term_definitions([
            r'\lambda_{nn}:\ \text{ambient air--air mean free path [m]};\quad D:\ \text{grain diameter [m]}',
            r's:\ \text{molecular speed ratio [dimensionless]};\quad v:\ \text{grain--air relative speed [m/s]}',
            r'T_A:\ \text{air temperature [K]};\quad m_A:\ \text{air-particle mass [kg]};\quad k_B:\ \text{Boltzmann constant [J/K]}'],[0,-1.55,0],24,12.4)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('Free molecular hypersonic flow: momentum transfer is set by gas--surface collisions.',26).shift(DOWN*2.85)))
        self.play(FadeIn(self.prose('An ablation-vapour shield can change the transfer coefficients.',24,RED).shift(DOWN*3.35)))
        self.citation('Bariselli et al. (2020)','https://doi.org/10.1093/mnras/stz3559')
        self.finish()

        self.start_slide('The same impacts transfer momentum and energy',
            'The intercepted atmospheric mass flux is rho_A v A. Multiplying by transferred momentum per kilogram '
            'gives drag; multiplying by deposited kinetic energy per kilogram gives grain heating. '
            'Gamma and Lambda are distinct dimensionless coefficients. The aerodynamic coefficient C_D is '
            'defined with dynamic pressure rho v squared over two, so C_D equals two Gamma. '
            'For an unshielded sphere at high molecular speed ratio, with outgoing molecular speeds small '
            'compared with incident speed, Gamma is approximately one and C_D approximately two. '
            'A low-speed continuum value around 0.47 is not appropriate here. '
            'At low molecular speed ratio free molecular Epstein drag is instead proportional to v; '
            'the present meteor-entry limit is hypersonic. The numerical solver is unchanged.')
        flux=self.equation(r'\dot M_{\rm air}=\rho_AvA\qquad[\mathrm{kg\,s^{-1}}]',35,BLUE).shift(UP*2.4)
        self.play(Write(flux))
        momentum=self.term_definitions([
            r'\frac{\text{transferred momentum}}{\text{incident mass}}=\Gamma v\quad[\mathrm{m/s}]',
            r'F_D=\Gamma\dot M_{\rm air}v=\Gamma\rho_AAv^2\quad[\mathrm N]',
            r'\dot v_{\rm drag}=-\frac{\Gamma\rho_AAv^2}{m}'],[-3.4,.9,0],30,6.3)
        energy=self.term_definitions([
            r'\frac{\text{deposited energy}}{\text{incident mass}}=\Lambda\frac{v^2}{2}\quad[\mathrm{J/kg}]',
            r'P_{\rm heat}=\frac12\Lambda\dot M_{\rm air}v^2',
            r'P_{\rm heat}=\frac12\Lambda\rho_AAv^3\quad[\mathrm W]'],[3.4,.9,0],30,6.3)
        for left,right in zip(momentum,energy):self.play(Write(left),Write(right))
        convention=self.equation(r'F_D\equiv\frac12C_D\rho_AAv^2\quad\Longrightarrow\quad\boxed{\Gamma=C_D/2}'
            r'\quad\xrightarrow[\text{hypersonic sphere}]{\text{free molecular}}\quad\Gamma\simeq1\ (C_D\simeq2)',30,GOLD).shift(DOWN*1.05)
        self.play(Write(convention))
        defs=self.term_definitions([
            r'F_D:\ \text{drag magnitude [N], opposite grain motion};\quad m:\ \text{grain mass [kg]}',
            r'\Gamma,\ C_D:\ \text{drag coefficients};\quad\Lambda:\ \text{heat-transfer coefficient (all dimensionless)}',
            r'\rho_A:\ \text{air mass density [kg/m}^3\text{]};\quad A=\pi a^2:\ \text{projected grain area [m}^2\text{]}'],[0,-2.25,0],23,12.4)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('Reflection and thermal accommodation affect momentum and heating differently.',25,RED).shift(DOWN*3.25)))
        self.citation('Loth et al. (2021)','https://doi.org/10.2514/1.J060153')
        self.finish()

    def cooling_terms(self):
        # Source: Stefan--Boltzmann radiation and latent-heat energy balance.
        self.start_slide('Radiation and escaping material remove energy',
            'Radiation is the net exchange between the whole hot surface and the effective ambient radiation temperature, '
            'approximated by atmospheric T_A here. Evaporation carries latent heat L for each kilogram lost. '
            'These are distinct energy sinks. Positive P_rad denotes net cooling when T_M exceeds T_A.')
        left=np.array([-3.3,1.3,0]);right=np.array([3.3,1.3,0])
        radiation_grain=Circle(.38,color=RED,fill_opacity=.15).move_to(left)
        evaporation_grain=Circle(.38,color=RED,fill_opacity=.15).move_to(right)
        self.play(Create(radiation_grain),Create(evaporation_grain))
        photons=VGroup(*[self.radiation_wave(left+.46*d,left+1.1*d,RED) for d in [LEFT,RIGHT,UP,DOWN]])
        atoms=VGroup(*[Dot(right+.43*np.array([np.cos(t),np.sin(t),0]),radius=.045,color=GREEN) for t in np.linspace(0,TAU,8,endpoint=False)])
        rad=self.equation(r'P_{\rm rad}=4A\epsilon\sigma_{\rm SB}(T_M^4-T_A^4)',30,RED).move_to([-3.3,-.35,0])
        evap=self.equation(r'P_{\rm evap}=L(-\dot m)',34,GREEN).move_to([3.3,-.35,0])
        self.play(LaggedStart(*[Create(p) for p in photons],lag_ratio=.1),Write(rad))
        self.add(atoms)
        self.play(*[atom.animate.shift((atom.get_center()-right)*1.3) for atom in atoms],evaporation_grain.animate.scale(.86),Write(evap))
        d1=self.term_definitions([
            r'T_M:\ \text{grain temperature [K]}',r'T_A:\ \text{ambient temperature [K]}',
            r'\epsilon:\ \text{emissivity [dimensionless]}',
            r'\sigma_{\rm SB}:\ \text{Stefan--Boltzmann constant}',
            r'\sigma_{\rm SB}=5.6704\times10^{-8}\ \mathrm{W\,m^{-2}\,K^{-4}}'],[-3.3,-2.05,0],23)
        d2=self.term_definitions([
            r'L:\ \text{specific latent heat [J/kg]}',r'-\dot m:\ \text{positive mass-loss rate [kg/s]}',
            r'4A:\ \text{radiating and evaporating surface [m}^2\text{]}'],[3.3,-2.05,0],23)
        self.play(FadeIn(d1),FadeIn(d2));self.finish()

    def energy(self):
        # Source: Hill et al. (2005), doi:10.1051/0004-6361:20053053;
        # native implementation: fdtd/src/bin/meteor-ablation.rs.
        self.start_slide('Build the grain energy balance',
            'Click through the three power terms. The left side is energy stored as changing grain temperature. '
            'All powers are in watts. The spherical isothermal approximation assigns one T_M to the grain.')
        top=self.equation(r'T_M:\ \text{grain temperature [K]};\quad m:\ \text{mass [kg]};\quad c_p:\ \text{specific heat [J/(kg K)]}',23,MUTED).shift(UP*2.6)
        equation=MathTex(r'mc_p\dot T_M','=',r'P_{\rm heat}','-',r'P_{\rm rad}','-',r'P_{\rm evap}',font_size=40,color=FG).shift(UP*1.8)
        for i,color in [(2,GOLD),(4,RED),(6,GREEN)]:equation[i].set_color(color)
        self.play(FadeIn(top),Write(equation[0]),Write(equation[1]))
        self.play(FadeIn(self.equation(r'\dot T_M=dT_M/dt:\ \text{temperature change per second [K/s]}',22,MUTED).shift(DOWN*3.32)))
        for x,index,color,kind in [(-4.3,2,GOLD,'heat'),(0,4,RED,'radiation'),(4.3,6,GREEN,'evaporation')]:
            center=np.array([x,.3,0])
            grain=Circle(.25,color=RED,fill_opacity=.13).move_to(center)
            additions=[Write(equation[index])] if index==2 else [Write(equation[index-1]),Write(equation[index])]
            self.play(Create(grain),*additions)
            if kind=='heat':
                particles=VGroup(*[Dot(center+[-1,.18*j,0],radius=.04,color=GOLD) for j in [-1,0,1]])
                self.add(particles);self.play(particles.animate.shift(RIGHT*.75),Indicate(equation[index],color=GOLD))
                defs=[r'P_{\rm heat}=\frac12\Lambda A\rho_Av^3',r'\Lambda:\ \text{heat transfer [dimensionless]}',
                    r'A:\ \text{projected area [m}^2\text{]}',r'\rho_A:\ \text{air mass density [kg/m}^3\text{]}',r'v:\ \text{relative speed [m/s]}']
            elif kind=='radiation':
                rays=VGroup(*[self.radiation_wave(center+.3*d,center+.8*d,RED) for d in [LEFT,RIGHT,UP,DOWN]])
                self.play(Create(rays),Indicate(equation[index],color=RED))
                defs=[r'P_{\rm rad}=4A\epsilon\sigma_{\rm SB}(T_M^4-T_A^4)',r'4A:\ \text{whole surface area [m}^2\text{]}',
                    r'\epsilon:\ \text{emissivity [dimensionless]}',r'\sigma_{\rm SB}:\ \text{Stefan--Boltzmann constant}',
                    r'[\sigma_{\rm SB}]=\mathrm{W\,m^{-2}\,K^{-4}}',r'T_A:\ \text{ambient temperature [K]}']
            else:
                atoms=VGroup(*[Dot(center+.3*d,radius=.045,color=GREEN) for d in [LEFT,RIGHT,UP,DOWN]])
                self.add(atoms);self.play(*[a.animate.shift((a.get_center()-center)*1.5) for a in atoms],grain.animate.scale(.88),Indicate(equation[index],color=GREEN))
                defs=[r'P_{\rm evap}=L(-\dot m)',r'L:\ \text{specific latent heat [J/kg]}',
                    r'-\dot m:\ \text{mass lost per second [kg/s]}']
            definitions=self.term_definitions(defs,[x,0,0],21,4.)
            definitions.arrange(DOWN,buff=.16,aligned_edge=LEFT).next_to(np.array([x,-.75,0]),DOWN,buff=0)
            for definition in definitions:self.play(FadeIn(definition),run_time=.23)
            self.wait(.5)
            if kind!='evaporation':
                self.next_slide('Add radiative cooling' if kind=='heat' else 'Add evaporative cooling',
                    notes='Add the next physical power term while retaining the previous terms and definitions.')
        self.next_slide('Expand the energy terms',notes='Substitute all three powers. Their colors retain the graphical interpretation; every symbol is defined on this frame.')
        expanded=MathTex(r'mc_p\dot T_M','=',r'\tfrac12\Lambda A\rho_Av^3','-',
            r'4A\epsilon\sigma_{\rm SB}(T_M^4-T_A^4)','-',r'L(-\dot m)',font_size=34,color=FG)
        if expanded.width>12.7:expanded.scale_to_fit_width(12.7)
        expanded.move_to(equation)
        for i,color in [(2,GOLD),(4,RED),(6,GREEN)]:expanded[i].set_color(color)
        self.remove(*equation)
        self.add(equation)
        self.play(TransformMatchingTex(equation,expanded),run_time=1.2)
        for index,color in [(2,GOLD),(4,RED),(6,GREEN)]:self.play(Indicate(expanded[index],color=color),run_time=.55)
        self.finish()

    def mass_loss(self):
        # Source: MetAblate material vapor-pressure law. The effective vapor
        # mass is 50 u; it is distinct from the later Si ionization proxy.
        self.start_slide('Langmuir evaporation gives the mass-loss rate',
            'Build mass loss as whole surface area times vapor pressure times the kinetic conversion factor. '
            'All atoms are represented by an effective 50-u vapor species in this thermal model. '
            'The formula assumes free evaporation with the adopted effective material law; it is not a species-resolved calculation.')
        eq=MathTex(r'-\dot m','=',r'4A',r'p_{\rm vap}(T_M)',r'\sqrt{\frac{m_{\rm vap}}{2\pi k_BT_M}}',font_size=42,color=FG).shift(UP*1.92)
        eq[2].set_color(BLUE);eq[3].set_color(RED);eq[4].set_color(GOLD)
        self.play(Write(eq[:2]))
        grain=Circle(.52,color=RED,fill_opacity=.15).move_to([-4.5,.38,0])
        shell=Circle(.62,color=BLUE,stroke_width=3).move_to(grain)
        self.play(Create(grain),Create(shell),Write(eq[2]),run_time=.8)
        self.play(Write(self.equation(r'4A=4\pi a^2:\ \text{whole evaporating surface [m}^2\text{]}',24,BLUE).move_to([1.5,.75,0])))
        self.play(Write(eq[3]),Indicate(grain,color=RED))
        self.play(FadeIn(self.equation(r'p_{\rm vap}(T_M):\ \text{equilibrium vapor pressure [Pa]}',24,RED).move_to([1.5,.15,0])))
        atoms=VGroup(*[Dot(grain.get_center()+.65*np.array([np.cos(t),np.sin(t),0]),radius=.045,color=GOLD) for t in np.linspace(0,TAU,10,endpoint=False)])
        self.add(atoms);self.play(Write(eq[4]),*[a.animate.shift((a.get_center()-grain.get_center())*.7) for a in atoms],grain.animate.scale(.9))
        self.play(FadeIn(self.equation(r'-\dot m:\ \text{positive mass-loss rate [kg/s]}',24,GREEN).move_to([1.5,-.45,0])))
        left=self.term_definitions([r'T_M:\ \text{grain temperature [K]}',r'm_{\rm vap}:\ \text{mass of one effective vapor atom}',
            r'm_{\rm vap}=50u;\quad u=1.66054\times10^{-27}\ \mathrm{kg}'],[-3.3,-1.8,0],23)
        right=self.term_definitions([r'k_B:\ \text{Boltzmann constant}',r'k_B=1.380649\times10^{-23}\ \mathrm{J\,K^{-1}}',
            r'A=\pi a^2:\ \text{projected grain area [m}^2\text{]}',r'a:\ \text{grain radius [m]}'],[3.3,-1.8,0],23)
        self.play(FadeIn(left),FadeIn(right))
        self.play(Write(self.equation(r'\text{Material fit: }p_{\rm vap}(T_M)=0.1\times10^{10.6-(13500\,\mathrm K)/T_M}\ \mathrm{Pa}',29).shift(DOWN*3.12)))
        self.finish()

    def trajectory_equations(self):
        # Source: native trajectory ODEs in fdtd/src/bin/meteor-ablation.rs.
        self.start_slide('Close the trajectory and thermal evolution together',
            'The state is altitude h, speed v, mass m and grain temperature T_M. '
            'Chi is zenith angle, measured from the local vertical. This drag coefficient convention has no factor one half: '
            'F_drag=Gamma A rho_A v squared. The heating efficiency Lambda is separate.')
        grain=Dot([-3.8,1.1,0],radius=.13,color=GOLD)
        down=Arrow([-3.8,1.5,0],[-3.8,-.6,0],buff=0,color=MUTED)
        motion=Arrow([-3.8,1.1,0],[-2.35,-.35,0],buff=0,color=GOLD)
        drag=Arrow([-3.8,1.1,0],[-4.7,2.,0],buff=0,color=BLUE)
        self.play(FadeIn(grain),GrowArrow(down),GrowArrow(motion),GrowArrow(drag))
        angle=Angle(down,motion,radius=.6,other_angle=False,color=GREEN)
        self.play(Create(angle))
        self.add(self.equation(r'\chi',27,GREEN).move_to([-3.36,.3,0]),self.equation(r'v',27,GOLD).next_to(motion,RIGHT),
            self.equation(r'F_{\rm drag}',26,BLUE).next_to(drag,LEFT),self.prose('Vertical',21).move_to([-4.45,-.75,0]))
        eqs=VGroup(self.equation(r'\dot h=-v\cos\chi',35),self.equation(r'\dot v=-\frac{\Gamma A\rho_Av^2}{m}+g\cos\chi',35),
            self.equation(r'\dot m:\ \text{Langmuir evaporation};\quad\dot T_M:\ \text{energy balance}',24)).arrange(DOWN,buff=.4).move_to([2.3,1.05,0])
        for eq in eqs:self.play(Write(eq))
        left=self.term_definitions([r'h:\ \text{altitude [m]};\quad\dot h:\ \text{vertical rate [m/s]}',
            r'v:\ \text{speed [m/s]};\quad\dot v:\ \text{acceleration [m/s}^2\text{]}',
            r'\chi:\ \text{entry zenith angle from vertical}',r'g:\ \text{gravitational acceleration [m/s}^2\text{]}'],[-3.3,-2.,0],23)
        right=self.term_definitions([r'\Gamma:\ \text{drag coefficient [dimensionless]}',r'A:\ \text{projected area [m}^2\text{]};\quad m:\ \text{grain mass [kg]}',
            r'\rho_A(h):\ \text{atmospheric mass density [kg/m}^3\text{]}',r'T_M:\ \text{grain temperature [K]}'],[3.3,-2.,0],23)
        self.play(FadeIn(left),FadeIn(right));self.finish()

    def trajectory(self):
        # Source: Archived native trajectory: meteor_rcs/inputs.h5; native plots: rustplotlib
        self.start_slide('The output is a trajectory, not a single mass-loss rate',
            'Archived native Rust example: initial diameter 100 micrometers, initial speed 49.684 km/s, entry zenith 45 degrees, '
            'density 3300 kg/m3. Curves show the peak region; full arrays are bundled in HDF5.')
        self.play(FadeIn(self.image('ablation.png',10.2).shift(UP*.15)))
        self.play(FadeIn(self.prose('100 micrometre grain; initial speed 49.684 km/s; entry zenith 45 degrees',24).shift(DOWN*2.65)))
        self.finish()

    def ionization(self):
        # Source: Jones (1997), Eq. 33 / Table 1, doi:10.1093/mnras/288.4.995
        self.start_slide('Convert lost mass into an electron source',
            'Use the Jones Si first-collision probability. All lost mass is represented by Si in this example. '
            'This bounded probability omits secondary ionizing collisions and species-resolved ablation.')
        image=self.image('ionization.png',5.7).move_to([3.25,-.15,0]);self.play(FadeIn(image))
        group=VGroup(self.equation(r'\dot N_e=\beta_{\rm Si}\frac{-\dot m}{m_{\rm Si}}',38,GREEN),
            self.equation(r'm_{\rm Si}=28.085\,u',28),
            self.equation(r'\beta_{\rm Si}=\frac{X}{1+X}',34),
            self.equation(r'X=18.5\!\times\!10^{-6}[\max(v_k-11,0)]^2v_k^{0.8}',24),
            self.equation(r'v_k:\ \text{speed in km/s}',23,MUTED),self.prose('Primary Si proxy; not a chemical mixture.',22)).arrange(DOWN,buff=.3)
        group.move_to([-3.25,0,0])
        for item in group:self.play(FadeIn(item),run_time=.35)
        self.finish()

    def line_density(self):
        # Source: Source normalization: fdtd/examples/ablation_head_rcs.py and src/bin/meteor-
        # ablation.rs
        self.start_slide('Line density is production per distance travelled',
            'In dt the source produces dotN_e dt electrons while traveling ds=v dt. q is the production line density. '
            'It is neither a surviving mature-trail line density nor automatically an integral across the near-head distribution.')
        path=Line(LEFT*4,RIGHT*4,color=MUTED).shift(UP*1.65)
        meteor=Dot(path.get_start(),radius=.12,color=GOLD)
        self.play(Create(path),FadeIn(meteor))
        self.play(meteor.animate.move_to(path.get_end()),run_time=1.5,rate_func=linear)
        length=Brace(path,DOWN,color=MUTED);self.play(GrowFromCenter(length))
        self.add(self.equation(r'ds=v\,dt',30).next_to(length,DOWN))
        first=self.equation(r'q=\frac{dN_e}{ds}=\frac{\dot N_e\,dt}{v\,dt}',43).shift(DOWN*.2)
        result=self.equation(r'\boxed{q=\frac{\beta_{\rm Si}(-\dot m)}{m_{\rm Si}v}}\qquad[\mathrm{electrons\ m^{-1}}]',43,GREEN).shift(DOWN*1.35)
        self.play(Write(first));self.play(Write(result))
        self.play(FadeIn(self.prose('Use instantaneous v, not initial entry speed.',27).shift(DOWN*2.5)))
        self.finish()

    def collision_length(self):
        # Source: Dimant--Oppenheim Part 1, primary-neutral collision rate and path; adopted sigma_c
        # in fdtd
        self.start_slide('The DO length is the ablated-neutral travel distance',
            'V_T is the thermal speed of the Si proxy. Collision rate is set by atmospheric flux past the grain. '
            'The effective velocity-dependent cross section is adopted, not a new validation of high-speed collision physics.')
        self.stack(self.equation(r'V_T=\sqrt{k_BT_M/m_{\rm Si}},\qquad \nu_c=n_A\sigma_c(v)v',37),
            self.equation(r'n_A:\ \text{atmospheric number density};\quad\sigma_c:\ \text{heavy-particle collision cross section}',24,MUTED),
            self.equation(r'\boxed{\lambda_T=\frac{V_T}{\nu_c}=\frac{V_T}{v}\ell_A},\qquad \ell_A=\frac{1}{n_A\sigma_c}',43,BLUE),
            self.equation(r'\sigma_c=5.61\times10^{-19}v_k^{-0.8}\ \mathrm{m^2}',30),
            self.equation(r'\text{Both coordinates scale with }\lambda_T\text{; angular structure stays anisotropic.}',25,MUTED))
        self.finish()

    def source_terms(self):
        # Source: Jones (1997), primary Si probability; source bookkeeping in fdtd
        self.start_slide('Read the line-density equation one conversion at a time',
            'The all-Si approximation converts kilograms to atoms with a mass per atom, not a molar mass. '
            'Beta is the primary ionization probability for each released Si atom. '
            'Divide the resulting electron production rate by instantaneous meteor speed.')
        rows = [
            (r'-\dot m', r'\mathrm{kg\,s^{-1}}', 'Mass leaving the grain', GOLD),
            (r'(-\dot m)/m_{\rm Si}', r'\mathrm{atoms\,s^{-1}}', 'Divide by mass of one Si atom', GOLD),
            (r'\dot N_e=\beta_{\rm Si}(-\dot m)/m_{\rm Si}', r'\mathrm{electrons\,s^{-1}}', 'Multiply by primary ionization probability', GREEN),
            (r'q=\dot N_e/v', r'\mathrm{electrons\,m^{-1}}', 'Divide by distance travelled per second', BLUE),
        ]
        for y, (tex, unit, text, color) in zip([1.9,.7,-.5,-1.7], rows):
            formula = self.equation(tex, 32, color).move_to([-3.6,y,0])
            units = self.equation(unit, 23).move_to([.65,y,0])
            meaning = self.prose(text, 22).move_to([4.3,y,0])
            if meaning.width>4.5:meaning.scale_to_fit_width(4.5)
            self.play(FadeIn(formula),FadeIn(units),FadeIn(meaning),run_time=.5)
        self.play(FadeIn(self.prose('Production per path: losses and later trail chemistry require additional physics.',24).shift(DOWN*2.8)))
        self.finish()

    def do_parameters(self):
        # Source: DO Parts 1--2; atmospheric inputs: archived MSIS; Si source approximation
        self.start_slide('Separate the source, atmosphere, and kinetic shape',
            'The source supplies q, speed and temperature. MSIS supplies n_A and mean air-particle mass. '
            'The collision model supplies sigma_c(v). These determine the DO spatial scale and amplitude. '
            'Grain radius already affects mass loss; an additional core radius regularizes the ideal singular source.')
        entries = [
            (r'q\ [\mathrm{m^{-1}}]', 'Electron production per travelled metre', GREEN),
            (r'v\ [\mathrm{m\,s^{-1}}],\quad T_M\ [\mathrm K]', 'Relative atmospheric flux and neutral thermal speed', GOLD),
            (r'n_A\ [\mathrm{m^{-3}}],\quad m_A=\rho_A/n_A', 'Atmospheric number density and mean particle mass', BLUE),
            (r'\sigma_c(v)\ [\mathrm{m^2}]', 'Effective meteor-atom / air collision cross section', BLUE),
            (r'm_{\rm Si}=28.085\,u', 'Ablated atom mass in this single-species proxy', GREEN),
        ]
        for y, (tex, text, color) in zip([2.05,1.1,.15,-.8,-1.75],entries):
            a=self.equation(tex,29,color).move_to([-3.9,y,0])
            b=self.prose(text,23).move_to([2.8,y,0])
            if b.width>7:b.scale_to_fit_width(7)
            self.play(FadeIn(a),FadeIn(b),run_time=.4)
        self.play(FadeIn(self.prose('After source normalization, grain area is not another free amplitude factor.',24).shift(DOWN*2.8)))
        self.finish()

    def collision_frames(self):
        # Source: DO Part 1: primary neutrals have V about V_T, much less than meteor speed
        self.start_slide('Two frames explain two very different path lengths',
            'Both lengths use the same fast meteor-atom / air collision cross section. '
            'ell_A is not the ordinary air-air thermal neutral mean free path. '
            'In the grain rest frame the evaporated atom moves at thermal speed while atmospheric targets stream past at v.')
        headings=VGroup(self.prose('Atmosphere frame',28,FG).move_to([-3.5,2.15,0]),
            self.prose('Grain rest frame',28,FG).move_to([3.5,2.15,0]))
        self.play(FadeIn(headings))
        for center,span,color in [(-3.5,2.4,GOLD),(3.5,.8,BLUE)]:
            atom=Dot([center-span/2,.6,0],radius=.09,color=GREEN)
            target=Circle(.13,color=MUTED).move_to([center+span/2,.6,0])
            arrow=Arrow(atom.get_center(),target.get_center(),buff=.17,color=color)
            self.play(FadeIn(atom),FadeIn(target),GrowArrow(arrow),run_time=.5)
        left=VGroup(self.equation(r'v\gg V_T',30,GOLD),
            self.equation(r'\ell_A=v/\nu_c=1/(n_A\sigma_c)',30),
            self.prose('Fast atom travels through nearly stationary air.',22)).arrange(DOWN,buff=.35).move_to([-3.5,-1.15,0])
        right=VGroup(self.equation(r'V_T=\sqrt{k_BT_M/m_{\rm Si}}',30,BLUE),
            self.equation(r'\lambda_T=V_T/\nu_c=(V_T/v)\ell_A',30),
            self.prose('Neutral separates thermally from the grain.',22)).arrange(DOWN,buff=.35).move_to([3.5,-1.15,0])
        self.play(FadeIn(left),FadeIn(right))
        self.play(FadeIn(self.equation(r'\text{Same collision time: }1/\nu_c.\quad\text{Different velocities give different distances.}',27).shift(DOWN*2.65)))
        self.finish()

    def velocity_dependence(self):
        # Source: DO collision-length interpretation; effective sigma_c(v) adopted in fdtd
        self.start_slide('Why does meteoroid speed change the cloud size?',
            'These are controlled comparisons at fixed atmospheric number density and fixed grain temperature. '
            'A faster incoming atmospheric flux increases collision frequency. The adopted cross section decreases with speed, '
            'so its speed dependence partly compensates the faster flux. Along a real trajectory n_A and T_M also vary.')
        self.stack(self.equation(r'\lambda_T=\frac{\sqrt{k_BT_M/m_{\rm Si}}}{n_A\sigma_c(v)v}',43,BLUE),
            self.prose('Hold atmosphere and temperature fixed:',27,FG),
            self.equation(r'\sigma_c=\mathrm{constant}:\qquad\lambda_T\propto v^{-1}',34),
            self.equation(r'\sigma_c\propto v^{-0.8}:\quad\nu_c\propto v^{0.2},\quad\lambda_T\propto v^{-0.2},\quad\ell_A\propto v^{0.8}',31,GOLD),
            self.equation(r'\text{Both coordinates use }\lambda_T\text{; front/back asymmetry comes from the shape.}',25,MUTED),
            self.prose('A real entry also changes density, temperature, mass loss, and ionization.',24))
        self.finish()

    def mean_free_path_coordinates(self):
        # Source: Dimant--Oppenheim Part 2, axis and dimensionless-coordinate conventions
        self.start_slide('Measure every cloud coordinate in thermal collision lengths',
            'DO is axisymmetric about the meteor trajectory but not spherically symmetric. '
            'Positive z points behind the grain. The radial coordinate is nonnegative; signed radial values only draw a slice. '
            'One lambda_T scales both longitudinal and transverse coordinates.')
        ax=Axes(x_range=[-1,4,1],y_range=[-2,2,1],x_length=5,y_length=3.5,
            tips=True,axis_config={'color':MUTED,'include_ticks':True}).move_to([-3.5,.3,0])
        point=ax.c2p(2,1)
        self.play(Create(ax),FadeIn(Dot(ax.c2p(0,0),radius=.1,color=GOLD)))
        self.play(Create(DashedLine(ax.c2p(2,0),point,color=BLUE)),Create(DashedLine(ax.c2p(0,1),point,color=BLUE)),FadeIn(Dot(point,color=GREEN)))
        self.add(MathTex(r'\zeta',font_size=27).next_to(ax.x_axis,RIGHT),MathTex(r'\eta',font_size=27).next_to(ax.y_axis,UP),
                 self.equation(r'(2,1)',27,GREEN).next_to(point,UR))
        items=VGroup(self.equation(r'\zeta=\frac{z}{\lambda_T},\quad\eta=\frac{r_\perp}{\lambda_T}',38,BLUE),
            self.equation(r'r_\perp=\sqrt{x^2+y^2}',31),
            self.equation(r's=\sqrt{\zeta^2+\eta^2}=R/\lambda_T,\quad\mu=\zeta/s',29),
            self.equation(r'\text{Illustration: }\lambda_T=0.16\ \mathrm m',24,MUTED),
            self.equation(r'(z,r_\perp)=(0.32,0.16)\,\mathrm m\ \Rightarrow\ (\zeta,\eta)=(2,1)',25,GREEN)).arrange(DOWN,buff=.38).move_to([3.2,.3,0])
        for item in items:self.play(FadeIn(item),run_time=.35)
        self.play(FadeIn(self.prose('Rescaling both axes preserves the angular structure of the dimensionless model.',25).shift(DOWN*2.55)))
        self.finish()

    def normalization_meaning(self):
        # Source: DO Eqs. 45--48, rewritten using source production q
        self.start_slide('Normalization gives an amplitude and a length scale',
            'n_star is a reference amplitude. F is the specified kinetic solution, not a unit-integral probability density. '
            'Consequently q is not determined by integrating this near-head density over a transverse plane. '
            'A change in lambda changes both sampled dimensionless coordinates and the prefactor.')
        self.stack(self.equation(r'n_e=n_\star F_{\rm DO}(\zeta,\eta),\qquad n_\star=\frac{q(1+m_{\rm Si}/m_A)}{2\sqrt{6\pi}\lambda_T^2}',38,BLUE),
            self.equation(r'\frac{q}{\lambda_T^2}:\quad\frac{\mathrm{m^{-1}}}{\mathrm{m^2}}=\mathrm{m^{-3}}',32),
            self.equation(r'n_\star:\ \text{reference density, not maximum};\quad F:\ \text{not normalized to integrate to one}',25,MUTED),
            self.equation(r'q\to2q,\ \lambda_T\ \mathrm{fixed}:\quad n_e(\mathbf r)\to2n_e(\mathbf r)',31,GREEN),
            self.equation(r'\lambda_T\to2\lambda_T,\ q\ \mathrm{fixed}:\quad n_e^{\rm new}(\mathbf r)=\tfrac14 n_e^{\rm old}(\mathbf r/2)',31,GOLD),
            self.prose('Twice the length scale: twice the width and length, one quarter the reference amplitude.',24))
        self.finish()

    def shape_terms(self):
        # Source: DO Part 2, Eqs. 45--48; standalone implementation: meteor_rcs/do_density.py
        self.start_slide('The kinetic solution sets the shape, not q alone',
            'In the implemented analytic approximation, f1 and f2 depend on s and abs(mu); '
            'f3 is evaluated by one-dimensional quadrature. The term mu*f2 changes sign across z=0. '
            'This creates front/back asymmetry without different axial and radial coordinate scales.')
        self.stack(self.equation(r'F_{\rm DO}(\zeta,\eta)=\frac{|\mu|f_1+\mu f_2+f_3}{s}',47,BLUE),
            self.equation(r's=\sqrt{\zeta^2+\eta^2},\qquad\mu=\zeta/s',33),
            self.equation(r'f_1(s,|\mu|),f_2(s):\quad\text{analytic collision-integral terms}',28),
            self.equation(r'f_3(s,|\mu|):\quad\text{one numerical integral over collision geometry}',28),
            self.equation(r'\mu f_2:\quad\text{odd term giving different upstream and downstream densities}',26,GOLD),
            self.prose('Near-head, single-collision model; it does not describe the mature multi-collision trail.',24))
        self.finish()

    def density_3d(self):
        # Source: Axisymmetric reconstruction of the DO solution; ring is schematic geometry
        self.start_slide('Rotate the axisymmetric shape to reconstruct 3D density',
            'The meridional slice supplies the density at any point by its axial distance z and transverse distance r_perp. '
            'Rotation about the DO z axis changes azimuth, not density. This geometric reconstruction adds no fit parameter. '
            'The illustrated ring is a set of evaluation points, not a plasma boundary or an isodensity contour.')
        center=np.array([2.1,-.15,0]);r=1.2
        axis=Arrow([-1.2,-.15,0],[5.6,-.15,0],buff=0,color=MUTED)
        ring=Ellipse(width=.85,height=2*r,color=BLUE).move_to(center)
        meridian=Line(center,center+UP*r,color=GREEN)
        grain=Dot([-.8,-.15,0],color=GOLD,radius=.1)
        self.play(GrowArrow(axis),FadeIn(grain),Create(meridian),Create(ring))
        dots=VGroup(*[Dot(center+np.array([.425*np.sin(phi),r*np.cos(phi),0]),color=GREEN,radius=.055)
            for phi in np.linspace(0,TAU,12,endpoint=False)])
        self.play(LaggedStart(*[FadeIn(p) for p in dots],lag_ratio=.08))
        self.add(self.equation(r'z',28).next_to(axis,RIGHT),self.equation(r'r_\perp',28,GREEN).next_to(meridian,LEFT),
            self.prose('Equal density at every azimuth',24).move_to([2.2,-1.8,0]))
        formula=self.equation(r'\boxed{n_e(x,y,z)=n_\star F_{\rm DO}\!\left(\frac{z}{\lambda_T},\frac{\sqrt{x^2+y^2}}{\lambda_T}\right)}',41,BLUE).shift(UP*2.25)
        self.play(Write(formula))
        items=VGroup(self.equation(r'q\text{ sets production}',24,GREEN),self.equation(r'\lambda_T\text{ sets size}',24,BLUE),
            self.equation(r'F_{\rm DO}\text{ sets morphology}',24)).arrange(DOWN,buff=.4).move_to([-3.8,.1,0])
        self.play(FadeIn(items))
        self.play(FadeIn(self.prose('Rotate this 3D distribution to the radar aspect before sampling the FDTD mesh.',25).shift(DOWN*2.55)))
        self.finish()

    def normalization(self):
        # Source: DO Part 1 surface flux; DO Part 2 Eqs. 45--48; derivation in
        # fdtd/memos/ablation_to_rcs.tex
        self.start_slide('Eliminate the unknown surface neutral density',
            'Let n0 denote the surface ablated-neutral density and m_A the mean atmospheric particle mass. '
            'Use the isotropic differential ionization cross section and DO surface flux, then substitute production per path.')
        self.stack(self.equation(r'J_{R0}=\sqrt{2/\pi}\,n_0V_T,\qquad \dot N_{\rm vap}=4\pi a^2J_{R0}',32),
            self.equation(r'G_{\rm ion}=\frac{\beta_{\rm Si}\sigma_c}{4\pi},\qquad m_A=\rho_A/n_A',32),
            self.equation(r'n_\star=\frac{\dot N_{\rm vap}n_A\sigma_c\beta_{\rm Si}(1+m_{\rm Si}/m_A)}{2\sqrt{6\pi}\,V_T\lambda_T}',34),
            self.equation(r'\boxed{n_\star=\frac{q(1+m_{\rm Si}/m_A)}{2\sqrt{6\pi}\,\lambda_T^2}}\qquad[\mathrm{m^{-3}}]',42,BLUE),
            self.equation(r'q\text{ supplies source amplitude};\quad\lambda_T\text{ supplies spatial scale}',25,MUTED))
        self.finish()

    def density(self):
        # Source: DO Part 2, doi:10.1002/2017JA023963; meteor_rcs/do_density.py
        self.start_slide('Dimant--Oppenheim supplies the spatial shape',
            'F is computed from DO Eqs. 45--48. In dimensionless variables s=R/lambda_T and mu=z/R, '
            'F=(abs(mu)f1+mu f2+f3)/s; f1 and f2 are analytic, f3 uses one-dimensional quadrature. '
            'The quasi-neutral approximation identifies ion density with electron density.')
        self.play(FadeIn(self.image('density.png',7.8).move_to([-2.4,.1,0])))
        items=VGroup(self.equation(r'n_e=n_\star F_{\rm DO}',36,BLUE),
            self.equation(r'F_{\rm DO}=F(z/\lambda_T,r_\perp/\lambda_T)',27),
            self.equation(r'n_e\simeq n_i',30),
            self.prose('Near grain: 1/R',25),self.prose('Far downstream: 1/R squared',23),
            self.equation(r'n_\star:\ \text{scale, not peak density}',22,MUTED),
            self.prose('The ideal origin is singular.',23,RED)).arrange(DOWN,buff=.33).move_to([4.15,.15,0])
        for item in items:self.play(FadeIn(item),run_time=.3)
        self.finish()

    def worked_example(self):
        # Source: Exact archived sample: meteor_rcs/inputs.h5; derived values: meteor_rcs/data.h5
        self.start_slide('A numerical check of the interfaces',
            'These are input-chain values from one archived native ablation sample, not a new RCS prediction. '
            'Numerical validation independently reconstructs the source normalization from the archived atmosphere.')
        s=self.sample
        self.stack(self.equation(r'h=%.3f\ \mathrm{km},\quad v=%.3f\ \mathrm{km\,s^{-1}}'%(s['sample_altitude_km'],s['sample_speed_kms']),32),
            self.equation(r'-\dot m=%.3f\times10^{-9}\ \mathrm{kg\,s^{-1}},\quad\beta_{\rm Si}=%.4f'%(s['sample_loss_kg_s']*1e9,s['sample_beta']),33,GOLD),
            self.equation(r'\dot N_e=%.3f\times10^{16}\ \mathrm{s^{-1}}\quad\Longrightarrow\quad q=%.3f\times10^{11}\ \mathrm{m^{-1}}'%(self.production/1e16,self.q/1e11),34,GREEN),
            self.equation(r'\lambda_T=%.4f\ \mathrm m\quad\Longrightarrow\quad n_\star=%.3f\times10^{12}\ \mathrm{m^{-3}}'%(s['sample_lambda_m'],self.nstar/1e12),36,BLUE),
            self.prose('The next step must solve how the radar field penetrates this plasma.',27))
        self.finish()

    def mesh(self):
        # Source: Input construction: fdtd/examples/maarsy_rcs.py; all mesh geometry here is
        # schematic
        self.start_slide('Turn a singular continuum model into finite solver inputs',
            'The implementation caps density at a grain-radius value, tapers the support, rotates the axis to the radar aspect, '
            'and uses eight-point Gauss averages around the electric-field edges. This regularizes unresolved scales.')
        grid=VGroup(*[Line([-5.8+j*.4,-1.8,0],[-5.8+j*.4,1.8,0],stroke_width=1,color=MUTED) for j in range(10)],
                    *[Line([-5.8,-1.8+j*.4,0],[-2.2,-1.8+j*.4,0],stroke_width=1,color=MUTED) for j in range(10)])
        support=Circle(1.35,color=BLUE,fill_opacity=.12).move_to([-4,0,0])
        pml=Rectangle(width=4.3,height=4.3,color=RED,stroke_width=8,stroke_opacity=.45).move_to([-4,0,0])
        self.play(Create(grid),FadeIn(support),Create(pml))
        sites=VGroup(*[Dot([-5.6+.4*j,.2,0],radius=.045,color=GREEN) for j in range(9)])
        self.play(LaggedStart(*[FadeIn(d) for d in sites],lag_ratio=.08))
        items=VGroup(self.equation(r'n_{\rm input}=w_{\rm cut}\min(n_\star F,n_{\rm cap})',30),
            self.prose('Fixed Cartesian Yee mesh',26,FG),self.prose('Green: electric-field sample edges',22,GREEN),
            self.prose('Red: absorbing CPML boundary',22,RED),
            self.prose('Check core cap, support, spacing, and box size.',22),
            self.prose('Density is frozen for each EM calculation.',24)).arrange(DOWN,buff=.36).move_to([2.65,0,0])
        for item in items:self.play(FadeIn(item),run_time=.3)
        self.finish()

    def plasma_response(self):
        # Source: Marshall--Close (2015), doi:10.1002/2015JA021238; independent current update:
        # fdtd/src/main.rs
        self.start_slide('Electron inertia and collisions determine the current',
            'Cold electron-fluid current driven by the total electric field. Ions provide a stationary neutralizing background '
            'on the radar timescale. In the scalar B=0 limit, the dielectric uses exp(-i omega t).')
        self.stack(self.equation(r'\omega_p^2=\frac{n_e e^2}{\epsilon_0m_e},\qquad\boldsymbol\Omega_e=\frac{e\mathbf B_0}{m_e}',36),
            self.equation(r'\partial_t\mathbf J+\nu_{en}\mathbf J+\mathbf J\times\boldsymbol\Omega_e=\epsilon_0\omega_p^2\mathbf E_{\rm total}',37,GREEN),
            self.equation(r'B_0=0:\quad\epsilon_r(\omega)=1-\frac{\omega_p^2}{\omega(\omega+i\nu_{en})}',36),
            self.equation(r'\nu_{en}:\ \text{electron momentum-loss rate, distinct from heavy-particle collision rate}',24,MUTED),
            self.equation(r'\text{Example input: }\nu_{en}=10^7\ \mathrm{s^{-1}}\text{, assumed constant}',25,MUTED))
        self.finish()

    def maxwell(self):
        # Source: Native Rust Yee/CPML solver: fdtd/src/main.rs; MPI domain slabs and Rayon threads
        self.start_slide('Advance scattered fields and self-consistent current',
            'The native solver uses analytic incident fields, Yee staggered finite differences and CPML. '
            'The total field drives the current. The current then modifies scattered fields, including field feedback.')
        self.stack(self.equation(r'\mathbf E_{\rm total}=\mathbf E_{\rm inc}+\mathbf E_s',36,BLUE),
            self.equation(r'\mathbf H_s^{n+1/2}=\mathbf H_s^{n-1/2}-\frac{\Delta t}{\mu_0}\nabla_h\times\mathbf E_s^n',34),
            self.equation(r'\mathbf J^{n+1/2}\ \longleftarrow\ \text{cold-plasma response to }\mathbf E_{\rm total}^n',31,GREEN),
            self.equation(r'\mathbf E_s^{n+1}=\mathbf E_s^n+\frac{\Delta t}{\epsilon_0}(\nabla_h\times\mathbf H_s^{n+1/2}-\mathbf J^{n+1/2})',33),
            self.equation(r'\Delta t\leq\min\!\left[\frac{\Delta x}{2c},\frac{0.7}{\sqrt{\omega_{p,\max}^2+|\boldsymbol\Omega_e|^2}}\right]',29),
            self.prose('Resolve vacuum wavelength and the shorter plasma response scales.',24))
        self.finish()

    def response_animation(self):
        # Source: Schematic animation: meteor_head_rcs.py; harmonic current response, exp(-i omega
        # t)
        self.start_slide('The induced current is the radiating source',
            'Schematic only: illustrates a phase-lagged cold-plasma current and a backward wave. '
            'These curves are not exported FDTD fields and no quantitative amplitude is implied.')
        phase=ValueTracker(0)
        sphere=Circle(1.05,color=BLUE,fill_opacity=.15).move_to([1,0,0])
        incoming=always_redraw(lambda:ParametricFunction(lambda s:np.array([s,1+.32*np.cos(2.2*s-phase.get_value()),0]),t_range=[-5.6,-.3],color=BLUE))
        outgoing=always_redraw(lambda:ParametricFunction(lambda s:np.array([s,-1+.22*np.cos(2.2*s+phase.get_value()),0]),t_range=[-5.6,-.3],color=GOLD))
        current=always_redraw(lambda:Arrow([1,0,0],[1,.04+.85*(.3*np.cos(phase.get_value())+np.sin(phase.get_value()))/np.sqrt(1.09),0],buff=0,color=GREEN,max_tip_length_to_length_ratio=.2))
        self.add(sphere,incoming,outgoing,current)
        self.add(self.prose('Incident field',24,BLUE).move_to([-3,2,0]),self.prose('Scattered field',24,GOLD).move_to([-3,-2,0]),
                 self.equation(r'\mathbf J(t)',32,GREEN).move_to([3,.5,0]))
        self.play(phase.animate.set_value(6*PI),run_time=3.2,rate_func=linear)
        for item in [incoming,outgoing,current]:item.clear_updaters()
        self.play(FadeIn(self.prose('Total field drives J; J changes the field that drives it.',28,FG).shift(DOWN*2.7)))
        self.finish()

    def far_field(self):
        # Source: Far-zone induced-current integral: fdtd/src/main.rs; E-hat is the phasor at the
        # radar frequency
        self.start_slide('Fourier transform the current, then sum radiation',
            'The Fourier sign is consistent with exp(-i omega t). Spatial phase and transverse projection are required. '
            'Because J came from the Maxwell solve, this radiation integral contains field feedback rather than a Born density sum.')
        self.stack(self.equation(r'\widehat{\mathbf J}(\mathbf r,\omega_0)\ \propto\ \int\mathbf J(\mathbf r,t)e^{+i\omega_0t}\,dt',35,GREEN),
            self.equation(r'\mathbf A(\widehat{\mathbf n})=(\mathbf I-\widehat{\mathbf n}\widehat{\mathbf n}^{\mathsf T})\int\widehat{\mathbf J}(\mathbf r)e^{-ik\widehat{\mathbf n}\cdot\mathbf r}\,d^3r',35),
            self.equation(r'\widehat{\mathbf n}:\ \text{viewing direction};\quad k=\omega_0/c;\quad Z_0:\ \text{vacuum impedance}',24,MUTED),
            self.equation(r'\widehat{\mathbf E}_s(R\widehat{\mathbf n})\simeq\frac{ikZ_0e^{ikR}}{4\pi R}\,\mathbf A(\widehat{\mathbf n})',40,GOLD),
            self.prose('Current amplitudes interfere; density alone is not the radiation amplitude.',26))
        self.finish()

    def rcs(self):
        # Source: RCS convention and implementation: fdtd/src/main.rs
        self.start_slide('RCS is the echo normalized to incident intensity',
            'Receive polarization e_rx is a complex unit vector. The dagger is a conjugate transpose. '
            'The range factors cancel in the far-zone definition. A consistent temporal Fourier normalization cancels as well.')
        self.stack(self.equation(r'\sigma_{\rm rx}=\lim_{R\to\infty}4\pi R^2\frac{|\mathbf e_{\rm rx}^{\dagger}\widehat{\mathbf E}_s|^2}{|\widehat{\mathbf E}_{\rm inc}|^2}',40),
            self.equation(r'\boxed{\sigma_{\rm rx}=\frac{k^2Z_0^2}{4\pi|\widehat{\mathbf E}_{\rm inc}|^2}|\mathbf e_{\rm rx}^{\dagger}\mathbf A|^2}',45,GOLD),
            self.equation(r'[\sigma]=\mathrm{m^2},\qquad\sigma_{\rm dBsm}=10\log_{10}(\sigma/1\ \mathrm{m^2})',34),
            self.equation(r'\text{The solver transforms }Z_0\mathbf J\text{, so its equivalent prefactor omits }Z_0^2.',24,MUTED))
        self.finish()

    def polarization(self):
        # Source: Polarization basis and current phases: fdtd/src/main.rs
        self.start_slide('Specify the monostatic polarization channel',
            'Incident propagation is +x and monostatic observation is -x. The following backward RHCP analyzer is the explicit '
            'solver convention; handedness must be referred to the propagation direction.')
        self.stack(self.equation(r'\widehat{\mathbf n}_{\rm back}=-\widehat{\mathbf k}_{\rm inc}=-\widehat{\mathbf x}',36),
            self.equation(r'\mathbf e_{\mathrm{rx},R}=\frac{i\widehat{\mathbf y}+\widehat{\mathbf z}}{\sqrt2},\qquad \mathbf e_{\mathrm{rx},R}^{\dagger}\mathbf A=\frac{A_z-iA_y}{\sqrt2}',38,BLUE),
            self.equation(r'\sigma_R\ \propto\ \frac{|A_z-iA_y|^2}{2}\quad\neq\quad |A_y|^2+|A_z|^2',38,GOLD),
            self.prose('MAARSY example: LHCP transmit, backward RHCP receive.',29,FG),
            self.prose('Keep radar aspect and receive polarization explicit in every comparison.',25))
        self.finish()

    def limits(self):
        # Source: Independent benchmark implementation: fdtd/examples/sphere_scattering.py and
        # tests/validate_sphere_scattering.py
        self.start_slide('Check the solver against classical scattering',
            'For a homogeneous nonmagnetic sphere at B=0, compare angular radar cross sections with exact Mie theory. '
            'The displayed electric-dipole Rayleigh formula requires ka and abs(sqrt(epsilon_r))ka both small.')
        self.stack(self.equation(r'\text{Homogeneous sphere: radius }a_s\text{; scalar complex permittivity }\epsilon_r',27,MUTED),
            self.equation(r'ka_s\ll1,\quad|\sqrt{\epsilon_r}|ka_s\ll1:\qquad\sigma_{\rm back}=4\pi k^4a_s^6\left|\frac{\epsilon_r-1}{\epsilon_r+2}\right|^2',37,GREEN),
            self.prose('Compare monostatic RCS with monostatic RCS, not total scattering cross section.',25),
            self.prose('Use exact Mie outside this limit; halve mesh spacing at fixed geometry.',27,FG),
            self.prose('A q-squared law needs weak scattering and fixed spatial shape.',27,GOLD))
        self.finish()

    def convergence(self):
        # Source: Archived native cutoff study: fdtd/outputs/cutoff_d500_v23; exact values bundled
        # in inputs.h5
        self.start_slide('The plasma cutoff can dominate the RCS error',
            'Completed native FDTD results for a 500-micrometre initial grain at 23.16 km/s, frozen altitude 92.5 km. '
            'Grid spacing is 2.80 cm. Widest-box duplicates are retained. No result is shown for the stopped 512-length case.')
        self.play(FadeIn(self.image('cutoff.png',9.0).shift(UP*.15)))
        self.play(FadeIn(self.prose('6.12 to 9.19 m support: 0.19 dB change. Universal cutoff remains unvalidated.',24,RED).shift(DOWN*2.65)))
        self.finish()

    def detection(self):
        # Source: MAARSY detection geometry: Huyghebaert et al. (2026), doi:10.5194/amt-19-4277-2026
        self.start_slide('From RCS to detection: include the radar beam',
            'The radar equation turns RCS into received power. A meteor may already be ablating before entering the beam. '
            'Large zenith angles shift ablation upward, while delayed beam entry shifts first detection downward.')
        self.stack(self.equation(r'P_r=\frac{P_tG_t(\theta)G_r(\theta)\lambda_0^2\sigma_{\rm rx}}{(4\pi)^3R^4}',41,GOLD),
            self.prose('R: radar range; theta: position within beam; gains and threshold matter.',25),
            self.equation(r'h_{\rm first\ detection}\neq h_{\max(-\dot m)}\neq h_{\max\sigma}',38,RED),
            self.prose('Two opposite altitude effects:',29,FG),
            self.prose('Oblique entry: ablation occurs higher. Beam entry: detection can occur later.',26),
            self.prose('A height correction must include selection by the beam.',28,BLUE))
        self.finish()

    def inference(self):
        # Source: Physical inference: calibrated RCS + trajectory + validated ablation and
        # scattering model
        self.start_slide('Use the forward model to constrain the meteoroid',
            'Fit the trajectory and a calibrated echo history jointly. Initial mass, bulk density and material parameters '
            'are coupled to ionization efficiency, collision frequency, plasma shape and beam position. '
            'One RCS value does not uniquely determine a meteoroid mass. Use multiple times, geometry and, where available, frequencies.')
        self.stack(self.equation(r'\mathbf d=\{h(t),v(t),\sigma_{\rm rx}(t),\text{viewing geometry}\}',34,BLUE),
            self.equation(r'\boldsymbol\theta=\{m_0,\rho_M,\text{material},\beta,\nu_{en},\ldots\}',33,GOLD),
            self.equation(r'\boldsymbol\theta\ \longrightarrow\ (-\dot m,q,n_e)\ \longrightarrow\ \sigma_{\rm model}(t;\boldsymbol\theta)',35),
            self.equation(r'p(\boldsymbol\theta\mid\mathbf d)\propto p(\mathbf d\mid\boldsymbol\theta)\,p(\boldsymbol\theta)',38,GREEN),
            self.prose('Compare the predicted and measured echo histories; report parameter uncertainty.',26),
            self.prose('A single RCS value does not uniquely determine mass.',27,RED))
        self.finish()

    def references(self):
        # Source: Source and data: github.com/jvierine/manimations | solver:
        # github.com/jvierine/fdtd
        self.start_slide('References',
            'Equations are drawn from the cited primary sources. The chained calculation is an independent implementation '
            'with stated one-species assumptions and unresolved cutoff convergence. All figure inputs are bundled as HDF5.')
        entries=[('Solar radiation: Burns, Lamy and Soter (1979)','doi:10.1016/0019-1035(79)90050-2'),
                 ('Rarefied entry: Bariselli et al. (2020)','doi:10.1093/mnras/stz3559'),
                 ('Free molecular sphere drag: Loth et al. (2021)','doi:10.2514/1.J060153'),
                 ('Thermal ablation: Hill et al. (2005)','doi:10.1051/0004-6361:20053053'),
                 ('Primary Si ionization: Jones (1997)','doi:10.1093/mnras/288.4.995'),
                 ('Kinetics / density: Dimant and Oppenheim (2017)','doi:10.1002/2017JA023960 and 10.1002/2017JA023963'),
                 ('Plasma FDTD: Marshall and Close (2015)','doi:10.1002/2015JA021238'),
                 ('Head-plasma profiles: Marshall, Brown and Close (2017)','doi:10.1016/j.pss.2016.12.011')]
        rows=VGroup(*[VGroup(self.prose(title,22,FG),self.prose(doi,18,BLUE)).arrange(DOWN,buff=.08,aligned_edge=LEFT)
                      for title,doi in entries]).arrange(DOWN,buff=.2,aligned_edge=LEFT).move_to(ORIGIN)
        for row in rows:self.play(FadeIn(row),run_time=.35)
        links=[]
        for (title,doi),row in zip(entries,rows):
            dois=doi.removeprefix('doi:').split(' and ')
            for index,value in enumerate(dois):
                target=row if len(dois)==1 else row.copy().stretch(.5,0).move_to(
                    row.get_left()+row.width*(.25+.5*index)*RIGHT)
                links.append((title+(' Part '+str(index+1) if len(dois)>1 else ''),'https://doi.org/'+value,target))
        self.paper_links(links)
        self.wait(1.)
