"""Click-controlled derivation of meteor-head RCS, with archived numerical data.

conda run -n base python -m meteor_rcs.prepare_assets
conda run -n base manim-slides render -r 1920,1080 --fps 30 meteor_head_rcs.py MeteorHeadRCS
Plot provenance is kept in code comments and HDF5 metadata only.
"""
from pathlib import Path

import h5py
import numpy as np
from manim import *
from manim_slides import Slide
from planck_to_ktb import Text

ROOT = Path(__file__).resolve().parent/'meteor_rcs'
BG, FG, MUTED = '#FFFFFF', '#172333', '#596779'
BLUE, GOLD, GREEN, RED = '#245774', '#9B4825', '#267369', '#B33C3C'


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

    def image(self, name, width=9.5):
        return ImageMobject(ROOT/'assets'/name).set(width=width)

    def construct(self):
        self.story_release()
        self.story_orbits()
        self.story_final_laps()
        self.story_entry()
        self.story_evaporation()
        self.story_collision()
        self.story_cloud()
        self.opening()
        self.geometry()
        self.energy()
        self.mass_loss()
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
        self.play(FadeIn(self.prose('P--R drag removes angular momentum; planetary gravity perturbs the orbit.',25,FG).shift(DOWN*2.8)))
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
        self.add(self.prose('Meteoroid',25,GREEN).move_to([-3.6,1.5,0]),self.prose('Earth',25,BLUE).move_to([3.2,-1.2,0]))
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
        grain=self.grain(np.array([-1.5,0,0]),.65).set_color(RED)
        self.play(FadeIn(grain),FadeIn(self.prose('Grain rest frame',25).move_to([-4,2,0])))
        directions=np.linspace(-PI,PI,16,endpoint=False)
        atoms=VGroup(*[Dot(grain.get_center()+.65*np.array([np.cos(a),np.sin(a),0]),radius=.045,color=GOLD) for a in directions])
        self.add(atoms)
        self.play(*[atom.animate.shift(1.4*np.array([np.cos(a),np.sin(a),0])) for atom,a in zip(atoms,directions)],
                  grain.animate.scale(.85),run_time=1.8)
        self.play(FadeIn(self.prose('Hot solid or melt',28,RED).move_to([3,1,0])),
                  FadeIn(self.prose('Neutral vapour',28,GOLD).move_to([3,.2,0])))
        self.play(FadeIn(self.prose('A hotter surface releases atoms much faster.',31,FG).shift(DOWN*2.5)))
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
        # Source: Schematic head plasma and radar: meteor_head_rcs.py | MAARSY carrier 53.5 MHz
        self.start_slide('MAARSY sees the plasma surrounding the grain',
            'The ion/electron cloud is much larger than the solid particle. A high-power large-aperture radar probes the '
            'induced plasma current, provided the echo exceeds its detection threshold. The cloud drawing is schematic; '
            'its quantitative kinetic shape is derived later.')
        rng=np.random.default_rng(2017)
        center=np.array([-2.,.35,0])
        grain=Dot(center,radius=.035,color=GOLD)
        electrons=VGroup(*[Dot(center+np.array([rng.normal(.45,.75),rng.normal(0,.55),0]),radius=.018,color=GREEN,fill_opacity=.6) for _ in range(140)])
        radar=VGroup(Arc(radius=.55,start_angle=-PI*.1,angle=PI*1.2,color=FG),Line([0,-.2,0],[0,-.9,0],color=FG)).move_to([4,-1,0])
        self.play(FadeIn(grain),LaggedStart(*[FadeIn(p) for p in electrons],lag_ratio=.006),FadeIn(radar))
        beam=Polygon(radar.get_center(),[-3,1.9,0],[-3,-1.1,0],color=BLUE,fill_opacity=.07,stroke_width=1)
        self.play(FadeIn(beam))
        self.play(GrowArrow(Arrow([3.4,-.7,0],[-.5,.1,0],color=BLUE)),
                  GrowArrow(Arrow([-.4,.5,0],[3.4,-.3,0],color=GOLD)))
        self.add(self.prose('MAARSY',27,FG).move_to([4,-2,0]),self.prose('Incident wave',23,BLUE).move_to([1.6,1.5,0]),
                 self.prose('Head echo',23,GOLD).move_to([1.7,.7,0]))
        self.play(Write(self.equation(r'D_{\rm grain}\sim100\ \mu\mathrm m\qquad\ll\qquad\text{plasma scale}',35,GREEN).shift(DOWN*2.65)))
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
        definitions=self.equation(r'h\ [\mathrm m],\quad v\ [\mathrm{m\,s^{-1}}],\quad m\ [\mathrm{kg}],\quad T_M\ [\mathrm K]',31).shift(UP*2)
        frequency=self.equation(r'f_0=53.5\ \mathrm{MHz},\quad \lambda_0=c/f_0=5.60\ \mathrm m,\quad T_0=18.7\ \mathrm{ns}',29).shift(DOWN*2.35)
        self.play(Write(definitions),Write(frequency));self.finish()

    def energy(self):
        # Source: Hill et al. (2005), doi:10.1051/0004-6361:20053053; fdtd/src/bin/meteor-
        # ablation.rs
        self.start_slide('Heating competes with radiation and evaporation',
            'A spherical isothermal grain has area A=pi a squared. Introduce all energy terms before using the mass-loss history.')
        self.stack(self.equation(r'a=\left(\frac{3m}{4\pi\rho_M}\right)^{1/3},\qquad A=\pi a^2',34),
            self.equation(r'a:\ \text{grain radius};\quad\rho_M:\ \text{bulk density};\quad\rho_A:\ \text{atmospheric mass density}',25,MUTED),
            self.equation(r'mc_p\dot T_M=\tfrac12\Lambda A\rho_Av^3-4A\epsilon\sigma_{\rm SB}(T_M^4-T_A^4)-L(-\dot m)',34),
            self.prose('Heating  |  radiative cooling  |  latent heat carried away',27,GOLD),
            self.equation(r'c_p:\ \text{heat capacity};\quad\Lambda:\ \text{heat transfer};\quad\epsilon:\ \text{emissivity};\quad L:\ \text{latent heat}',23,MUTED))
        self.finish()

    def mass_loss(self):
        # Source: Thermal model: MetAblate material law; independent Rust integration in fdtd
        self.start_slide('Langmuir evaporation closes the ablation equations',
            'Evaporation uses the vapor pressure law. The 50-u effective vapor mass in the thermal model is distinct from '
            'the 28.085-u Si proxy introduced for electron production. Entry chi is measured from vertical.')
        self.stack(self.equation(r'-\dot m=4A\,p_{\rm vap}(T_M)\sqrt{\frac{m_{\rm vap}}{2\pi k_BT_M}}',41,GOLD),
            self.equation(r'p_{\rm vap}=0.1\,10^{10.6-13500\,\mathrm K/T_M}\ \mathrm{Pa},\qquad m_{\rm vap}=50\,u',29),
            self.equation(r'\dot h=-v\cos\chi,\qquad \dot v=-\Gamma A\rho_Av^2/m+g\cos\chi',35),
            self.prose('chi: entry zenith angle; Gamma: drag coefficient; g: gravity',24),
            self.equation(r'\text{Integrate }h,v,m,T_M\text{ through an MSIS atmosphere.}',29))
        self.finish()

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
        entries=[('Thermal ablation: Hill et al. (2005)','doi:10.1051/0004-6361:20053053'),
                 ('Primary Si ionization: Jones (1997)','doi:10.1093/mnras/288.4.995'),
                 ('Kinetics / density: Dimant and Oppenheim (2017)','doi:10.1002/2017JA023960 and 10.1002/2017JA023963'),
                 ('Plasma FDTD: Marshall and Close (2015)','doi:10.1002/2015JA021238'),
                 ('Head-plasma profiles: Marshall, Brown and Close (2017)','doi:10.1016/j.pss.2016.12.011')]
        rows=VGroup(*[VGroup(self.prose(title,25,FG),self.prose(doi,21,BLUE)).arrange(DOWN,buff=.08,aligned_edge=LEFT)
                      for title,doi in entries]).arrange(DOWN,buff=.28,aligned_edge=LEFT).move_to(ORIGIN)
        for row in rows:self.play(FadeIn(row),run_time=.35)
        self.wait(1.)
