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
        self.noise()
        self.bpsk_field()
        self.receiver()
        self.constellation()
        self.noise_error()
        self.bit_stream()
        self.energy_per_bit()
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
            self.eq(r"\frac{600\ \mathrm{Mbit}}{600\ \mathrm s}=1\ \mathrm{Mbit\,s^{-1}}", -.25, 48, RADIO),
            self.txt("Then allow for framing, coding, retransmissions and missed contacts.", -1.45, 27),
            self.txt("The budget connects received power to reliable bit decisions.", -2.5, 30, ACCENT),
        ])
        self.finish()

    def power_budget(self):
        self.begin("Received power: gains and losses")
        self.lines([
            self.eq(r"P_r=P_tG_tG_r\left(\frac{\lambda}{4\pi R}\right)^2\frac{1}{L}", 2.0, 46),
            self.eq(r"P_{r,\mathrm{dBW}}=P_{t,\mathrm{dBW}}+G_{t,\mathrm{dBi}}+G_{r,\mathrm{dBi}}"
                    r"-L_{\mathrm{FS,dB}}-L_{\mathrm{other,dB}}", .65, 36, RADIO),
            self.eq(r"L_{\mathrm{FS,dB}}=20\log_{10}\!\left(\frac{4\pi R}{\lambda}\right)", -.55, 40),
            self.txt("Other losses: feed cables, pointing, polarization and atmosphere.", -1.6, 26),
            self.eq(r"P_t,P_r\ [\mathrm W],\quad R,\lambda\ [\mathrm m],\quad G_t,G_r,L\ [1]", -2.4, 29),
            self.txt("dBW references 1 W. dBi references an isotropic antenna. Losses are positive.", -3.05, 23),
        ])
        self.finish()

    def noise(self):
        self.begin("The receiver also collects noise")
        self.lines([
            self.eq(r"N=k_{\mathrm B}T_{\mathrm{sys}}B", 2.0, 58, RADIO),
            self.eq(r"\mathrm{SNR}=\frac{P_r}{N}=\frac{P_r}{k_{\mathrm B}T_{\mathrm{sys}}B}", .55, 50),
            self.eq(r"N_0=k_{\mathrm B}T_{\mathrm{sys}}\quad[\mathrm{W/Hz}]", -.8, 43, ACCENT),
            self.eq(r"T_{\mathrm{sys}}:\ \text{system noise temperature}\ [\mathrm K],\quad "
                    r"B:\ \text{noise bandwidth}\ [\mathrm{Hz}]", -2.0, 28),
            self.txt("Refer signal power and system noise temperature to the same receiver point.", -2.8, 25),
        ])
        self.finish()

    def bpsk_field(self):
        self.begin("Binary phase-shift keying (BPSK)")
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
            self.eq(r"v(t)\propto E(t),\qquad u(t)=I(t)+jQ(t)", .65, 42),
            self.txt("Mix with cosine and sine at the carrier frequency, then low-pass filter.", -.2, 25),
            self.eq(r"z_k=a_k+w_k,\quad a_k\in\{-1,+1\},\qquad "
                    r"\widehat b_k=\begin{cases}1,&\Re z_k\geq0\\0,&\Re z_k<0\end{cases}", -1.35, 37),
            self.txt("After phase recovery, timing recovery, matched filtering and normalization.", -2.45, 24),
            self.txt("The ADC may sample much faster. The final decision is once per symbol.", -3.05, 24),
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
        self.play(FadeIn(self.txt("I = −0.35: receiver decides 0, but we sent 1", -2.4, 30, RED)))
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
        self.begin("Energy per bit connects the budget to BER")
        self.lines([
            self.eq(r"E_b=\frac{P_r}{R_b}\ [\mathrm J],\qquad N_0=k_{\mathrm B}T_{\mathrm{sys}}\ [\mathrm{W/Hz}]",2.05,39),
            self.eq(r"\frac{E_b}{N_0}=\frac{P_r}{k_{\mathrm B}T_{\mathrm{sys}}R_b}"
                    r"=\mathrm{SNR}\,\frac{B}{R_b}",.65,49,RADIO),
            self.eq(r"\left(\frac{E_b}{N_0}\right)_{\mathrm{dB}}"
                    r"=\mathrm{SNR}_{\mathrm{dB}}+10\log_{10}\!\left(\frac{B}{R_b}\right)",-.75,37),
            self.txt("At fixed received power, a slower bit rate gives more energy to each bit.",-1.85,27),
            self.eq(r"B:\ \text{noise bandwidth [Hz]},\qquad R_b:\ \text{bit rate [bit/s]}",-2.65,30,ACCENT),
        ])
        self.finish()

    def gaussian_tail(self):
        self.begin("BER is the probability of crossing zero")
        axes=Axes(x_range=[-3,3,1],y_range=[0,1,.5],x_length=10.7,y_length=2.55,
                  tips=False,axis_config={"color":MUTED}).move_to(UP*.75)
        sigma=.65
        pdf=lambda x,mu: np.exp(-.5*((x-mu)/sigma)**2)/(sigma*np.sqrt(2*np.pi))
        left=axes.plot(lambda x:pdf(x,-1),color=PLANCK)
        right=axes.plot(lambda x:pdf(x,1),color=RADIO)
        tails=VGroup(axes.get_area(left,x_range=[0,3],color=RED,opacity=.65),
                     axes.get_area(right,x_range=[-3,0],color=RED,opacity=.65))
        cut=DashedLine(axes.c2p(0,0),axes.c2p(0,.85),color=RED)
        labels=VGroup(MathTex(r"p(I\mid 0)",font_size=29,color=PLANCK).move_to(axes.c2p(-1,.8)),
                      MathTex(r"p(I\mid 1)",font_size=29,color=RADIO).move_to(axes.c2p(1,.8)))
        ticks=VGroup(*[MathTex(label,font_size=24,color=MUTED).next_to(axes.c2p(x,0),DOWN,buff=.08)
                      for x,label in [(-1,"-1"),(0,"0"),(1,"+1")]])
        self.play(Create(axes),Create(left),Create(right),Write(labels),Write(ticks),Create(cut))
        self.play(FadeIn(tails))
        self.lines([
            self.eq(r"I=a+n_I,\quad n_I\sim\mathcal N(0,\sigma^2),\quad "
                    r"\sigma^2=\frac{1}{2E_b/N_0}",-1.15,34),
            self.eq(r"P_b=P(I<0\mid a=+1)=Q(1/\sigma)"
                    r"=Q\!\left(\sqrt{2E_b/N_0}\right)",-2.15,38,ACCENT),
            self.eq(r"Q(x)=\frac{1}{\sqrt{2\pi}}\int_x^\infty e^{-t^2/2}\,dt",-3.1,30),
        ])
        self.finish()

    def ber_curve(self):
        self.begin("More energy per bit means fewer errors")
        axes=Axes(x_range=[0,11,2],y_range=[-6,0,1],x_length=8.4,y_length=4.1,
                  tips=False,axis_config={"color":MUTED}).move_to(LEFT*.9+DOWN*.1)
        curve=axes.plot(lambda x: np.log10(bpsk_ber(x)),x_range=[0,10.5,.04],color=RADIO)
        ticks=VGroup(*[MathTex(rf"10^{{{i}}}",font_size=23).next_to(axes.c2p(0,i),LEFT,buff=.15) for i in range(-6,1)])
        xticks=VGroup(*[MathTex(str(i),font_size=23).next_to(axes.c2p(i,-6),DOWN,buff=.1) for i in range(0,11,2)])
        labels=VGroup(Text("BER",font_size=25).next_to(axes,LEFT,buff=.7),
                      MathTex(r"E_b/N_0\ [\mathrm{dB}]",font_size=28).next_to(axes,DOWN,buff=.42))
        self.play(Create(axes),Write(ticks),Write(xticks),Write(labels),Create(curve))
        rows=[]
        dots=VGroup()
        for db in [0,2,4,6,8]:
            bits,_,_,decoded=simulate_bpsk(db)
            count=int(np.sum(bits!=decoded)); estimate=count/len(bits)
            rows.append((db,count,len(bits),estimate,float(bpsk_ber(db))))
            dots.add(Dot(axes.c2p(db,np.log10(estimate)),radius=.065,color=ACCENT))
        self.play(LaggedStart(*[FadeIn(d) for d in dots],lag_ratio=.3))
        legend=VGroup(Text("Theory",font_size=25,color=RADIO),
                      Text("Simulation",font_size=25,color=ACCENT),
                      Text("400,000 bits\nper point",font_size=23,color=MUTED)).arrange(DOWN,buff=.35).move_to(RIGHT*4.95)
        self.play(FadeIn(legend))
        self.play(FadeIn(self.txt("Uncoded coherent BPSK in AWGN, with perfect phase and timing recovery.",-3.3,24)))
        output=Path("media/link_budget");output.mkdir(parents=True,exist_ok=True)
        with h5py.File(output/"ber_validation.h5","w") as h:
            h.create_dataset("ebn0_db",data=[r[0] for r in rows])
            h.create_dataset("errors",data=[r[1] for r in rows])
            h.create_dataset("bit_count",data=[r[2] for r in rows])
            h.create_dataset("measured_ber",data=[r[3] for r in rows])
            h.create_dataset("theoretical_ber",data=[r[4] for r in rows])
            h.attrs["seed"]=20260924
        self.finish()

    def worked_budget(self):
        self.begin("Illustrative X-band downlink")
        b=example_budget()
        self.lines([
            self.txt("8.4 GHz, 1000 km slant range, 2 W transmitter",2.45,29,FG),
            self.txt("0 dBi transmit antenna; 1 m receive dish with 60% aperture efficiency",1.9,25),
        ])
        rows=[
            ("Transmit power",f"+{b['tx_dbw']:.2f} dBW"),
            ("Transmit gain / feed loss","+0.00 / −1.00 dB"),
            ("Free-space path loss",f"−{b['fspl']:.2f} dB"),
            ("Receive antenna gain",f"+{b['rx_gain']:.2f} dBi"),
            ("Other propagation / pointing losses","−2.00 dB"),
            ("Received signal power",f"{b['pr_dbw']:.2f} dBW"),
        ]
        table=VGroup(*[VGroup(Text(label,font_size=26,color=FG).move_to(LEFT*2.2),
                              Text(value,font_size=26,color=RADIO).move_to(RIGHT*3.3))
                       for label,value in rows]).arrange(DOWN,buff=.3).move_to(DOWN*.25)
        self.play(LaggedStart(*[FadeIn(row) for row in table],lag_ratio=.3),run_time=4)
        self.play(FadeIn(self.txt("Assumed design values, not measurements of a specific mission.",-3.1,24)))
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
            self.txt("Positive margin meets this assumed requirement. Check the worst point in the pass.",-3.0,24),
        ])
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
            self.txt("Coding adds redundancy and changes the energy and rate requirements.",0,27),
            self.txt("Use the actual modulation and code performance curve for the target BER.",-.7,26),
            self.txt("Include hardware losses and worst-case range, pointing and weather.",-1.65,27),
            self.eq(r"\text{Data requirement}\ \longrightarrow\ P_r,\ N_0,\ R_b"
                    r"\ \longrightarrow\ E_b/N_0\ \longrightarrow\ \mathrm{BER\ and\ margin}",-2.75,33,RADIO),
        ])
        self.wait(3)
        # Final completed content remains visible. Never clear here.
