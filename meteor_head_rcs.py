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
        self.title_slide()
        self.lecture_map()
        self.section_card('1. The journey to Earth','How does comet dust reach an Earth-crossing orbit?')
        self.story_release()
        self.story_pr_drag()
        self.pr_drag_derivation()
        self.solar_radiation_pressure()
        self.story_orbits()
        self.dust_collision_outcomes()
        self.dust_collision_energy()
        self.dust_relative_velocity()
        self.dust_collision_rate()
        self.dust_collision_population()
        self.dust_collision_survival()
        self.grun_collisions()
        self.later_collision_models()
        self.collisional_grooming()
        self.story_final_laps()
        self.interlude('The grain has a long commute. You get a short break.',
            ['Drink some water.','Call your mom.','Next: what happens when the atmosphere gets in the way.'])
        self.section_card('2. Atmospheric entry and ablation','Where do the heat and evaporated atoms come from?')
        self.story_entry()
        self.story_evaporation()
        self.grain_geometry()
        self.atmospheric_heating()
        self.free_molecular_drag()
        self.cooling_terms()
        self.energy()
        self.mass_loss()
        self.trajectory_equations()
        self.ablation_profiles()
        self.trajectory()
        self.interlude('The meteor is losing mass. You can gain a snack.',
            ['Go for a short run.','Eat a Snickers bar.','Next: why the escaped atoms become visible to radar.'])
        self.section_card('3. The plasma around the meteoroid','How do evaporated atoms make a three-dimensional electron cloud?')
        self.story_cloud()
        self.story_collision()
        self.geometry()
        self.ionization()
        self.line_density()
        self.source_terms()
        self.do_introduction()
        self.isotropic_ionization()
        self.density_amplitude_introduction()
        self.do_gallery_animation()
        self.do_parameters()
        self.collision_frames()
        self.collision_cross_section()
        self.collision_length()
        self.velocity_dependence()
        self.mean_free_path_coordinates()
        self.normalization()
        self.normalization_meaning()
        self.density()
        self.shape_terms()
        self.density_3d()
        self.worked_example()
        self.interlude('The plasma has a shape. The radar still wants a number.',
            ['Stretch your legs.','Tickle somebody who consents.','Next: turn the electron cloud into a measurable echo.'])
        self.section_card('4. From plasma to a radar measurement','How much power returns, and what can it tell us about the grain?')
        self.opening()
        self.yee_mesh()
        self.cpml_boundary()
        self.mesh()
        self.plasma_response()
        self.maxwell()
        self.response_animation()
        self.far_field()
        self.rcs()
        self.polarization()
        self.rayleigh_geometry()
        self.limits()
        self.radar_equation()
        self.radar_worked_examples()
        self.references()

    def lecture_map(self):
        self.start_slide('One grain, four physical questions',
            'Roadmap: dynamics brings dust to Earth; atmospheric entry supplies evaporated atoms; '
            'ionization and kinetic transport make plasma; electromagnetic scattering and the radar equation make an observation.')
        entries=[('1. Space','Radiation forces, planetary perturbations, and collisions',GOLD),
            ('2. Atmosphere','Heating, evaporation, and the evolving grain',RED),
            ('3. Plasma','Ionization, collision lengths, and electron density',GREEN),
            ('4. Radar','Induced current, scattering, and received echo power',BLUE)]
        blocks=VGroup(*[VGroup(self.prose(title,31,color),self.prose(desc,26,FG)).arrange(DOWN,buff=.13,aligned_edge=LEFT)
            for title,desc,color in entries]).arrange(DOWN,buff=.38,aligned_edge=LEFT).move_to(ORIGIN)
        for block in blocks:self.play(FadeIn(block))
        self.finish()

    def section_card(self,title,question):
        self.start_slide(title,question)
        self.play(FadeIn(self.prose(question,34,FG).shift(UP*.6)))
        line=Line(LEFT*4.8,RIGHT*4.8,color=BLUE).shift(DOWN*.7)
        self.play(Create(line));self.finish()

    def interlude(self,title,lines):
        self.start_slide('Interlude',title)
        self.play(FadeIn(self.prose(title,32,BLUE).shift(UP*1.8)))
        group=VGroup(*[self.prose(line,29,FG if i<2 else MUTED) for i,line in enumerate(lines)]).arrange(DOWN,buff=.55).shift(DOWN*.2)
        for item in group:self.play(FadeIn(item))
        self.finish()

    def title_slide(self):
        self.start_slide('Meteor head echo radar cross section',
            'Juha Vierinen. Ablation, formation of the near-meteoroid plasma, and electromagnetic scattering.')
        subtitle=self.prose('Ablation, plasma formation, and electromagnetic scattering',30,FG).shift(UP*1.8)
        author=self.prose('Juha Vierinen',36,BLUE).shift(UP*.85)
        self.play(FadeIn(subtitle),FadeIn(author))
        rng=np.random.default_rng(13)
        center=np.array([0,-1.25,0])
        plasma=VGroup(*[Dot(center+[rng.normal(.3,.9),rng.normal(0,.45),0],
            radius=.025,color=GREEN,fill_opacity=.65) for _ in range(100)])
        grain=self.grain(center,.08)
        self.play(FadeIn(plasma),FadeIn(grain))
        self.play(FadeIn(self.prose('The solid grain creates the plasma that scatters the radar wave.',27).shift(DOWN*2.8)))
        self.finish()

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

    def pr_drag_derivation(self):
        self.start_slide('Why is the Poynting--Robertson drag proportional to velocity?',
            'Ideal absorbing grain, isotropic thermal emission in its rest frame, and radiative equilibrium. '
            'For tangential motion, incident sunlight has no tangential momentum in the Sun frame. '
            'A Lorentz boost of the total emitted photon momentum gives outgoing tangential momentum per unit time. '
            'At first order in v/c, rest-frame emitted power equals absorbed power in this balance.')
        self.play(FadeIn(self.prose('Isotropic emission has zero net momentum in the grain frame.',28,FG).shift(UP*2.35)))
        self.play(Write(self.equation(r'\sum p_t^\prime=0,\qquad E^\prime=P_{\rm em}^\prime\,dt^\prime',36).shift(UP*1.3)))
        self.play(Write(self.equation(r'\text{Sun frame: }\quad\sum p_t=\gamma\frac{E^\prime v_t}{c^2},\qquad dt=\gamma\,dt^\prime',35,BLUE).shift(UP*.1)))
        self.play(Write(self.equation(r'\dot p_{t,\rm out}=\frac{P_{\rm em}^\prime v_t}{c^2}\simeq\frac{P_{\rm abs}v_t}{c^2}',35,GREEN).shift(DOWN*1.05)))
        self.play(Write(self.equation(r'\boxed{\mathbf F_{\mathrm{PR},t}=-\frac{P_{\rm abs}}{c^2}\mathbf v_t}',40,GOLD).shift(DOWN*2.2)))
        self.play(FadeIn(self.equation(r'P_{\rm em}^\prime,P_{\rm abs}:\ \mathrm W;\quad\gamma=(1-v^2/c^2)^{-1/2};\quad p_t:\ \text{tangential photon momentum}',22,MUTED).shift(DOWN*3.25)))
        self.citation('Burns, Lamy and Soter (1979), solar radiation forces','https://doi.org/10.1016/0019-1035(79)90050-2')
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


    def dust_collision_outcomes(self):
        # Solid-grain impacts in interplanetary space, not the atomic collisions
        # used later to derive the Dimant--Oppenheim plasma distribution.
        self.start_slide('Space is dilute. The grain can still hit another grain.',
            'Solid meteoroid--meteoroid impacts can crater, erode or fragment a target; energetic impacts '
            'can also melt or vaporize part of the material. These are schematic outcomes, not a computed '
            'impact experiment. Slow collisions can stick, depending on material and speed; a hypervelocity '
            'encounter should not be illustrated as two grains gently merging.')
        self.play(FadeIn(self.prose('An impact can remove a little material---or destroy the original grain.',29,FG).shift(UP*2.5)))
        rng=np.random.default_rng(833)
        for x,title,outcome,color in [
            (-4.3,'Small damage','A crater and some ejecta',GREEN),
            (0,'Fragmentation','Several surviving pieces',GOLD),
            (4.3,'Catastrophic breakup','The original grain is lost',RED)]:
            center=np.array([x,.4,0])
            target=self.grain(center,.46)
            projectile=Dot(center+[-1.4,.7,0],radius=.065,color=BLUE)
            label=self.prose(title,26,color).move_to([x,1.65,0])
            caption=self.prose(outcome,22,FG)
            if caption.width>3.9:caption.scale_to_fit_width(3.9)
            caption.move_to([x,-1.,0])
            self.play(FadeIn(label),FadeIn(target),FadeIn(projectile),run_time=.35)
            self.play(projectile.animate.move_to(center+[-.2,.1,0]),run_time=.65)
            self.remove(projectile)
            if x<0:
                chips=VGroup(*[Dot(center,radius=.027,color=GOLD) for _ in range(6)])
                self.add(chips)
                self.play(target.animate.scale(.93),
                    *[d.animate.shift([-rng.uniform(.6,1),rng.uniform(-.35,.4),0]) for d in chips],run_time=.6)
            else:
                self.remove(target)
                fragments=VGroup(*[self.grain(center,.13 if x==0 else .075) for _ in range(7 if x==0 else 16)])
                self.add(fragments)
                self.play(*[f.animate.shift([rng.uniform(-1.25,1.25),rng.uniform(-.75,.65),0])
                    for f in fragments],run_time=.8)
            self.play(FadeIn(caption),run_time=.3)
        self.play(FadeIn(self.prose('Some impact energy becomes fracture, deformation, heat, and ejecta motion.',25).shift(DOWN*2.1)))
        self.play(FadeIn(self.prose('Fragments inherit the bulk orbit plus recoil; their new sizes change radiation forces.',25,BLUE).shift(DOWN*2.85)))
        self.citation('Grün et al. (1985): collisional balance','https://doi.org/10.1016/0019-1035(85)90121-6')
        self.finish()

    def dust_collision_energy(self):
        self.start_slide('Can a small projectile destroy a larger grain?',
            'Use the target-frame projectile kinetic energy per target mass, Q_t. This target-mass convention '
            'is appropriate when the projectile is much smaller. It is not the reduced-mass energy per combined '
            'mass. Q_D* denotes a material- and size-dependent catastrophic-disruption threshold, commonly '
            'associated with a largest remnant containing about half the original target mass. Not all available '
            'kinetic energy is deposited in the target. No universal micron-grain Q_D* is assumed here.')
        target=self.grain(np.array([-4.3,1.,0]),.55)
        projectile=Dot([-6,1,0],radius=.055,color=BLUE)
        arrow=Arrow([-5.8,1.6,0],[-4.9,1.6,0],color=BLUE,buff=0)
        self.play(FadeIn(target),FadeIn(projectile),GrowArrow(arrow))
        self.add(self.equation(r'v_{\rm rel}',27,BLUE).next_to(arrow,UP,buff=.12),
            self.equation(r'D_t',27,GOLD).next_to(target,DOWN,buff=.2),
            self.equation(r'D_p',24,BLUE).next_to(projectile,DOWN,buff=.25))
        energy=self.term_definitions([
            r'E_{\rm imp}=\tfrac12 m_p v_{\rm rel}^2\quad[\mathrm J]',
            r'Q_t=\frac{E_{\rm imp}}{m_t}=\tfrac12\frac{m_p}{m_t}v_{\rm rel}^2\quad[\mathrm{J\,kg^{-1}}]',
            r'\rho_p=\rho_t:\qquad \frac{m_p}{m_t}=\left(\frac{D_p}{D_t}\right)^3'],
            [2.25,1.25,0],32,7.4)
        for row in energy:self.play(Write(row))
        self.play(projectile.animate.move_to(target.get_center()),run_time=.75)
        self.remove(projectile)
        example=self.equation(r'D_t=100\,\mu{\rm m},\ D_p=10\,\mu{\rm m},\ v_{\rm rel}=10\,{\rm km\,s^{-1}}'
            r'\quad\Rightarrow\quad Q_t=50\,{\rm kJ\,kg^{-1}}',31,BLUE).shift(DOWN*.7)
        self.play(Write(example))
        self.play(FadeIn(self.equation(r'Q_t\gtrsim Q_D^*,\qquad Q_D^*:\ \text{disruption threshold [J/kg]}',32,RED).shift(DOWN*1.65)))
        defs=self.term_definitions([
            r'm_p,m_t:\ \text{projectile and target masses [kg]};\quad D_p,D_t:\ \text{diameters [m]}',
            r'v_{\rm rel}:\ \text{relative impact speed [m/s]};\quad \rho_p,\rho_t:\ \text{bulk densities [kg/m}^3\text{]}'],
            [0,-2.55,0],23,12.3)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('The threshold depends on size, composition, porosity, and impact geometry.',24,GOLD).shift(DOWN*3.25)))
        self.citation('Pokorný et al. (2024), impact-energy prescription','https://doi.org/10.3847/PSJ/ad2de8')
        self.finish()

    def dust_relative_velocity(self):
        self.start_slide('The orbits determine how hard the grains collide',
            'The local relative velocity is the difference of the two orbital velocity vectors. '
            'Equal-speed streams at the same radius give the simple angle formula shown here. '
            'The numerical example uses approximately circular 30 km/s streams at 1 AU; it is not a '
            'calculation of the eccentric retrograde 55P stream. Inclination can increase encounter speed '
            'while reducing time in the dense zodiacal plane. A high inclination alone does not fix a rate.')
        self.play(Write(self.equation(r'\mathbf v_{\rm rel}=\mathbf v_t-\mathbf u_p'
            r'\qquad v_{\rm rel}=|\mathbf v_{\rm rel}|',35,BLUE).shift(UP*2.35)))
        self.play(FadeIn(self.prose('Target and projectile velocities are evaluated at the same location.',25).shift(UP*1.65)))
        for x,angle,title,speed in [(-4.3,0,'Nearly parallel','0'),(0,PI/2,'Crossing','42'),(4.3,PI,'Opposite','60')]:
            center=np.array([x,-.35,0])
            vt=Arrow(center+[-.85,-.32,0],center+[.85,-.32,0],buff=0,color=GREEN)
            direction=np.array([np.cos(angle),np.sin(angle),0])
            up=Arrow(center-.85*direction+[0,.25,0],center+.85*direction+[0,.25,0],buff=0,color=GOLD)
            caption=self.prose(title,25,FG).move_to([x,1.05,0])
            result=self.equation(r'v_{\rm rel}\simeq '+speed+r'\ {\rm km/s}',27,BLUE).move_to([x,-1.35,0])
            self.play(GrowArrow(vt),GrowArrow(up),FadeIn(caption),run_time=.5)
            self.play(FadeIn(result),run_time=.3)
        self.play(Write(self.equation(r'|\mathbf v_t|=|\mathbf u_p|=v_K:\quad '
            r'v_{\rm rel}=2v_K\sin(\psi/2),\qquad v_K\simeq30\,{\rm km/s}\ \text{at 1 AU}',30).shift(DOWN*2.2)))
        self.play(FadeIn(self.equation(r'\text{Green: }\mathbf v_t\ \text{(target)};\quad\text{rust: }\mathbf u_p\ \text{(projectile)};\quad\psi:\ \text{angle between them}',24).shift(DOWN*2.95)))
        self.citation('Nesvorný et al. (2011): orbits and the meteoroid population','https://doi.org/10.1088/0004-637X/743/2/129')
        self.finish()

    def dust_collision_rate(self):
        self.start_slide('How often is the grain hit? Count a swept volume.',
            'For dilute uncorrelated hard spheres, a projectile center hits when it passes within the sum '
            'of target and projectile radii. Neglect gravitational focusing for these small fast grains. '
            'The animation uses target-rest coordinates, one projectile size and one relative speed. '
            'A number density times swept volume gives the expected number of impacts, not necessarily destruction.')
        center=np.array([-4.6,.6,0])
        target=Circle(.42,color=GOLD,fill_opacity=.8).move_to(center)
        corridor=Rectangle(width=4.8,height=1.4,color=BLUE,fill_opacity=.06).move_to([-2.3,.6,0])
        self.play(Create(corridor),FadeIn(target))
        radius=DoubleArrow([-4.6,.6,0],[-4.6,1.3,0],buff=0,color=GREEN)
        self.play(GrowArrow(radius))
        self.add(self.equation(r'a_t+a_p',26,GREEN).move_to([-5.65,.9,0]))
        travel=DoubleArrow([-4.6,-.6,0],[.1,-.6,0],buff=0,color=BLUE)
        self.play(GrowArrow(travel))
        self.add(self.equation(r'v_{\rm rel}\,\Delta t',27,BLUE).next_to(travel,DOWN,buff=.12))
        rng=np.random.default_rng(93)
        dots=VGroup(*[Dot([rng.uniform(-4.2,-.2),rng.uniform(-.04,1.22),0],radius=.03,color=BLUE) for _ in range(23)])
        self.play(FadeIn(dots))
        formula=self.term_definitions([
            r'\sigma_{\rm geom}=\pi(a_t+a_p)^2\quad[\mathrm{m^2}]',
            r'\Delta V=\sigma_{\rm geom}v_{\rm rel}\Delta t\quad[\mathrm{m^3}]',
            r'\langle N_{\rm hit}\rangle=n_p\Delta V',
            r'\Gamma_{\rm hit}=n_p\sigma_{\rm geom}v_{\rm rel}\quad[\mathrm{s^{-1}}]'],
            [3.55,.65,0],29,5.3)
        for row in formula:self.play(Write(row))
        self.play(dots.animate.shift(LEFT*.32),run_time=.6)
        defs=self.term_definitions([
            r'a_t,a_p:\ \text{target/projectile radii [m]};\quad n_p:\ \text{projectile number density [m}^{-3}\text{]}',
            r'\Delta t:\ \text{time interval [s]};\quad \Gamma_{\rm hit}:\ \text{impact rate per target [s}^{-1}\text{]}'],
            [0,-2.1,0],24,12.3)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('More projectiles, a larger collision area, or faster encounters increase the rate.',25,FG).shift(DOWN*3.05)))
        self.citation('Stark and Kuchner (2009): collision rates along particle orbits','https://doi.org/10.1088/0004-637X/707/1/543')
        self.finish()

    def dust_collision_population(self):
        self.start_slide('Add up the projectiles that can destroy this target',
            'Generalize the swept-volume result over projectile radius and velocity. '
            'f_p da_p d^3u is the local projectile number density in that phase-space element. '
            'The outcome factor selects catastrophic disruption; erosion would require a separate gradual '
            'mass-loss and size-evolution equation. The spatial distribution and velocity distribution must '
            'be specified by an environment or dynamical model. This is not the atomic collision cross section '
            'sigma_c used later in the plasma model.')
        prompt=self.prose('A dust cloud contains many sizes, speeds, and crossing orbits.',28,FG).shift(UP*2.35)
        self.play(FadeIn(prompt))
        eq=self.equation(r'\Gamma_{\rm dest}(\mathbf r,\mathbf v_t)'
            r'=\int f_p(a_p,\mathbf u,\mathbf r)\,\pi(a_t+a_p)^2'
            r'|\mathbf v_t-\mathbf u|\,\mathcal P_{\rm dest}\,da_p\,d^3u',32,BLUE).shift(UP*1.25)
        self.play(Write(eq))
        defs=self.term_definitions([
            r'f_p\,da_p\,d^3u:\ \text{number of projectiles per unit volume [m}^{-3}\text{]}',
            r'\mathbf r:\ \text{target position [m]};\quad \mathbf v_t,\mathbf u:\ \text{target/projectile velocities [m/s]}',
            r'\mathcal P_{\rm dest}:\ \text{probability that this encounter destroys the target [dimensionless]}',
            r'\text{Simple threshold model:}\quad \mathcal P_{\rm dest}=\Theta(Q_t-Q_D^*)',
            r'\Theta(x)=0\ (x<0),\ 1\ (x\geq0):\ \text{step function}'],
            [0,-.35,0],25,12.1)
        for row in defs:self.play(FadeIn(row),run_time=.4)
        self.play(FadeIn(self.prose('The projectile size spectrum and the strength law decide which impacts count.',26,GOLD).shift(DOWN*2.45)))
        self.play(FadeIn(self.prose('The orbit decides which densities and velocities the target encounters.',26,GREEN).shift(DOWN*3.1)))
        self.citation('Pokorný et al. (2024): a three-dimensional collision environment','https://doi.org/10.3847/PSJ/ad2de8')
        self.finish()

    def dust_collision_survival(self):
        self.start_slide('Survival depends on the whole journey through the dust',
            'Assume independent destructive encounters. The probability of survival falls at the local '
            'destruction rate, so dP/dt=-Gamma_dest P. Integrating gives the cumulative hazard expression. '
            'For a fixed slowly evolving orbit define the collision lifetime by the orbit-averaged rate. '
            'The forty-grain cartoon illustrates probabilities only; no collision lifetime has been '
            'calculated here for 55P or for the secular track.')
        self.play(Write(self.equation(r'\frac{dP_{\rm surv}}{dt}=-\Gamma_{\rm dest}(t)P_{\rm surv}'
            r'\quad\Rightarrow\quad P_{\rm surv}(t)=e^{-H(t)}',34,BLUE).shift(UP*2.2)))
        self.play(Write(self.equation(r'H(t)=\int_0^t\Gamma_{\rm dest}(t^\prime)\,dt^\prime,\qquad '
            r'\tau_{\rm coll}^{-1}=\langle\Gamma_{\rm dest}\rangle_{\rm orbit}',33).shift(UP*1.15)))
        defs=self.equation(r'P_{\rm surv}:\ \text{surviving fraction};\quad H:\ \text{cumulative exposure (dimensionless)};'
            r'\quad\tau_{\rm coll}:\ \text{collision lifetime [s]}',23).shift(UP*.35)
        self.play(FadeIn(defs))
        grains=VGroup(*[self.grain(np.array([-4.7+.48*(i%20),-1.-.55*(i//20),0]),.09) for i in range(40)])
        label=self.equation(r'H=0:\quad P_{\rm surv}=1',31,GREEN).shift(DOWN*2.25)
        self.play(FadeIn(grains),FadeIn(label))
        # Deterministic thinning is a visual expectation, not a Monte Carlo result.
        self.play(*[g.animate.set_opacity(.08) for g in list(grains)[15:]],
            Transform(label,self.equation(r'H=1:\quad P_{\rm surv}=e^{-1}\simeq37\%',31,GREEN).move_to(label)),run_time=.9)
        self.play(*[g.animate.set_opacity(.08) for g in list(grains)[2:15]],
            Transform(label,self.equation(r'H=3:\quad P_{\rm surv}=e^{-3}\simeq5\%',31,RED).move_to(label)),run_time=.9)
        self.play(FadeIn(self.prose('Compare accumulated collision exposure with the time needed for P--R migration.',25,FG).shift(DOWN*3.05)))
        self.citation('Nesvorný et al. (2011), section 2.3: stochastic collisional removal','https://doi.org/10.1088/0004-637X/743/2/129')
        self.finish()

    def grun_collisions(self):
        self.start_slide('Grün et al. (1985): the dust population is a balance',
            'Grün, Zook, Fechtig and Giese combined the empirical meteoroid environment near 1 AU with '
            'collisional destruction, fragment production and radiation-related removal. Their collisional '
            'lifetimes require an assumed projectile population and disruption strength. The diagram is a '
            'conceptual balance, not a reproduction of a quantitative Grün lifetime curve.')
        self.play(FadeIn(self.prose('Observed flux and size distribution constrain the collision environment.',28,FG).shift(UP*2.4)))
        positions=[[-4.6,.65,0],[0,.65,0],[4.6,.65,0]]
        titles=['Large grains','Impact fragments','Small dust']
        sizes=[.5,.24,.07]
        for i,(pos,title,size) in enumerate(zip(positions,titles,sizes)):
            count=[1,4,12][i]
            rng=np.random.default_rng(i+200)
            objects=VGroup(*[self.grain(np.array(pos)+[rng.uniform(-.55,.55) if count>1 else 0,
                rng.uniform(-.35,.35) if count>1 else 0,0],size) for _ in range(count)])
            self.play(FadeIn(objects),FadeIn(self.prose(title,26,GOLD).move_to([pos[0],1.65,0])),run_time=.45)
            if i<2:self.play(GrowArrow(Arrow(np.array(pos)+[1,.0,0],np.array(positions[i+1])+[-1,0,0],buff=0,color=BLUE)))
        sink1=self.prose('P--R transport toward the Sun',25,GREEN).move_to([-3.1,-1.6,0])
        sink2=self.prose('Radiation pressure can eject small fragments',25,RED)
        sink2.scale_to_fit_width(5.7).move_to([3.45,-1.6,0])
        self.play(GrowArrow(Arrow([-4.6,.05,0],[-3.1,-1.2,0],buff=0,color=GREEN)),
            GrowArrow(Arrow([4.6,.05,0],[3.45,-1.2,0],buff=0,color=RED)))
        self.play(FadeIn(sink1),FadeIn(sink2))
        self.play(FadeIn(self.prose('Collisions are both a sink for targets and a source of daughter grains.',26,BLUE).shift(DOWN*2.15)))
        self.play(FadeIn(self.prose('Lifetime estimates depend on the orbit, dust population, and assumed grain strength.',25).shift(DOWN*3.)))
        self.citation('Grün, Zook, Fechtig and Giese (1985), Icarus 62, 244--272','https://doi.org/10.1016/0019-1035(85)90121-6')
        self.finish()

    def later_collision_models(self):
        self.start_slide('Later models connect collisions to orbits and observations',
            'Two examples of subsequent zodiacal-cloud models. Nesvorný et al. 2011 use numerical orbital '
            'populations and a scaled Grün collision lifetime; destroyed grains are removed, not followed '
            'as a full fragment cascade. Their radar comparison favors longer millimetre-grain survival '
            'than the standard prescription. Rigley and Wyatt 2022 use comet splitting to supply a '
            'kinetically evolved size distribution with fragment production, destruction and radiation forces. '
            'These are different model ingredients, not one universally calibrated lifetime.')
        n=self.prose('Nesvorný et al. (2011)',29,BLUE).move_to([-3.8,2.3,0])
        ntext=VGroup(*[self.prose(t,25,FG) for t in [
            'Integrate grain orbits; compare with infrared emission and meteor radars.',
            'Scale the Grün lifetime to explore uncertain collisional removal.',
            'Radar data favor longer survival for millimetre grains in that model.']]).arrange(DOWN,buff=.24,aligned_edge=LEFT).move_to([0,1.05,0])
        self.play(FadeIn(n))
        for row in ntext:self.play(FadeIn(row),run_time=.4)
        rule=self.equation(r'\tau_{\rm coll}=S\,\tau_{\rm G85},\qquad '
            r'S:\ \text{dimensionless lifetime scale factor}',29,GOLD).shift(DOWN*.05)
        self.play(Write(rule))
        r=self.prose('Rigley and Wyatt (2022)',29,GREEN).move_to([-3.5,-1.05,0])
        rtext=VGroup(*[self.prose(t,25,FG) for t in [
            'Comet splitting supplies dust; a kinetic model evolves the size distribution.',
            'Fragment production and destruction compete with radiation forces.',
            'The small grains are replenished by the breakup of larger bodies.']]).arrange(DOWN,buff=.24,aligned_edge=LEFT).move_to([0,-2.25,0])
        self.play(FadeIn(r))
        for row in rtext:self.play(FadeIn(row),run_time=.4)
        links=[('Nesvorný et al. (2011)','https://doi.org/10.1088/0004-637X/743/2/129',n),
            ('Rigley and Wyatt (2022)','https://doi.org/10.1093/mnras/stab3482',r)]
        self.paper_links(links)
        self.finish()

    def collisional_grooming(self):
        self.start_slide('Three-dimensional models ask where the grain spends its time',
            'Stark and Kuchner 2009 introduced iterative collisional grooming: orbital particle streams '
            'provide the density and velocity distribution, and collisions change their weights. '
            'Pokorný et al. 2024 apply this to Jupiter-family comet dust and several observations, finding '
            'greater grain resistance than older assumptions in their model. Their implementation neglects '
            'gradual erosion and removes catastrophic daughters rather than evolving a full fragment cascade. '
            'The illustrative circles are projected orbit crossings, not a quantitative density map. '
            '55P is a retrograde Halley-type comet, not a Jupiter-family comet; these fits cannot simply be '
            'assigned as its lifetime. Our following Earth encounter is conditional on a surviving grain.')
        center=np.array([-4.3,.6,0])
        sun=Dot(center,radius=.12,color=GOLD)
        paths=VGroup(*[Ellipse(width=3.3,height=h,color=c,stroke_width=2).rotate(a).move_to(center)
            for h,a,c in [(1.2,.3,GREEN),(1.7,-.35,BLUE),(2.2,.8,MUTED)]])
        self.play(FadeIn(sun),Create(paths))
        dust=Dot(paths[0].point_from_proportion(0),radius=.06,color=RED)
        self.add(dust)
        self.play(MoveAlongPath(dust,paths[0]),run_time=2.,rate_func=linear)
        self.add(self.prose('Orbit crossings set local encounters',22).move_to([-4.3,-1.5,0]))
        body=self.term_definitions([
            r'\text{Orbits}\ \longrightarrow\ f_p(\mathbf r,\mathbf u,a_p)',
            r'\text{Local impacts}\ \longrightarrow\ \text{stream survival weights}',
            r'\text{Updated cloud}\ \longrightarrow\ \text{new collision rates}'],
            [2.35,1.4,0],27,7.3)
        for row in body:self.play(FadeIn(row))
        text=VGroup(self.prose('Pokorný et al. (2024)',27,BLUE),
            self.prose('Radar, infrared, and probe constraints favor stronger grains',24,FG),
            self.prose('within their Jupiter-family comet dust model.',24,FG)).arrange(DOWN,buff=.17).move_to([2.35,-.3,0])
        if text.width>7.4:text.scale_to_fit_width(7.4)
        self.play(FadeIn(text))
        self.play(FadeIn(self.prose('Strength, source populations, and fragment treatment remain model assumptions.',25).shift(DOWN*2.15)))
        self.play(FadeIn(self.prose('For 55P: compute exposure along its own retrograde orbit before quoting a lifetime.',25,RED).shift(DOWN*2.85)))
        refs=[]
        for x,label,url in [(-3.2,'Stark and Kuchner (2009)','https://doi.org/10.1088/0004-637X/707/1/543'),
            (3.2,'Pokorný et al. (2024)','https://doi.org/10.3847/PSJ/ad2de8')]:
            item=self.prose(label,18,BLUE).move_to([x,-3.78,0])
            self.play(FadeIn(item),run_time=.2)
            refs.append((label,url,item))
        self.paper_links(refs)
        self.finish()

    def story_final_laps(self):
        # Source: Encounter animation: meteor_head_rcs.py | illustrative geometry, not an impact
        # ephemeris
        self.start_slide('Follow a surviving grain: the final few laps',
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
        self.play(FadeIn(self.prose('One surviving grain meets Earth at the right place and time.',31,FG).shift(DOWN*2.6)))
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

    def ablation_profiles(self):
        self.start_slide('What the ablation model predicts along the path',
            'Previously computed MetAblate profiles from sabmod, six speeds and 45 degree entry elevation. '
            'Initial mass is 1e-8 kg for these cometary cases, distinct from the illustrative 100 micrometre stony chain example. '
            'The profiles show temperature, remaining mass, speed, and physical mass loss versus altitude. No new integration is launched.')
        self.play(FadeIn(self.image('ablation_profiles.png',11.7).shift(UP*.2)))
        self.play(FadeIn(self.equation(r'm_0=10^{-8}\ \mathrm{kg},\quad\chi=45^\circ;\quad v_0=11,15,20,32,53,72\ \mathrm{km/s}',26,BLUE).shift(DOWN*2.65)))
        self.play(FadeIn(self.prose('Heating precedes strong evaporation; mass loss and deceleration then change the grain.',25).shift(DOWN*3.25)))
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
        self.start_slide('Count the air particles intercepted in a short time',
            'Derive the collision rate as number density times relative speed times effective collision area. '
            'For independent encounters in a dilute gas the no-collision survival probability is exponential. '
            'The fast-stream approximation uses relative speed v; thermal launch speeds are much smaller.')
        box=Rectangle(width=4.5,height=1.15,color=BLUE,fill_opacity=.05).move_to([-3.8,1.,0])
        target=Circle(.57,color=GOLD,fill_opacity=.08).move_to([-1.55,1.,0])
        self.play(Create(box),Create(target))
        rng=np.random.default_rng(133)
        air=VGroup(*[Dot([-5.8+rng.uniform(0,3.9),rng.uniform(.5,1.5),0],radius=.035,color=BLUE) for _ in range(20)])
        self.play(FadeIn(air));self.play(air.animate.shift(RIGHT*.25),run_time=.7)
        self.add(self.equation(r'\sigma_c\ [\mathrm{m^2}]',25,GOLD).move_to([-1.5,2.,0]),
            self.equation(r'v\,dt\ [\mathrm m]',26,BLUE).move_to([-4.,.1,0]))
        count=self.equation(r'dN=n_A\,\sigma_c\,v\,dt',35,BLUE).move_to([2.8,1.65,0])
        rate=self.equation(r'\nu_c=\frac{dN}{dt}=n_A\sigma_c v\quad[\mathrm{s^{-1}}]',34,BLUE).move_to([2.8,.55,0])
        self.play(Write(count),run_time=1.);self.play(Write(rate),run_time=1.)
        self.play(FadeIn(self.equation(r'n_A:\ \text{air number density [m}^{-3}\text{]};\quad '
            r'dN:\ \text{expected encounters in }dt;\quad v:\ \mathrm{m/s}',24,MUTED).shift(DOWN*1.15)))
        self.next_slide('From encounter rate to a mean waiting time',
            notes='A Poisson process at rate nu_c has P0(t)=exp(-nu_c t). Its mean waiting time is the integral of P0, equal to 1/nu_c. P0 is a probability and tau_c is in seconds.')
        self.play(Write(self.equation(r'P_0(t)=e^{-\nu_c t}:\quad\text{probability of no collision by time }t',30).shift(DOWN*2.0)))
        self.play(Write(self.equation(r'\tau_c=\int_0^\infty P_0(t)\,dt=\frac{1}{\nu_c}\quad[\mathrm s]',36,GREEN).shift(DOWN*3.)))
        self.citation('Dimant and Oppenheim (2017), Part 1, equations 6 and 20','https://doi.org/10.1002/2017JA023960')
        self.finish()

        self.start_slide('One collision clock, two different measured displacements',
            'The same neutral and same waiting time produce two distance scales because the reference '
            'frames differ. ell_A is travel through air to the first collision; lambda_T is a characteristic '
            'thermal displacement relative to the grain. They are not two independent collision processes. '
            'The air-frame path is approximated by v tau because u is much smaller than v.')
        common=self.equation(r'\tau_c=\frac{1}{n_A\sigma_c(v)v}',38).shift(UP*2.2)
        self.play(Write(common))
        left=self.equation(r'\ell_A\simeq v\tau_c=\frac{1}{n_A\sigma_c}',37,BLUE).move_to([-3.4,.9,0])
        self.play(FadeIn(self.prose('Distance travelled through air',26,BLUE).move_to([-3.4,1.65,0])))
        self.play(Write(left),run_time=1.1)
        self.next_slide('Measure displacement relative to the grain',
            notes='The reference-frame subtraction already established thermal separation u t. Use its characteristic speed V_T in the same waiting time; do not interpret the long air-frame flight as the size of the electron cloud.')
        self.play(FadeIn(self.prose('Distance separated from the grain',26,GREEN).move_to([3.4,1.65,0])))
        right=self.equation(r'\lambda_T=V_T\tau_c=\frac{V_T}{n_A\sigma_c v}',37,GREEN).move_to([3.4,.9,0])
        self.play(Write(right),run_time=1.1)
        self.play(Write(self.equation(r'\frac{\lambda_T}{\ell_A}=\frac{V_T}{v}\ll1',42,GOLD).shift(DOWN*.6)))
        self.play(FadeIn(self.equation(r'V_T=\sqrt{k_BT_M/m_{\rm Si}}:\ \text{thermal speed [m/s]};'
            r'\quad T_M:\ \text{grain temperature [K]}',25,MUTED).shift(DOWN*1.8)))
        self.play(FadeIn(self.equation(r'k_B:\ \text{Boltzmann constant [J/K]};\quad '
            r'm_{\rm Si}:\ \text{Si atom mass [kg]}',24,MUTED).shift(DOWN*2.4)))
        self.play(FadeIn(self.prose('Use the thermal displacement to scale the plasma surrounding the moving grain.',26,FG).shift(DOWN*3.15)))
        self.citation('Dimant and Oppenheim (2017), Part 1, equation 20','https://doi.org/10.1002/2017JA023960')
        self.finish()

    def collision_force_physics(self):
        # Classical scattering: MIT 16.55 (2014), lectures 6--7, pp. 6--9.
        # Molecular potentials and their limits: Khrapak (2014), arXiv:1404.5476.
        # Sugar et al. (2018), section 5.3, adopts Bronshten separately from its LJ test.
        from meteor_rcs.collision_physics import trajectory
        def column(item, position, width=6.):
            if item.width>width:item.scale_to_fit_width(width)
            return item.move_to(position)
        mechanics='https://ocw.mit.edu/courses/16-55-ionized-gases-fall-2014/ba010aa23f0da845aa3ff555f3d60921_MIT16_55F14_Lecture6-7.pdf'
        molecular='https://arxiv.org/abs/1404.5476'
        self.start_slide('Neutral atoms still exert forces on each other',
            'The colliding objects are an evaporated meteor atom and an air molecule, not two solid grains. '
            'Neutral means zero net charge, not absence of interactions. Correlated electronic fluctuations '
            'give dispersion attraction; overlap of electronic clouds gives strong repulsion through electronic '
            'structure, including Pauli exclusion and electrostatic interactions. The shaded clouds are schematic, '
            'not electron orbits. A Lennard-Jones pair potential is an illustrative effective model, not a '
            'first-principles meteor atom-air potential or the source of the empirical exponent 0.8.')
        clouds=VGroup()
        for x,c in [(-3.8,GOLD),(-.6,BLUE)]:
            cloud=Circle(.7,color=c,fill_opacity=.12).move_to([x,.95,0])
            centre=Dot([x,.95,0],radius=.07,color=c)
            clouds.add(VGroup(cloud,centre))
        labels=VGroup(self.prose('Meteor atom',25,GOLD).move_to([-3.8,2.25,0]),
            self.prose('Air molecule',25,BLUE).move_to([-.6,2.25,0]))
        self.play(FadeIn(clouds),FadeIn(labels))
        self.play(FadeIn(column(self.prose('Electron fluctuations create attraction',25),[3.5,1.8,0],5.3)))
        attraction=VGroup(Arrow([-3.05,.95,0],[-2.4,.95,0],color=GREEN,buff=0),
            Arrow([-1.35,.95,0],[-2.0,.95,0],color=GREEN,buff=0))
        self.play(*[GrowArrow(a) for a in attraction])
        self.next_slide('Electronic overlap produces strong repulsion',
            notes='The nuclei do not need to make mechanical contact. Effective forces arise from the electronic state of the pair. The attractive and repulsive terms below describe a model potential energy, in joules.')
        self.play(FadeOut(attraction),FadeOut(labels))
        self.play(clouds[0].animate.shift(RIGHT*.95),clouds[1].animate.shift(LEFT*.95))
        self.play(GrowArrow(Arrow([-2.8,.95,0],[-3.5,.95,0],color=RED,buff=0)),
            GrowArrow(Arrow([-1.6,.95,0],[-.9,.95,0],color=RED,buff=0)))
        self.play(FadeIn(column(self.prose('Overlapping clouds resist compression',25,RED),[3.5,.55,0],5.3)))
        self.play(FadeIn(column(self.prose('Electronic structure, including Pauli exclusion',24),[3.5,-.1,0],5.3)))
        self.play(FadeIn(self.prose('An illustrative neutral-particle potential',24).shift(DOWN*.5)))
        self.play(Write(self.equation(r'U(r)=\underbrace{C_{12}/r^{12}}_{\text{short-range repulsion}}'
            r'-\underbrace{C_6/r^6}_{\text{dispersion attraction}}',36,BLUE).shift(DOWN*1.3)))
        self.play(FadeIn(self.equation(r'r:\ \text{separation [m]};\quad U:\ \text{pair potential energy [J]}',25).shift(DOWN*2.45)))
        self.play(FadeIn(self.equation(r'C_{12}\ [\mathrm{J\,m^{12}}],\quad C_6\ [\mathrm{J\,m^6}]:\ \text{interaction strengths}',24).shift(DOWN*3.1)))
        self.citation('Pair potentials: Khrapak (2014); Sugar et al. (2018), section 5.3',molecular)
        self.finish()

        self.start_slide('A potential-energy gradient changes the relative motion',
            'Reduce the two-body elastic problem to relative separation r with reduced mass mu. '
            'The force is minus the gradient of potential energy. For the repulsive term, the force points '
            'outward along the separation vector. The fixed origin in the animation is the interaction centre '
            'of the relative-coordinate problem, not an infinitely heavy atmospheric molecule. The two '
            'trajectories are numerical integrations of the same inverse-twelfth-power repulsion at the same '
            'impact parameter and different incoming speeds. Only the illustrative elastic encounter is modeled.')
        self.play(Write(self.equation(r'm_M\ddot{\mathbf r}_M=\mathbf F,\qquad '
            r'm_A\ddot{\mathbf r}_A=-\mathbf F',37,BLUE).shift(UP*2.65)))
        self.play(FadeIn(self.equation(r'm_M,m_A:\ \text{masses [kg]};\quad '
            r'\mathbf F:\ \text{equal and opposite interaction forces [N]}',25).shift(UP*1.8)))
        self.play(Write(self.equation(r'\mathbf r=\mathbf r_M-\mathbf r_A\quad\Rightarrow\quad '
            r'\ddot{\mathbf r}=\left(\frac1{m_M}+\frac1{m_A}\right)\mathbf F',34,GREEN).shift(UP*.75)))
        self.play(Write(self.equation(r'\mu\equiv\frac{m_Mm_A}{m_M+m_A}\quad\Rightarrow\quad '
            r'\mu\ddot{\mathbf r}=\mathbf F',35,GREEN).shift(DOWN*.4)))
        self.next_slide('The interaction energy supplies the force',
            notes='Both particles recoil. Subtract their Newton equations to obtain the relative-coordinate equation. The reduced mass includes both recoils. The force is minus the potential gradient, so the positive inverse-twelfth-power term gives an outward force.')
        self.play(Write(self.equation(r'\mathbf F=-\nabla U,\qquad '
            r'U=\frac{C_{12}}{r^{12}}\ \Rightarrow\ '
            r'\mathbf F=\frac{12C_{12}}{r^{13}}\widehat{\mathbf r}',35,GOLD).shift(DOWN*1.6)))
        self.play(FadeIn(self.prose('Integrating this force gives the trajectories on the next slide.',27).shift(DOWN*2.65)))
        self.play(FadeIn(self.equation(r'\mu:\ \text{reduced mass [kg]};\quad '
            r'\widehat{\mathbf r}:\ \text{outward unit vector}',24).shift(DOWN*3.2)))
        self.citation('Central-force scattering: MIT 16.55 (2014), lectures 6--7',mechanics)
        self.finish()

        self.start_slide('The same force law bends slow and fast encounters differently',
            'Both rows use the same dimensionless repulsive potential and b=1.1 a. Length a and speed v0 '
            'are illustrative reference scales, not a calibrated atom-air interaction. A common physical clock '
            'advances both trajectories; the faster particle exits earlier. The arrows are proportional to '
            'the computed force, with one common scale. The final angle is measured from the numerical '
            'outgoing velocity. Energy and angular momentum are conserved by the integration to its tolerance.')
        results=[trajectory(1.),trajectory(2.)]
        clock=ValueTracker(0)
        total=max(r['time'][-1] for r in results)
        force_scale=max(np.linalg.norm(r['force'],axis=1).max() for r in results)
        animated=[]
        self.play(FadeIn(self.equation(r'b:\ \text{incoming-path offset [m]};\quad \theta:\ \text{deflection angle [rad]}',25).shift(UP*2.7)))
        self.add(column(self.prose('Relative-coordinate trajectories',23),[3.5,2.2,0],5.8))
        for result,y,c,ratio in zip(results,[.95,-1.45],[BLUE,GREEN],[1,2]):
            centre=np.array([-2.2,y,0.]);scale=.29
            def point_at(t,r=result,o=centre):
                return o+scale*np.r_[np.array([np.interp(t,r['time'],r['state'][:,k]) for k in [0,1]]),0.]
            def trace(r=result,o=centre,c=c):
                t=min(clock.get_value(),r['time'][-1]);pts=r['state'][r['time']<=t,:2]
                pts=np.vstack([pts,[np.interp(t,r['time'],r['state'][:,k]) for k in [0,1]]])
                return VMobject(color=c,stroke_width=3).set_points_as_corners([o+scale*np.r_[p,0.] for p in pts])
            line=always_redraw(trace)
            atom=Dot(point_at(0),radius=.055,color=c)
            atom.add_updater(lambda mob,fn=point_at:mob.move_to(fn(clock.get_value())))
            def force_arrow(r=result,fn=point_at,c=c):
                t=min(clock.get_value(),r['time'][-1]);f=np.array([np.interp(t,r['time'],r['force'][:,k]) for k in [0,1]])
                p=fn(t);delta=np.r_[.75*f/force_scale,0.]
                if np.linalg.norm(delta)<.005:delta=np.array([.005,0,0])
                return Arrow(p,p+delta,buff=0,color=RED,stroke_width=3,max_tip_length_to_length_ratio=.2)
            force=always_redraw(force_arrow)
            reference=DashedLine(centre+[-2.32,.319,0],centre+[2.6,.319,0],color=MUTED,stroke_opacity=.3)
            bracket=DoubleArrow(centre+[-2.7,0,0],centre+[-2.7,.319,0],buff=0,color=MUTED,tip_length=.07)
            self.add(reference,Dot(centre,radius=.045,color=RED),line,atom,force,bracket,
                self.equation(r'b',22).move_to(centre+[-3.,.16,0]))
            animated.extend([line,atom,force])
            label=self.equation(r'v='+('v_0' if ratio==1 else '2v_0'),30,c).move_to([3.5,y+.75,0])
            angle=self.equation(r'\theta='+f'{np.degrees(result["angle"]):.1f}'+r'^\circ',30,c).move_to([3.5,y+.05,0])
            self.play(FadeIn(label),FadeIn(angle),run_time=.4)
        scales=VGroup(self.equation(r'a:\ \text{reference length [m]}',22),
            self.equation(r'v_0:\ \text{reference speed [m/s]}',22)).arrange(DOWN,buff=.15).move_to([3.5,0,0])
        self.play(FadeIn(scales))
        self.play(FadeIn(self.equation(r'b=1.1a;\quad U/(\mu v_0^2)=\tfrac12(a/r)^{12}',25).shift(DOWN*2.65)))
        self.play(FadeIn(self.prose('Red arrows: force. Dashed lines: undeflected incoming direction.',24,RED).shift(DOWN*3.2)))
        self.play(clock.animate.set_value(total),run_time=9,rate_func=linear)
        for item in animated:item.clear_updaters()
        self.citation('Illustrative elastic trajectories; central-force mechanics: MIT 16.55',mechanics)
        self.finish()

        self.start_slide('Encounter time and incoming momentum both matter',
            'Use the small-angle approximation, where the unperturbed trajectory is nearly straight. '
            'At fixed b, the transverse force is the same function of position along the incoming path. '
            'Doubling speed compresses this force pulse in time by two without changing its height. '
            'Its time integral, the transverse impulse, halves. Incoming relative momentum doubles, '
            'so the weak deflection angle becomes one quarter. These pulse curves use the inverse-twelfth-power '
            'force along straight paths; this approximation is distinct from the finite-angle trajectories above.')
        axes=Axes(x_range=[-2,2,1],y_range=[0,1.2,.5],x_length=6.1,y_length=2.35,
            axis_config={'color':MUTED,'include_tip':False}).move_to([-2.65,.85,0])
        slow=axes.plot(lambda t:(1+t*t)**-7,x_range=[-2,2,.02],color=BLUE)
        fast=axes.plot(lambda t:(1+4*t*t)**-7,x_range=[-2,2,.02],color=GREEN)
        self.play(Create(axes),Create(slow),Create(fast))
        self.add(self.equation(r'F_\perp/F_0',24).move_to([-5.15,2.45,0]),
            self.equation(r't/t_0',24).move_to([-2.65,-.65,0]))
        self.play(FadeIn(column(self.equation(r'v_0:\ \text{wider force pulse}',27,BLUE),[3.3,1.8,0],6.)),
            FadeIn(column(self.equation(r'2v_0:\ \text{half the pulse duration}',27,GREEN),[3.3,1.,0],6.)))
        self.play(FadeIn(self.prose('Same impact parameter; weak deflection.',25).shift(UP*2.8)))
        self.play(FadeIn(self.equation(r't_0=b/v_0\ [\mathrm s];\quad F_0:\ \text{peak transverse force [N]}',24).shift(DOWN*1.2)))
        self.play(Write(self.equation(r'\Delta p_\perp=\int F_\perp\,dt,\qquad p_{\rm in}=\mu v\quad[\mathrm{kg\,m/s}]',34,BLUE).shift(DOWN*2.15)))
        self.next_slide('A smaller impulse turns a larger incoming momentum less',
            notes='Delta p is an impulse, in kilogram metres per second. The small-angle result theta=Delta p_perp/(mu v) follows from the transverse component of the outgoing momentum. At fixed impact parameter theta scales as v^-2 in this straight-path approximation. This is not the speed exponent of the cross section, which also integrates over impact parameters.')
        self.play(Write(self.equation(r'\theta\simeq\frac{\Delta p_\perp}{\mu v};\qquad '
            r'v\to2v:\ \Delta p_\perp\to\tfrac12\Delta p_\perp\ \Rightarrow\ \theta\to\tfrac14\theta',32,GOLD).shift(DOWN*3.05)))
        self.citation('Impulse approximation: MIT 16.55 (2014), lectures 6--7',mechanics)
        self.finish()

        self.start_slide('A cross section counts an area of incoming trajectories',
            'Look along the incoming relative velocity. Impact parameter b is the perpendicular separation '
            'between an undeflected path and the interaction centre. For a monotonically repulsive potential, '
            'a chosen deflection threshold theta0 selects a disk b less than b_star. An annulus has area '
            '2 pi b db. The velocity-dependent radius of this disk is an effective interaction radius, '
            'not an atomic surface shrinking. The radius ratio here is the exact inverse-twelfth-power '
            'similarity scaling 2^-1/6 for twice the speed.')
        origin=np.array([-3.45,.55,0.]);radius=1.55
        disk=Circle(radius,color=BLUE,fill_opacity=.07).move_to(origin)
        ring=Annulus(inner_radius=1.,outer_radius=1.15,color=GOLD,fill_opacity=.22).move_to(origin)
        rng=np.random.default_rng(782);positions=rng.uniform(-1.9,1.9,(130,2))
        dots=VGroup(*[Dot(origin+np.r_[p,0],radius=.025,color=BLUE if np.linalg.norm(p)<radius else MUTED) for p in positions])
        self.play(Create(disk),FadeIn(dots),FadeIn(ring))
        self.add(self.prose('View along the incoming velocity',24).move_to([-3.45,2.7,0]))
        radial=Arrow(origin,origin+[radius,0,0],color=BLUE,buff=0)
        self.play(GrowArrow(radial))
        self.add(self.equation(r'b_\star(v)',27,BLUE).move_to([-3.45,-1.45,0]))
        self.play(Write(column(self.equation(r'\theta(b,v)\geq\theta_0:\ \text{a specified deflection event}',29),[2.6,2.1,0],6.)))
        self.play(FadeIn(column(self.equation(r'b:\ \text{impact parameter [m]};\quad\theta_0:\ \text{threshold [rad]}',23),[2.6,1.25,0],6.)))
        self.play(Write(column(self.equation(r'd\sigma=2\pi b\,db',35,GOLD),[2.6,.2,0],6.)))
        self.play(Write(column(self.equation(r'\sigma_>(v)=\int_0^{b_\star(v)}2\pi b\,db=\pi b_\star^2(v)',34,BLUE),[2.6,-.95,0],6.)))
        self.next_slide('Higher speed reduces the area producing the same deflection',
            notes='Keep the threshold fixed and increase the speed. Some trajectories at larger b no longer satisfy the same deflection criterion. The dot positions remain fixed; only membership in the selected collision event changes. The atom has not changed size.')
        newradius=radius*2**(-1/6)
        self.play(disk.animate.scale(newradius/radius).set_color(GREEN),FadeOut(ring),FadeOut(radial),
            *[d.animate.set_color(GREEN if np.linalg.norm(p)<newradius else MUTED) for d,p in zip(dots,positions)],run_time=1.5)
        self.play(FadeIn(self.prose('Fewer incoming paths meet the same deflection threshold.',27,GREEN).shift(DOWN*2.5)))
        self.play(FadeIn(self.prose('The effective area changes; the physical atom does not shrink.',26).shift(DOWN*3.15)))
        self.citation('Impact-parameter cross sections: MIT 16.55 (2014)',mechanics)
        self.finish()

        self.start_slide('Momentum-transfer cross section weights the deflection',
            'A deflection threshold is one cross-section convention. Momentum-transfer cross section '
            'weights each impact-parameter annulus by its fractional loss of forward relative momentum, '
            '1-cos(theta). In elastic centre-of-mass scattering the momentum magnitude stays the same. '
            'Small forward deflections count weakly; large turns count strongly. This distinction matters '
            'because a total collision rate and a momentum-relaxation rate are not generally identical.')
        for x,theta,c in [(-3.5,np.pi/12,BLUE),(2.8,np.pi/2,GREEN)]:
            centre=np.array([x,.9,0.]);length=1.6
            self.play(GrowArrow(Arrow(centre+[-length,0,0],centre,buff=0,color=MUTED)),
                GrowArrow(Arrow(centre,centre+length*np.array([np.cos(theta),np.sin(theta),0]),buff=0,color=c)))
            self.play(FadeIn(self.equation(r'\theta='+('15' if theta<1 else '90')+r'^\circ:\quad '
                r'1-\cos\theta='+f'{1-np.cos(theta):.3f}',29,c).move_to([x,-.05,0])))
        self.play(FadeIn(self.prose('Elastic scattering: the loss of forward momentum is what matters.',27).shift(UP*2.7)))
        self.play(Write(self.equation(r'\Delta p_\parallel=\mu v(1-\cos\theta)',36,GOLD).shift(DOWN*1.15)))
        self.play(Write(self.equation(r'\sigma_{\rm mt}(v)=2\pi\int_0^\infty '
            r'[1-\cos\theta(b,v)]\,b\,db\quad[\mathrm{m^2}]',35,BLUE).shift(DOWN*2.2)))
        self.play(FadeIn(self.prose('Isotropic elastic scattering gives equal total and momentum-transfer cross sections.',24).shift(DOWN*3.15)))
        self.citation('Momentum transfer: MIT 16.55 (2014); Sugar et al. (2018)',mechanics)
        self.finish()

        self.start_slide('The force law determines a characteristic interaction length',
            'For a homogeneous repulsive potential U=Cs/r^s, compare interaction energy with relative '
            'kinetic energy. Define r0 by U(r0)=E. This is an interaction length, not the closest approach '
            'of every trajectory or a hard atomic radius. After rescaling r and b by r0, the dimensionless '
            'scattering equations contain no additional speed dependence. Thus any fixed-angle cross section '
            'and the finite momentum-transfer cross section scale with r0 squared. The prefactor depends on '
            'the exponent and on which cross section is used.')
        axes=Axes(x_range=[.8,1.7,.3],y_range=[0,4.5,1],x_length=4.5,y_length=2.7,
            axis_config={'color':MUTED,'include_tip':False}).move_to([-3.65,.8,0])
        potential=axes.plot(lambda r:r**-12,x_range=[.884,1.7,.006],color=RED)
        self.play(Create(axes),Create(potential))
        self.add(self.equation(r'U/E_0',23,RED).move_to([-5.2,2.55,0]),
            self.equation(r'r/a',23).move_to([-3.65,-.85,0]))
        for energy,c,label in [(1,BLUE,r'E_0'),(4,GREEN,r'4E_0')]:
            r0=energy**(-1/12)
            self.play(Create(DashedLine(axes.c2p(.8,energy),axes.c2p(1.7,energy),color=c)),
                FadeIn(Dot(axes.c2p(r0,energy),radius=.055,color=c)))
            self.add(self.equation(label,24,c).move_to([-.8,axes.c2p(1.7,energy)[1],0]))
        self.play(FadeIn(self.prose('Illustration: repulsive inverse-twelfth-power potential',23).move_to([-3.45,-1.45,0])))
        self.play(Write(column(self.equation(r'U(r)=\frac{C_s}{r^s},\quad s>1;\qquad E=\frac12\mu v^2',33,BLUE),[2.9,2.25,0],6.)))
        self.play(FadeIn(column(self.equation(r'C_s:\ \text{strength [J m}^s\text{]};\quad s:\ \text{dimensionless exponent}',23),[2.9,1.4,0],6.)))
        self.play(Write(column(self.equation(r'\frac{C_s}{r_0^s}=E\quad\Rightarrow\quad '
            r'r_0=\left(\frac{2C_s}{\mu v^2}\right)^{1/s}',34,GREEN),[2.9,.25,0],6.)))
        self.play(FadeIn(column(self.equation(r'r_0:\ \text{interaction length [m]};\quad a,E_0:\ \text{reference scales}',23),[2.9,-.85,0],6.)))
        self.next_slide('Cross section scales as the square of the interaction length',
            notes='This is a scaling derivation for an ideal homogeneous potential. It explains how an interaction can produce a speed-dependent cross section without assuming hard spheres. A fixed-angle or momentum-transfer convention gives a speed-independent dimensionless prefactor in this ideal model.')
        self.play(Write(self.equation(r'\sigma(v)\propto r_0^2\quad\Rightarrow\quad '
            r'\boxed{\sigma(v)\propto v^{-4/s}}',40,GOLD).shift(DOWN*2.45)))
        self.play(FadeIn(self.prose('A steeper repulsive core produces a weaker speed dependence.',26).shift(DOWN*3.2)))
        self.citation('Power-law scattering: MIT 16.55 (2014); Khrapak (2014)',mechanics)
        self.finish()

        self.start_slide('A microscopic mechanism does not fix the empirical exponent',
            'The illustrative r^-12 repulsion gives a high-energy cross-section exponent 1/3. '
            'It therefore cannot be presented as a derivation of the adopted 0.8. An ideal r^-5 '
            'potential would reproduce 0.8 algebraically, but choosing it to match the exponent would '
            'not establish the actual atom-air interaction. Real cross sections depend on species, '
            'collision energy, electronic potentials and the chosen collision convention. Sugar section '
            '5.3 tests model potentials for relative ion-neutral versus neutral-neutral behavior, then '
            'adopts the older Bronshten parametrization for absolute collision rates.')
        self.play(Write(self.equation(r'U\propto r^{-12}\quad\Rightarrow\quad '
            r'\sigma\propto v^{-1/3}',39,BLUE).shift(UP*2.3)))
        self.play(FadeIn(self.prose('That explains a mechanism for speed dependence.',28).shift(UP*1.45)))
        self.play(Write(self.equation(r'U\propto r^{-5}\quad\Rightarrow\quad '
            r'\sigma\propto v^{-0.8}\qquad\text{only for that ideal potential}',33,GREEN).shift(UP*.35)))
        self.play(FadeIn(self.prose('Choosing a power to match 0.8 would not establish the real atom--air potential.',25,RED).shift(DOWN*.55)))
        self.play(FadeIn(self.prose('The adopted 0.8 comes from the Bronshten collision parametrization.',27,GOLD).shift(DOWN*1.65)))
        self.play(FadeIn(self.prose('Sugar et al. use that law for collision rates after testing separate model potentials.',25).shift(DOWN*2.45)))
        self.play(FadeIn(self.prose('Species, collision energy, and the cross-section definition determine the appropriate law.',25).shift(DOWN*3.2)))
        self.citation('Adopted meteor law: Sugar et al. (2018), section 5.3',
            'https://doi.org/10.1002/2018JA025265')
        self.finish()

    def collision_cross_section(self):
        self.collision_force_physics()
        self.start_slide('The atom--air collision cross section',
            'The adopted sigma_c is the effective heavy-particle scattering cross section governing the first '
            'collision of an ablated atom with air. Bronshten (1983) supplies the empirical velocity law; '
            'Sugar et al. (2018), section 5.3, Eq. 13, uses it rather than deriving an absolute cross section '
            'from the Lennard-Jones potentials tested there. Their comparison of neutral--neutral and ion--neutral '
            'momentum-transfer cross sections supports treating those as similar under their assumptions, not '
            'universal species independence. This deck adopts the law for its Si proxy without a Si-specific '
            'cross-section validation. It is separate from ionization probability and electron-neutral damping.')
        target=Circle(.65,color=BLUE,fill_opacity=.08).move_to([-4.3,1.,0])
        atom=Dot([-6.,1.,0],radius=.06,color=GOLD)
        path=Arrow([-5.85,1.,0],[-4.95,1.,0],buff=0,color=GOLD)
        self.play(Create(target),FadeIn(atom),GrowArrow(path))
        self.add(self.equation(r'\sigma_c',31,BLUE).next_to(target,DOWN,buff=.2),
            self.prose('Effective collision area',23).move_to([-4.3,2.1,0]))
        law=self.equation(r'\sigma_c(v_{\rm rel})=5.61\times10^{-19}v_k^{-0.8}\ \mathrm{m^2}',38,BLUE).move_to([2.3,1.55,0])
        speed=self.equation(r'v_k\equiv\frac{v_{\rm rel}}{1\ \mathrm{km\,s^{-1}}},\qquad v_{\rm rel}\simeq v',30).move_to([2.3,.5,0])
        self.play(Write(law),Write(speed))
        self.play(FadeIn(self.prose('Bronshten (1983) empirical law; used by Sugar et al. (2018), section 5.3.',26,FG).shift(DOWN*.8)))
        self.play(FadeIn(self.prose('Next: turn the collision area into a rate, a waiting time, and two displacements.',25,GREEN).shift(DOWN*1.65)))
        self.play(FadeIn(self.prose('This is a collision cross section. Ionization probability is a separate input.',25).shift(DOWN*2.55)))
        self.play(FadeIn(self.prose('The same law is adopted for the Si proxy; it is not a Si-specific measurement.',25,RED).shift(DOWN*3.15)))
        refs=[('Bronshten (1983)','https://doi.org/10.1007/978-94-009-7222-3',-2.4),
              ('Sugar et al. (2018), section 5.3','https://doi.org/10.1002/2018JA025265',2.4)]
        labels=[(label,url,self.prose(label,18,BLUE).move_to([x,-3.78,0])) for label,url,x in refs]
        self.play(*[FadeIn(item) for _,_,item in labels]);self.paper_links(labels)
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

    def play_gpu_movie(self, name, center=ORIGIN, width=12.7):
        """Decode a Rustplotlib GPU-recorded MP4 sequentially; retain correct frame timing."""
        import cv2
        cap=cv2.VideoCapture(str(ROOT/'assets'/name))
        fps=cap.get(cv2.CAP_PROP_FPS);count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        success,pixels=cap.read()
        if not success or fps<=0:raise RuntimeError('Cannot decode '+name)
        picture=ImageMobject(cv2.cvtColor(pixels,cv2.COLOR_BGR2RGBA)).set(width=width).move_to(center)
        self.play(FadeIn(picture))
        clock=ValueTracker(0);decoded=[0]
        def update(mob):
            wanted=min(count-1,int(clock.get_value()*fps))
            while decoded[0]<wanted:
                success,frame=cap.read()
                if not success:break
                decoded[0]+=1
                mob.pixel_array=cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
        picture.add_updater(update)
        self.play(clock.animate.set_value((count-1)/fps),run_time=(count-1)/fps,rate_func=linear)
        picture.clear_updaters();cap.release()
        return picture

    def do_introduction(self):
        self.start_slide('What does the Dimant--Oppenheim model predict?',
            'A kinetic model for the near-meteoroid ion population formed from evaporated atoms. '
            'We infer electron density from quasi-neutrality. It predicts the spatial distribution, not the radar cross section. '
            'The first-collision approximation is not a model for the mature meteor trail.')
        grain=Dot([-4.6,.8,0],radius=.15,color=GOLD)
        air=VGroup(*[Dot([-3.+.35*j,1.25,0],radius=.045,color=BLUE) for j in range(5)])
        self.add(grain,air)
        atom=Dot(grain.get_center(),radius=.055,color=GOLD);self.add(atom)
        self.play(atom.animate.shift([1.8,.45,0]),run_time=1.)
        electron=Dot(atom.get_center()+DOWN*.3,radius=.045,color=GREEN)
        self.play(atom.animate.set_color(RED),FadeIn(electron))
        self.play(electron.animate.shift(RIGHT*.4))
        labels=VGroup(self.prose('Evaporated atom',24,GOLD),self.prose('Energetic atom--air collision',24,BLUE),
            self.prose('Ion and electron near the grain',24,GREEN)).arrange(DOWN,buff=.45).move_to([2.,.9,0])
        for label in labels:self.play(FadeIn(label))
        self.play(Write(self.equation(r'\text{evaporation}\ \longrightarrow\ \text{collisions}\ \longrightarrow\ n_i(\mathbf r)\simeq n_e(\mathbf r)',32,BLUE).shift(DOWN*1.35)))
        self.play(FadeIn(self.prose('Kinetics gives plasma morphology; Maxwell equations give the radar echo.',27,FG).shift(DOWN*2.5)))
        self.citation('Dimant and Oppenheim (2017): Part 1, physical model; Part 2, density solution','https://doi.org/10.1002/2017JA023960')
        self.finish()
        self.start_slide('The assumptions behind the near-meteoroid plasma shape',
            'A steady source in the grain frame; thermal neutral launch speeds much less than meteoroid speed; '
            'first ionizing collisions and ballistic secondary ions; isotropic differential ionization. '
            'Quasi-neutrality is an approximation away from microscopic charge-separation scales.')

        for y,tex,color in [
            (2.55,r'V_T\ll v:\quad\text{slow thermal escape from a fast-moving grain}',FG),
            (1.95,r'\text{steady spherical neutral source}+\text{directed atmospheric stream}',FG),
            (1.35,r'\text{first ionizing collision}\longrightarrow\text{ballistic secondary ions}',GREEN)]:
            self.play(Write(self.equation(tex,29,color).move_to([0,y,0])))
        self.play(Write(self.equation(r'G_{\rm ion}\equiv\frac{d\sigma_{\rm ion}}{d\Omega}'
            r'\quad[\mathrm{m^2\,sr^{-1}}]',34,BLUE).shift(UP*.45)))
        self.play(FadeIn(self.prose('Ionizing-collision cross section per unit scattering solid angle.',25,FG).shift(DOWN*.2)))
        self.play(FadeIn(self.equation(r'\sigma_{\rm ion}:\ \text{total ionization cross section [m}^2\text{]};'
            r'\quad\Omega:\ \text{scattering solid angle [sr]}',23,MUTED).shift(DOWN*.75)))
        self.play(Write(self.equation(r'n_e\simeq n_i:\quad\text{quasi-neutral electron-density approximation}',28,BLUE).shift(DOWN*2.7)))
        self.play(FadeIn(self.prose('The directed atmospheric stream still makes the plasma asymmetric.',24).shift(DOWN*3.25)))
        self.citation('Dimant and Oppenheim (2017), Parts 1--2','https://doi.org/10.1002/2017JA023963')
        self.finish()

    def isotropic_ionization(self):
        self.start_slide('Assume isotropic ion production: no preferred beam direction',
            'At a fixed relative collision speed, DO Part 2 replaces the angular ionization cross section by a constant. '
            'This movie shows outgoing ion directions in the collision centre-of-mass frame. '
            'Each red dot represents a different ionizing encounter, not many ions from one collision. '
            'Equal-area directional samples illustrate the angular distribution, not the plasma-cloud shape. '
            'Two equal solid-angle cones collect equal expected shares. A finite sample need not have exactly equal counts. '
            'The angular dependence is a simplifying assumption, not an established measurement for all species.')
        self.play_gpu_movie('g_ion.mp4',center=[0,.2,0],width=12.7)
        self.play(FadeIn(self.prose('Directions in velocity space; one dot per separate ionizing collision.',25).shift(DOWN*3.2)))
        self.citation('Dimant and Oppenheim (2017), Part 2, section 2','https://doi.org/10.1002/2017JA023963')
        self.finish()

        self.start_slide('Equal solid angles give a constant differential cross section',
            'A solid angle measures a patch of directions in three dimensions. The whole sphere is 4 pi steradians. '
            'The two cones have equal solid angle, therefore equal conditional probability for an ionizing collision. '
            'The probability per solid angle is G_ion divided by total sigma_ion. '
            'Integrate the constant over the entire sphere to obtain sigma_ion=4 pi G_ion.')
        self.play(FadeIn(self.prose('Keep the collision speed fixed. Compare two equal cones of directions.',28).shift(UP*2.55)))
        self.play(Write(self.equation(r'\Delta\Omega_A=\Delta\Omega_B\quad\Rightarrow\quad P_A=P_B',40,GREEN).shift(UP*1.5)))
        self.play(FadeIn(self.equation(r'\Delta\Omega:\ \text{solid angle [sr]};\quad P:\ \text{fraction of ionizing encounters [dimensionless]}',24,MUTED).shift(UP*.7)))
        self.play(Write(self.equation(r'P(\Delta\Omega)=\frac{1}{\sigma_{\rm ion}}\int_{\Delta\Omega}G_{\rm ion}\,d\Omega=\frac{\Delta\Omega}{4\pi}',37,BLUE).shift(DOWN*.2)))
        self.next_slide('Sum all directions to recover the total ionization cross section',
            notes='A complete sphere subtends 4 pi steradians. The differential cross section has units square metres per steradian; integrating it over all directions gives square metres. No preferential beam is added to the collision source in this frame.')
        self.play(Write(self.equation(r'\sigma_{\rm ion}=\int_{4\pi}G_{\rm ion}\,d\Omega=4\pi G_{\rm ion}\quad\Rightarrow\quad\boxed{G_{\rm ion}=\frac{\sigma_{\rm ion}}{4\pi}}',36,GOLD).shift(DOWN*1.5)))
        self.play(FadeIn(self.prose('Isotropic in the collision frame; bulk motion still affects the meteor-frame ions.',25).shift(DOWN*2.65)))
        self.play(FadeIn(self.prose('This describes production directions, not a spherical plasma-density cloud.',25,BLUE).shift(DOWN*3.2)))
        self.citation('Dimant and Oppenheim (2017), Part 2, section 2','https://doi.org/10.1002/2017JA023963')
        self.finish()


    def density_amplitude_introduction(self):
        self.start_slide('A density model needs an amount and a spatial distribution',
            'Introduce the reference density n_star before it appears in a normalization or figure label. '
            'It controls the amplitude of the electron density, while the dimensionless kinetic function '
            'describes its shape. Lambda_T is the characteristic distance from the grain; its collision-time '
            'origin is derived next. The point-source idealization has no finite peak, so n_star is not a maximum.')
        grain=self.grain(np.array([-4.25,.45,0]),.11)
        rng=np.random.default_rng(112)
        dots=VGroup(*[Dot([-4.25+rng.normal(.25,.75),.45+rng.normal(0,.6),0],radius=.03,color=GREEN)
            for _ in range(100)])
        self.play(FadeIn(grain),FadeIn(dots))
        self.play(FadeIn(self.prose('Electron cloud around the grain',23,GREEN).move_to([-4.1,2.,0])))
        idea=self.equation(r'n_e(\mathbf r)=\text{density scale}\times\text{dimensionless shape}',32,BLUE).shift(UP*2.6)
        self.play(Write(idea))
        items=self.term_definitions([
            r'n_\star:\ \text{reference density amplitude [m}^{-3}\text{]}',
            r'F_{\rm DO}:\ \text{dimensionless kinetic shape}',
            r'\lambda_T:\ \text{characteristic distance from the grain [m]}',
            r'\mathbf r:\ \text{position relative to the grain [m]}'],
            [2.4,.8,0],25,7.5)
        for row in items:self.play(FadeIn(row),run_time=.6)
        self.next_slide('Give the density scale its symbol',
            notes='The same shape at twice the amplitude means twice the electron density at every point. q controls supply; the collision length controls spatial dilution. The exact prefactor will be derived later from the published kinetic density.')
        self.play(Write(self.equation(r'n_e(\mathbf r)=n_\star F_{\rm DO}(\mathbf r/\lambda_T)',39,BLUE).shift(DOWN*1.4)))
        self.play(Write(self.equation(r'q\ [\mathrm{m^{-1}}]\ /\ \lambda_T^2\ [\mathrm{m^2}]'
            r'\quad\longrightarrow\quad n_\star\ [\mathrm{m^{-3}}]',29,GOLD).shift(DOWN*2.45)))
        self.play(FadeIn(self.prose('More electron production raises the scale; a wider distribution dilutes it.',25).shift(DOWN*3.2)))
        self.citation('Dimant and Oppenheim (2017), Part 2: density amplitude and kinetic shape','https://doi.org/10.1002/2017JA023963')
        self.finish()

    def do_gallery_animation(self):
        self.start_slide('See the predicted density before using its formula',
            'This rotating log-height surface uses the exact density function and colormap of the requested gallery example. '
            'The two base coordinates are a meridional slice in thermal collision lengths. Height is log density, '
            'not a third physical spatial coordinate. Positive axial coordinate is behind the grain.')
        self.play_gpu_movie('do_height.mp4',center=[0,.3,0],width=12.7)
        self.play(Write(self.equation(r'\text{Height and colour: }\log_{10}(8\pi n_e/n_\star)',29,BLUE).shift(DOWN*3.2)))
        self.citation('Dimant and Oppenheim (2017), Part 2, equations 45--48','https://doi.org/10.1002/2017JA023963')
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
            a=self.equation(tex,29,color)
            if a.width>4.7:a.scale_to_fit_width(4.7)
            a.move_to([-3.9,y,0])
            b=self.prose(text,23).move_to([2.8,y,0])
            if b.width>6.5:b.scale_to_fit_width(6.5)
            self.play(FadeIn(a),FadeIn(b),run_time=.4)
        self.play(FadeIn(self.prose('After source normalization, grain area is not another free amplitude factor.',24).shift(DOWN*2.8)))
        self.finish()


    def collision_frames(self):
        # Actual archived scales in two coordinate systems. Both panels use the
        # same transverse metre scale; the right panel zooms the forward scale.
        v=self.sample['sample_speed_kms']*1000
        vt=np.sqrt(1.380649e-23*self.sample['sample_temperature_k']/(28.085*1.66053906660e-27))
        length=self.sample['sample_lambda_m'];tau=length/vt;travel=v*tau
        self.start_slide('The atom and grain share the fast forward motion',
            'Start with a concrete trajectory before introducing two distance symbols. '
            'An illustrative neutral is emitted with a transverse thermal velocity V_T. '
            'In the atmosphere frame both bodies share v; in the grain frame that motion is subtracted. '
            'The neutral is followed for one mean waiting time, not a deterministic lifetime of every atom. '
            'Axes carry metres. Transverse scales are identical; the forward axis is zoomed in the grain frame.')
        self.play(FadeIn(self.prose('Atmosphere frame',28,FG).move_to([-3.45,2.45,0])),
            FadeIn(self.prose('Grain frame: forward-motion zoom',26,FG).move_to([3.35,2.45,0])))
        def axes(xrange,xlength,center):
            return Axes(x_range=xrange,y_range=[0,.24,.08],x_length=xlength,y_length=2.35,
                tips=False,axis_config={'color':MUTED,'include_numbers':True,'font_size':18,
                'decimal_number_config':{'color':MUTED,'num_decimal_places':2}}).move_to(center)
        left=axes([0,12,4],5.35,[-3.5,.8,0])
        right=axes([-.2,.2,.2],3.8,[3.25,.8,0])
        self.play(Create(left),Create(right))
        self.add(self.equation(r'x_{\rm air}\ [\mathrm m]',23).move_to([-3.5,-.85,0]),
            self.equation(r'x_{\rm grain}\ [\mathrm m]',23).move_to([3.25,-.85,0]),
            self.equation(r'y\ [\mathrm m]',23).rotate(PI/2).move_to([-6.85,1.,0]),
            self.equation(r'y\ [\mathrm m]',23).rotate(PI/2).next_to(right.y_axis,LEFT,buff=.55))
        clock=ValueTracker(0.)
        grain=always_redraw(lambda:self.grain(left.c2p(travel*clock.get_value(),0),.105))
        neutral=always_redraw(lambda:Dot(left.c2p(travel*clock.get_value(),length*clock.get_value()),radius=.055,color=GREEN))
        fixed=self.grain(right.c2p(0,0),.105)
        relative=always_redraw(lambda:Dot(right.c2p(0,length*clock.get_value()),radius=.055,color=GREEN))
        trace=TracedPath(neutral.get_center,stroke_color=GREEN,stroke_width=2.5)
        trace2=TracedPath(relative.get_center,stroke_color=GREEN,stroke_width=2.5)
        self.add(grain,neutral,fixed,relative,trace,trace2)
        legend=self.equation(r'\text{Gold: grain; green: neutral};\quad\tau_c:\ \text{mean time to first collision}',24,MUTED).shift(DOWN*1.5)
        self.play(FadeIn(legend))
        self.play(clock.animate.set_value(1.),run_time=4.,rate_func=linear)
        for m in [grain,neutral,relative,trace,trace2]:m.clear_updaters()
        self.play(Flash(neutral.get_center(),color=BLUE,flash_radius=.16),
            Flash(relative.get_center(),color=BLUE,flash_radius=.16))
        self.play(Write(self.equation(rf't=\tau_c={tau*1000:.3f}\,\mathrm{{ms}}:\qquad '
            rf'\text{{travel through air}}\simeq{travel:.1f}\,\mathrm m,\quad '
            rf'\text{{separation}}={length:.2f}\,\mathrm m',29,BLUE).shift(DOWN*2.25)))
        self.play(FadeIn(self.prose('The forward motion carries both objects; it does not separate them.',27,FG).shift(DOWN*3.1)))
        self.finish()

        self.start_slide('Subtract the common motion to obtain the cloud scale',
            'Derive the reference-frame difference before naming lambda_T. '
            'Choose the release point as the origin and ignore the microscopic grain radius. '
            'The velocity u is one atom thermal launch velocity, with characteristic scale V_T. '
            'Both the axial and transverse components of displacement are set by u, not by the common bulk velocity.')
        rows=self.term_definitions([
            r'\mathbf v:\ \text{grain velocity through air [m/s]}',
            r'\mathbf u:\ \text{thermal launch velocity relative to the grain [m/s]}',
            r'\mathbf r_{\rm grain}(t)=\mathbf v\,t',
            r'\mathbf r_{\rm atom}(t)=(\mathbf v+\mathbf u)t'],[0,1.4,0],33,12.)
        for row in rows:self.play(Write(row),run_time=.8)
        self.next_slide('The bulk velocity cancels',
            notes='Pause on the two actual positions before taking their difference. The common v t cancels, leaving u t in all three directions.')
        self.play(Write(self.equation(r'\Delta\mathbf r=\mathbf r_{\rm atom}-\mathbf r_{\rm grain}'
            r'=(\mathbf v+\mathbf u)t-\mathbf v t=\mathbf u t',36,BLUE).shift(DOWN*.55)))
        self.play(Write(self.equation(r't\sim\tau_c:\qquad|\Delta\mathbf r|\sim V_T\tau_c\equiv\lambda_T',38,GREEN).shift(DOWN*1.85)))
        self.play(FadeIn(self.prose('The DO coordinates measure separation from the moving grain.',28,FG).shift(DOWN*2.9)))
        self.citation('Dimant and Oppenheim (2017), Part 1, primary-neutral flight and collision length','https://doi.org/10.1002/2017JA023960')
        self.finish()

    def velocity_dependence(self):
        # Source: DO collision-length interpretation; effective sigma_c(v) adopted in fdtd
        self.start_slide('Velocity and the plasma surrounding the meteoroid',
            'These are controlled comparisons at fixed atmospheric number density and fixed grain temperature. '
            'A faster incoming atmospheric flux increases collision frequency. The adopted cross section decreases with speed, '
            'so its speed dependence partly compensates the faster flux. Along a real trajectory n_A and T_M also vary.')
        center=np.array([-4.,.3,0]);rng=np.random.default_rng(17)
        grain=self.grain(center,.075)
        plasma=VGroup(*[Dot(center+[rng.normal(.25,.75),rng.normal(0,.4),0],radius=.026,
            color=GREEN,fill_opacity=.7) for _ in range(90)])
        self.play(FadeIn(plasma),FadeIn(grain))
        self.add(self.prose('Electrons and ions',26,GREEN).move_to([-4,2.2,0]),
            self.prose('around the solid grain',24,FG).move_to([-4,1.65,0]))
        fixed=self.equation(r'\text{Hold }n_A,\ T_M\text{ fixed}\quad\Rightarrow\quad V_T\text{ fixed}',28).move_to([2.65,2.05,0])
        rate=self.equation(r'\nu_c=n_A\sigma_c(v)v',38,BLUE).move_to([2.65,1.1,0])
        length=self.equation(r'\lambda_T=\frac{V_T}{\nu_c}',39,GREEN).move_to([2.65,-.05,0])
        self.play(Write(fixed),Write(rate),Write(length))
        self.play(FadeIn(self.prose('A faster atmospheric flux shortens the time to collision.',26).shift(DOWN*1.5)))
        self.play(FadeIn(self.prose('The distance an evaporated atom separates from the grain sets the DO plasma scale.',25).shift(DOWN*2.4)))
        self.finish()


        self.start_slide('Carry the adopted cross section through the collision clock',
            'The -0.8 is an empirical model input, not an exponent derived by the DO solution. '
            'Derive the consequences first for an arbitrary exponent p, then insert p=0.8. '
            'Hold air density and grain temperature fixed; the thermal launch speed is then fixed.')
        self.play(FadeIn(self.prose('Hold atmospheric density and grain temperature fixed.',28,FG).shift(UP*2.5)))
        self.play(Write(self.equation(r'\sigma_c(v)=\sigma_0(v/v_0)^{-p},\qquad p=0.8\ \text{in the adopted law}',33,GOLD).shift(UP*1.5)),run_time=1.2)
        self.play(FadeIn(self.equation(r'\sigma_0=\sigma_c(v_0)\ [\mathrm{m^2}],\quad '
            r'v_0:\ \text{reference speed [m/s]},\quad p:\ \text{dimensionless fitted exponent}',23,MUTED).shift(UP*.7)))
        rate=self.equation(r'\nu_c=n_A\sigma_c v\ \propto\ v^{-p}v=v^{1-p}'
            r'\quad\Rightarrow\quad\nu_c\propto v^{0.2}',36,BLUE).shift(DOWN*.25)
        self.play(Write(rate),run_time=1.3)
        self.next_slide('The thermal distance uses the inverse collision rate',
            notes='Pause here. Faster motion raises the incoming particle flux, while the adopted decreasing cross section partly compensates it. The resulting collision rate increases only as v^0.2.')
        self.play(Write(self.equation(r'\lambda_T=V_T/\nu_c\ \propto\ v^{p-1}'
            r'\quad\Rightarrow\quad\lambda_T\propto v^{-0.2}',36,GREEN).shift(DOWN*1.4)),run_time=1.3)
        self.next_slide('The air-frame path also includes the forward speed',
            notes='Pause again before changing reference frame. The air-frame travel distance is v/nu, so it increases as v^0.8 even though the thermal separation decreases. There is no inconsistency: they measure different displacements.')
        self.play(Write(self.equation(r'\ell_A=v/\nu_c\ \propto\ v^p'
            r'\quad\Rightarrow\quad\ell_A\propto v^{0.8}',36,GOLD).shift(DOWN*2.5)),run_time=1.3)
        self.citation('Adopted empirical collision law: Bronshten (1983); Sugar et al. (2018), section 5.3','https://doi.org/10.1002/2018JA025265')
        self.finish()

        self.start_slide('What the scaling changes in the meteor head plasma',
            'Illustrate the adopted spatial scaling from 20 to 70 km/s, holding atmospheric density, temperature, '
            'and production line density fixed. The cartoon is schematic and only scales the near-head coordinates. '
            'The full DO shape is not a Gaussian cloud or a sharp boundary. Real trajectories also change q, n_A and T_M.')
        center=np.array([-3.8,.35,0]);rng=np.random.default_rng(17)
        plasma=VGroup(*[Dot(center+[rng.normal(.25,.75),rng.normal(0,.4),0],radius=.025,
            color=GREEN,fill_opacity=.65) for _ in range(90)])
        grain=self.grain(center,.07)
        self.add(plasma,grain,self.prose('Ionized plasma around the grain',24,GREEN).move_to([-3.8,2.1,0]))
        initial=self.equation(r'v=20\ \mathrm{km/s}',31,BLUE).move_to([-3.8,-1.35,0])
        self.play(Write(initial))
        final=self.equation(r'v=70\ \mathrm{km/s}',31,BLUE).move_to(initial)
        self.play(plasma.animate.scale((70/20)**(-.2),about_point=center),TransformMatchingTex(initial,final),run_time=1.5)
        self.play(Write(self.equation(r'\frac{\lambda_T(70)}{\lambda_T(20)}=\left(\frac{70}{20}\right)^{-0.2}\simeq0.78',37,GREEN).move_to([3.,1.,0])))
        self.play(Write(self.equation(r'n_e(\mathbf r)=n_\star F_{\rm DO}(\mathbf r/\lambda_T)',31,BLUE).move_to([3.,-.4,0])))
        self.play(FadeIn(self.prose('Fixed atmosphere, temperature, and line density.',25).shift(DOWN*2.35)))
        self.play(FadeIn(self.prose('The rescaled electron-density field is what the electromagnetic solver receives.',25,FG).shift(DOWN*3.05)))
        self.finish()

    def mean_free_path_coordinates(self):
        # Source: Dimant--Oppenheim Part 2, axis and dimensionless-coordinate conventions
        self.start_slide('Measure the plasma coordinates in thermal collision lengths',
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
        self.start_slide('Change electron production while keeping the plasma size fixed',
            'At fixed atmosphere, temperature and speed, lambda_T is fixed. Doubling q doubles n_star, '
            'and doubles the electron density at every fixed spatial coordinate. The dots are a schematic density reminder.')
        center=np.array([-3.6,.3,0]);rng=np.random.default_rng(9)
        cloud=VGroup(*[Dot(center+np.r_[rng.normal(size=2)*[.9,.6],0.],radius=.035,color=GREEN) for _ in range(65)])
        self.play(FadeIn(cloud),FadeIn(Dot(center,color=GOLD,radius=.1)))
        self.play(Write(self.equation(r'n_e(\mathbf r)=n_\star F_{\rm DO}(\mathbf r/\lambda_T)',33,BLUE).move_to([2.7,1.6,0])))
        first=self.equation(r'n_\star\propto q',39,GREEN).move_to([2.7,.45,0]);self.play(Write(first))
        self.play(FadeIn(cloud.copy().shift([.05,.08,0])),TransformMatchingTex(first,self.equation(r'q\to2q\quad\Rightarrow\quad n_e\to2n_e',35,GREEN).move_to([2.7,.45,0])))
        self.play(FadeIn(self.prose('The shape and spatial scale stay the same.',28).shift(DOWN*1.9)))
        self.play(FadeIn(self.prose('The reference density is an amplitude; the ideal point-source maximum is singular.',25).shift(DOWN*2.8)))
        self.finish()
        self.start_slide('Change the collision length at fixed electron line density',
            'Changing lambda_T stretches all coordinates and also changes the density prefactor. '
            'Twice the spatial scale means a quarter of the reference amplitude for fixed q and mass ratio. '
            'This is not a probability distribution normalized to contain a fixed total electron number.')
        cloud=Ellipse(width=2.,height=1.1,color=GREEN,fill_opacity=.22).move_to([-3.4,.35,0]);self.play(FadeIn(cloud))
        self.play(Write(self.equation(r'n_\star\propto\lambda_T^{-2}',39,BLUE).move_to([2.7,1.5,0])))
        self.play(cloud.animate.scale(2.).set_fill(opacity=.07),run_time=1.5)
        self.play(Write(self.equation(r'\lambda_T\to2\lambda_T:\quad n_e^{\rm new}(\mathbf r)=\tfrac14n_e^{\rm old}(\mathbf r/2)',31,GOLD).move_to([2.5,.2,0])))
        self.play(FadeIn(self.prose('Both width and length double; the reference density drops by four.',27,FG).shift(DOWN*1.8)))
        self.play(FadeIn(self.prose('The DO function fixes the kinetic shape; it is not a unit-integral probability density.',25).shift(DOWN*2.7)))
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
        self.start_slide('The plasma density in three physical dimensions',
            'The rotating surface is the actual DO isodensity F_DO=0.05, reconstructed by axisymmetry. '
            'It is one illustrative density level, not a material boundary or the numerical support cutoff. '
            'All three spatial directions have the same scale; colour is only surface shading.')
        self.play_gpu_movie('do_physical.mp4',center=[0,.3,0],width=12.7)
        self.play(FadeIn(self.prose('One isodensity surface; plasma also exists outside it.',26,FG).shift(DOWN*3.1)))
        self.finish()
        self.start_slide('Use axial distance and distance from the trajectory axis',
            'A ring of equal z and transverse radius has the same density at every azimuth. '
            'The ring is a set of evaluation points, not the plasma edge. Labels are outside the swept geometry.')
        center=np.array([1.8,-.3,0]);r=1.15
        axis=Arrow([-.7,-.3,0],[5.3,-.3,0],buff=0,color=MUTED)
        ring=Ellipse(width=.9,height=2*r,color=BLUE).move_to(center)
        meridian=Line(center,center+UP*r,color=GREEN)
        self.play(GrowArrow(axis),Create(ring),Create(meridian))
        self.play(FadeIn(Dot([-.6,-.3,0],color=GOLD,radius=.1)))
        dots=VGroup(*[Dot(center+np.array([.45*np.sin(phi),r*np.cos(phi),0]),color=GREEN,radius=.045) for phi in np.linspace(0,TAU,12,endpoint=False)])
        self.play(LaggedStart(*[FadeIn(p) for p in dots],lag_ratio=.04))
        label=self.equation(r'r_\perp',29,GREEN).move_to([-.1,1.,0])
        leader=Line(label.get_right()+RIGHT*.12,center+UP*.65,stroke_width=1.5,color=GREEN)
        self.play(FadeIn(label),Create(leader))
        self.add(self.equation(r'z',28).next_to(axis,RIGHT,buff=.18),self.prose('Equal density at every azimuth',24).move_to([2.2,-1.9,0]))
        self.play(Write(self.equation(r'n_e(x,y,z)=n_\star F_{\rm DO}\!\left(\frac{z}{\lambda_T},\frac{\sqrt{x^2+y^2}}{\lambda_T}\right)',39,BLUE).shift(UP*2.15)))
        self.play(FadeIn(self.prose('Rotate this distribution to the radar aspect, then sample the solver grid.',26).shift(DOWN*2.9)))
        self.finish()

    def ion_transport_derivation(self):
        # Particle conservation and characteristics, not a new DO simulation.
        from meteor_rcs.kinetic_transport import backtrace, slab_density
        kinetic_url='https://ocw.mit.edu/courses/16-55-ionized-gases-fall-2014/b7c22c3d68ab558bcc3a59867b710e1a_MIT16_55F14_Lecture8.pdf'
        do_url='https://doi.org/10.1002/2017JA023960'
        def at(item, xy, width=6.):
            if item.width>width:item.scale_to_fit_width(width)
            return item.move_to([*xy,0])
        def words(text, xy, size=27, color=MUTED, width=6.):
            return at(self.prose(text,size,color),xy,width)
        def eq(tex, xy, size=34, color=FG, width=12.4):
            return at(self.equation(tex,size,color),xy,width)

        self.start_slide('First count ions by position AND velocity',
            'We want the electron-density field around the meteor, but a birth location alone is insufficient: '
            'an ion velocity determines where it goes. Phase space means position and velocity together. '
            'f_i is a number distribution, not a probability. The drawing is a physical-space slice; the velocity '
            'bin on the right selects all three velocity components. Colours identify velocity classes, not species.')
        self.add(words('Phase space means three position coordinates plus three velocity components.',(0,2.95),24,width=12.4))
        box=Rectangle(width=3.6,height=2.5,color=BLUE).move_to([-3.8,.7,0])
        self.play(Create(box))
        particles=VGroup()
        for x,y,d,color in [(-4.8,1.25,RIGHT,GREEN),(-3.8,1.3,UP,GOLD),(-2.9,1.,LEFT,RED),
                             (-4.6,.15,RIGHT,GREEN),(-3.5,.2,DOWN,GOLD),(-2.9,.1,RIGHT,GREEN)]:
            p=VGroup(Dot([x,y,0],radius=.07,color=color),Arrow([x+.12,y,0],np.array([x+.12,y,0])+.42*d,buff=0,color=color,stroke_width=3))
            particles.add(p)
        self.play(FadeIn(particles))
        self.add(eq(r'd^3r=dx\,dy\,dz\quad[\mathrm{m^3}]',(-3.8,-1.05),27,BLUE,5.5))
        self.add(words('Small physical volume',(-3.8,2.35),27,BLUE))
        self.add(words('Select a small velocity range',(3.1,2.35),27,GREEN))
        self.play(Write(eq(r'\mathbf v_i=(v_x,v_y,v_z)',(3.1,1.35),33,GREEN,6.)))
        self.play(Write(eq(r'd^3v_i=dv_x\,dv_y\,dv_z',(3.1,.45),33,GREEN,6.)))
        self.add(eq(r'[d^3v_i]=(\mathrm{m/s})^3',(3.1,-.35),27,MUTED,6.))
        self.add(words('Only the green velocity class is counted.',(3.1,-1.05),24,GREEN))
        self.play(Write(eq(r'dN_i=f_i(\mathbf r,\mathbf v_i,t)\,d^3r\,d^3v_i',(0,-2.05),39,BLUE)))
        self.add(eq(r'[f_i]=\mathrm{m^{-3}(m/s)^{-3}}=\mathrm{s^3m^{-6}}',(0,-2.85),27))
        self.add(eq(r'f_i:\ \text{ion phase-space number density};\quad\mathbf r:\ \text{position [m]};\quad t:\ \text{time [s]}',(0,-3.32),24,MUTED))
        self.citation('Phase-space counting: MIT 16.55 (2014), lecture 8',kinetic_url)
        self.finish()

        self.start_slide('Ionizing collisions supply a local birth rate',
            'Q_i counts all new ions per physical volume per second. It follows from target density times '
            'the volume swept out by each neutral per second. n_n is the local evaporated-neutral density, '
            'not the surface density n_0. The velocity average is replaced by a single relative speed only '
            'for a narrow hyperthermal encounter distribution. Each primary single-ionization event also creates an electron.')
        self.add(words('Ablated neutral meets atmospheric particle',(0,2.55),29,width=12.4))
        neutral=Dot([-4.3,1.1,0],radius=.13,color=GOLD)
        air=Dot([-2.5,1.1,0],radius=.13,color=BLUE)
        self.add(neutral,air)
        self.play(neutral.animate.shift(RIGHT*1.5),run_time=1.3)
        self.play(neutral.animate.set_color(RED),FadeIn(Dot([-2.1,1.8,0],radius=.06,color=GREEN)))
        self.add(words('New ion',(-3.5,.25),24,RED),eq(r'e^-',(-1.75,2.),27,GREEN,1.))
        self.add(eq(r'\text{volume swept per second}=\sigma_{\rm ion}v_{\rm rel}',(2.6,1.25),30,BLUE,6.4))
        self.add(eq(r'\text{births per neutral per second}=n_A\sigma_{\rm ion}v_{\rm rel}',(2.6,.3),29,BLUE,6.4))
        self.play(Write(eq(r'Q_i(\mathbf r)=n_n(\mathbf r)n_A\langle\sigma_{\rm ion}v_{\rm rel}\rangle',(0,-.85),37,GREEN)))
        self.play(Write(eq(r'Q_i\simeq n_n n_A\beta_{\rm Si}\sigma_c(v)v\qquad[\mathrm{m^{-3}s^{-1}}]',(0,-1.85),34)))
        self.add(eq(r'n_n,n_A:\ \mathrm{m^{-3}};\quad\sigma_{\rm ion},\sigma_c:\ \mathrm{m^2};\quad v_{\rm rel},v:\ \mathrm{m/s}',(0,-2.72),25,MUTED))
        self.add(eq(r'n_n:\ \text{local ablated-neutral density};\quad n_A:\ \text{air density}',(0,-3.25),25,MUTED))
        self.citation('Dimant and Oppenheim (2017), Part 1: ion production',do_url)
        self.finish()

        self.start_slide('The source also records the newborn ion velocities',
            'Q_i alone cannot predict spatial transport. p_b is a normalized probability density of birth '
            'velocities, conditional on position. Multiplying it by Q_i gives S_ion, ions born per unit '
            'position volume per velocity volume per second. A constant differential ionization cross section '
            'in the collision centre-of-mass frame does not imply isotropic birth velocities in the grain frame.')
        self.add(words('One collision model, many possible recoil velocities',(0,2.55),29,width=12.4))
        origin=np.array([-3.8,.65,0]);self.add(Dot(origin,color=RED,radius=.12))
        # An illustrative set of unequal velocity classes, not an angular PDF.
        for delta in [[1.35,.6,0],[1.6,.05,0],[.9,-.65,0],[.45,.95,0]]:
            self.play(GrowArrow(Arrow(origin,origin+delta,buff=.15,color=BLUE)),run_time=.25)
        self.add(words('Recoil directions and speeds',(-3.4,-.7),24,BLUE))
        self.add(words('Grain-frame velocities need not be isotropic.',(-3.4,-1.35),23,width=5.8))
        self.add(words('Birth-velocity probability density',(3.,2.0),25,BLUE,width=6.4))
        self.play(Write(eq(r'\int p_b(\mathbf v_i\mid\mathbf r)\,d^3v_i=1',(3.,1.1),32,BLUE,6.4)))
        self.play(Write(eq(r'S_{\rm ion}(\mathbf r,\mathbf v_i)=Q_i(\mathbf r)p_b(\mathbf v_i\mid\mathbf r)',(3.,-.1),33,GREEN,6.4)))
        self.add(eq(r'[p_b]=(\mathrm{m/s})^{-3}',(3.,-1.2),26,MUTED,6.4))
        self.play(Write(eq(r'dN_{\rm born}=S_{\rm ion}\,d^3r\,d^3v_i\,dt',(0,-2.2),37,GREEN)))
        self.add(eq(r'[S_{\rm ion}]=[f_i]/\mathrm{s}=\mathrm{s^2m^{-6}};\quad\int S_{\rm ion}\,d^3v_i=Q_i',(0,-3.05),27))
        self.citation('Dimant and Oppenheim (2017), Part 1: collision source',do_url)
        self.finish()

        self.start_slide('Particle conservation: accumulation = in - out + births',
            'Follow one fixed velocity bin with v_x positive. The cartoon is a spatial cell of length '
            'Delta x and face area A. Keep transverse coordinates and all velocities fixed while taking '
            'the x derivative. Ions stream in, stream out, and are born locally. There are no sinks or forces '
            'in this first-flight approximation. A is a face area here, not a radiation amplitude.')
        cell=Rectangle(width=3.2,height=1.65,color=BLUE).move_to([0,.9,0])
        self.add(cell)
        incoming=Arrow([-5.,.9,0],[-1.9,.9,0],buff=0,color=GREEN)
        outgoing=Arrow([1.9,.9,0],[5.,.9,0],buff=0,color=GOLD)
        self.play(GrowArrow(incoming),GrowArrow(outgoing))
        self.add(eq(r'f_i(x),\ v_x>0',(-3.6,1.65),27,GREEN,3.6),eq(r'f_i(x+\Delta x)',(3.6,1.65),27,GOLD,3.6))
        self.add(eq(r'A\ [\mathrm{m^2}]',(-.0,2.35),29,BLUE))
        self.add(DoubleArrow([-1.6,-.25,0],[1.6,-.25,0],buff=0,color=BLUE),eq(r'\Delta x\ [\mathrm m]',(0,-.7),27,BLUE))
        birthdots=VGroup(*[Dot([x,y,0],radius=.06,color=RED) for x,y in [(-.7,.6),(.3,1.25),(.8,.65)]])
        self.play(FadeIn(birthdots))
        self.add(words('Born inside',(0,.32),22,RED,width=2.5))
        motion=VGroup(*[Dot([-4.6,y,0],radius=.065,color=GREEN) for y in [.65,1.15]])
        self.add(motion);self.play(motion.animate.shift(8.9*RIGHT),run_time=2.5,rate_func=linear)
        self.remove(motion)
        self.play(Write(eq(r'N\simeq f_i A\Delta x\,\Delta^3v_i',(0,-1.6),36)))
        self.add(eq(r'\Delta^3v_i=\Delta v_x\Delta v_y\Delta v_z\quad[(\mathrm{m/s})^3]',(0,-2.45),27))
        self.add(words('Keep the same velocity bin on both faces: count particles, then divide by the bin size.',(0,-3.15),24,width=12.4))
        self.wait(.6)
        self.next_slide('Count the rates through the two faces',notes='Flux of the chosen velocity bin is v_x f_i Delta^3v_i. Multiply by face area, add births, then divide by the cell volume and velocity-bin volume.')
        self.play(*[FadeOut(m) for m in list(self.mobjects) if m.get_center()[1]<2.9],run_time=.3)
        # Large, separately paced balance prevents undefined differential operators.
        self.play(Write(eq(r'\frac{dN}{dt}=\underbrace{A\Delta^3v_i\,v_x f_i(x)}_{\text{in}}-\underbrace{A\Delta^3v_i\,v_x f_i(x+\Delta x)}_{\text{out}}',(0,1.7),34)))
        self.play(Write(eq(r'\hspace{1.5cm}+\underbrace{S_{\rm ion}A\Delta x\,\Delta^3v_i}_{\text{births inside}}',(0,.25),34,RED)))
        self.add(words('Divide every term by the same cell and velocity-bin volume.',(0,-1.),26,width=12.4))
        self.play(Write(eq(r'\frac{\partial f_i}{\partial t}=-v_x\frac{f_i(x+\Delta x)-f_i(x)}{\Delta x}+S_{\rm ion}',(0,-2.),35,BLUE)))
        self.add(words('As the cell becomes small, the difference quotient becomes a spatial derivative.',(0,-3.05),24,width=12.4))
        self.citation('Particle conservation: MIT 16.55 (2014), lecture 8',kinetic_url)
        self.finish()

        self.start_slide('The streaming operator is just flow through all six faces',
            'The x-face argument repeats for y and z. The directional derivative v dot grad is the rate '
            'of change caused by motion through a spatially varying distribution. A stationary pattern '
            'in the grain frame sets partial_t f to zero; individual ions still move. The simplified '
            'equation neglects postbirth forces and subsequent collisions for the near-head secondary component.')
        self.add(words('Local accumulation + net streaming out = local creation',(0,2.55),29,width=12.4))
        self.play(Write(eq(r'\partial_t f_i+v_x\partial_x f_i+v_y\partial_y f_i+v_z\partial_z f_i=S_{\rm ion}',(0,1.45),35)))
        self.play(Write(eq(r'\mathbf v_i\cdot\nabla_{\mathbf r}f_i\equiv v_x\partial_xf_i+v_y\partial_yf_i+v_z\partial_zf_i',(0,.35),34,BLUE)))
        self.add(words('A steady pattern in the moving-grain frame',(0,-.75),29,GREEN,width=12.4))
        self.play(Write(eq(r'\partial_t f_i=0\quad\Longrightarrow\quad\boxed{\mathbf v_i\cdot\nabla_{\mathbf r}f_i=S_{\rm ion}}',(0,-1.7),39,GREEN)))
        self.add(words('Constant postbirth velocity; no later collisions or forces in this approximation.',(0,-2.75),25,width=12.4))
        self.add(words('Steady density does not mean stationary ions. Both sides have units of f per second.',(0,-3.27),23,width=12.4))
        self.citation('Dimant and Oppenheim (2017), Part 1, secondary particles',do_url)
        self.finish()

        self.start_slide('Ask where an ion at this point could have been born',
            'For one fixed velocity, all possible birth positions lie on one backward straight ray. '
            'The hollow point traces earlier locations computationally; real ions travel forward along the arrow. '
            'Tau is lookback time, not negative physical motion. A different velocity would require a different ray. '
            'The source patch is illustrative and need not be homogeneous.')
        observation=np.array([4.5,.7,0]);velocity=np.array([1.,0.,0.])
        patch=Rectangle(width=3.,height=1.8,fill_color=GOLD,fill_opacity=.10,stroke_color=GOLD).move_to([-1.6,.7,0])
        self.add(patch,Line([-5.5,.7,0],observation,color=BLUE))
        self.add(Dot(observation,color=GREEN,radius=.10),eq(r'\mathbf r',(4.5,1.35),33,GREEN,1.))
        self.add(words('Ion-producing region',(-1.6,2.),26,GOLD),words('Observe here',(4.5,2.),25,GREEN,width=3.))
        physical=Arrow([-3.1,-.65,0],[.0,-.65,0],buff=0,color=BLUE)
        self.play(GrowArrow(physical))
        self.add(words('Actual ion motion',(-1.6,-1.2),24,BLUE),eq(r'\mathbf v_i',(1.,-.65),29,BLUE,1.))
        marker=Circle(.14,color=RED).move_to(observation)
        self.add(marker)
        self.add(words('Trace earlier positions',(-3.8,-2.),26,RED,width=5.))
        self.play(marker.animate.move_to(backtrace(observation,velocity,7.8)),run_time=3.,rate_func=linear)
        self.add(eq(r'\mathbf r_b(\tau)=\mathbf r-\mathbf v_i\tau,\qquad\tau\geq0',(0,-2.75),37,RED))
        self.add(words('Lookback time in seconds; subtract velocity times elapsed time to find the birth position.',(0,-3.3),22,width=12.4))
        self.citation('Characteristics of the kinetic equation: MIT 16.55, lecture 8',kinetic_url)
        self.finish()

        self.start_slide('Along that ray, the transport equation becomes ordinary calculus',
            'Apply the chain rule holding the chosen ion velocity fixed. Increasing lookback time moves '
            'opposite to the physical velocity, which explains the minus sign. The stationary transport '
            'equation then replaces v dot grad f by the source. This converts a partial differential '
            'equation to an integral along a particle trajectory.')
        self.add(words('Use the same velocity class along the whole straight path.',(0,2.55),28,width=12.4))
        self.play(Write(eq(r'\frac{d}{d\tau}f_i(\mathbf r-\mathbf v_i\tau,\mathbf v_i)=-\mathbf v_i\cdot\nabla_{\mathbf r}f_i',(0,1.35),38,BLUE)))
        self.add(words('The minus sign comes from tracing backward.',(0,.15),28,RED,width=12.4))
        self.play(Write(eq(r'\frac{d}{d\tau}f_i(\mathbf r-\mathbf v_i\tau,\mathbf v_i)=-S_{\rm ion}(\mathbf r-\mathbf v_i\tau,\mathbf v_i)',(0,-1.),37,GREEN)))
        self.add(words('Every short segment adds the ions born there to the population that can reach us.',(0,-2.25),27,width=12.4))
        self.add(eq(r'\Delta f_i\simeq S_{\rm ion}\,\Delta\tau\quad\text{when following the flow forward}',(0,-3.),30))
        self.citation('Dimant and Oppenheim (2017), Part 1: ballistic transport',do_url)
        self.finish()

        self.start_slide('The integral needs an upstream boundary condition',
            'Integrate the chain rule from zero to a finite lookback T. Keep the upstream value explicitly. '
            'The source alone does not fix the solution: there could also be ions entering from outside. '
            'For the meteoric component, impose zero incoming distribution sufficiently far upstream; '
            'a background ionosphere, if included, is a separate component. A finite boundary needs its own value.')
        self.add(eq(r'T:\ \text{finite lookback time [s]}',(0,2.7),27,MUTED))
        self.add(words('Current population = arriving population + births along the path',(0,2.05),27,width=12.4))
        self.play(Write(eq(r'f_i(\mathbf r,\mathbf v_i)=\underbrace{f_i(\mathbf r-\mathbf v_iT,\mathbf v_i)}_{\text{incoming at the earlier boundary}}',(0,.85),37,BLUE)))
        self.play(Write(eq(r'\hspace{2cm}+\int_0^T S_{\rm ion}(\mathbf r-\mathbf v_i\tau,\mathbf v_i)\,d\tau',(0,-.25),37,GREEN)))
        self.add(words('T is the finite travel time from the earlier boundary to the observation point.',(0,-1.7),26,width=12.4))
        self.add(words('A source equation alone cannot tell us whether ions were already coming in.',(0,-2.7),27,BLUE,width=12.4))
        self.wait(.6)
        self.next_slide('Remove the incoming term only with a stated boundary condition',notes='For the meteoric component, f tends to zero far upstream and the source integral converges. The infinite upper limit includes the whole earlier ray, not an infinite local production time.')
        self.play(*[FadeOut(m) for m in list(self.mobjects) if m.get_center()[1]<2.9],run_time=.3)
        self.add(words('No incoming meteoric ions far upstream; the source integral converges.',(0,2.4),28,width=12.4))
        self.play(Write(eq(r'\boxed{f_i(\mathbf r,\mathbf v_i)=\int_0^\infty S_{\rm ion}(\mathbf r-\mathbf v_i\tau,\mathbf v_i)\,d\tau}',(0,.95),40,GREEN)))
        self.add(words('Look backward along one trajectory and add its source contributions.',(0,-.55),28,width=12.4))
        self.add(words('The infinite limit includes the entire earlier source region.',(0,-1.6),27,width=12.4))
        self.add(words('It does not mean ions accumulate at this point forever.',(0,-2.45),27,BLUE,width=12.4))
        self.add(eq(r'[S_{\rm ion}]\,\mathrm s=[f_i]',(0,-3.15),29,MUTED))
        self.citation('Source integration of ballistic ions: DO (2017), Part 1',do_url)
        self.finish()

        self.start_slide('Why integrate over time? It measures residence in the source',
            'Approximate the integral by short source segments. A velocity class crossing length Delta ell '
            'spends Delta tau = Delta ell / V there. Therefore each segment adds S Delta ell / V to f. '
            'Holding the source fixed, faster particles spend less time in the same region and have a smaller '
            'steady population. V is the ion speed in the grain frame, not the meteoroid atmospheric speed v.')
        self.add(words('Each earlier path segment contributes source rate times time spent there.',(0,2.55),28,width=12.4))
        for j in range(6):
            segment=Rectangle(width=1.1,height=.8,color=GOLD,fill_opacity=.08).move_to([-3.3+j*1.1,1.,0])
            self.play(FadeIn(segment),run_time=.15)
        self.add(Arrow([-4.3,-.1,0],[4.3,-.1,0],buff=0,color=BLUE))
        self.add(eq(r'V=|\mathbf v_i|\quad[\mathrm{m/s}]',(0,-.65),29,BLUE))
        self.play(Write(eq(r'\Delta\tau=\frac{\Delta\ell}{V},\qquad\Delta f_i\simeq S_{\rm ion}\Delta\tau',(0,-1.65),38)))
        self.play(Write(eq(r'f_i=\int_{\rm upstream}^{\mathbf r}\frac{S_{\rm ion}}{V}\,d\ell',(0,-2.8),37,GREEN)))
        self.citation('Ballistic characteristics: MIT 16.55 (2014), lecture 8',kinetic_url)
        self.finish()

        self.start_slide('Density means adding all velocities at the same location',
            'Now sum velocity classes in one physical volume, without summing over space. Each bin '
            'contributes f Delta^3v to the local number density. The sum becomes a velocity integral '
            'as bins shrink. This is number counting, not a new plasma model. Quasineutrality is a separate '
            'near-head assumption that lets the single-charge ion density approximate electron density.')
        self.add(words('Keep this physical cell fixed; include every velocity class.',(0,2.55),28,width=12.4))
        colors=[GREEN,GOLD,BLUE,RED]
        for j,color in enumerate(colors):
            x=-4.5+3*j
            self.add(Rectangle(width=2.2,height=1.,color=color).move_to([x,1.05,0]))
            self.play(FadeIn(eq(r'f_i(\mathbf r,\mathbf v_{%d})\,\Delta^3v_i'%j,(x,1.05),26,color,2.)) ,run_time=.25)
        self.play(Write(eq(r'n_i(\mathbf r)\simeq\sum_k f_i(\mathbf r,\mathbf v_k)\,\Delta^3v_i',(0,-.35),38,BLUE)))
        self.play(Write(eq(r'\boxed{n_i(\mathbf r)=\int_{\mathbb R^3}f_i(\mathbf r,\mathbf v_i)\,d^3v_i}',(0,-1.55),40,GREEN)))
        self.add(eq(r'[f_i](\mathrm{m/s})^3=\mathrm{m^{-3}}',(0,-2.55),29))
        self.add(eq(r'n_e\simeq n_i\quad\text{for singly charged, quasineutral near-head plasma}',(0,-3.2),26,MUTED))
        self.citation('Velocity moments: MIT 16.55, lecture 8; DO (2017), Part 2',kinetic_url)
        self.finish()

        self.start_slide('A simple source slab makes the integral tangible',
            'Teaching example only: one-dimensional constant-area flow, one ion speed, uniform volume '
            'birth rate inside a slab, no loss and no incoming ions. dn/dx = Q_0/V inside and zero outside. '
            'Unlike a real meteor cloud, this example has no geometric spreading. The downstream flat '
            'profile belongs only to this example. The numbers are illustrative, not a DO or MSIS prediction.')
        axes=Axes(x_range=[-.5,1.6,.5],y_range=[0,1.5,.5],x_length=6.,y_length=2.7,
            axis_config={'color':MUTED,'include_ticks':True,'include_tip':False}).move_to([-3.2,.75,0])
        slab=Polygon(axes.c2p(0,0),axes.c2p(1,0),axes.c2p(1,1.4),axes.c2p(0,1.4),
            stroke_width=0,fill_color=GOLD,fill_opacity=.10)
        x=np.linspace(-.5,1.6,140)
        curve=VMobject(color=GREEN,stroke_width=4).set_points_as_corners([axes.c2p(a,b) for a,b in zip(x,slab_density(x,1e3,1e10)/1e7)])
        axes.x_axis.add_numbers([0,1],font_size=24,color=MUTED)
        axes.y_axis.add_numbers([1],font_size=24,color=MUTED)
        self.add(axes,slab)
        self.add(eq(r'x\ [\mathrm m]',(-3.2,-1.),25),eq(r'n_i/(10^7\,\mathrm{m^{-3}})',(-3.2,2.55),25,GREEN))
        self.play(Create(curve),run_time=2.)
        self.add(words('Uniform births only in the shaded slab',(-3.2,-1.65),23,GOLD,width=6.))
        rows=self.term_definitions([
            r'Q_0=10^{10}\ \mathrm{m^{-3}s^{-1}}',r'L=1\ \mathrm m,\quad V=10^3\ \mathrm{m/s}',
            r'V\frac{dn_i}{dx}=Q_0\quad(0<x<L)',r'n_{\rm out}=\frac{Q_0L}{V}=10^7\ \mathrm{m^{-3}}'],[3.3,.45,0],30,6.)
        for row in rows:self.play(Write(row))
        self.add(words('Constant-area, single-speed teaching example; no geometric spreading.',(0,-2.65),25,width=12.4))
        self.add(words('Double V at fixed Q and L: half the time in the source, half the steady density.',(0,-3.25),25,GREEN,width=12.4))
        self.finish()

        self.start_slide('The factor V squared is a velocity-space volume',
            'The drawing is a slice through velocity space, not an ion trajectory or physical plasma shape. '
            'A shell at speed V has surface area 4 pi V squared. A solid-angle patch occupies area '
            'V squared dOmega_v; multiply by radial thickness dV to get its small velocity volume. '
            'Angles here specify grain-frame velocity direction; they are not collision centre-of-mass scattering angles.')
        c=np.array([-3.8,.4,0]);radius=1.55
        self.add(Circle(radius,color=BLUE).move_to(c),Circle(radius+.22,color=BLUE,stroke_opacity=.5).move_to(c))
        wedge=AnnularSector(inner_radius=radius,outer_radius=radius+.22,angle=.60,start_angle=.30,
            color=GOLD,fill_opacity=.55,stroke_width=1).shift(c)
        self.play(FadeIn(wedge))
        self.add(Dot(c,color=FG,radius=.045),Arrow(c,c+radius*np.array([np.cos(.6),np.sin(.6),0]),buff=0,color=GREEN))
        self.add(eq(r'V=|\mathbf v_i|',(-3.8,-.35),29,GREEN,3.))
        self.add(eq(r'dV',(-1.65,1.7),27,GOLD,1.),words('Slice of a 3D velocity shell',(-3.8,2.65),25,BLUE,width=5.7))
        self.add(words('All axes are velocities, not metres.',(-3.8,-1.7),23,width=6.))
        rows=self.term_definitions([r'\text{shell patch area}=V^2\,d\Omega_v',r'\text{radial thickness}=dV',
            r'\boxed{d^3v_i=V^2\,dV\,d\Omega_v}',r'[d^3v_i]=(\mathrm{m/s})^3'],[3.2,.55,0],31,6.)
        for row in rows:self.play(Write(row))
        self.add(eq(r'd\Omega_v=\sin\vartheta_v\,d\vartheta_v\,d\varphi_v\quad[\mathrm{sr}]',(0,-2.6),31))
        self.add(eq(r'\vartheta_v,\varphi_v:\ \text{velocity polar and azimuthal angles [rad]};\quad dV:\ \mathrm{m/s}',(0,-3.2),24,MUTED))
        self.citation('Velocity-space integration: DO (2017), Part 2, equation 10','https://doi.org/10.1002/2017JA023963')
        self.finish()

        self.start_slide('Sum the whole velocity shell, without assuming isotropy',
            'Integrate the radial speeds from zero to infinity and the velocity directions over the whole '
            'sphere. The V squared factor is the spherical-coordinate Jacobian. f can depend on direction. '
            'Only an isotropic f in this same grain frame permits replacing the angular integral by 4 pi. '
            'This counting measure is what enters the next recoil-kinematics mass-ratio derivation.')
        self.add(words('Different directions can contain different numbers of ions.',(0,2.55),29,width=12.4))
        self.play(Write(eq(r'n_i(\mathbf r)=\int_0^\infty\!\int_{4\pi}f_i(\mathbf r,V,\Omega_v)\,V^2\,d\Omega_v\,dV',(0,1.15),39,GREEN)))
        self.add(words('Speed: every V from zero upward. Direction: every point on the velocity sphere.',(0,-.3),27,width=12.4))
        self.play(Write(eq(r'\int_{4\pi}f_i\,d\Omega_v=4\pi f_i\quad\text{only if }f_i\text{ is isotropic}',(0,-1.5),34,RED)))
        self.add(words('An isotropic collision cross section does not guarantee an isotropic grain-frame distribution.',(0,-2.65),25,width=12.4))
        self.add(words('Next: use the recoil speeds supplied by two-body collision kinematics.',(0,-3.25),25,BLUE,width=12.4))
        self.citation('Dimant and Oppenheim (2017), Part 2, equations 3 and 10','https://doi.org/10.1002/2017JA023963')
        self.finish()

        self.start_slide('Why show these equations? They connect births to the radar target',
            'The ablation and collision model supplies a source, the kinetic equation transports it, and '
            'the velocity integral counts the ions at each position. Quasineutrality gives electron density '
            'for the near-head component. DO evaluates these integrals with its source and collision kinematics. '
            'This is why a collision model can predict a spatial electron-density field for the EM calculation.')
        stages=[('COLLISIONS',r'S_{\rm ion}(\mathbf r,\mathbf v_i)','Where and how fast ions are born',GOLD),
                ('TRANSPORT',r'f_i=\int_{\rm past}S_{\rm ion}\,d\tau','Which births can reach this point',BLUE),
                ('COUNT',r'n_i=\int f_i\,d^3v_i','All velocities at the same place',GREEN)]
        for j,(label,formula,caption,color) in enumerate(stages):
            y=2.1-j*1.5
            self.play(FadeIn(words(label,(-4.8,y),27,color,width=3.)))
            self.play(Write(eq(formula,(0,y),34,color,5.)))
            self.add(words(caption,(4.5,y),23,width=4.))
        self.play(Write(eq(r'n_e(\mathbf r)\simeq n_i(\mathbf r)\quad\longrightarrow\quad\text{plasma response and radar scattering}',(0,-2.35),34,GREEN)))
        self.add(words('DO evaluates the source and trajectory integrals; it does not postulate a cloud shape.',(0,-3.2),25,width=12.4))
        self.citation('Dimant and Oppenheim (2017), Parts 1 and 2','https://doi.org/10.1002/2017JA023963')
        self.finish()

    def recoil_mass_derivation(self):
        # Elastic heavy-particle kinematics and a transparent directional source
        # slab explain the explicit mass factors of DO Part 2 Eqs. 3 and 11.
        # The slab is not a substitute for DO's nonuniform trajectory integrals.
        from meteor_rcs.kinetic_transport import cold_recoil
        paper1='https://doi.org/10.1002/2017JA023960'
        paper2='https://doi.org/10.1002/2017JA023963'
        def place(item,xy,width=6.):
            if item.width>width:item.scale_to_fit_width(width)
            return item.move_to([*xy,0])
        def words(text,xy,size=27,color=MUTED,width=6.):
            return place(self.prose(text,size,color),xy,width)
        def eq(tex,xy,size=35,color=FG,width=12.4):
            return place(self.equation(tex,size,color),xy,width)

        self.start_slide('Why does particle mass affect the plasma density?',
            'The preceding transport calculation needs the newborn ion velocities. Collision mechanics supplies '
            'them. Work in the grain frame: atmospheric particles stream past, and the freshly evaporated '
            'meteor atom has only a small thermal velocity. Set that initial velocity to zero to derive the '
            'leading recoil relation. The ionization probability remains in the source model; here we neglect '
            'ionization energy only in the heavy-particle mechanical energy balance.')
        self.add(words('We need the recoil speed to calculate how long an ion stays near the grain.',(0,2.6),29,width=12.4))
        air=Dot([-5.,.9,0],color=BLUE,radius=.13)
        target=Dot([-2.8,.9,0],color=GOLD,radius=.15)
        self.add(air,target,Arrow([-5.,.2,0],[-3.1,.2,0],buff=0,color=BLUE))
        self.add(words('Incoming air',(-4.9,1.85),25,BLUE,width=3.),words('Evaporated atom',(-2.1,1.85),25,GOLD,width=3.))
        self.add(eq(r'v\hat{\mathbf z}',(-4.,-.35),30,BLUE,width=2.))
        self.add(words('The grain frame',(-3.8,-1.15),26,width=5.))
        rows=self.term_definitions([r'm_A:\ \text{representative air-particle mass [kg]}',
            r'm_{\rm Si}:\ \text{mass of one vapor atom [kg]}',
            r'v:\ \text{incoming air speed [m/s]}',r'V_T\ll v:\ \text{initial vapor motion is small}'],[3.,.75,0],27,6.4)
        for row in rows:self.play(FadeIn(row),run_time=.35)
        self.add(eq(r'\hat{\mathbf z}:\ \text{unit vector along the incoming air stream [dimensionless]}',(0,-1.7),25,MUTED))
        self.add(words('Small ionization losses are neglected in the heavy-particle energy balance.',(0,-2.4),26,width=12.4))
        self.add(words('This requires collision energy well above the losses; very slow recoils need more care.',(0,-3.15),25,BLUE,width=12.4))
        self.citation('Dimant and Oppenheim (2017), Part 1, section 6.1',paper1)
        self.finish()

        self.start_slide('A collision redistributes momentum and kinetic energy',
            'The air particle has velocity u_A after collision and the meteor ion has velocity V. '
            'The direction z-hat is along the incoming air stream, hence opposite to the meteor velocity. '
            'V is the speed magnitude. Vartheta is the recoil angle to the air stream, not a spatial '
            'position angle and not the centre-of-mass scattering angle. The drawn example uses equal masses '
            'and a 35-degree recoil, with both outgoing velocities calculated from conservation.')
        origin=np.array([-3.8,.55,0]);angle=35*DEGREES
        ion_v,air_v=cold_recoil(1.,1.,angle)
        self.add(Arrow([-6.1,.55,0],origin,buff=.15,color=BLUE),Dot(origin,color=GOLD,radius=.10))
        self.play(GrowArrow(Arrow(origin,origin+2.1*np.array([ion_v[0],ion_v[1],0]),buff=.1,color=RED)),
                  GrowArrow(Arrow(origin,origin+2.1*np.array([air_v[0],air_v[1],0]),buff=.1,color=BLUE)))
        self.add(eq(r'\mathbf V',(-2.35,2.),31,RED,width=1.4),eq(r'\mathbf u_A',(-2.9,-1.05),31,BLUE,width=1.6))
        self.add(DashedLine(origin,origin+RIGHT*2.5,color=MUTED,stroke_width=2))
        self.play(Create(Arc(radius=.6,start_angle=0,angle=angle,color=GREEN).shift(origin)))
        self.add(eq(r'\vartheta',(-2.9,.83),27,GREEN,width=1.),eq(r'\hat{\mathbf z}',(-1.35,.1),26,width=1.))
        self.add(words('After collision',(-4.,-1.6),25,width=5.5))
        rows=self.term_definitions([r'\mathbf V:\ \text{ion velocity [m/s]},\quad V=|\mathbf V|',
            r'\mathbf u_A:\ \text{outgoing air velocity [m/s]}',r'\vartheta=\angle(\mathbf V,\hat{\mathbf z})\quad[\mathrm{rad}]',
            r'\mathbf V\cdot\hat{\mathbf z}=V\cos\vartheta'],[3.1,.85,0],28,6.4)
        for row in rows:self.play(FadeIn(row),run_time=.3)
        self.play(Write(eq(r'\underbrace{m_Av\hat{\mathbf z}}_{\text{incoming momentum}}=\underbrace{m_A\mathbf u_A+m_{\rm Si}\mathbf V}_{\text{outgoing momentum}}',(0,-2.45),35,BLUE)))
        self.citation('Two-body collision mechanics: DO (2017), Part 1, section 6.1',paper1)
        self.finish()

        self.start_slide('Eliminate the unknown outgoing air velocity',
            'Momentum conservation expresses u_A in terms of the ion velocity. Substitute this expression '
            'in the kinetic-energy balance. Expanding the squared vector gives the cross term '
            '-2(m_Si/m_A)vV cos(vartheta). The squared magnitude and dot product are why the angle enters. '
            'All velocities refer to the same grain frame and the initial vapor-atom velocity is approximated as zero.')
        self.add(words('Momentum gives the air velocity; energy determines the recoil speed.',(0,2.65),28,width=12.4))
        self.play(Write(eq(r'\mathbf u_A=v\hat{\mathbf z}-\frac{m_{\rm Si}}{m_A}\mathbf V',(0,1.55),40,BLUE)))
        self.play(Write(eq(r'\frac12m_Av^2=\frac12m_A|\mathbf u_A|^2+\frac12m_{\rm Si}V^2',(0,.3),39,GREEN)))
        self.add(words('Substitute and divide by the incoming air mass.',(0,-.85),27,width=12.4))
        self.play(Write(eq(r'v^2=\left|v\hat{\mathbf z}-\frac{m_{\rm Si}}{m_A}\mathbf V\right|^2+\frac{m_{\rm Si}}{m_A}V^2',(0,-1.95),38)))
        self.add(words('Each kinetic-energy term has units of joules before division by mass.',(0,-3.1),25,width=12.4))
        self.citation('Conservation of momentum and energy: DO (2017), Part 1',paper1)
        self.finish()

        self.start_slide('The recoil formula follows from the cross term',
            'Expand the squared air velocity. Cancel v squared from both sides and divide by the positive '
            'mass ratio. For nonzero recoil V, divide by V to obtain the published cold-target speed-angle '
            'relation. Positive speeds require cos(vartheta)>0. Zero recoil is the no-transfer endpoint.')
        self.add(words('Expand the squared vector, then cancel the incoming kinetic-energy term.',(0,2.65),28,width=12.4))
        self.play(Write(eq(r'0=-2\frac{m_{\rm Si}}{m_A}vV\cos\vartheta+\left[\left(\frac{m_{\rm Si}}{m_A}\right)^2+\frac{m_{\rm Si}}{m_A}\right]V^2',(0,1.45),36)))
        self.play(Write(eq(r'2v\cos\vartheta=\left(1+\frac{m_{\rm Si}}{m_A}\right)V\qquad(V>0)',(0,.05),39,BLUE)))
        self.play(Write(eq(r'\boxed{V=\frac{2m_A}{m_{\rm Si}+m_A}\,v\cos\vartheta}',(0,-1.45),43,GREEN)))
        self.add(eq(r'0\leq\vartheta<\pi/2:\quad\text{recoil is into the forward air-stream hemisphere}',(0,-2.75),28))
        self.add(words('The ion can leave at many angles; its speed is tied to its chosen direction.',(0,-3.3),24,width=12.4))
        self.citation('DO (2017), Part 1, section 6.1; Part 2, equation 3',paper1)
        self.finish()

        self.start_slide('Head-on examples: a heavier vapor atom recoils more slowly',
            'Three illustrative head-on collisions use the same incident speed and three mass ratios. '
            'All outgoing velocities conserve both momentum and kinetic energy in the stated elastic '
            'heavy-particle approximation. Circle sizes are schematic; labels give the mass ratios. '
            'The equal-mass target takes the air-particle speed and the air particle stops.')
        self.add(eq(r'\vartheta=0,\qquad V=\frac{2v}{1+m_{\rm Si}/m_A}',(0,2.6),37,BLUE))
        for j,ratio in enumerate([1/3,1.,3.]):
            y=1.15-1.45*j
            target=Dot([-2.2,y,0],radius=.13*ratio**(1/3),color=GOLD)
            air=Dot([-4.,y,0],radius=.13,color=BLUE)
            ion_v,air_v=cold_recoil(1.,ratio,0.)
            self.add(target,air,eq(r'm_{\rm Si}/m_A='+['1/3','1','3'][j],(-5.3,y+.55),26,width=3.))
            self.play(air.animate.move_to([-2.46,y,0]),run_time=.65,rate_func=linear)
            self.play(target.animate.set_color(RED).shift(1.8*ion_v[0]*RIGHT),
                      air.animate.shift(1.8*air_v[0]*RIGHT),run_time=1.4,rate_func=linear)
            self.add(eq(r'V/v='+['1.5','1','0.5'][j],(3.5,y+.25),31,RED,width=3.),
                     eq(r'u_{A,z}/v='+['0.5','0','-0.5'][j],(3.5,y-.35),27,BLUE,width=3.))
        self.add(words('Same incoming speed; different masses partition momentum and energy differently.',(0,-3.1),26,width=12.4))
        self.citation('Elastic heavy-particle kinematics: DO (2017), Part 1, section 6.1',paper1)
        self.finish()

        self.start_slide('The allowed velocities lie on a shifted sphere',
            'Introduce alpha, the air mass fraction of the collision pair. Complete the square in the '
            'recoil relation to show a sphere in three-dimensional velocity space. Its center and radius '
            'are both alpha v. This is the Galilean shift of the constant-speed center-of-mass sphere. '
            'The diagram is a two-dimensional slice through that sphere; it is not a physical cloud surface.')
        self.add(eq(r'\alpha\equiv\frac{m_A}{m_{\rm Si}+m_A}=\frac{1}{1+m_{\rm Si}/m_A}\quad\text{[dimensionless]}',(0,2.65),32,BLUE))
        c=np.array([-3.8,.45,0]);radius=1.35;zero=c-radius*RIGHT
        self.add(Circle(radius,color=BLUE).move_to(c),Dot(c,color=BLUE,radius=.04),Dot(zero,color=FG,radius=.045),
            Arrow(zero+LEFT*.3,zero+RIGHT*3.3,buff=0,color=MUTED,stroke_width=2))
        angle=35*DEGREES
        end=zero+2*radius*np.cos(angle)*np.array([np.cos(angle),np.sin(angle),0])
        self.play(GrowArrow(Arrow(zero,end,buff=0,color=RED)))
        self.add(eq(r'0',(zero[0]-.22,zero[1]-.45),25,width=.7),
                 eq(r'\alpha v',(-3.8,-.1),27,BLUE,width=2.),
                 eq(r'V_z\ [\mathrm{m/s}]',(-2.,-.25),24,width=2.5))
        self.add(words('Slice of the 3D velocity sphere',(-3.8,2.05),24,BLUE,width=5.8))
        self.add(words('Red: an allowed ion velocity',(-3.8,-1.4),24,RED,width=5.8))
        rows=self.term_definitions([r'V^2=2\alpha v V_z',r'V_x^2+V_y^2+(V_z-\alpha v)^2=(\alpha v)^2',
            r'\text{center}=\alpha v\hat{\mathbf z}',r'\text{radius}=\alpha v'],[3.2,.5,0],30,6.2)
        for row in rows:self.play(Write(row))
        self.add(words('Changing the mass fraction scales all recoil speeds by the same factor.',(0,-2.5),27,width=12.4))
        self.add(words('Isotropic scattering in the center-of-mass frame still gives a shifted sphere here.',(0,-3.2),25,width=12.4))
        self.citation('DO (2017), Part 1: the collision shell in velocity space',paper1)
        self.finish()

        self.start_slide('The delta function represents a narrowly selected recoil speed',
            'Fix the recoil direction. The cold-target relation allows one speed V_0, so the distribution '
            'is narrow in speed. A unit-area rectangular kernel illustrates the delta function: as its '
            'speed width epsilon shrinks its height grows as one over epsilon. This is a distribution '
            'under an integral, not a literal infinite particle population. Thermal motion gives a finite shell thickness.')
        self.add(eq(r'V_0=2\alpha v\cos\vartheta:\quad\text{allowed speed in this direction [m/s]}',(0,2.65),32,BLUE))
        origin=np.array([-5.2,-.55,0]);center=origin+2.2*RIGHT
        self.add(Arrow(origin+LEFT*.2,origin+RIGHT*4.8,buff=0,color=MUTED,stroke_width=2),
                 Arrow(origin+DOWN*.1,origin+UP*2.8,buff=0,color=MUTED,stroke_width=2))
        self.add(eq(r'V\ [\mathrm{m/s}]',(-1.1,-1.1),25,width=2.),eq(r'\delta_\epsilon\ [\mathrm{s/m}]',(-5.85,.7),24,width=2.8).rotate(PI/2))
        self.add(eq(r'V_0',(-3.,-1.1),28,BLUE,width=1.))
        def kernel(width):
            height=1./width
            return Polygon(center+LEFT*width/2,center+LEFT*width/2+UP*height,
                center+RIGHT*width/2+UP*height,center+RIGHT*width/2,
                color=GREEN,fill_opacity=.15)
        box=kernel(1.3);self.play(Create(box))
        self.play(Transform(box,kernel(.75)),run_time=1.2)
        self.play(Transform(box,kernel(.45)),run_time=1.2)
        rows=self.term_definitions([r'\text{width}=\epsilon\quad[\mathrm{m/s}]',r'\text{height}=1/\epsilon\quad[\mathrm{s/m}]',
            r'\int\delta_\epsilon(V-V_0)\,dV=1',r'\epsilon\to0:\quad\delta_\epsilon\to\delta'],[3.15,.7,0],30,6.1)
        for row in rows:self.play(Write(row))
        self.add(words('A narrower speed range gives a taller curve with the same unit area.',(0,-2.25),28,GREEN,width=12.4))
        self.add(words('Finite initial thermal motion broadens the idealized shell.',(0,-3.15),26,width=12.4))
        self.citation('DO (2017), Part 1, thin-shell approximation; Part 2, equation 3',paper1)
        self.finish()

        self.start_slide('Integrating the delta function means evaluating at the allowed speed',
            'For V_0 positive, the delta function samples the integrand at V_0. Applied to V squared, '
            'this gives V_0 squared. The derivative of the argument V-V_0 with respect to V is one, '
            'so there is no extra mass factor in this particular delta integration. A scaled argument '
            'would require its derivative factor. The speed-volume factor was derived in the preceding section.')
        self.add(eq(r'g(V):\ \text{a smooth weighting function of speed}',(0,2.65),30,BLUE))
        self.play(Write(eq(r'\int_0^\infty g(V)\,\delta(V-V_0)\,dV=g(V_0)\qquad(V_0>0)',(0,1.4),37,BLUE)))
        self.add(words('Use the velocity-space counting weight as the function being sampled.',(0,.05),27,width=12.4))
        self.play(Write(eq(r'\boxed{\int_0^\infty V^2\delta(V-V_0)\,dV=V_0^2=4\alpha^2v^2\cos^2\vartheta}',(0,-1.3),37,GREEN)))
        self.add(eq(r'\frac{d}{dV}(V-V_0)=1:\quad\text{no hidden factor from this delta argument}',(0,-2.4),29))
        self.add(words('Velocity-space counting supplies two powers of the recoil speed.',(0,-3.15),25,width=12.4))
        self.citation('DO (2017), Part 2, speed integration in equations 10--11',paper2)
        self.finish()

        self.start_slide('Where do the first TWO inverse-speed powers come from?',
            'Define Q_Omega as the local production rate per velocity solid angle. Hold this directional '
            'birth rate fixed while tracking the explicit recoil mass dependence. Integrating S over V '
            'with the V squared measure must return Q_Omega. Therefore the delta-shell source has a '
            'coefficient Q_Omega/V_0 squared. This is number conservation in velocity space, not an '
            'extra physical enhancement of ionization. Its angular weighting is supplied by the collision model.')
        self.add(words('Count births into one chosen direction before transporting them.',(0,2.65),29,width=12.4))
        self.add(eq(r'Q_\Omega(\mathbf r,\Omega_v):\quad\text{births per volume, per second, per solid angle}',(0,1.7),29,BLUE))
        self.add(eq(r'[Q_\Omega]=\mathrm{m^{-3}s^{-1}sr^{-1}},\qquad\int Q_\Omega\,d\Omega_v=Q_i',(0,.85),29))
        self.play(Write(eq(r'Q_\Omega=\int_0^\infty S_{\rm ion}(\mathbf r,V,\Omega_v)\,V^2\,dV',(0,-.25),36)))
        self.play(Write(eq(r'\boxed{S_{\rm ion}=\frac{Q_\Omega}{V_0^2}\,\delta(V-V_0)}\quad\Longrightarrow\quad V_0^{-2}\propto\alpha^{-2}',(0,-1.65),37,GREEN)))
        self.add(words('The same births occupy a smaller velocity shell as recoil speeds decrease.',(0,-2.65),25,width=12.4))
        self.add(words('Direction weighting comes from the collision model.',(0,-3.3),25,width=12.4))
        self.citation('Velocity-space source counting; DO (2017), Part 1, section 6',paper1)
        self.finish()

        self.start_slide('The THIRD inverse-speed power is time spent in the source',
            'Use the preceding characteristic solution. A simple constant-area source segment with length '
            'L and uniform directional birth rate Q_Omega contributes S times L/V. The delta restricts '
            'V to V_0, so the coefficient becomes Q_Omega L/V_0 cubed. The real DO calculation integrates '
            'a spatially varying source along the paths. At fixed direction and fixed source geometry, '
            'that integration preserves the same explicit recoil mass power.')
        self.add(words('Use the same straight-path transport derived in the preceding section.',(0,2.65),28,width=12.4))
        slab=Rectangle(width=3.2,height=.8,color=GOLD,fill_opacity=.1).move_to([-3.8,.65,0])
        self.add(slab,Arrow([-5.8,-.25,0],[-1.7,-.25,0],buff=0,color=BLUE),
            eq(r'L:\ \text{source length [m]}',(-3.8,1.5),27,GOLD,width=5.8),eq(r'\text{travel time}=L/V_0',(-3.8,-1.05),30,BLUE,width=5.8))
        rows=self.term_definitions([r'f_i=\int S_{\rm ion}\,dt=\int\frac{S_{\rm ion}}V\,d\ell',
            r'\text{uniform source segment: }f_i=\frac{L}{V}S_{\rm ion}',
            r'\boxed{f_i=\frac{Q_\Omega L}{V_0^3}\delta(V-V_0)}'],[3.15,.55,0],31,6.4)
        for row in rows:self.play(Write(row))
        self.play(Write(eq(r'\underbrace{\alpha^{-2}}_{\text{source per velocity volume}}\ \underbrace{\alpha^{-1}}_{\text{residence time}}=\alpha^{-3}=\left(1+\frac{m_{\rm Si}}{m_A}\right)^3',(0,-2.15),34,GREEN)))
        self.add(words('Keep incoming speed, direction, birth rate and source geometry fixed.',(0,-3.3),24,width=12.4))
        self.citation('Ballistic source integration: DO (2017), Part 1, section 6.3',paper1)
        self.finish()

        self.start_slide('Counting velocities removes two powers and leaves residence time',
            'The directional ion density n_Omega equals the speed integral of f V squared. The source '
            'normalization and speed-volume measure cancel, leaving Q_Omega times the crossing time L/V_0. '
            'This is precisely the source-slab residence-time reasoning from the preceding transport section. '
            'Integrating the actual source along the trajectory, and then over directions, gives the DO field. '
            'Only the explicit kinematic mass dependence is being isolated here; real cross sections and '
            'thermal source geometry can also depend on composition.')
        self.add(eq(r'n_\Omega\equiv\frac{dn_i}{d\Omega_v}\quad[\mathrm{m^{-3}sr^{-1}}]',(0,2.65),33,BLUE))
        self.play(Write(eq(r'n_\Omega=\int_0^\infty f_iV^2\,dV=\frac{Q_\Omega L}{V_0^3}\underbrace{\int_0^\infty V^2\delta(V-V_0)\,dV}_{V_0^2}',(0,1.2),36)))
        self.play(Write(eq(r'\boxed{n_\Omega=Q_\Omega\frac{L}{V_0}=\frac{Q_\Omega L}{2v\cos\vartheta}\left(1+\frac{m_{\rm Si}}{m_A}\right)}',(0,-.65),39,GREEN)))
        self.add(words('Density = production rate into this direction times time spent crossing the source.',(0,-2.1),27,width=12.4))
        self.add(eq(r'\alpha^{-3}\alpha^2=\alpha^{-1}=1+\frac{m_{\rm Si}}{m_A}',(0,-3.05),35,BLUE))
        self.citation('Explicit mass dependence: DO (2017), Part 2, equations 3 and 11',paper2)
        self.finish()

        self.start_slide('Now the mass factor in the DO density has a physical origin',
            'The recoil relation sets the speed shell; phase-space normalization gives two inverse-speed '
            'powers in the source; ballistic transport adds one; the density measure removes two. '
            'The remaining first power is a residence-time factor. DO evaluates the nonuniform source '
            'and angular integrals, giving the coefficient used on the next slides. The derivation assumes '
            'small initial thermal speed and negligible ionization energy in the heavy-particle balance. '
            'It becomes weak for very slow recoil at nearly 90 degrees. Changing actual composition also '
            'changes cross sections, ionization, and thermal properties, so the isolated factor is not the whole trend.')
        stages=[('COLLISION',r'V_0=2\alpha v\cos\vartheta','Masses set recoil speed',BLUE),
                ('VELOCITY COUNTING',r'\text{source amplitude}\propto\alpha^{-2}','Same births in a smaller speed shell',GOLD),
                ('TRANSPORT',r'\text{shell amplitude}\propto\alpha^{-3}','Slower ions spend longer near the source',RED),
                ('DENSITY',r'\int f_iV^2dV\propto\alpha^{-1}','One residence-time factor remains',GREEN)]
        for j,(label,formula,caption,color) in enumerate(stages):
            y=2.25-j*1.1
            self.play(FadeIn(words(label,(-4.7,y),24,color,width=3.8)),Write(eq(formula,(0,y),31,color,width=4.6)))
            self.add(words(caption,(4.55,y),23,width=4.2))
        self.add(words('Fixed source and collision law: the explicit factor is 1 + meteor-ion mass / air-particle mass.',(0,-2.6),25,width=12.4))
        self.add(words('Next: insert the DO coefficient, then replace the unknown surface density with ablation rate.',(0,-3.25),24,BLUE,width=12.4))
        self.citation('Dimant and Oppenheim (2017), Part 2, equations 3, 11 and 45',paper2)
        self.finish()

    def normalization(self):
        # DO Part 1 Eq. 18 outgoing half-Maxwellian and surface flux; Part 2
        # Eq. 45. Keep its n0 convention, including sqrt(2/pi), throughout.
        self.start_slide('Count the neutral atoms leaving the hot surface',
            'n0 is the outgoing ablated-neutral number density at the surface in the DO boundary condition. '
            'Its normal velocity follows a half-Maxwellian. J_R0 is a flux per square metre, not a volume density. '
            'The coefficient sqrt(2/pi) comes from the mean positive normal speed with this outgoing-density convention.')
        center=np.array([-4.,.6,0]);grain=Circle(.7,color=GOLD,fill_opacity=.15).move_to(center)
        self.play(Create(grain))
        directions=[np.array([np.cos(a),np.sin(a),0]) for a in np.linspace(-PI,PI,10,endpoint=False)]
        particles=VGroup(*[Dot(center+.75*d,radius=.045,color=GREEN) for d in directions])
        self.add(particles)
        self.play(*[p.animate.shift(.65*d) for p,d in zip(particles,directions)],run_time=1.3)
        normal=Arrow(center+.7*RIGHT,center+1.5*RIGHT,buff=0,color=BLUE)
        self.play(GrowArrow(normal));self.add(self.equation(r'V_n>0',26,BLUE).next_to(normal,DOWN,buff=.2))
        rows=self.term_definitions([
            r'J_{R0}=n_0\langle V_n\rangle\quad[\mathrm{m^{-2}s^{-1}}]',
            r'p(V_n)=\frac{\sqrt{2/\pi}}{V_T}e^{-V_n^2/(2V_T^2)},\quad V_n>0',
            r'\langle V_n\rangle=\int_0^\infty V_n p(V_n)\,dV_n=\sqrt{2/\pi}\,V_T'],[2.8,.65,0],31,7.2)
        for row in rows:self.play(Write(row))
        self.play(Write(self.equation(r'\boxed{J_{R0}=\sqrt{2/\pi}\,n_0V_T}',39,GREEN).shift(DOWN*1.5)))
        defs=self.term_definitions([
            r'n_0:\ \text{outgoing surface neutral density [m}^{-3}\text{]};\quad V_n:\ \text{outward normal speed [m/s]}',
            r'V_T=\sqrt{k_BT_M/m_{\rm Si}};\quad p(V_n):\ \text{normal-speed probability density [s/m]}'],[0,-2.7,0],23,12.4)
        self.play(FadeIn(defs));self.citation('Dimant and Oppenheim (2017), Part 1, surface boundary condition','https://doi.org/10.1002/2017JA023960')
        self.finish()

        self.start_slide('The ablation model fixes the total neutral source',
            'Assume uniform evaporation over a spherical grain. Multiply surface flux by the entire surface area. '
            'Independently divide mass loss by the mass of one vapor atom. Equating the two eliminates the unknown '
            'surface density. This uses the all-Si source proxy, distinct from the thermal model effective vapor mass.')
        grain=Circle(.65,color=GOLD,fill_opacity=.15).move_to([-4.1,.65,0])
        self.play(Create(grain))
        rays=VGroup(*[Arrow(grain.get_center()+.7*d,grain.get_center()+1.15*d,buff=0,color=GREEN)
            for d in directions])
        self.play(LaggedStart(*[GrowArrow(ray) for ray in rays],lag_ratio=.05))
        self.add(self.equation(r'4\pi a^2',30,GOLD).move_to([-4.1,-.9,0]),self.prose('Whole evaporating surface',22).move_to([-4.1,-1.5,0]))
        rows=self.term_definitions([
            r'\dot N_{\rm vap}=4\pi a^2J_{R0}',
            r'\dot N_{\rm vap}=\frac{-\dot m}{m_{\rm Si}}',
            r'\dot N_{\rm vap}=4\pi a^2\sqrt{2/\pi}\,n_0V_T'],[2.8,.8,0],36,7.)
        for row in rows:self.play(Write(row))
        solved=self.equation(r'\boxed{a^2n_0=\frac{\dot N_{\rm vap}}{4\pi\sqrt{2/\pi}\,V_T}}',39,BLUE).shift(DOWN*1.8)
        self.play(Write(solved))
        self.play(FadeIn(self.equation(r'\dot N_{\rm vap}:\ \text{neutral atoms/s};\quad-\dot m:\ \mathrm{kg/s};\quad m_{\rm Si}:\ \mathrm{kg/atom};\quad a:\ \mathrm m',24,MUTED).shift(DOWN*3.05)))
        self.finish()

        self.start_slide('Which collisions create ions and electrons?',
            'sigma_c counts effective scattering collisions. The primary Si probability beta_Si selects the ionizing '
            'fraction in this model. DO assumes isotropic differential ionization in the collision centre-of-mass '
            'frame. The integral of a constant over all solid angles is 4pi times that constant. This assumption '
            'about individual collisions does not make the meteor plasma spatially spherical.')
        atom=Dot([-5.,.65,0],radius=.09,color=GOLD)
        air=VGroup(Dot([-3.7,.65,0],radius=.09,color=BLUE),Dot([-3.52,.65,0],radius=.09,color=BLUE))
        self.add(atom,air);self.play(atom.animate.shift(RIGHT*1.1),run_time=.7)
        electron=Dot([-3.5,1.25,0],radius=.05,color=GREEN)
        self.play(FadeIn(electron),air.animate.shift(RIGHT*.4),atom.animate.set_color(RED))
        self.add(self.prose('Ion',23,RED).move_to([-4.,-.1,0]),self.equation(r'e^-',25,GREEN).next_to(electron,UP,buff=.15))
        rows=self.term_definitions([
            r'\sigma_{\rm ion}=\beta_{\rm Si}\sigma_c',
            r'G_{\rm ion}\equiv\frac{d\sigma_{\rm ion}}{d\Omega}',
            r'\sigma_{\rm ion}=\int_{4\pi}G_{\rm ion}\,d\Omega=4\pi G_{\rm ion}',
            r'\boxed{G_{\rm ion}=\frac{\beta_{\rm Si}\sigma_c}{4\pi}}'],[2.8,.4,0],34,7.2)
        for row in rows:self.play(Write(row))
        self.play(FadeIn(self.equation(r'\Omega:\ \text{scattering solid angle [sr]};\quad G_{\rm ion}:\ \mathrm{m^2/sr};\quad\beta_{\rm Si}:\ \text{probability}',24,MUTED).shift(DOWN*2.35)))
        self.play(FadeIn(self.prose('Isotropic scattering is a collision assumption; the spatial plasma density remains asymmetric.',25).shift(DOWN*3.1)))
        self.citation('Dimant and Oppenheim (2017), Part 2, isotropic ionization assumption','https://doi.org/10.1002/2017JA023963')
        self.finish()

        self.ion_transport_derivation()

        self.recoil_mass_derivation()

        self.start_slide('Separate the DO kinetic shape from its density scale',
            'Start from DO Part 2 Eq. 45, rather than a dimensional guess. H denotes the dimensionless angular/radial '
            'combination of f1, f2 and f3. Write R=lambda_T*s and absorb H/s into F_DO. The mass ratio is from '
            'the two-body collision kinematics in the DO solution. It is not a fitted coefficient. The numerical '
            'coefficient follows the published isotropic kinetic solution and the stated surface-density convention.')
        self.play(FadeIn(self.prose('Dimant--Oppenheim, Part 2, equation 45',27,BLUE).shift(UP*2.4)))
        original=self.equation(r'n_i(R,\theta)=\frac{8\pi a^2n_0n_AG_{\rm ion}}{\sqrt3\,R}'
            r'\left(1+\frac{m_{\rm Si}}{m_A}\right)H(R/\lambda_T,\cos\theta)',35).shift(UP*1.35)
        self.play(Write(original))
        definitions=self.equation(r's=R/\lambda_T,\quad H=|\mu|f_1+\mu f_2+f_3,\quad F_{\rm DO}=H/s,\quad\mu=\cos\theta',28,MUTED).shift(UP*.25)
        self.play(Write(definitions))
        self.play(Write(self.equation(r'\frac{H}{R}=\frac{1}{\lambda_T}\frac{H}{s}=\frac{F_{\rm DO}}{\lambda_T}',35,GREEN).shift(DOWN*.7)))
        self.play(Write(self.equation(r'n_e\simeq n_i=n_\star F_{\rm DO},\qquad '
            r'\boxed{n_\star=\frac{8\pi a^2n_0n_AG_{\rm ion}}{\sqrt3\lambda_T}\left(1+\frac{m_{\rm Si}}{m_A}\right)}',34,BLUE).shift(DOWN*1.85)))
        self.play(FadeIn(self.equation(r'm_A=\rho_A/n_A:\ \text{mean air-particle mass [kg]};\quad R:\ \text{distance from grain [m]}',23,MUTED).shift(DOWN*2.9)))
        self.citation('Dimant and Oppenheim (2017), Part 2, equations 45--48','https://doi.org/10.1002/2017JA023963')
        self.finish()

        self.start_slide('Replace the surface density with the evaporated atom rate',
            'Substitute a squared n0 from the whole-surface flux balance and G_ion from the primary ionization '
            'probability. Color carries the same factor across the substitutions. pi and grain area cancel; '
            'the remaining numerical coefficient is shown explicitly. No additional grain area is applied afterward.')
        substitutions=self.equation(r'a^2n_0=\frac{\dot N_{\rm vap}}{4\pi\sqrt{2/\pi}V_T},\qquad '
            r' G_{\rm ion}=\frac{\beta_{\rm Si}\sigma_c}{4\pi}',34,GREEN).shift(UP*2.15)
        self.play(Write(substitutions))
        first=self.equation(r'n_\star=\frac{8\pi}{\sqrt3\lambda_T}'
            r'\frac{\dot N_{\rm vap}}{4\pi\sqrt{2/\pi}V_T}'
            r'n_A\frac{\beta_{\rm Si}\sigma_c}{4\pi}'
            r'\left(1+\frac{m_{\rm Si}}{m_A}\right)',34).shift(UP*.55)
        self.play(Write(first))
        coefficient=self.equation(r'\frac{8\pi}{\sqrt3\,(4\pi)\sqrt{2/\pi}\,(4\pi)}=\frac{1}{2\sqrt{6\pi}}',32,GOLD).shift(DOWN*.8)
        self.play(Write(coefficient))
        result=self.equation(r'\boxed{n_\star=\frac{\beta_{\rm Si}\dot N_{\rm vap}\,n_A\sigma_c}'
            r'{2\sqrt{6\pi}V_T\lambda_T}\left(1+\frac{m_{\rm Si}}{m_A}\right)}',37,BLUE).shift(DOWN*2.15)
        self.play(TransformFromCopy(first,result))
        self.play(FadeIn(self.prose('The source is now the atom production rate supplied by the ablation model.',25).shift(DOWN*3.15)))
        self.finish()

        self.start_slide('Replace atom production with electron line density',
            'Use q=beta_Si dotN_vap/v from the earlier mass-to-ionization conversion. Then use '
            'lambda_T=V_T/(n_A sigma_c v). The explicit cross section and speed combine into the same lambda_T '
            'that already sets the spatial coordinates. They are not absent from the physics. The final result '
            'gives a volume-density scale from production per travelled metre divided by a squared collision length.')
        self.play(Write(self.equation(r'q=\frac{\beta_{\rm Si}\dot N_{\rm vap}}{v}\quad\Rightarrow\quad '
            r'\beta_{\rm Si}\dot N_{\rm vap}=qv',38,GREEN).shift(UP*2.3)))
        first=self.equation(r'n_\star=\frac{q\,(1+m_{\rm Si}/m_A)}{2\sqrt{6\pi}\lambda_T}'
            r'\frac{n_A\sigma_c v}{V_T}',39).shift(UP*.9)
        self.play(Write(first))
        identity=self.equation(r'\lambda_T=\frac{V_T}{n_A\sigma_c v}\quad\Rightarrow\quad '
            r'\frac{n_A\sigma_c v}{V_T}=\frac{1}{\lambda_T}',35,GOLD).shift(DOWN*.35)
        self.play(Write(identity))
        result=self.equation(r'\boxed{n_\star=\frac{q(1+m_{\rm Si}/m_A)}{2\sqrt{6\pi}\lambda_T^2}}',44,BLUE).shift(DOWN*1.75)
        self.play(TransformFromCopy(first,result),Indicate(identity,color=GOLD))
        self.play(Write(self.equation(r'[n_\star]=\frac{\mathrm{m^{-1}}}{\mathrm{m^2}}=\mathrm{m^{-3}}',29,MUTED).shift(DOWN*2.95)))
        self.citation('Dimant and Oppenheim (2017), Parts 1--2; source-rate substitution','https://doi.org/10.1002/2017JA023963')
        self.finish()

    def density(self):
        self.start_slide('The same plasma density, with distances in metres',
            'Secondary axes convert dimensionless coordinates using the archived MSIS neutral density at 100 km. '
            'Assumed speed is 50 km/s and grain temperature is 2000 K. These assumptions set lambda_T, '
            'not altitude alone. The origin is the ideal point-source singularity, omitted from the colour map.')
        self.play(FadeIn(self.image('density.png',9.0).move_to([0,.1,0])))
        self.play(FadeIn(self.equation(r'h=100\ \mathrm{km},\ v=50\ \mathrm{km/s},\ T_M=2000\ \mathrm K:\quad\lambda_T=%.3f\ \mathrm m'%self.sample['density_100km_lambda_m'],24,BLUE).shift(DOWN*3.25)))
        self.citation('Dimant and Oppenheim (2017), Part 2; MSIS atmosphere at 100 km','https://doi.org/10.1002/2017JA023963')
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
            self.prose('Fixed Cartesian Yee mesh',26,FG),self.equation(r'n_{\rm cap}:\ \text{finite-grain core density}',22),
            self.equation(r'0\leq w_{\rm cut}\leq1:\ \text{smooth outer taper}',22),self.prose('Green: electric-field sample edges',22,GREEN),
            self.prose('Red: absorbing CPML boundary',22,RED),
            self.prose('Check core cap, support, spacing, and box size.',22),
            self.prose('Density is frozen for each EM calculation.',24)).arrange(DOWN,buff=.36).move_to([2.65,0,0])
        for item in items:self.play(FadeIn(item),run_time=.3)
        self.finish()

    def yee_mesh(self):
        self.start_slide('A Yee mesh staggers electric and magnetic fields',
            'Kane Yee (1966): electric components are sampled on cell edges, magnetic components through face centres. '
            'Each discrete curl uses the surrounding field circulation. The cube is one schematic Cartesian cell.')
        origin=np.array([-4.6,-.8,0]);u=np.array([2.0,0,0]);v=np.array([.75,.65,0]);w=np.array([0,1.9,0])
        edges=VGroup()
        for a,b in [(u,v),(u,w),(v,w)]:
            other=w if a is u and b is v else (v if a is u and b is w else u)
            for offset in [np.zeros(3),a,b,a+b]:edges.add(Line(origin+offset,origin+offset+other,color=MUTED,stroke_opacity=.45))
        self.play(Create(edges))
        e=Arrow(origin,origin+u,buff=0,color=GREEN)
        # H_x lies at the x-normal face centre, not the volume centre.
        face=origin+(v+w)/2
        h=Arrow(face,face+RIGHT*.65,buff=0,color=BLUE)
        self.play(GrowArrow(e),GrowArrow(h),FadeIn(Dot(face,color=BLUE,radius=.04)))
        self.play(Create(Line([-5.22,.6,0],face,color=BLUE,stroke_width=1.2)))
        self.add(self.equation(r'E_x',28,GREEN).move_to([-3.6,-1.25,0]),self.equation(r'H_x',28,BLUE).move_to([-5.6,.6,0]))
        rows=self.term_definitions([r'E_x:\ (i+\tfrac12,j,k),\quad t=n\Delta t',
            r'H_x:\ (i,j+\tfrac12,k+\tfrac12),\quad t=(n+\tfrac12)\Delta t',
            r'\nabla\times\mathbf E\ \longrightarrow\ \text{differences of neighbouring edges}'],[2.7,.7,0],28,7.0)
        for row in rows:self.play(Write(row))
        timeline=VGroup(*[self.equation(t,28,c) for t,c in [(r'\mathbf E^n',GREEN),(r'\longrightarrow\mathbf H^{n+1/2}',BLUE),(r'\longrightarrow\mathbf E^{n+1}',GREEN)]]).arrange(RIGHT,buff=.3).shift(DOWN*2.15)
        for item in timeline:self.play(Write(item))
        self.play(FadeIn(self.prose('Space staggering forms the curl; time staggering gives the leapfrog update.',25).shift(DOWN*3.05)))
        self.citation('Yee (1966), Maxwell equations on a staggered grid','https://doi.org/10.1109/TAP.1966.1138693')
        self.finish()

    def cpml_boundary(self):
        self.start_slide('Let radiation leave the finite simulation box',
            'CPML means convolutional perfectly matched layer: an artificial absorbing layer surrounding the physical domain. '
            'A graded coordinate stretch damps outgoing waves while ideally matching the interior impedance. '
            'Discrete grids still reflect weakly; thickness and absorption must be checked. The pulse is schematic.')
        self.play(FadeIn(self.prose('CPML: convolutional perfectly matched layer',31,RED).shift(UP*2.35)))
        box=Rectangle(width=9.,height=2.2,color=MUTED).shift(UP*.4)
        absorber=Rectangle(width=1.8,height=2.2,color=RED,fill_opacity=.12).move_to([3.6,.4,0])
        self.play(Create(box),FadeIn(absorber))
        travel=ValueTracker(-3.)
        pulse=always_redraw(lambda:ParametricFunction(lambda x:np.array([x,.4+.65*np.exp(-((x-travel.get_value())/.4)**2)*np.cos(15*(x-travel.get_value()))*np.exp(-2.5*max(0,x-2.7)),0]),t_range=[-4.5,4.5,.02],color=BLUE))
        self.add(pulse);self.play(travel.animate.set_value(5.5),run_time=3.,rate_func=linear);pulse.clear_updaters()
        self.play(FadeIn(self.prose('Physical domain',25).move_to([-1.,-1.15,0])),FadeIn(self.prose('Absorbing layer',25,RED).move_to([3.3,-1.15,0])))
        self.play(Write(self.equation(r'\partial_x\ \longrightarrow\ \kappa_x^{-1}\partial_x+\psi_x,\qquad\psi_x^{n+1}=b_x\psi_x^n+a_x(\partial_x f)^n',29,BLUE).shift(DOWN*2.15)))
        self.play(FadeIn(self.prose('A memory variable implements the time convolution of the absorbing profile.',24).shift(DOWN*2.85)))
        self.play(Write(self.equation(r'f:\ E\text{ or }H;\quad\kappa_x,a_x,b_x:\ \text{profile/update coefficients};\quad\psi_x:\ \text{derivative memory}',21,MUTED).shift(DOWN*3.3)))
        self.citation('Roden and Gedney (2000), convolution PML','https://doi.org/10.1002/1098-2760(20001205)27:5%3C334::AID-MOP14%3E3.0.CO;2-A')
        self.finish()


    def charge_separation_picture(self, y=1.0):
        """Uniform slab, ions fixed; positive displacement of the electron fluid."""
        left=-5.7; right=-2.0; delta=.65; height=1.45
        ions=Rectangle(width=right-left,height=height,color=RED,stroke_width=2).move_to([(left+right)/2,y,0])
        electrons=Rectangle(width=right-left,height=height,color=GREEN,fill_opacity=.12,stroke_width=2).move_to([(left+right)/2,y,0])
        self.add(ions,electrons)
        self.play(electrons.animate.shift(RIGHT*delta),run_time=1.5)
        positive=Rectangle(width=delta,height=height,color=RED,fill_opacity=.18,stroke_width=0).move_to([left+delta/2,y,0])
        negative=Rectangle(width=delta,height=height,color=GREEN,fill_opacity=.18,stroke_width=0).move_to([right+delta/2,y,0])
        self.play(FadeIn(positive),FadeIn(negative))
        self.add(self.equation('+',28,RED).move_to(positive),self.equation('-',28,GREEN).move_to(negative))
        displacement=DoubleArrow([left,y-height/2-.35,0],[left+delta,y-height/2-.35,0],buff=0,color=GREEN,tip_length=.12)
        self.play(GrowArrow(displacement))
        self.add(self.equation(r'\xi',26,GREEN).move_to([left+delta/2,y-height/2-.75,0]))
        return left,right,delta,height

    def plasma_frequency_derivation(self):
        self.start_slide('Displacing electrons exposes equal and opposite charge',
            'A local, uniform, cold plasma slab has fixed ions and mobile electrons. '
            'Displace the entire electron fluid by a small xi along positive x. '
            'An ion-only layer remains on the left; an equal electron excess appears on the right. '
            'The diagram is a one-dimensional slab model, not the finite meteor-cloud eigenmode.')
        self.play(FadeIn(self.prose('Fixed positive ions; electrons displaced to the right',26).shift(UP*2.55)))
        self.charge_separation_picture(.9)
        self.add(self.prose('Positive excess',22,RED).move_to([-5.4,2.,0]),
                 self.prose('Negative excess',22,GREEN).move_to([-1.7,2.,0]))
        defs=self.term_definitions([
            r'n_e:\ \text{equilibrium electron number density [m}^{-3}\text{]}',
            r'\xi:\ \text{electron-fluid displacement [m]}',
            r'S:\ \text{slab face area [m}^2\text{]};\quad e>0:\ \text{charge magnitude [C]}'],
            [2.8,1.1,0],24,6.2)
        self.play(FadeIn(defs))
        self.play(Write(self.equation(r'\text{exposed volume}=S\xi\quad\Rightarrow\quad N=n_eS\xi',33).shift(DOWN*1.45)))
        self.next_slide('Count charge in the exposed layer',
            notes='Number density times exposed volume is the missing-electron count. Each missing electron leaves charge plus e. Divide the charge by face area to obtain the surface-charge magnitude. Sigma_q is not a collision cross section.')
        self.play(Write(self.equation(r'Q=eN=n_eeS\xi,\qquad \sigma_q\equiv Q/S=n_ee\xi\quad[\mathrm{C/m^2}]',34,BLUE).shift(DOWN*2.45)))
        self.play(FadeIn(self.prose('The two thin edge layers carry +Q and -Q; the interior remains neutral.',25).shift(DOWN*3.15)))
        self.citation('Fitzpatrick, Plasma Physics: Plasma Frequency','https://farside.ph.utexas.edu/teaching/plasma/Plasma/node5.html')
        self.finish()

        self.start_slide('Gauss law turns separated charge into a restoring field',
            'Approximate the thin exposed layers as infinite sheets. Their fields cancel outside and add inside. '
            'A Gaussian pillbox around the positive sheet has one face in the zero exterior field and one in the interior field. '
            'Its flux is E S, and its enclosed charge is sigma_q S. This gives positive E_x for positive electron displacement.')
        x0,x1,delta,h=self.charge_separation_picture(1.)
        self.play(GrowArrow(Arrow([x0+delta+.2,1.,0],[x1-.25,1.,0],buff=0,color=BLUE)))
        self.add(self.equation(r'E_x>0',26,BLUE).move_to([-3.5,1.55,0]),
            self.prose('Fields cancel outside; add inside',23).move_to([-3.6,-.55,0]))
        pill=DashedVMobject(Rectangle(width=1.45,height=2.1,color=GOLD).move_to([x0+.3,1.,0]))
        self.play(Create(pill))
        self.add(self.prose('Gaussian pillbox',22,GOLD).move_to([-5.3,2.5,0]))
        self.play(Write(self.equation(r'\oint\mathbf E\cdot d\mathbf S=Q_{\rm enclosed}/\epsilon_0',31).move_to([2.8,2.,0])))
        self.play(Write(self.equation(r'E_xS=\sigma_qS/\epsilon_0',34,BLUE).move_to([2.8,.8,0])))
        self.play(Write(self.equation(r'E_x=\sigma_q/\epsilon_0=n_ee\xi/\epsilon_0',35,BLUE).shift(DOWN*1.4)))
        self.next_slide('The electron force points back toward neutrality',
            notes='An electron has charge minus e, so its force is opposite to the restoring electric field. The field points in the displacement direction, whereas the force points against displacement. The sign is the origin of the stable oscillator.')
        self.play(Write(self.equation(r'F_x=(-e)E_x=-\frac{n_ee^2}{\epsilon_0}\xi',37,RED).shift(DOWN*2.35)))
        self.play(FadeIn(self.equation(r'\epsilon_0:\ \text{vacuum permittivity [F/m]};\quad F_x:\ \text{force on one electron [N]}',24,MUTED).shift(DOWN*3.2)))
        self.citation('Feynman Lectures II, section 7-4: plasma oscillations','https://www.feynmanlectures.caltech.edu/II_07.html')
        self.finish()

        self.start_slide('Electron inertia and the restoring field make an oscillator',
            'Newton law applied to one electron gives a linear oscillator. Identify the coefficient of xi '
            'with omega_p squared. Use angular frequency in radians per second, and f_p=omega_p/(2 pi) in Hz. '
            'This ideal derivation neglects collisions, magnetic field and pressure; those are restored in the response model.')
        self.play(Write(self.equation(r'm_e\ddot\xi=-\frac{n_ee^2}{\epsilon_0}\xi',39,BLUE).shift(UP*2.25)))
        self.play(Write(self.equation(r'\ddot\xi+\underbrace{\frac{n_ee^2}{\epsilon_0m_e}}_{\omega_p^2}\xi=0',42).shift(UP*.9)))
        self.next_slide('Identify the natural oscillation frequency',
            notes='Compare with the harmonic oscillator x double dot plus omega squared x equals zero. The square root follows from that equation, not a dimensional guess. Four times the density gives twice the angular frequency.')
        self.play(Write(self.equation(r'\boxed{\omega_p=\sqrt{\frac{n_ee^2}{\epsilon_0m_e}}},\qquad \xi(t)=\xi_0\cos(\omega_pt)',39,GREEN).shift(DOWN*.65)))
        self.play(Write(self.equation(r'\omega_p:\ \mathrm{rad/s};\quad f_p=\omega_p/(2\pi):\ \mathrm{Hz};\quad m_e:\ \text{electron mass [kg]}',24,MUTED).shift(DOWN*1.75)))
        self.play(FadeIn(self.prose('A denser electron fluid creates a stronger restoring field.',26).shift(DOWN*2.5)))
        self.play(Write(self.equation(r'n_e\longrightarrow4n_e\quad\Rightarrow\quad\omega_p\longrightarrow2\omega_p',31,BLUE).shift(DOWN*3.15)))
        self.citation('Feynman Lectures II, equations 7.22--7.25','https://www.feynmanlectures.caltech.edu/II_07.html')
        self.finish()

    def polarization_derivation(self):
        self.start_slide('Polarization measures charge separation per unit volume',
            'P is electric dipole moment per unit volume. A positive charge at r_i and an electron at r_i+xi '
            'have dipole p=e r_i-e(r_i+xi)=-e xi. Summing n_e pairs per unit volume gives P=-n_e e xi. '
            'This is the linear local displacement description with ions fixed; P points opposite to electron displacement.')
        ion=Dot([-4.8,1.2,0],color=RED,radius=.12)
        electron=Dot([-2.4,1.2,0],color=GREEN,radius=.1)
        self.play(FadeIn(ion),FadeIn(electron))
        self.add(self.equation('+e',26,RED).move_to([-4.8,1.9,0]),
            self.equation('-e',26,GREEN).move_to([-2.4,1.9,0]))
        self.play(GrowArrow(Arrow([-4.65,.6,0],[-2.55,.6,0],buff=0,color=GREEN)))
        self.add(self.equation(r'\boldsymbol\xi=\mathbf r_e-\mathbf r_i',27,GREEN).move_to([-3.6,-.05,0]))
        self.play(GrowArrow(Arrow([-2.55,2.55,0],[-4.65,2.55,0],buff=0,color=BLUE)))
        self.add(self.equation(r'\mathbf p',26,BLUE).move_to([-3.6,2.95,0]))
        self.play(FadeIn(self.equation(r'\mathbf r_i,\mathbf r_e:\ \text{ion and electron positions [m]}',23,MUTED).move_to([2.8,.5,0])))
        self.play(Write(self.equation(r'\mathbf p=e\mathbf r_i-e\mathbf r_e=-e\boldsymbol\xi',32,BLUE).move_to([2.8,1.55,0])))
        self.play(Write(self.equation(r'\mathbf P\equiv\frac{\sum\mathbf p}{\Delta V}=-n_ee\boldsymbol\xi',36,BLUE).shift(DOWN*1.25)))
        self.play(FadeIn(self.equation(r'\mathbf p:\ \text{dipole moment [C m]};\quad \mathbf P:\ \text{dipole moment per volume [C/m}^2\text{]}',24,MUTED).shift(DOWN*2.35)))
        self.play(FadeIn(self.prose('The dipole arrow points from the negative charge toward the positive charge.',25).shift(DOWN*3.15)))
        self.citation('Feynman Lectures II, chapters 10--11: polarization and dielectric response','https://www.feynmanlectures.caltech.edu/II_10.html')
        self.finish()

        self.start_slide('Changing polarization is an electric current',
            'With density held fixed, differentiate P=-n_e e xi. The time derivative of electron displacement '
            'is electron mean velocity u_e, so partial_t P=-n_e e u_e=J. For a single harmonic with exp(-i omega t), '
            'a time derivative is multiplication by -i omega. This is the bridge from mechanical response to permittivity.')
        self.play(Write(self.equation(r'\mathbf P=-n_ee\boldsymbol\xi,\qquad \partial_t n_e=0',37,BLUE).shift(UP*2.3)))
        self.play(Write(self.equation(r'\partial_t\mathbf P=-n_ee\,\partial_t\boldsymbol\xi=-n_ee\mathbf u_e=\mathbf J',38,GREEN).shift(UP*.95)))
        self.play(FadeIn(self.equation(r'\mathbf u_e=\partial_t\boldsymbol\xi:\ \text{electron mean velocity [m/s]};\quad \mathbf J:\ \mathrm{A/m^2}',24,MUTED).shift(DOWN*.2)))
        self.next_slide('Write the same relation for a sinusoidal field',
            notes='Introduce the complex exponential time convention explicitly. Physical fields are the real parts. Differentiating exp(-i omega t) produces minus i omega. P is a displacement response; its derivative is the moving-electron current.')
        self.play(Write(self.equation(r'\mathbf P(t)=\operatorname{Re}\{\widetilde{\mathbf P}e^{-i\omega t}\}',34).shift(DOWN*1.25)))
        self.play(Write(self.equation(r'\widetilde{\mathbf J}=-i\omega\widetilde{\mathbf P},\qquad \widetilde{\mathbf P}=\frac{i}{\omega}\widetilde{\mathbf J}',36,GREEN).shift(DOWN*2.35)))
        self.play(FadeIn(self.prose('Next: use the current response to find polarization, then permittivity.',25).shift(DOWN*3.2)))
        self.citation('Feynman Lectures II, section 7-4; linear polarization response','https://www.feynmanlectures.caltech.edu/II_07.html')
        self.finish()

    def plasma_response(self):
        self.start_slide('Start from the force on an electron',
            'Cold electron-fluid momentum equation: electric and magnetic Lorentz forces, plus linear momentum relaxation. '
            'Pressure gradients, nonlinear advection and ion motion are neglected in this radar-frequency response.')
        electron=Dot([-4.,.5,0],radius=.12,color=GREEN);self.add(electron)
        electric=Arrow([-4.,.5,0],[-5.3,.5,0],buff=.1,color=BLUE)
        drag=Arrow([-4.,.5,0],[-3.,.5,0],buff=.1,color=RED)
        self.play(GrowArrow(electric));self.add(self.equation(r'-e\mathbf E',27,BLUE).move_to([-5.,1.15,0]))
        self.play(electron.animate.shift(LEFT*.3),GrowArrow(drag));self.add(self.equation(r'-m_e\nu_{en}\mathbf u_e',25,RED).move_to([-3.,-.3,0]))
        law=self.equation(r'm_e\partial_t\mathbf u_e=-e\mathbf E-e\mathbf u_e\times\mathbf B_0-m_e\nu_{en}\mathbf u_e',36,BLUE).shift(UP*2.)
        self.play(Write(law))
        defs=self.term_definitions([r'\mathbf u_e:\ \text{electron mean velocity [m/s]};\quad e>0:\ \text{elementary charge [C]}',
            r'm_e:\ \text{electron mass [kg]};\quad\mathbf E:\ \text{total electric field [V/m]};\quad\mathbf B_0:\ \text{background field [T]}',
            r'\nu_{en}:\ \text{electron--neutral momentum relaxation [s}^{-1}\text{]}'],[0,-1.8,0],24,12.3)
        self.play(FadeIn(defs))
        self.play(FadeIn(self.prose('Collision rate uses electron energies and neutral species, rather than meteoroid speed.',24).shift(DOWN*3.1)))
        self.citation('Marshall and Close (2015), section 2: cold, collisional, magnetized response','https://doi.org/10.1002/2015JA021238')
        self.finish()
        self.plasma_frequency_derivation()
        self.start_slide('Convert electron motion into electric current',
            'For fixed local electron density, multiply the momentum equation by minus n_e e/m_e. '
            'The sign comes from the negative electron charge. Define omega_p squared and the positive-e gyrovector '
            'to obtain the current equation used by the electromagnetic solver.')
        self.play(Write(self.equation(r'\mathbf J=-n_e e\mathbf u_e\quad[\mathrm{A/m^2}],\qquad\partial_t n_e=0',38,GREEN).shift(UP*2.25)))
        first=self.equation(r'\partial_t\mathbf J=\frac{n_e e^2}{m_e}\mathbf E-\frac e{m_e}\mathbf J\times\mathbf B_0-\nu_{en}\mathbf J',36).shift(UP*.9);self.play(Write(first))
        self.play(Write(self.equation(r'\omega_p^2\equiv\frac{n_e e^2}{\epsilon_0m_e},\qquad\boldsymbol\Omega_e\equiv\frac{e\mathbf B_0}{m_e}',36,BLUE).shift(DOWN*.3)))
        result=self.equation(r'\boxed{\partial_t\mathbf J+\nu_{en}\mathbf J+\mathbf J\times\boldsymbol\Omega_e=\epsilon_0\omega_p^2\mathbf E}',37,GREEN).shift(DOWN*1.6)
        self.play(TransformFromCopy(first,result))
        self.play(FadeIn(self.equation(r'\omega_p:\ \text{electron plasma angular frequency [rad/s]};\quad|\boldsymbol\Omega_e|:\ \text{gyrofrequency [rad/s]}',24,MUTED).shift(DOWN*2.65)))
        self.play(FadeIn(self.equation(r'\epsilon_0:\ \text{vacuum permittivity [F/m]};\quad n_e:\ \text{fixed local density [m}^{-3}\text{]}',24,MUTED).shift(DOWN*3.2)))
        self.citation('Marshall and Close (2015), equation 6','https://doi.org/10.1002/2015JA021238')
        self.finish()
        self.polarization_derivation()
        self.start_slide('Derive the collisional dielectric response',
            'Set B0=0 and use fields proportional to exp(-i omega t), with positive real omega. '
            'J=sigma E, J=partial_t P and D=epsilon_0 E+P give the stated dielectric. '
            'Its positive imaginary part represents passive loss with this convention.')
        self.play(Write(self.equation(r'\mathbf B_0=0,\quad e^{-i\omega t}:\qquad(\nu_{en}-i\omega)\mathbf J=\epsilon_0\omega_p^2\mathbf E',34).shift(UP*2.2)))
        self.play(Write(self.equation(r'\mathbf J=\sigma\mathbf E,\quad\sigma=\frac{\epsilon_0\omega_p^2}{\nu_{en}-i\omega},\qquad\mathbf J=\partial_t\mathbf P=-i\omega\mathbf P',33,GREEN).shift(UP*.9)))
        self.play(Write(self.equation(r'\mathbf D=\epsilon_0\mathbf E+\mathbf P=\epsilon_0\epsilon_r\mathbf E\quad\Rightarrow\quad\epsilon_r=1+\frac{i\sigma}{\epsilon_0\omega}',33).shift(DOWN*.35)))
        self.play(Write(self.equation(r'\boxed{\epsilon_r(\omega)=1-\frac{\omega_p^2}{\omega(\omega+i\nu_{en})}}',42,BLUE).shift(DOWN*1.65)))
        self.play(FadeIn(self.equation(r'\mathbf P:\ \text{polarization [C/m}^2\text{]};\quad\mathbf D:\ \text{electric displacement [C/m}^2\text{]};\quad\sigma:\ \text{conductivity [S/m]}',22,MUTED).shift(DOWN*2.7)))
        self.play(FadeIn(self.equation(r'\nu_{en}=10^7\ \mathrm{s^{-1}}:\ \text{example assumption, not inferred from }\nu_c',24,RED).shift(DOWN*3.25)))
        self.citation('Marshall and Close (2015), cold collisional plasma model','https://doi.org/10.1002/2015JA021238')
        self.finish()

    def maxwell(self):
        self.start_slide('Why solve Maxwell equations after finding electron density?',
            'The radar drives electrons; their current radiates; that field changes electron motion. '
            'The analytic incident wave satisfies vacuum Maxwell equations. Subtract it to solve for scattered fields.')
        self.play(FadeIn(self.prose('We need the field sent back toward the radar.',31,FG).shift(UP*2.35)))
        blocks=VGroup(*[VGroup(RoundedRectangle(width=3.1,height=1.2,color=c),self.prose(label,24,c))
            for label,c in [('Total electric field',BLUE),('Electron current',GREEN),('Scattered field',GOLD)]]).arrange(RIGHT,buff=.75).shift(UP*.6)
        for block in blocks:self.play(FadeIn(block))
        for i in range(2):self.play(GrowArrow(Arrow(blocks[i].get_right(),blocks[i+1].get_left(),buff=.08,color=MUTED)))
        self.play(Create(CurvedArrow(blocks[2].get_bottom()+DOWN*.1,blocks[0].get_bottom()+DOWN*.1,angle=-PI/5,color=BLUE)))
        self.play(Write(self.equation(r'\mathbf E_{\rm total}=\mathbf E_{\rm inc}+\mathbf E_s',38,BLUE).shift(DOWN*1.75)))
        self.play(FadeIn(self.equation(r'\mathbf E_{\rm inc}:\ \text{known radar wave};\quad\mathbf E_s:\ \text{unknown scattered field}\quad[\mathrm{V/m}]',25,MUTED).shift(DOWN*2.8)))
        self.citation('Marshall and Close (2015), section 2: self-consistent plasma scattering','https://doi.org/10.1002/2015JA021238')
        self.finish()
        self.start_slide('Two coupled laws propagate an electromagnetic wave',
            'Faraday law couples an electric-field curl to changing magnetic field. '
            'Ampere-Maxwell law couples a magnetic-field curl to changing electric field and conduction current. '
            'Together, with the charge/divergence constraints and initial conditions, they propagate electromagnetic waves. '
            'The plasma current adds a material response; scattered fields satisfy the incident-subtracted equations.')
        self.play(FadeIn(self.prose('Faraday: a circulating electric field changes the magnetic field.',27,BLUE).shift(UP*2.55)))
        self.play(Write(self.equation(r'\mu_0\partial_t\mathbf H_s=-\nabla\times\mathbf E_s',38,BLUE).shift(UP*1.55)))
        self.play(FadeIn(self.equation(r'\mu_0:\ \text{vacuum permeability [H/m]}',24,MUTED).shift(UP*.9)))
        self.next_slide('The Ampere-Maxwell partner',
            notes='The displacement-current term epsilon_0 partial_t E is essential for a vacuum wave. In plasma, electron current also contributes. These two curl equations are coupled; neither is an independent propagation rule for only one field.')
        self.play(FadeIn(self.prose('Ampere-Maxwell: a circulating magnetic field changes E and carries current.',26,GREEN).shift(UP*.35)))
        self.play(Write(self.equation(r'\epsilon_0\partial_t\mathbf E_s=\nabla\times\mathbf H_s-\mathbf J',38,GREEN).shift(DOWN*.7)))
        self.play(Write(self.equation(r'\mathbf J=0:\quad \partial_t^2\mathbf E=c^2\nabla^2\mathbf E,\qquad c=(\mu_0\epsilon_0)^{-1/2}',31).shift(DOWN*1.9)))
        self.play(FadeIn(self.prose('The electric and magnetic fields sustain the travelling wave together.',26).shift(DOWN*2.8)))
        self.play(FadeIn(self.equation(r'\mathbf E_s:\ \mathrm{V/m};\quad\mathbf H_s:\ \mathrm{A/m};\quad\mathbf J:\ \mathrm{A/m^2};\quad s:\ \text{scattered field}',24,MUTED).shift(DOWN*3.3)))
        self.citation('Yee (1966), Maxwell curl equations and staggered discretization','https://doi.org/10.1109/TAP.1966.1138693')
        self.finish()

        self.start_slide('The Yee grid alternates magnetic and electric updates',
            'E samples live at integer times n Delta t. H samples live at half times (n+1/2) Delta t. '
            'Replace each time derivative by a centred difference and each spatial curl by its staggered-grid curl. '
            'Superscripts label time samples, not powers. The plasma-current update is synchronized to the half step.')
        self.play(FadeIn(self.equation(r't_n=n\Delta t:\quad \mathbf E^n;\qquad t_{n+1/2}=(n+\tfrac12)\Delta t:\quad \mathbf H^{n+1/2},\mathbf J^{n+1/2}',27).shift(UP*2.65)))
        self.play(FadeIn(self.prose('Faraday law: use the electric curl to advance H by one time step.',25,BLUE).shift(UP*1.9)))
        self.play(Write(self.equation(r'\mu_0\frac{\mathbf H_s^{n+1/2}-\mathbf H_s^{n-1/2}}{\Delta t}=-\nabla_h\times\mathbf E_s^n',32,BLUE).shift(UP*.95)))
        self.play(Write(self.equation(r'\mathbf H_s^{n+1/2}=\mathbf H_s^{n-1/2}-\frac{\Delta t}{\mu_0}\nabla_h\times\mathbf E_s^n',32,BLUE).shift(DOWN*.05)))
        self.next_slide('Then advance the electric field',
            notes='Use the newly updated magnetic field and the half-step plasma current. This is the discrete Ampere-Maxwell law. The electron current response was derived in the preceding section and is driven by the total electric field.')
        self.play(FadeIn(self.prose('Ampere-Maxwell law: use the new magnetic curl and plasma current to advance E.',25,GREEN).shift(DOWN*1.05)))
        self.play(Write(self.equation(r'\mathbf E_s^{n+1}=\mathbf E_s^n+\frac{\Delta t}{\epsilon_0}(\nabla_h\times\mathbf H_s^{n+1/2}-\mathbf J^{n+1/2})',33,GREEN).shift(DOWN*2.05)))
        self.play(FadeIn(self.equation(r'\Delta t:\ \text{time step [s]};\quad n:\ \text{time index};\quad \nabla_h\times:\ \text{curl on the staggered spatial grid}',23,MUTED).shift(DOWN*3.05)))
        self.citation('Yee (1966); Marshall and Close (2015), equations 4--6','https://doi.org/10.1109/TAP.1966.1138693')
        self.finish()
        self.start_slide('Is half a grid cell per time step safe?',
            'For the vacuum Yee scheme on a cubic three-dimensional grid, the von Neumann dispersion relation '
            'bounds the Courant number S=c Delta t/Delta x by one over sqrt(3). S=0.5 is inside that bound. '
            'This is stability of the vacuum update, not a guarantee of spatial accuracy or of a coupled material update.')
        self.play(FadeIn(self.prose('Test the discrete wave, rather than judging the distance by eye.',27).shift(UP*2.6)))
        self.play(Write(self.equation(r'\sin^2\!\frac{\omega\Delta t}{2}=S^2\!\left[\sin^2\!\frac{k_x\Delta x}{2}+\sin^2\!\frac{k_y\Delta x}{2}+\sin^2\!\frac{k_z\Delta x}{2}\right]',31,BLUE).shift(UP*1.45)))
        self.play(FadeIn(self.equation(r'S\equiv c\Delta t/\Delta x:\ \text{Courant number};\quad k_x,k_y,k_z:\ \text{spatial wavevector components}',23,MUTED).shift(UP*.45)))
        self.next_slide('Bound all three spatial directions',
            notes='Each squared sine is at most one. To keep the temporal frequency real for every spatial grid mode, require 3 S squared no greater than one. If S is too large, some grid modes grow exponentially.')
        self.play(Write(self.equation(r'3S^2\le1\quad\Rightarrow\quad S\le1/\sqrt3\simeq0.577',36).shift(DOWN*.65)))
        self.play(Write(self.equation(r'\Delta t=\Delta x/(2c)\quad\Rightarrow\quad S=0.5<0.577',38,GREEN).shift(DOWN*1.85)))
        self.play(FadeIn(self.prose('Stable in vacuum; refine the mesh and time step to check phase and RCS accuracy.',25).shift(DOWN*3.0)))
        self.citation('Schneider, Understanding the FDTD Method, chapters 7 and 9','https://eecs.wsu.edu/~schneidj/ufdtd/')
        self.finish()

        self.start_slide('The plasma adds a second, faster response to resolve',
            'The solver also restricts the step by plasma and gyrofrequency. The coefficient 0.7 is an implementation '
            'margin, not a universal coupled-scheme stability theorem. Material-update stability and numerical phase '
            'accuracy must be tested against analytic cases and step refinement, separately from the vacuum CFL test.')
        self.play(Write(self.equation(r'\Delta t=\min\!\left[\frac{\Delta x}{2c},\frac{0.7}{\sqrt{\omega_{p,\max}^2+|\boldsymbol\Omega_e|^2}}\right]',39,GREEN).shift(UP*2.1)))
        self.play(FadeIn(self.equation(r'\omega_{p,\max}:\ \text{largest local plasma frequency [rad/s]};\quad|\boldsymbol\Omega_e|:\ \text{gyrofrequency [rad/s]}',24,MUTED).shift(UP*.7)))
        self.play(FadeIn(self.prose('First bound: propagate the EM wave stably on the Yee grid.',27,BLUE).shift(DOWN*.35)))
        self.play(FadeIn(self.prose('Second bound: sample the electron response; 0.7 is a solver margin.',27,GREEN).shift(DOWN*1.2)))
        self.play(FadeIn(self.prose('Then check convergence: smaller cells and steps must reproduce the echo.',27).shift(DOWN*2.2)))
        self.play(FadeIn(self.prose('A stable calculation can still have inaccurate phase or scattering amplitude.',25,RED).shift(DOWN*3.05)))
        self.citation('Yee (1966); Marshall and Close (2015), plasma FDTD','https://doi.org/10.1002/2015JA021238')
        self.finish()

    def response_animation(self):
        self.start_slide('Watch the radar pulse drive current in the plasma cloud',
            'Actual small-grid Rust FDTD solution, frozen DO density. Left: total electric Ez in V/m; '
            'right: physical electron Jz in A/m2, in the same xz plane. The incident peak field is 1 V/m, '
            'frequency 53.5 MHz. The wave propagates along x, the meteor trajectory is along z. '
            'The signed current scale is fixed for the whole movie; asinh makes weak current visible. '
            'E and J have their native half-step Yee timing offset. Playback is slowed; the nanosecond clock is physical. '
            'This illustrates current formation, not a converged quantitative RCS calculation.')
        self.play_gpu_movie('fdtd_current.mp4',center=[0,.25,0],width=12.7)
        self.play(FadeIn(self.prose('The total field drives electron current; that current generates the scattered field.',26,FG).shift(DOWN*3.2)))
        self.citation('Cold-plasma FDTD formulation: Marshall and Close (2015)','https://doi.org/10.1002/2015JA021238')
        self.finish()

    def far_field(self):
        self.start_slide('Keep the current amplitude and its phase at the radar frequency',
            'Write the real current as the real part of a complex amplitude times exp(-i omega_0 t). '
            'The hat on a field denotes its complex sinusoidal amplitude; the hat on n denotes a unit direction. '
            'A finite time Fourier integral needs its normalization to give an amplitude, not amplitude times time.')
        self.play(Write(self.equation(r'\mathbf J(\mathbf r,t)=\operatorname{Re}\{\widehat{\mathbf J}(\mathbf r)e^{-i\omega_0t}\}',38,GREEN).shift(UP*2.2)))
        self.play(Write(self.equation(r'\widehat{\mathbf J}(\mathbf r)=\frac2T\int_{t_0}^{t_0+T}\mathbf J(\mathbf r,t)e^{+i\omega_0t}\,dt',37).shift(UP*.6)))
        self.play(FadeIn(self.prose('Over complete cycles after transients; the phase carries the timing of each current.',26).shift(DOWN*.65)))
        self.play(FadeIn(self.equation(r'\widehat{\mathbf J}:\ \mathrm{A/m^2};\quad\omega_0=2\pi f_0:\ \mathrm{rad/s};\quad T:\ \text{interval [s]};\quad t_0:\ \text{window start [s]}',25,MUTED).shift(DOWN*1.6)))
        self.play(FadeIn(self.prose('Each small current element radiates. Add the complex fields, including travel phase.',27,BLUE).shift(DOWN*2.75)))
        self.finish()

        self.start_slide('The magnetic vector potential carries radiation from the current',
            'Use the outgoing free-space Green function in Lorenz gauge. A is the magnetic vector potential, '
            'with B=curl A and E=-grad phi-partial_t A. Expand distance to an observer far from the source. '
            'The scalar potential supplies the longitudinal cancellation; the far electric radiation is transverse.')
        self.play(Write(self.equation(r'\mathbf B=\nabla\times\mathbf A,\qquad\mathbf E=-\nabla\phi-\partial_t\mathbf A',34,BLUE).shift(UP*2.5)))
        self.play(FadeIn(self.equation(r'\mathbf A:\ \text{magnetic vector potential [T m]};\quad \phi:\ \text{electric scalar potential [V]}',24,MUTED).shift(UP*1.7)))
        self.play(Write(self.equation(r'\widehat{\mathbf A}(\mathbf R)=\frac{\mu_0}{4\pi}\int\frac{\widehat{\mathbf J}(\mathbf r)e^{ik|\mathbf R-\mathbf r|}}{|\mathbf R-\mathbf r|}\,d^3r',34).shift(UP*.4)))
        self.next_slide('Keep source-to-observer phase in the far field',
            notes='At R much greater than source size, use one over R for the amplitude but retain the first-order path-length difference in the exponential. Losing this phase would incorrectly force all source points to radiate in phase in every direction.')
        self.play(Write(self.equation(r'\mathbf R=R\widehat{\mathbf n},\quad|\mathbf R-\mathbf r|\simeq R-\widehat{\mathbf n}\cdot\mathbf r,\quad k=\omega_0/c',30).shift(DOWN*.8)))
        self.play(Write(self.equation(r'\widehat{\mathbf A}(R\widehat{\mathbf n})\simeq\frac{\mu_0e^{ikR}}{4\pi R}\int\widehat{\mathbf J}(\mathbf r)e^{-ik\widehat{\mathbf n}\cdot\mathbf r}\,d^3r',33,BLUE).shift(DOWN*2.0)))
        self.play(FadeIn(self.equation(r'R:\ \text{range [m]};\quad\widehat{\mathbf n}:\ \text{unit viewing direction};\quad k:\ \text{wavenumber [rad/m]}',24,MUTED).shift(DOWN*3.15)))
        self.citation('Feynman Lectures II, chapter 21: retarded potentials','https://www.feynmanlectures.caltech.edu/II_21.html')
        self.finish()

        self.start_slide('Only the transverse current sum reaches the far-field receiver',
            'Call the transverse current integral C_perp to avoid confusing it with magnetic vector potential A. '
            'The matrix I-n n^T removes the component parallel to the observation direction. '
            'C_perp has units ampere metres, while A has units tesla metres. E_s=i omega A_perp in the radiation zone.')
        self.play(Write(self.equation(r'\mathbf C_\perp(\widehat{\mathbf n})\equiv(\mathbf I-\widehat{\mathbf n}\widehat{\mathbf n}^{\mathsf T})\int\widehat{\mathbf J}(\mathbf r)e^{-ik\widehat{\mathbf n}\cdot\mathbf r}\,d^3r',34,GREEN).shift(UP*2.2)))
        self.play(FadeIn(self.equation(r'\mathbf C_\perp:\ \text{transverse current integral [A m]};\quad\mathbf I:\ \text{identity matrix}',25,MUTED).shift(UP*1.1)))
        self.play(Write(self.equation(r'\mathbf I-\widehat{\mathbf n}\widehat{\mathbf n}^{\mathsf T}:\quad \mathbf v\longmapsto\mathbf v-\widehat{\mathbf n}(\widehat{\mathbf n}\cdot\mathbf v)',31).shift(DOWN*.05)))
        self.next_slide('Convert the transverse current sum to the radiated field',
            notes='Multiply the transverse vector potential by i omega_0. Since omega_0 mu_0=k Z_0, the electric radiation amplitude follows. Its one over R decay makes intensity decay as one over R squared.')
        self.play(Write(self.equation(r'\widehat{\mathbf E}_s\simeq i\omega_0\widehat{\mathbf A}_\perp=\frac{ikZ_0e^{ikR}}{4\pi R}\mathbf C_\perp,\qquad Z_0=\sqrt{\mu_0/\epsilon_0}',36,GOLD).shift(DOWN*1.5)))
        self.play(FadeIn(self.equation(r'Z_0\simeq377\ \Omega:\ \text{vacuum impedance};\quad \widehat{\mathbf E}_s:\ \text{scattered electric-field amplitude [V/m]}',24,MUTED).shift(DOWN*2.6)))
        self.play(FadeIn(self.prose('Source phases can reinforce or cancel: the current distribution determines the echo.',25).shift(DOWN*3.2)))
        self.citation('Marshall and Close (2015), induced-current radiation and RCS','https://doi.org/10.1002/2015JA021238')
        self.finish()

    def rcs(self):
        self.start_slide('The receiving antenna selects a polarization',
            'e_rx is a complex, dimensionless unit polarization vector transverse to the viewing direction. '
            'Dagger means conjugate transpose: first complex conjugate every component, then transpose the column to a row. '
            'The resulting inner product is the electric-field amplitude measured in that receive channel.')
        self.play(Write(self.equation(r'\mathbf e_{\rm rx}^{\dagger}\mathbf e_{\rm rx}=1,\qquad \mathbf e_{\rm rx}\cdot\widehat{\mathbf n}=0',35,BLUE).shift(UP*2.3)))
        self.play(Write(self.equation(r'\mathbf e_{\rm rx}=\begin{bmatrix}e_x\\e_y\\e_z\end{bmatrix}\quad\Rightarrow\quad\mathbf e_{\rm rx}^{\dagger}=\begin{bmatrix}e_x^*&e_y^*&e_z^*\end{bmatrix}',34).shift(UP*.9)))
        self.play(Write(self.equation(r'E_{\rm rx}=\mathbf e_{\rm rx}^{\dagger}\widehat{\mathbf E}_s=e_x^*\widehat E_{s,x}+e_y^*\widehat E_{s,y}+e_z^*\widehat E_{s,z}',32,GREEN).shift(DOWN*.6)))
        self.play(FadeIn(self.equation(r'*:\ \text{complex conjugate};\quad \dagger:\ \text{conjugate transpose};\quad \widehat{\mathbf E}_s:\ \text{complex amplitude [V/m]}',23,MUTED).shift(DOWN*1.7)))
        self.next_slide('A linear polarization example',
            notes='For a real linear y-polarized receiver, the operation reduces to selecting E_y. For circular or elliptical polarization, relative complex phases matter and the conjugation is essential.')
        self.play(Write(self.equation(r'\mathbf e_{\rm rx}=(0,1,0)^{\mathsf T}\quad\Rightarrow\quad E_{\rm rx}=\widehat E_{s,y};\qquad |E_{\rm rx}|^2=E_{\rm rx}E_{\rm rx}^*',32,BLUE).shift(DOWN*2.85)))
        self.finish()

        self.start_slide('RCS is the equivalent area that reproduces the measured echo',
            'Compare receive-polarized scattered intensity at a large range R with incident intensity at the target. '
            'Vacuum intensity is squared peak field divided by twice Z_0. Define the equivalent isotropic scattering area '
            'by S_rx=S_inc sigma_rx/(4 pi R squared). The limiting range removes the one over R squared geometrical spreading.')
        self.play(Write(self.equation(r'S_{\rm inc}=\frac{|\widehat{\mathbf E}_{\rm inc}|^2}{2Z_0},\qquad S_{\rm rx}=\frac{|E_{\rm rx}|^2}{2Z_0}\quad[\mathrm{W/m^2}]',34,BLUE).shift(UP*2.2)))
        self.play(Write(self.equation(r'S_{\rm rx}=\frac{S_{\rm inc}\sigma_{\rm rx}}{4\pi R^2}\quad\Rightarrow\quad \sigma_{\rm rx}=4\pi R^2\frac{S_{\rm rx}}{S_{\rm inc}}',36).shift(UP*.8)))
        self.play(Write(self.equation(r'\boxed{\sigma_{\rm rx}=\lim_{R\to\infty}4\pi R^2\frac{|\mathbf e_{\rm rx}^{\dagger}\widehat{\mathbf E}_s|^2}{|\widehat{\mathbf E}_{\rm inc}|^2}}',40,GOLD).shift(DOWN*.8)))
        self.play(FadeIn(self.prose('R is observer range; the incident field is evaluated at the plasma cloud.',25).shift(DOWN*1.95)))
        self.play(FadeIn(self.equation(r'\sigma_{\rm rx}:\ \mathrm{m^2};\quad\text{hats on fields: complex amplitudes at }f_0',25,MUTED).shift(DOWN*2.75)))
        self.citation('MIT Lincoln Laboratory, radar cross section and the radar equation','https://www.ll.mit.edu/sites/default/files/outreach/doc/2018-07/lecture%201.pdf')
        self.finish()

        self.start_slide('Insert the radiated field: the range factors cancel',
            'Substitute the transverse-current far-field amplitude into the RCS definition. '
            'The squared outgoing phase is unity and the range squared cancels the squared one-over-range field. '
            'The remaining result is an area, with receive polarization explicitly selected.')
        self.stack(self.equation(r'\widehat{\mathbf E}_s=\frac{ikZ_0e^{ikR}}{4\pi R}\mathbf C_\perp',36,BLUE),
            self.equation(r'\sigma_{\rm rx}=4\pi R^2\frac{k^2Z_0^2}{16\pi^2R^2}\frac{|\mathbf e_{\rm rx}^{\dagger}\mathbf C_\perp|^2}{|\widehat{\mathbf E}_{\rm inc}|^2}',34),
            self.equation(r'\boxed{\sigma_{\rm rx}=\frac{k^2Z_0^2}{4\pi|\widehat{\mathbf E}_{\rm inc}|^2}|\mathbf e_{\rm rx}^{\dagger}\mathbf C_\perp|^2}',40,GOLD),
            self.equation(r'\sigma_{\rm dBsm}=10\log_{10}(\sigma_{\rm rx}/1\ \mathrm{m^2})',31),
            self.prose('This is the sigma to put into the radar equation.',28,BLUE))
        self.finish()

    def polarization(self):
        # Source: Polarization basis and current phases: fdtd/src/main.rs
        self.start_slide('Specify the monostatic polarization channel',
            'Incident propagation is +x and monostatic observation is -x. The following backward RHCP analyzer is the explicit '
            'solver convention; handedness must be referred to the propagation direction.')
        self.stack(self.equation(r'\widehat{\mathbf n}_{\rm back}=-\widehat{\mathbf k}_{\rm inc}=-\widehat{\mathbf x}',36),
            self.equation(r'\mathbf e_{\mathrm{rx},R}=\frac{i\widehat{\mathbf y}+\widehat{\mathbf z}}{\sqrt2},\qquad \mathbf e_{\mathrm{rx},R}^{\dagger}\mathbf C_\perp=\frac{C_z-iC_y}{\sqrt2}',38,BLUE),
            self.equation(r'\sigma_R\ \propto\ \frac{|C_z-iC_y|^2}{2}\quad\neq\quad |C_y|^2+|C_z|^2',38,GOLD),
            self.prose('MAARSY example: LHCP transmit, backward RHCP receive.',29,FG),
            self.prose('Keep radar aspect and receive polarization explicit in every comparison.',25))
        self.finish()

    def rayleigh_geometry(self):
        self.start_slide('A simple alternative: locate the overdense part of the cloud',
            'Marshall and Close compare the plasma to a conducting sphere whose radius is the location where '
            'plasma frequency equals radar frequency. First derive the critical density from omega_p=2 pi f_r. '
            'For a spherical cloud the projected overdense area is pi r_p squared, not the full surface area. '
            'The approximation applies to an overdense cloud; underdense clouds still scatter through their induced current.')
        self.play(Write(self.equation(r'f_p=\frac1{2\pi}\sqrt{\frac{n_ee^2}{\epsilon_0m_e}},\quad f_p=f_r\ \Rightarrow\quad n_{\rm crit}=\frac{\epsilon_0m_e}{e^2}(2\pi f_r)^2',34,BLUE).shift(UP*2.65)))
        outer=Circle(1.35,color=GREEN,fill_opacity=.06).move_to([-3.8,.15,0])
        core=Circle(.8,color=GOLD,fill_opacity=.2).move_to(outer)
        self.play(Create(outer),Create(core))
        self.play(GrowArrow(Arrow([-6.1,.15,0],[-5.3,.15,0],buff=0,color=BLUE)))
        self.add(self.prose('Incident radar wave',22,BLUE).move_to([-4.5,1.95,0]))
        self.play(Create(Line(core.get_center(),core.get_right(),color=GOLD)))
        self.add(self.equation(r'r_p',27,GOLD).move_to([-3.35,-.25,0]),
            self.equation(r'f_p=f_r',27,GOLD).move_to([-3.8,-1.6,0]))
        self.play(Write(self.equation(r'n_e(r_p)=n_{\rm crit},\qquad A_{\rm od}=\pi r_p^2',34,GOLD).move_to([2.5,.7,0])))
        self.play(FadeIn(self.equation(r'f_r:\ \text{radar frequency [Hz]};\quad n_{\rm crit}:\ \text{critical density [m}^{-3}\text{]}',23,MUTED).move_to([2.5,-.5,0])))
        self.play(FadeIn(self.equation(r'r_p:\ \text{critical-surface radius [m]};\quad A_{\rm od}:\ \text{projected area [m}^2\text{]}',24,MUTED).shift(DOWN*2.5)))
        self.play(FadeIn(self.prose('The enclosed core is overdense. The surrounding plasma also contributes to scattering.',24).shift(DOWN*3.2)))
        self.citation('Marshall and Close (2015), sections 1.1 and 3, figures 7--8','https://doi.org/10.1002/2015JA021238')
        self.finish()

        self.start_slide('Rayleigh to geometric scattering: area alone is not always enough',
            'Use the critical radius in a conducting-sphere surrogate. A small conducting sphere has Rayleigh '
            'backscatter 9 pi r_p squared times (k r_p) to the fourth. The large-sphere optical limit is pi r_p squared. '
            'These are limiting approximations, not an exact equality for a graded collisional plasma. '
            'Marshall and Close find a useful association with overdense size, with Rayleigh-like and optical regimes.')
        self.play(Write(self.equation(r'x\equiv kr_p=\frac{2\pi r_p}{\lambda_0}:\quad\text{electrical size of the overdense core}',31,BLUE).shift(UP*2.5)))
        self.play(FadeIn(self.prose('Small compared with wavelength: Rayleigh limit',29,GREEN).shift(UP*1.45)))
        self.play(Write(self.equation(r'x\ll1:\quad\sigma_{\rm R}\simeq9\pi r_p^2(kr_p)^4\propto r_p^6/\lambda_0^4',37,GREEN).shift(UP*.45)))
        self.next_slide('A large overdense core approaches the geometric area',
            notes='The projected area estimate is the optical or geometric limit. It should not be used for every meteor size. The factor nine belongs to a perfectly conducting sphere, including its electromagnetic response; it is not the electric-dipole dielectric-sphere formula on the next benchmark slide.')
        self.play(FadeIn(self.prose('Large compared with wavelength: geometric / optical limit',29,GOLD).shift(DOWN*.75)))
        self.play(Write(self.equation(r'x\gg1:\quad\sigma_{\rm G}\simeq A_{\rm od}=\pi r_p^2',40,GOLD).shift(DOWN*1.75)))
        self.play(FadeIn(self.prose('Near the transition, use the full plasma scattering solution.',24).shift(DOWN*2.65)))
        self.play(FadeIn(self.prose('Changing radar frequency also changes the critical radius.',24,BLUE).shift(DOWN*3.15)))
        self.citation('Marshall and Close (2015): conducting-sphere approximation','https://doi.org/10.1002/2015JA021238')
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

    def radar_equation(self):
        self.start_slide('Why RCS connects the plasma calculation to received power',
            'The transmitter sends power outward, the target redirects power, and effective aperture collects it. '
            'The two propagation legs give R to the fourth. Assume monostatic far field, matched polarization, no additional system losses.')
        rows=[(r'S_{\rm inc}=\frac{P_tG_t}{4\pi R^2}\quad[\mathrm{W/m^2}]','Incident flux at the meteor',BLUE),
            (r'S_{\rm back}=\frac{S_{\rm inc}\sigma_{\rm rx}}{4\pi R^2}\quad[\mathrm{W/m^2}]','Flux returning to the antenna',GOLD),
            (r'A_{\rm eff}=\frac{G_r\lambda_0^2}{4\pi},\quad P_r=S_{\rm back}A_{\rm eff}','Receiver collects flux over an area',GREEN)]
        for y,(eq,description,color) in zip([2.,.4,-1.2],rows):
            self.play(Write(self.equation(eq,32,color).move_to([-2.9,y,0])),FadeIn(self.prose(description,24,FG).move_to([3.6,y,0])))
        self.play(Write(self.equation(r'\boxed{P_r=\frac{P_tG_tG_r\lambda_0^2\sigma_{\rm rx}}{(4\pi)^3R^4}}',37,BLUE).shift(DOWN*2.35)))
        self.play(FadeIn(self.equation(r'P_t,P_r:\ \mathrm W;\quad G_t,G_r:\ \text{power gains};\quad R:\ \text{range [m]};\quad A_{\rm eff}:\ \mathrm{m^2}',23,MUTED).shift(DOWN*3.25)))
        self.citation('MIT Lincoln Laboratory, Introduction to Radar Systems: radar equation','https://www.ll.mit.edu/sites/default/files/outreach/doc/2018-07/lecture%201.pdf')
        self.finish()

    def radar_worked_examples(self):
        self.start_slide('Put the computed RCS here to obtain received power',
            'The scattering calculation supplies receive-polarized RCS in square metres. The radar parameters supply '
            'peak transmit power, boresight gains, wavelength and range. Gains must be linear, not dBi, in this equation. '
            'These examples omit additional propagation/feed losses; use RCS for the selected receive polarization.')
        formula=MathTex(r'P_r=\frac{P_tG_tG_r\lambda_0^2}{(4\pi)^3R^4}',r'\sigma_{\rm rx}',font_size=48,color=FG).shift(UP*1.7)
        formula[1].set_color(GOLD);self.play(Write(formula))
        box=SurroundingRectangle(formula[1],color=GOLD,buff=.15)
        self.play(Create(box))
        self.play(FadeIn(self.prose('RCS from the plasma scattering calculation, in square metres',28,GOLD).shift(UP*.4)))
        self.play(Write(self.equation(r'\sigma_{\rm dBsm}=-40\quad\Rightarrow\quad\sigma_{\rm rx}=10^{-40/10}=10^{-4}\ \mathrm{m^2}',35,GOLD).shift(DOWN*.8)))
        self.play(Write(self.equation(r'G_{\rm dBi}=33.5\quad\Rightarrow\quad G=10^{33.5/10}\simeq2239',34,BLUE).shift(DOWN*1.95)))
        self.play(FadeIn(self.prose('Use peak power during the pulse; waveform processing enters the SNR calculation.',25).shift(DOWN*3.0)))
        self.finish()
        with h5py.File(ROOT/'radar_examples.h5') as f:
            sig=f['worked/rcs_m2'][:];power=f['worked/power_w'][:];snr=f['worked/snr_db'][:]
            params=f['parameters'][:];mn=f['sigma_min_m2_10db_1mhz'][:]
            gaussian=f['gaussian_sigma_m2'][:];gpower=f['gaussian_received_w'][:]
            gsnr=f['gaussian_snr_db_10khz'][:]

        self.start_slide('Worked example: RCS to power to SNR',
            'MAARSY-like full-array parameters: 53.5 MHz, 736 kW peak, 33.5 dBi transmit and receive gains. '
            'Choose 100 km range, assumed 1000 K system noise and 10 kHz effective noise bandwidth. '
            'This is an ideal calculation, not a measured MAARSY threshold. dBm is power relative to one milliwatt.')
        self.play(Write(self.equation(r'f_0=53.5\ \mathrm{MHz},\ P_t=736\ \mathrm{kW},\ G_t=G_r=2239,\ R=100\ \mathrm{km}',29,BLUE).shift(UP*2.55)))
        self.play(Write(self.equation(r'T_{\rm sys}=1000\ \mathrm K,\ B=10\ \mathrm{kHz}:\quad P_n=k_BT_{\rm sys}B=1.38\times10^{-16}\ \mathrm W',29).shift(UP*1.55)))
        self.play(Write(self.equation(r'\mathrm{SNR}=P_r/P_n,\quad\mathrm{SNR}_{\rm dB}=10\log_{10}(P_r/P_n),\quad P_{\rm dBm}=10\log_{10}(P_r/10^{-3}\ \mathrm W)',25).shift(UP*.55)))
        self.next_slide('Compare three echo strengths',
            notes='Each tenfold increase in RCS gives tenfold power and ten dB more SNR. Values are computed from the stated ideal radar equation and noise assumptions. No unmentioned coherent integration is included.')
        xs=[-4.6,-1.8,1.5,4.7]
        for x,label in zip(xs,['RCS [dBsm]','RCS [square m]','Power [dBm]','SNR [dB]']):
            self.add(self.prose(label,25,BLUE).move_to([x,-.35,0]))
        for y,sg,pw,sn in zip([-1.1,-1.85,-2.6],sig,power,snr):
            values=[f'{10*np.log10(sg):.0f}',f'{sg:.0e}',f'{10*np.log10(pw/1e-3):.1f}',f'{sn:+.1f}']
            self.play(*[FadeIn(self.prose(value,28,FG).move_to([x,y,0])) for x,value in zip(xs,values)])
        self.play(FadeIn(self.prose('Double the range: -12 dB. Reduce noise bandwidth by ten: +10 dB SNR.',24,GOLD).shift(DOWN*3.25)))
        self.citation('MAARSY power/gain: Latteck et al.; noise temperature and bandwidth here are assumed','https://doi.org/10.1002/2015JD023291')
        self.finish()

        self.start_slide('Radar comparison: specify the instrument and the observing mode',
            'Representative on-axis monostatic link budgets. Arecibo is a historical 430 MHz configuration. '
            'Jicamarca is a full-array illustration with gain derived from the 75000 square metre effective aperture, '
            'not the quarter-array meteor mode. Millstone uses the zenith antenna. EISCAT 3D uses published Stage 1 design parameters. '
            'These are not contemporaneous calibrated operating records.')
        xs=[-4.9,-1.8,.3,2.6,4.8]
        for x,label in zip(xs,['Radar / configuration','f [MHz]','Peak [MW]','Gain [dBi]','Noise [K]']):
            self.add(self.prose(label,24,BLUE).move_to([x,2.25,0]))
        names=['Arecibo: historical','Jicamarca: full array','Millstone: zenith','EISCAT 3D: design']
        for y,name,row in zip([1.3,.3,-.7,-1.7],names,params):
            self.play(FadeIn(self.prose(name,24).move_to([xs[0],y,0])),
                *[FadeIn(self.prose(f'{value:g}' if j!=2 else f'{value:.1f}',26,FG).move_to([x,y,0])) for j,(x,value) in enumerate(zip(xs[1:],row))])
        self.play(FadeIn(self.prose('Use one common range, bandwidth, polarization and SNR criterion for comparison.',25).shift(DOWN*2.8)))
        refs=[('Arecibo: Janches et al. (2015)','https://pmc.ncbi.nlm.nih.gov/articles/PMC5023023/',-3.7,-3.45),
            ('Jicamarca: Wannberg et al. (2010)','https://www.diva-portal.org/smash/get/diva2:981094/FULLTEXT01.pdf',3.7,-3.45),
            ('Millstone: Haystack; US ISR school','https://www.sgo.fi/Events/RS2012/l/04_Stromme_US_ISRs.pdf',-3.7,-3.85),
            ('EISCAT 3D: Kastinen et al. (2020)','https://doi.org/10.5194/angeo-38-861-2020',3.7,-3.85)]
        links=[(label,url,self.prose(label,17,BLUE).move_to([x,y,0])) for label,url,x,y in refs]
        self.play(*[FadeIn(item) for _,_,item in links]);self.paper_links(links)
        self.finish()

        self.start_slide('Illustrative sensitivity: what RCS gives 10 dB SNR?',
            'Solve the radar equation for RCS using P_r=SNR k_B T_sys B. '
            'Take range 100 km, matched on-axis polarization, loss factor one, and no extra processing gain. '
            'Columns show one MHz and ten kHz effective noise bandwidth. They are standardized ideal thresholds, '
            'not published operational detection limits. A detector threshold also depends on false-alarm probability and search trials.')
        self.play(Write(self.equation(r'\sigma_{\min}=\frac{(4\pi)^3R^4\,k_BT_{\rm sys}B\,\mathrm{SNR}_{\min}}{P_tG_tG_r\lambda_0^2}',36,BLUE).shift(UP*2.2)))
        self.play(Write(self.equation(r'R=100\ \mathrm{km},\quad \mathrm{SNR}_{\min}=10\ (=10\ \mathrm{dB}),\quad L=1',27).shift(UP*1.2)))
        xs=[-4.5,0,4.4]
        for x,label in zip(xs,['Radar','Min. RCS: 1 MHz [dBsm]','Min. RCS: 10 kHz [dBsm]']):
            self.add(self.prose(label,24,BLUE).move_to([x,.3,0]))
        for y,name,sg in zip([-.5,-1.2,-1.9,-2.6],['Arecibo (historical)','Jicamarca (full array)','Millstone Hill (zenith)','EISCAT 3D (design)'],mn):
            self.play(FadeIn(self.prose(name,24).move_to([xs[0],y,0])),
                FadeIn(self.prose(f'{10*np.log10(sg):.1f}',28,FG).move_to([xs[1],y,0])),
                FadeIn(self.prose(f'{10*np.log10(sg)-20:.1f}',28,GREEN).move_to([xs[2],y,0])))
        self.play(FadeIn(self.prose('A smaller noise bandwidth requires enough coherent signal duration and correct Doppler matching.',23).shift(DOWN*3.35)))
        self.finish()

        self.start_slide('The same plasma can have a different RCS at each frequency',
            'For an explicit teaching benchmark use a weak unmagnetized Gaussian cloud, rather than assigning a universal '
            'frequency-independent meteor RCS. N_e is the total electron number and a is the standard deviation in every spatial direction. '
            'For matched linear polarization, first Born scattering is the squared spatial Fourier integral of density at backscatter wavevector 2k. '
            'This benchmark is not a Dimant-Oppenheim FDTD prediction.')
        self.play(Write(self.equation(r'n_e(\mathbf r)=\frac{N_e}{(2\pi)^{3/2}a^3}e^{-r^2/(2a^2)},\quad N_e=10^{10},\quad a=0.10\ \mathrm m',31,BLUE).shift(UP*2.2)))
        self.play(FadeIn(self.equation(r'N_e:\ \text{total electrons};\quad a:\ \text{Gaussian width};\quad\nu_{en}=10^7\ \mathrm{s^{-1}};\quad B_0=0',25).shift(UP*1.25)))
        self.play(Write(self.equation(r'\int n_e(\mathbf r)e^{2ikx}\,d^3r=N_ee^{-2k^2a^2}',35,GREEN).shift(UP*.1)))
        self.next_slide('Shorter wavelength increases phase cancellation across this cloud',
            notes='Fourier-transforming a Gaussian produces another Gaussian. Square its amplitude for power. The collision response adds omega squared over omega squared plus nu squared. The peak plasma frequency is about 7.2 MHz, well below the lowest radar frequency here; this is a weak-scattering example.')
        self.play(Write(self.equation(r'\sigma_{\rm back}=4\pi r_e^2N_e^2\,e^{-4k^2a^2}\frac{\omega^2}{\omega^2+\nu_{en}^2}',37,GOLD).shift(DOWN*1.3)))
        self.play(FadeIn(self.equation(r'r_e=\frac{e^2}{4\pi\epsilon_0m_ec^2}:\ \text{classical electron radius [m]};\quad k=\omega/c',25,MUTED).shift(DOWN*2.4)))
        self.play(FadeIn(self.prose('Illustrative weak-scattering cloud; replace it with the full plasma solve for a meteor prediction.',24,RED).shift(DOWN*3.2)))
        self.citation('Coherent-electron scattering: Janches et al. (2015); far-field current integral above','https://pmc.ncbi.nlm.nih.gov/articles/PMC5023023/')
        self.finish()

        self.start_slide('Same example cloud: RCS, received power and SNR',
            'Apply each radar frequency to the same Gaussian benchmark, then use each stated radar link budget. '
            'Use 100 km range and ten kHz equivalent noise bandwidth, matched linear polarization and no additional losses. '
            'RCS differs through scattering; power and SNR additionally depend on radar hardware. '
            'These are illustrative calculations, not measurements of this cloud at four radars.')
        xs=[-4.8,-1.1,2.,5.]
        for x,label in zip(xs,['Radar','RCS [dBsm]','Power [dBm]','SNR [dB]']):
            self.add(self.prose(label,25,BLUE).move_to([x,2.3,0]))
        for y,name,sg,pw,sn in zip([1.3,.25,-.8,-1.85],['Arecibo (historical)','Jicamarca (full array)','Millstone Hill (zenith)','EISCAT 3D (design)'],gaussian,gpower,gsnr):
            values=[name,f'{10*np.log10(sg):.1f}',f'{10*np.log10(pw/1e-3):.1f}',f'{sn:+.1f}']
            self.play(*[FadeIn(self.prose(value,25,FG).move_to([x,y,0])) for x,value in zip(xs,values)])
        self.play(FadeIn(self.prose('Same electrons; different interference and radar sensitivity.',25,GOLD).shift(DOWN*2.85)))
        self.play(FadeIn(self.prose('R = 100 km; B = 10 kHz; instrument parameters from the preceding table.',23).shift(DOWN*3.45)))
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
        entries=[('Solar radiation: Burns, Lamy and Soter (1979)','10.1016/0019-1035(79)90050-2'),
            ('Meteoroid collisions: Grün et al. (1985)','10.1016/0019-1035(85)90121-6'),
            ('Orbital dust populations: Nesvorný et al. (2011)','10.1088/0004-637X/743/2/129'),
            ('Collisional grooming: Stark and Kuchner (2009)','10.1088/0004-637X/707/1/543'),
            ('Comet fragmentation: Rigley and Wyatt (2022)','10.1093/mnras/stab3482'),
            ('Dust strength: Pokorný et al. (2024)','10.3847/PSJ/ad2de8'),
            ('Rarefied entry: Bariselli et al. (2020)','10.1093/mnras/stz3559'),
            ('Free molecular sphere drag: Loth et al. (2021)','10.2514/1.J060153'),
            ('Thermal ablation: Hill et al. (2005)','10.1051/0004-6361:20053053'),
            ('Primary Si ionization: Jones (1997)','10.1093/mnras/288.4.995'),
            ('Molecular scattering: Khrapak (2014)','10.1140/epjd/e2014-50449-y'),
            ('Classical collision theory: MIT 16.55 (2014)',
             'https://ocw.mit.edu/courses/16-55-ionized-gases-fall-2014/ba010aa23f0da845aa3ff555f3d60921_MIT16_55F14_Lecture6-7.pdf'),
            ('Empirical collisions: Bronshten (1983)','10.1007/978-94-009-7222-3'),
            ('Collision cross section: Sugar et al. (2018), section 5.3','10.1002/2018JA025265'),
            ('Phase-space conservation: MIT 16.55 (2014), lecture 8',
             'https://ocw.mit.edu/courses/16-55-ionized-gases-fall-2014/b7c22c3d68ab558bcc3a59867b710e1a_MIT16_55F14_Lecture8.pdf'),
            ('Kinetic model: Dimant and Oppenheim (2017), Part 1','10.1002/2017JA023960'),
            ('Density solution: Dimant and Oppenheim (2017), Part 2','10.1002/2017JA023963'),
            ('Staggered Maxwell grid: Yee (1966)','10.1109/TAP.1966.1138693'),
            ('Absorbing layer: Roden and Gedney (2000)','10.1002/1098-2760(20001205)27:5%3C334::AID-MOP14%3E3.0.CO;2-A'),
            ('Plasma FDTD: Marshall and Close (2015)','10.1002/2015JA021238'),
            ('Head-plasma profiles: Marshall, Brown and Close (2017)','10.1016/j.pss.2016.12.011')]
        pages=(len(entries)+5)//6
        for page in range(pages):
            self.start_slide('References (%d/%d)'%(page+1,pages),'Clickable primary references for the physical derivation.')
            subset=entries[page*6:page*6+6]
            rows=VGroup(*[VGroup(self.prose(title,23,FG),self.prose(('MIT OpenCourseWare: Kinetic Theory' if 'Lecture8' in doi else 'MIT OpenCourseWare: Collision Theory') if doi.startswith('https://') else 'doi:'+doi.replace('%3C','<').replace('%3E','>'),16,BLUE)).arrange(DOWN,buff=.14,aligned_edge=LEFT)
                for title,doi in subset]).arrange(DOWN,buff=.3,aligned_edge=LEFT).move_to(ORIGIN)
            for row in rows:self.play(FadeIn(row),run_time=.3)
            self.paper_links([(title,doi if doi.startswith('https://') else 'https://doi.org/'+doi,row) for (title,doi),row in zip(subset,rows)])
            if page<pages-1:self.finish()
        self.wait(1.)
