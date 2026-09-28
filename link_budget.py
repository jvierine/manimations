"""Satellite link budget and coherent BPSK bit-error demonstration.

Render:
    conda run -n base manim-slides render -r 1920,1080 --fps 30 link_budget.py LinkBudget
Export:
    conda run -n base python export_web.py /tmp/link-budget-web LinkBudget

Scientific conventions:
* Uncoded, equiprobable BPSK; coherent phase/timing recovery; AWGN.
* N0 = k_B T_sys is one-sided RF noise PSD. Each real matched-filter
  noise coordinate has variance N0/2 (energy-normalized coordinates).
* Normalized complex samples z=a+w, a=+-1, Var(Re w)=1/(2 Eb/N0).
* Receiver matched-filter decisions occur once per symbol, not once per
  carrier cycle or ADC sample. BPSK has one bit per symbol.
* All budget numbers are a labeled illustrative design, not mission data.

References (kept in source, not an intrusive slide footer):
https://www.mathworks.com/help/matlab/ref/erfc.html
https://www.mathworks.com/help/comm/ug/analytical-expressions-used-in-berawgn-function-and-bit-error-rate-analysis-app.html
https://directreadout.sci.gsfc.nasa.gov/aqua_documents/Dbiddbo1.pdf
"""
from pathlib import Path

import h5py
import numpy as np
from scipy.special import erfc, erfcinv
from manim import *
from planck_to_ktb import PlanckToKTB, BG, FG, MUTED, PLANCK, RJ, RADIO, ACCENT, RED
# Use the same TeX-backed prose renderer as every other teaching deck.
from planck_to_ktb import Text


def bpsk_ber(ebn0_db):
    return .5 * erfc(np.sqrt(10.0 ** (np.asarray(ebn0_db) / 10)))


def simulate_bpsk(ebn0_db, count=400_000, seed=20260924):
    """Independent complex AWGN, normalized by sqrt(Eb)."""
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, count)
    symbols = 2 * bits - 1
    sigma = np.sqrt(1 / (2 * 10 ** (ebn0_db / 10)))
    samples = symbols + sigma * (rng.normal(size=count) + 1j * rng.normal(size=count))
    decoded = (samples.real >= 0).astype(int)
    return bits, symbols, samples, decoded


def example_budget():
    c, kb = 299_792_458., 1.380649e-23
    f, distance, diameter, efficiency = 8.4e9, 1e6, 1., .6
    tx_w, tx_gain, tx_loss, other_loss = 2., 0., 1., 2.
    temperature, bit_rate, bandwidth = 150., 1e6, 1e6
    wavelength = c / f
    rx_gain = 10 * np.log10(efficiency * (np.pi * diameter / wavelength) ** 2)
    fspl = 20 * np.log10(4 * np.pi * distance / wavelength)
    tx_dbw = 10 * np.log10(tx_w)
    pr_dbw = tx_dbw + tx_gain - tx_loss - fspl + rx_gain - other_loss
    n0_db = 10 * np.log10(kb * temperature)
    noise_dbw = n0_db + 10 * np.log10(bandwidth)
    eb_db = pr_dbw - n0_db - 10 * np.log10(bit_rate)
    required_db = 10 * np.log10(erfcinv(2e-5) ** 2)
    return dict(rx_gain=rx_gain, fspl=fspl, tx_dbw=tx_dbw, pr_dbw=pr_dbw,
                n0_db=n0_db, noise_dbw=noise_dbw, eb_db=eb_db,
                required_db=required_db, margin_db=eb_db-required_db-1.,
                gt_db=rx_gain-10*np.log10(temperature))


class LinkBudget(PlanckToKTB):
    """Standalone browser deck; inherits the tested pause-before-cleanup behavior."""

    def setup(self):
        super().setup()
        self.provenance.become(Text("Source: link_budget.py", font_size=15, color=MUTED).to_corner(DR))

    def eq(self, tex, y=0, size=41, color=FG):
        m = MathTex(tex, font_size=size, color=color)
        if m.width > 12.4:
            m.scale_to_fit_width(12.4)
        return m.move_to(UP * y)

    def txt(self, text, y=0, size=28, color=MUTED):
        m = Text(text, font_size=size, color=color)
        if m.width > 12.4:
            m.scale_to_fit_width(12.4)
        return m.move_to(UP * y)

    def begin(self, title):
        self.start_slide(title)
        self.play(FadeIn(self.title(title)))

    def finish(self):
        self.wait(2.5)
        self.clear_slide()

    def lines(self, objects):
        for obj in objects:
            self.play(Write(obj) if isinstance(obj, MathTex) else FadeIn(obj))

    def construct(self):
        self.requirements()
        self.power_budget()
        self.bpsk_field()
        self.receiver()
        self.constellation()
        self.noise()
        self.noise_error()
        self.energy_per_bit()
        self.bit_stream()
        self.gaussian_tail()
        self.ber_curve()
        self.worked_budget()
        self.margin()
        self.shorthand()
        self.conclusion()

    def requirements(self):
        self.begin("Link budget")
        self.lines([
            self.txt("Can the satellite deliver its data with an acceptable error rate?", 2.15, 33, FG),
            self.eq(r"R_{\mathrm{payload}}\geq\frac{\text{data volume}}{\text{usable contact time}}", .9, 43),
            self.eq(r"\text{For example:}\quad\frac{600\ \mathrm{Mbit}}{600\ \mathrm s}=1\ \mathrm{Mbit\,s^{-1}}", -.25, 48, RADIO),
            self.txt("Is the received signal strong enough to send data at this rate with few enough errors?", -2.5, 30, ACCENT),
        ])
        self.finish()

    def power_budget(self):
        self.begin("Received power: gains and losses")
        factors = [r"P_r", "=", r"P_t", r"G_t", r"G_r",
                   r"\left(\frac{\lambda}{4\pi R}\right)^2"]
        shades = [FG,FG,RADIO,PLANCK,RJ,ACCENT,RED]
        ordinary = MathTex(*factors,font_size=46).move_to(UP*2)
        linear = MathTex(*factors,r"\frac{1}{L}",font_size=46).move_to(UP*2)
        for formula in (ordinary,linear):
            for term,shade in zip(formula,shades):
                term.set_color(shade)
        intro = self.txt("Friis: received power for ideal free-space propagation.",.65,28,FG)
        self.play(Write(ordinary),FadeIn(intro))
        self.wait(1.5)
        loss_definition = self.eq(r"L\geq1:\quad\text{additional power-loss factor}",.55,35,RED)
        loss_examples = self.txt("Feed and cable losses, atmospheric absorption, pointing and polarization mismatch.",-.6,26,RED)
        self.play(TransformMatchingTex(ordinary,linear),FadeOut(intro),run_time=2)
        self.play(Indicate(linear[6],color=RED),Write(loss_definition))
        self.play(FadeIn(loss_examples))
        self.wait(2)
        self.start_slide("Map every Friis factor to decibels")
        self.play(FadeOut(loss_definition),FadeOut(loss_examples))
        rule = self.txt("Take 10 log10: multiplication becomes addition; division becomes subtraction.",-2.8,25)
        self.play(FadeIn(rule))
        db = MathTex(r"P_{r,\mathrm{dBW}}","=",r"P_{t,\mathrm{dBW}}","+",
                     r"G_{t,\mathrm{dBi}}","+",r"G_{r,\mathrm{dBi}}",
                     r"-L_{\mathrm{FS,dB}}",r"-L_{\mathrm{other,dB}}",font_size=34)
        if db.width>12.7:
            db.scale_to_fit_width(12.7)
        db.move_to(DOWN*.05)
        self.play(*[Write(db[i]) for i in (1,3,5)])
        conversions = [
            (0,0,r"P_{r,\mathrm{dBW}}=10\log_{10}(P_r/1\,\mathrm W)"),
            (2,2,r"P_{t,\mathrm{dBW}}=10\log_{10}(P_t/1\,\mathrm W)"),
            (3,4,r"G_{t,\mathrm{dBi}}=10\log_{10}G_t"),
            (4,6,r"G_{r,\mathrm{dBi}}=10\log_{10}G_r"),
            (5,7,r"10\log_{10}\!\left[\left(\frac{\lambda}{4\pi R}\right)^2\right]"
                 r"=-20\log_{10}\!\left(\frac{4\pi R}{\lambda}\right)=-L_{\mathrm{FS,dB}}"),
            (6,8,r"10\log_{10}(1/L)=-10\log_{10}L=-L_{\mathrm{other,dB}}"),
        ]
        for source,target,conversion in conversions:
            shade=shades[source]
            db[target].set_color(shade)
            detail=self.eq(conversion,-1.5,32,shade)
            arrow=Arrow(linear[source].get_bottom()+DOWN*.08,db[target].get_top()+UP*.08,
                        buff=.05,color=shade,stroke_width=2)
            self.play(Indicate(linear[source],color=shade),GrowArrow(arrow),run_time=.65)
            self.play(TransformFromCopy(linear[source],db[target]),Write(detail),run_time=1.4)
            self.wait(.65)
            self.play(FadeOut(arrow),FadeOut(detail),run_time=.3)
        self.play(FadeOut(rule))
        self.play(Write(self.eq(r"L_{\mathrm{FS,dB}}=20\log_{10}\!\left(\frac{4\pi R}{\lambda}\right)",-1.3,35,ACCENT)),
                  Write(self.eq(r"L_{\mathrm{other,dB}}=10\log_{10}L",-2.2,35,RED)))
        self.play(FadeIn(self.txt("dBW: power relative to 1 W. dBi: gain relative to isotropic. Losses are subtracted.",-3.2,23)))
        self.finish()

    def noise(self):
        self.begin("The receiver also collects noise")
        assets = Path(__file__).resolve().parent / "assets"
        # Hold each source map until the presenter advances; then fade it out.
        def show_image(filename, heading, explanation, credit):
            picture = ImageMobject(str(assets / filename))
            picture.scale_to_fit_width(11.5)
            if picture.height > 4.2:
                picture.scale_to_fit_height(4.2)
            picture.move_to(UP*.1)
            caption = self.txt(heading,2.65,30,ACCENT)
            detail = self.txt(explanation,-2.55,25,FG)
            attribution = self.txt(credit,-3.2,19)
            self.play(FadeIn(picture),FadeIn(caption),FadeIn(detail),FadeIn(attribution))
            self.wait(4)
            self.next_slide()
            self.play(FadeOut(picture),FadeOut(caption),FadeOut(detail),FadeOut(attribution))

        show_image("haslam_408mhz.png","Galactic synchrotron emission: the 408 MHz sky",
                   "Electrons spiraling in Galactic magnetic fields emit radio waves.",
                   "Haslam et al. (1982), the same map used in the Planck deck")
        show_image("planck_cmb_esa.jpg","Cosmic microwave background: the Big Bang's afterglow",
                   "Colors show tiny temperature variations around the nearly uniform 2.725 K background.",
                   "Credit: ESA and the Planck Collaboration (2013)")
        sky = VGroup(
            Text("Galactic synchrotron emission",font_size=25,color=PLANCK),
            Text("Electrons spiraling in the Galaxy's magnetic field",font_size=19,color=MUTED),
            Text("Cosmic microwave background",font_size=25,color=ACCENT),
            Text("A small contribution from the Big Bang's afterglow",font_size=19,color=MUTED),
        ).arrange(DOWN,buff=.18).move_to([-3.6,1.65,0])
        antenna = VGroup(Line([-.6,.9,0],[-.6,-.3,0],color=RADIO),
                         Line([-1.1,1.4,0],[-.6,.9,0],color=RADIO),
                         Line([-.1,1.4,0],[-.6,.9,0],color=RADIO))
        amp = Polygon([1.45,.1,0],[1.45,1.4,0],[2.7,.75,0],color=RJ)
        cable = VMobject(color=RADIO,stroke_width=4).set_points_as_corners(
            [[-.6,-.3,0],[.65,-.3,0],[.65,.75,0],[1.45,.75,0]])
        labels = VGroup(Text("Antenna",font_size=23,color=RADIO).move_to([-.6,-.65,0]),
                        Text("Amplifier",font_size=23,color=RJ).move_to([2.05,-.3,0]),
                        Text("Adds its own electronic noise",font_size=21,color=RJ).move_to([3,2.15,0]))
        self.play(FadeIn(sky),Create(antenna),Create(amp),Create(cable),FadeIn(labels))
        for y,shade in [(.2,PLANCK),(-.35,ACCENT)]:
            wave=ParametricFunction(lambda t,y=y:np.array([-2.4+1.2*t,y+.09*np.sin(18*t),0]),t_range=[0,1],color=shade)
            self.play(Create(wave),run_time=.7)
            self.play(wave.animate.shift(RIGHT*.45),run_time=.7)
            self.play(FadeOut(wave),run_time=.2)
        signal_label=Text("Signal",font_size=24,color=RADIO).move_to([4.5,-.05,0])
        def waveform(perturbation=None):
            sample_t=np.linspace(0,1,240)
            values=.22*np.sin(12*np.pi*sample_t)
            if perturbation is not None:
                values += perturbation
            curve=VMobject(stroke_width=3,color=RADIO if perturbation is None else RED)
            curve.set_points_as_corners([np.array([3+2.8*t,.75+y,0]) for t,y in zip(sample_t,values)])
            return curve
        output=waveform()
        self.play(Create(Arrow([2.7,.75,0],[3,.75,0],buff=0,color=RJ)),Create(output))
        self.play(FadeIn(signal_label))
        self.wait(1.5)
        # Seeded random perturbations, not a second periodic signal.
        rng=np.random.default_rng(20260928)
        noisy_label=Text("Signal + noise",font_size=24,color=RED).move_to(signal_label)
        self.play(Transform(output,waveform(rng.normal(0,.055,240))),
                  Transform(signal_label,noisy_label),run_time=2)
        for _ in range(3):
            self.play(Transform(output,waveform(rng.normal(0,.055,240))),run_time=.7)
        diagram=Group(*[m for m in self.mobjects if m is not self.provenance][1:])
        self.play(FadeOut(diagram))
        atmosphere=ImageMobject(str(assets / "atmospheric_windows_nasa.gif")).scale_to_fit_width(12)
        atmosphere.move_to(UP*.15)
        heading=self.txt("The atmosphere has microwave transmission windows",2.6,30,ACCENT)
        # NASA chart: microwave region occupies the rightmost quarter.
        window=SurroundingRectangle(Rectangle(width=atmosphere.width*.24,height=atmosphere.height)
                                    .move_to(atmosphere.get_right()+LEFT*atmosphere.width*.12),
                                    buff=.08,color=ACCENT)
        explanation=self.txt("High transmission means little absorption. Water vapour and oxygen close some windows.",-2.25,25,FG)
        emission=self.txt("Absorbing atmospheric gases also emit thermal noise into the receiver.",-2.85,25,PLANCK)
        credit=self.txt("Source: NASA Earth Observatory, Remote Sensing (wavelength axis is not to scale)",-3.4,19)
        self.play(FadeIn(atmosphere),FadeIn(heading),FadeIn(explanation),FadeIn(emission),FadeIn(credit))
        self.play(Create(window))
        self.wait(4)
        self.play(*[FadeOut(m) for m in [atmosphere,heading,window,explanation,emission,credit]])
        self.play(FadeIn(diagram))
        self.lines([
            self.txt("Atmosphere, warm ground and lossy feed components can contribute too.",-1.35,25),
            self.eq(r"N=k_{\mathrm B}T_{\mathrm{sys}}B",-2.15,43,RADIO),
            self.txt("System noise temperature summarizes these contributions at the receiver input.",-2.9,24),
            self.txt("N is noise power. B is the receiver's noise bandwidth in hertz.",-3.4,23),
        ])
        self.finish()

    def bpsk_field(self):
        self.begin("An example of sending bits: BPSK")
        purpose=self.txt("We will use two carrier phases to send 0 and 1, then see how noise causes errors.",2.65,26,FG)
        self.play(FadeIn(purpose))
        self.wait(2)
        self.play(FadeOut(purpose))
        bits = np.array([1, 0, 1, 1, 0, 0])
        symbols = 2 * bits - 1
        self.play(Write(self.eq(r"1\mapsto a_k=+1,\qquad 0\mapsto a_k=-1", 2.45, 38, ACCENT)))
        axes = Axes(x_range=[0, 6, 1], y_range=[-1.3, 1.3, 1], x_length=11,
                    y_length=2.0, tips=False, axis_config={"color": MUTED}).move_to(UP * .7)
        waves = VGroup(*[axes.plot(
            lambda t, k=k: symbols[k] * np.cos(6 * np.pi * t),
            x_range=[k, k + 1, .008], color=RADIO if bits[k] else PLANCK)
            for k in range(6)])
        labels = VGroup(*[MathTex(str(b), font_size=30, color=RADIO if b else PLANCK)
                          .move_to(axes.c2p(k+.5, 1.65)) for k,b in enumerate(bits)])
        boundaries = VGroup(*[DashedLine(axes.c2p(k,-1.2),axes.c2p(k,1.2),
                                        color=MUTED, stroke_opacity=.4) for k in range(1,6)])
        self.play(Create(axes), Create(boundaries), Write(labels))
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=.35), run_time=4)
        self.play(Write(MathTex(r"E/E_0",font_size=25,color=MUTED).next_to(axes,LEFT,buff=.12)),
                  Write(MathTex(r"t/T_s",font_size=25,color=MUTED).next_to(axes,RIGHT,buff=.12)))
        self.lines([
            self.eq(r"E(t)=E_0a_k\cos(2\pi f_ct),\qquad kT_s\leq t<(k+1)T_s", -1.05, 37),
            self.eq(r"R_s=1/T_s\ [\mathrm{baud}],\qquad R_b=R_s\ [\mathrm{bit/s}]\quad\text{for BPSK}", -2.05, 32),
            self.eq(r"E_0\ [\mathrm{V/m}],\quad f_c\ [\mathrm{Hz}],\quad T_s\ [\mathrm s]"
                    r"\qquad -\cos(\omega t)=\cos(\omega t+\pi)", -2.9, 29),
        ])
        self.finish()

    def receiver(self):
        self.begin("The receiver recovers one sample per symbol")
        stages = ["Antenna", "I/Q mixing", "Matched filter", "Sample", "Decide bit"]
        group = VGroup(*[Text(s, font_size=25, color=RADIO) for s in stages]).arrange(RIGHT, buff=.65).move_to(UP*1.8)
        arrows = VGroup(*[Arrow(group[i].get_right(),group[i+1].get_left(),
                               buff=.12,color=MUTED,max_tip_length_to_length_ratio=.3) for i in range(4)])
        self.play(FadeIn(group), Create(arrows))
        self.lines([
            self.eq(r"v(t)\propto E(t),\qquad u(t)=I(t)+iQ(t)", .65, 42),
            self.txt("Mix with cosine and sine at the carrier frequency, then low-pass filter.", -.2, 25),
            self.eq(r"z_k=a_k+w_k,\quad a_k\in\{-1,+1\},\qquad "
                    r"\widehat b_k=\begin{cases}1,&\Re z_k\geq0\\0,&\Re z_k<0\end{cases}", -1.35, 37),
            self.eq(r"w_k=n_{I,k}+i n_{Q,k}:\quad\text{complex noise in the }k\text{-th decision sample}", -2.3, 28,ACCENT),
            self.txt("Its real and imaginary parts are noise after matched filtering and normalization.", -2.9, 24),
            self.txt("The ADC may sample much faster. The final decision is once per symbol.", -3.45, 23),
        ])
        self.finish()

    def iq_axes(self):
        axes = Axes(x_range=[-2.5,2.5,1], y_range=[-1.7,1.7,1],
                    x_length=9.6,y_length=3.5,tips=False,
                    axis_config={"color":MUTED}).move_to(DOWN*.15)
        labels=VGroup(MathTex(r"I=\Re z",font_size=28).next_to(axes.x_axis,RIGHT,buff=.12),
                      MathTex(r"Q=\Im z",font_size=28).next_to(axes.y_axis,UP,buff=.12))
        boundary=DashedLine(axes.c2p(0,-1.6),axes.c2p(0,1.6),color=RED)
        ideals=VGroup(*[Dot(axes.c2p(x,0),radius=.1,color=c) for x,c in [(-1,PLANCK),(1,RADIO)]])
        return axes, labels, boundary, ideals

    def constellation(self):
        self.begin("BPSK in complex baseband")
        axes, labels, boundary, ideals = self.iq_axes()
        self.play(Create(axes),Write(labels),Create(boundary),FadeIn(ideals))
        self.lines([
            self.eq(r"0:\ (-1,0)\qquad\qquad 1:\ (+1,0)",2.4,35,ACCENT),
            self.txt("Negative I: decide 0                         Positive I: decide 1", -2.35, 29),
            self.txt("BPSK uses two phases. The ideal Q component is zero.", -3.0, 27),
        ])
        self.finish()

    def noise_error(self):
        self.begin("Noise can move a symbol across the boundary")
        axes, labels, boundary, ideals = self.iq_axes()
        self.play(Create(axes),Write(labels),Create(boundary),FadeIn(ideals))
        self.play(FadeIn(self.txt("Transmit bit 1: start at +1", 2.4, 30, RADIO)))
        point=Dot(axes.c2p(1,0),radius=.12,color=ACCENT)
        self.add(point)
        small=Arrow(axes.c2p(1,0),axes.c2p(.65,.35),buff=0,color=ACCENT)
        self.play(GrowArrow(small),point.animate.move_to(axes.c2p(.65,.35)),run_time=2)
        status=self.txt("I = +0.65: still decoded as 1", -2.45, 30, RJ)
        self.play(FadeIn(status))
        self.wait(1.5)
        self.start_slide("A noise realization causes a bit error")
        self.play(FadeOut(small),FadeOut(status),point.animate.move_to(axes.c2p(1,0)))
        kick=Arrow(axes.c2p(1,0),axes.c2p(-.35,.55),buff=0,color=RED)
        self.play(GrowArrow(kick),point.animate.move_to(axes.c2p(-.35,.55)),run_time=3)
        self.play(FadeIn(self.txt("I = -0.35: receiver decides 0, but we sent 1", -2.4, 30, RED)))
        self.play(FadeIn(self.txt("Illustrative noise draws. Crossing I = 0 causes the error.", -3.05, 25)))
        self.finish()

    def bit_stream(self):
        self.begin("A noisy bit stream")
        bits, symbols, z, decoded = simulate_bpsk(0., count=24, seed=8)
        errors=decoded != bits
        self.play(Write(self.eq(r"24\ \text{random bits},\quad E_b/N_0=0\ \mathrm{dB}",2.45,34)))
        axes=Axes(x_range=[0,25,5],y_range=[-2.8,2.8,1],x_length=11.4,y_length=2.5,
                  tips=False,axis_config={"color":MUTED}).move_to(UP*.3)
        self.play(Create(axes))
        self.play(Write(MathTex(r"I=\Re z_k",font_size=26,color=MUTED).next_to(axes,UP,buff=.05)))
        dots=VGroup(*[Dot(axes.c2p(k+1,float(z[k].real)),radius=.045,
                         color=RED if errors[k] else RJ) for k in range(24)])
        ideals=VGroup(*[Dot(axes.c2p(k+1,int(symbols[k])),radius=.025,color=MUTED) for k in range(24)])
        self.play(FadeIn(ideals),LaggedStart(*[FadeIn(d) for d in dots],lag_ratio=.09),run_time=4)
        tx=VGroup(*[Text(str(b),font_size=22,color=FG).move_to([axes.c2p(k+1,0)[0],-1.55,0]) for k,b in enumerate(bits)])
        rx=VGroup(*[Text(str(b),font_size=22,color=RED if errors[k] else RJ).move_to([axes.c2p(k+1,0)[0],-2.0,0]) for k,b in enumerate(decoded)])
        self.play(FadeIn(tx),FadeIn(rx))
        row_labels=VGroup(Text("Sent",font_size=19,color=FG).move_to([-6.35,-1.55,0]),
                          Text("Read",font_size=19,color=RJ).move_to([-6.35,-2.,0]))
        self.play(FadeIn(row_labels))
        self.play(Write(self.eq(r"\widehat{\mathrm{BER}}=\frac{\text{wrong bits}}{\text{transmitted bits}}"
                               rf"=\frac{{{errors.sum()}}}{{24}}={errors.mean():.3f}",-2.75,37,ACCENT)))
        self.play(FadeIn(self.txt("A short sample fluctuates. Estimating BER accurately takes many more bits.",-3.4,22)))
        self.finish()

    def energy_per_bit(self):
        self.begin("Signal-to-noise ratio per bit")
        # B is a chosen noise bandwidth, not a universal identity with baud rate.
        # Reference: https://www.mathworks.com/help/comm/ug/awgn-channel.html
        rates=self.eq(r"\text{BPSK: one bit per symbol, so }"
                      r"\underbrace{R_s}_{\text{baud rate}}=\underbrace{R_b}_{\text{bit rate}}",2.45,31)
        self.play(Write(rates))
        start=self.eq(r"\mathrm{SNR}=\frac{P_r}{N}=\frac{P_r}{k_{\mathrm B}T_{\mathrm{sys}}B}",1.15,45)
        self.play(Write(start))
        assumption=self.eq(r"\text{For this example, choose noise bandwidth }B=R_s=R_b.",-.05,29,ACCENT)
        self.play(Write(assumption))
        self.wait(1)
        substituted=self.eq(r"\mathrm{SNR}=\frac{P_r}{k_{\mathrm B}T_{\mathrm{sys}}R_b}"
                            r"=\frac{P_r/R_b}{k_{\mathrm B}T_{\mathrm{sys}}}",1.15,45)
        self.play(TransformMatchingTex(start,substituted),run_time=2)
        definitions=self.eq(r"\underbrace{E_b=P_r/R_b=P_rT_b}_{\text{energy received during one bit }[\mathrm J]}"
                            r"\qquad\underbrace{N_0=k_{\mathrm B}T_{\mathrm{sys}}=N/B}_{\text{noise power per hertz }[\mathrm{W/Hz}]}",-1.35,31)
        definitions.set_color_by_tex(r"E_b",PLANCK,substring=False)
        self.play(Write(definitions),run_time=2)
        result=self.eq(r"\mathrm{SNR}=\frac{E_b}{N_0}\qquad(B=R_b)",1.15,51,RADIO)
        self.play(TransformMatchingTex(substituted,result),run_time=2)
        explanation=Tex(r"$T_b=1/R_b$ is one bit's duration. $E_b/N_0$ compares signal energy per bit with noise per hertz.",
                        font_size=25,color=FG)
        if explanation.width>12.4:
            explanation.scale_to_fit_width(12.4)
        explanation.move_to(DOWN*2.55)
        self.play(FadeIn(explanation))
        self.play(Write(self.eq(r"\text{For any noise bandwidth: }\quad"
                               r"\frac{E_b}{N_0}=\mathrm{SNR}\,\frac{B}{R_b}",-3.3,28,MUTED)))
        self.finish()

    def gaussian_tail(self):
        self.begin("Why each noise component has half the variance")
        self.lines([
            self.eq(r"z=I+iQ=a+w,\qquad a=\pm1,\qquad w=n_I+i n_Q",2.25,38),
            self.eq(r"\text{Normalize the symbol energy to }|a|^2=1:\quad"
                    r"\mathbb E[|w|^2]=\frac{N_0}{E_b}=\frac{1}{E_b/N_0}",1.1,36,RADIO),
            self.eq(r"n_I,n_Q:\ \text{independent real Gaussian noise, zero mean, equal variance}",.05,27),
        ])
        split=self.eq(r"\mathbb E[|w|^2]=\mathbb E[n_I^2+n_Q^2]"
                      r"=\sigma_I^2+\sigma_Q^2",-1.05,39)
        self.play(Write(split))
        equal=self.eq(r"\mathbb E[|w|^2]=\sigma_I^2+\sigma_Q^2=2\sigma_I^2",-1.05,39)
        self.play(TransformMatchingTex(split,equal),run_time=2)
        self.play(Write(self.eq(r"\boxed{\sigma_I^2=\sigma_Q^2=\frac12\frac{N_0}{E_b}"
                               r"=\frac{1}{2(E_b/N_0)}}",-2.25,43,ACCENT)))
        self.play(Write(self.eq(r"I=a+n_I:\quad\text{only the real component determines the BPSK bit decision.}",-3.25,27)))
        self.finish()
        self.begin("BER is the probability of crossing zero")
        axes=Axes(x_range=[-3,3,1],y_range=[0,1,.5],x_length=10.7,y_length=2.55,
                  tips=False,axis_config={"color":MUTED}).move_to(UP*.75)
        sigma=.65
        pdf=lambda x,mu: np.exp(-.5*((x-mu)/sigma)**2)/(sigma*np.sqrt(2*np.pi))
        left=axes.plot(lambda x:pdf(x,-1),color=PLANCK)
        right=axes.plot(lambda x:pdf(x,1),color=RADIO)
        error_zero=axes.get_area(left,x_range=[0,3],color=PLANCK,opacity=.65)
        error_one=axes.get_area(right,x_range=[-3,0],color=RADIO,opacity=.65)
        cut=DashedLine(axes.c2p(0,0),axes.c2p(0,.85),color=RED)
        labels=VGroup(MathTex(r"p(I\mid 0)",font_size=29,color=PLANCK).move_to(axes.c2p(-1,.8)),
                      MathTex(r"p(I\mid 1)",font_size=29,color=RADIO).move_to(axes.c2p(1,.8)))
        ticks=VGroup(*[MathTex(label,font_size=24,color=MUTED).next_to(axes.c2p(x,0),DOWN,buff=.08)
                      for x,label in [(-1,"-1"),(0,"0"),(1,"+1")]])
        self.play(Create(axes),Create(left),Create(right),Write(labels),Write(ticks),Create(cut))
        self.play(Write(self.eq(r"I=a+n_I,\qquad n_I\sim\mathcal N(0,\sigma_I^2),\qquad"
                               r"\sigma_I^2=\frac{1}{2(E_b/N_0)}",-1.15,32)))
        first=self.eq(r"a=+1:\quad\Pr(I<0)=\Pr(n_I<-1)"
                      r"=\int_{-\infty}^{-1}\frac{e^{-u^2/(2\sigma_I^2)}}{\sqrt{2\pi}\sigma_I}\,du",-2.0,32,RADIO)
        second=self.eq(r"a=-1:\quad\Pr(I>0)=\Pr(n_I>1)"
                       r"=\int_{1}^{\infty}\frac{e^{-u^2/(2\sigma_I^2)}}{\sqrt{2\pi}\sigma_I}\,du",-2.85,32,PLANCK)
        # Each noise-tail integral is the matching received-I tail, shifted by a.
        displacement=Arrow(axes.c2p(1,.3),axes.c2p(0,.3),buff=0,color=RADIO)
        shift_label=MathTex(r"n_I<-1",font_size=25,color=RADIO).next_to(displacement,UP,buff=.08)
        self.play(Indicate(labels[1]),
                  GrowArrow(displacement),Write(shift_label))
        self.play(FadeIn(error_one),Write(first),run_time=2)
        self.play(Indicate(first,color=RADIO),Indicate(error_one,color=RADIO))
        self.wait(1.5)
        self.play(FadeOut(displacement),FadeOut(shift_label))
        displacement=Arrow(axes.c2p(-1,.3),axes.c2p(0,.3),buff=0,color=PLANCK)
        shift_label=MathTex(r"n_I>1",font_size=25,color=PLANCK).next_to(displacement,UP,buff=.08)
        self.play(Indicate(labels[0]),GrowArrow(displacement),Write(shift_label))
        self.play(FadeIn(error_zero),Write(second),run_time=2)
        self.play(Indicate(second,color=PLANCK),Indicate(error_zero,color=PLANCK))
        self.wait(1.5)
        self.play(FadeOut(displacement),FadeOut(shift_label))
        self.play(FadeIn(self.txt("By symmetry, either shaded area gives the bit-error probability.",-3.55,24,ACCENT)))
        self.finish()

    def ber_curve(self):
        self.begin("More energy per bit means fewer errors")
        axes=Axes(x_range=[-10,10.5,2],y_range=[-6,0,1],x_length=10.5,y_length=4.1,
                  tips=False,axis_config={"color":MUTED}).move_to(DOWN*.1)
        curve=axes.plot(lambda x: np.log10(bpsk_ber(x)),x_range=[-10,10.5,.04],color=RADIO)
        ticks=VGroup(*[MathTex(rf"10^{{{i}}}",font_size=23).next_to(axes.c2p(-10,i),LEFT,buff=.15) for i in range(-6,1)])
        xticks=VGroup(*[MathTex(str(i),font_size=23).next_to(axes.c2p(i,-6),DOWN,buff=.1) for i in range(-10,11,2)])
        labels=VGroup(Text("BER",font_size=25).next_to(axes,LEFT,buff=.7),
                      MathTex(r"E_b/N_0\ [\mathrm{dB}]",font_size=28).next_to(axes,DOWN,buff=.42))
        self.play(Create(axes),Write(ticks),Write(xticks),Write(labels),Create(curve))
        guessing=DashedLine(axes.c2p(-10,np.log10(.5)),axes.c2p(10.5,np.log10(.5)),
                            color=RED,stroke_width=2)
        guessing_label=MathTex(r"P_b\longrightarrow\frac12:\ \text{random guessing}",font_size=24,color=RED)
        guessing_label.move_to(axes.c2p(5,np.log10(.5))+UP*.3)
        self.play(Create(guessing),Write(guessing_label))
        self.play(Write(self.eq(r"E_b/N_0=-10\ \mathrm{dB}:\quad P_b\approx0.327"
                               r"\quad\text{about one wrong bit in three}",2.55,28,ACCENT)))
        self.play(Write(self.eq(r"E_b/N_0\to0\ (-\infty\,\mathrm{dB}):\ "
                               r"\text{noise hides the signal; guessing two equally likely bits gives half wrong.}",-3.3,23)))
        # Monte Carlo validation is kept off-slide: validate_bpsk.py.
        self.finish()

    def worked_budget(self):
        self.begin("Illustrative X-band downlink")
        b=example_budget()
        # Editable schematic: satellite transmits, ground dish receives.
        front=Rectangle(width=1.0,height=1.25,color=FG,fill_color=RADIO,fill_opacity=.16).move_to([-4.25,1.15,0])
        top=Polygon([-4.75,1.775,0],[-4.35,2.025,0],[-3.35,2.025,0],[-3.75,1.775,0],
                    color=FG,fill_color=RADIO,fill_opacity=.3)
        side=Polygon([-3.75,.525,0],[-3.35,.775,0],[-3.35,2.025,0],[-3.75,1.775,0],
                     color=FG,fill_color=RADIO,fill_opacity=.25)
        patch=Polygon([-3.68,.94,0],[-3.42,1.10,0],[-3.42,1.65,0],[-3.68,1.49,0],
                      color=PLANCK,fill_color=PLANCK,fill_opacity=.8)
        satellite=VGroup(front,top,side,patch)
        dish=ParametricFunction(lambda t:np.array([4.55-.6*t*t,1.25+.75*t,0]),
                                t_range=[-1,1,.02],color=RADIO,stroke_width=5)
        feed=Dot([3.9,1.25,0],radius=.055,color=PLANCK)
        support=VGroup(Line([4.55,1.25,0],[3.9,1.25,0],color=RADIO),
                       Line([4.55,1.25,0],[4.55,.15,0],color=RADIO),
                       Line([4.1,.15,0],[5,.15,0],color=RADIO))
        station=VGroup(dish,feed,support)
        headings=VGroup(Text("CubeSat transmitter",font_size=27,color=PLANCK).move_to([-4.2,2.6,0]),
                        Text("Ground receiver",font_size=27,color=RADIO).move_to([4.35,2.6,0]),
                        MathTex(r"f=8.4\ \mathrm{GHz}",font_size=30,color=ACCENT).move_to([0,2.45,0]))
        self.play(FadeIn(satellite),Create(station),Write(headings))
        patch_label=Text("Patch antenna",font_size=22,color=PLANCK).move_to([-2.25,1.95,0])
        patch_leader=Line(patch_label.get_left()+DOWN*.08,patch.get_center(),color=PLANCK,stroke_width=2)
        self.play(FadeIn(patch_label),Create(patch_leader))
        path=Arrow([-3.25,1.25,0],[3.85,1.25,0],buff=0,color=MUTED,stroke_width=2)
        self.play(GrowArrow(path))
        packet=ParametricFunction(lambda t:np.array([-3.25+t,1.25+.12*np.sin(6*np.pi*t),0]),
                                  t_range=[0,.75,.005],color=ACCENT,stroke_width=4)
        for _ in range(3):
            pulse=packet.copy()
            self.add(pulse)
            self.play(pulse.animate.shift(RIGHT*6.35),run_time=1.5,rate_func=linear)
            self.play(FadeOut(pulse),run_time=.15)
        distance=DoubleArrow([-3.2,.45,0],[3.6,.45,0],buff=0,color=MUTED,stroke_width=2)
        self.play(Create(distance),Write(MathTex(r"R=1000\ \mathrm{km}",font_size=27).move_to([.2,.05,0])))
        diameter=DoubleArrow([4.95,.5,0],[4.95,2,0],buff=0,color=RADIO,stroke_width=2)
        self.play(Create(diameter),Write(MathTex(r"D=1\ \mathrm m",font_size=25,color=RADIO).next_to(diameter,RIGHT,buff=.12)))
        tx=VGroup(MathTex(r"P_t=2\ \mathrm W=3.01\ \mathrm{dBW}",font_size=29,color=PLANCK),
                  MathTex(r"G_t=0\ \mathrm{dBi}\quad L_{\mathrm{feed}}=1\ \mathrm{dB}",font_size=27,color=PLANCK),
                  Text("Assumed gain toward Earth",font_size=20,color=MUTED)).arrange(DOWN,buff=.2).move_to([-4.1,-1.25,0])
        rx=VGroup(MathTex(r"\eta=0.60",font_size=29,color=RADIO),
                  MathTex(rf"G_r={b['rx_gain']:.2f}\ \mathrm{{dBi}}",font_size=29,color=RADIO),
                  Text("Dish aperture efficiency and gain",font_size=20,color=MUTED)).arrange(DOWN,buff=.2).move_to([4.15,-1.25,0])
        propagation=VGroup(MathTex(rf"L_{{\mathrm{{FS}}}}={b['fspl']:.2f}\ \mathrm{{dB}}",font_size=29,color=ACCENT),
                           MathTex(r"L_{\mathrm{other}}=2\ \mathrm{dB}",font_size=29,color=ACCENT),
                           Text("Propagation and pointing",font_size=20,color=MUTED)).arrange(DOWN,buff=.2).move_to([.2,-1.25,0])
        self.play(Create(Line(front.get_bottom(),tx.get_top(),color=PLANCK,stroke_width=2)),FadeIn(tx))
        self.play(Create(Line([4.55,.15,0],rx.get_top(),color=RADIO,stroke_width=2)),FadeIn(rx))
        self.play(Create(Line([.2,-.15,0],propagation.get_top(),color=ACCENT,stroke_width=2)),FadeIn(propagation))
        self.play(Write(self.eq(rf"P_r=3.01+0.00-1.00-{b['fspl']:.2f}+{b['rx_gain']:.2f}-2.00"
                               rf"={b['pr_dbw']:.2f}\ \mathrm{{dBW}}",-2.65,33,RADIO)))
        self.play(FadeIn(self.txt("Illustrative assumptions, not mission measurements. Diagram not to scale.",-3.4,23)))
        self.finish()

    def margin(self):
        self.begin("Does the link meet the error-rate requirement?")
        b=example_budget()
        self.lines([
            self.eq(r"T_{\mathrm{sys}}=150\ \mathrm K,\qquad R_b=10^6\ \mathrm{bit/s},"
                    r"\qquad B=10^6\ \mathrm{Hz}",2.35,33),
            self.eq(rf"N=k_{{\mathrm B}}T_{{\mathrm{{sys}}}}B={b['noise_dbw']:.2f}\ \mathrm{{dBW}},"
                    rf"\qquad E_b/N_0={b['eb_db']:.2f}\ \mathrm{{dB}}",1.25,37,RADIO),
            self.eq(rf"P_b\leq10^{{-5}}\quad\Longrightarrow\quad "
                    rf"(E_b/N_0)_{{\mathrm{{required}}}}={b['required_db']:.2f}\ \mathrm{{dB}}",.05,38),
            self.txt("Allow 1 dB for receiver implementation loss.",-1.05,28),
            self.eq(rf"M={b['eb_db']:.2f}-{b['required_db']:.2f}-1.00"
                    rf"={b['margin_db']:.2f}\ \mathrm{{dB}}",-2.0,48,ACCENT),
            self.txt("2 dB meets the nominal requirement, but leaves a thin reserve. Aim for at least 3 dB here.",-3.0,24),
        ])
        self.finish()
        self.begin("How easily can 2 dB of margin disappear?")
        # Cheung (NASA/JPL, 2015), The Role of Margin in Link Design and Optimization.
        # https://ntrs.nasa.gov/citations/20160009671
        self.lines([
            self.txt("For this X-band example, use 3 dB as a starting design target.",2.5,29,ACCENT),
            self.txt("NASA/JPL cites 3 dB as a common S/X-band rule of thumb, not a guarantee.",1.9,25),
            self.eq(r"T_{\mathrm{sys}}:150\to200\ \mathrm K\quad\Longrightarrow\quad"
                    r"\Delta N=10\log_{10}(200/150)=1.25\ \mathrm{dB}",.85,35,RADIO),
            self.txt("Then suppose pointing is worse than expected: another 1 dB of signal loss.",-.1,26,PLANCK),
        ])
        initial=self.eq(r"M=2.00\ \mathrm{dB}",-1.15,45,ACCENT)
        noise=self.eq(r"M=2.00-1.25=0.75\ \mathrm{dB}",-1.15,45,ACCENT)
        depleted=self.eq(r"M=2.00-1.25-1.00=-0.25\ \mathrm{dB}",-1.15,45,RED)
        self.play(Write(initial))
        self.play(TransformMatchingTex(initial,noise),run_time=1.5)
        self.play(TransformMatchingTex(noise,depleted),run_time=1.5)
        self.play(FadeIn(self.txt("The link now misses the target error rate. These losses are additional to the budget.",-2.05,25,RED)))
        self.play(FadeIn(self.txt("Choose the final margin from uncertainties and required availability, at the worst pass conditions.",-2.75,23)))
        citation=Tex(r"Cheung, NASA/JPL (2015), \emph{The Role of Margin in Link Design and Optimization}\\"
                     r"\texttt{ntrs.nasa.gov/citations/20160009671}",font_size=18,color=MUTED).move_to(DOWN*3.45)
        self.play(FadeIn(citation))
        self.finish()

    def shorthand(self):
        self.begin("Common link-budget shorthand")
        self.lines([
            self.eq(r"\mathrm{EIRP}=P_tG_t/L_t\quad[\mathrm W]",2.2,39),
            self.txt("Equivalent isotropic radiated power includes the transmit feed loss.",1.5,25),
            self.eq(r"G_r/T_{\mathrm{sys}}\quad[\mathrm{K^{-1}}],\qquad "
                    r"(G/T)_{\mathrm{dB/K}}=G_{r,\mathrm{dBi}}-10\log_{10}(T_{\mathrm{sys}}/\mathrm K)",.45,32),
            self.eq(r"C/N_0=\frac{P_r}{k_{\mathrm B}T_{\mathrm{sys}}}\quad[\mathrm{Hz}],"
                    r"\qquad E_b/N_0=\frac{C/N_0}{R_b}",-.85,37),
            self.txt("Here C means received signal power, not transmitted power.",-1.8,27,ACCENT),
            self.txt("These are compact ways to express the same power, noise and bit-rate calculation.",-2.8,24),
        ])
        self.finish()

    def conclusion(self):
        self.begin("Reliable data delivery")
        self.lines([
            self.txt("More received power or lower noise temperature reduces decision errors.",2.25,29,FG),
            self.eq(r"R_b\ \text{doubled at fixed }P_r:\quad E_b/N_0\ \text{drops by }3.01\ \mathrm{dB}",1.15,35,ACCENT),
            self.txt("Occasional bit errors are normal. Error-correcting codes help us cope with them.",.05,27,FG),
            self.txt("Some transmitted bits carry redundancy instead of new data,",-.6,27),
            self.txt("allowing the receiver to detect and correct errors within the code's capability.",-1.15,27),
            self.txt("Use the chosen code's error-rate curve and allow for hardware and propagation losses.",-1.95,24),
            self.eq(r"\text{Data requirement}\ \longrightarrow\ P_r,\ N_0,\ R_b"
                    r"\ \longrightarrow\ E_b/N_0\ \longrightarrow\ \mathrm{BER\ and\ margin}",-2.75,33,RADIO),
        ])
        self.wait(3)
        # Final completed content remains visible. Never clear here.
