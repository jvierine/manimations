"""Manim presentation: Planck radiation to the radio noise formula P = k_B T B.

Render a quick preview:
    conda run -n base manim -pql planck_to_ktb.py PlanckToKTB

Render the final 1080p video:
    conda run -n base manim -pqh planck_to_ktb.py PlanckToKTB

Set SHOW_PROVENANCE=1 to show a small source-script footer.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from manim import *
from manim_slides import Slide


BG = "#07111F"
FG = "#F3F7FA"
MUTED = "#9DB0C3"
PLANCK = "#F5A65B"
RJ = "#45C2B1"
RADIO = "#74A9FF"
ACCENT = "#F3D35A"
RED = "#FF6B6B"

SHOW_PROVENANCE = os.getenv("SHOW_PROVENANCE", "0") == "1"
HASLAM_MAP = Path(__file__).resolve().parent / "assets" / "haslam_408mhz.png"


class PlanckToKTB(Slide):
    """An animated derivation for a 16:9 screen."""

    def setup(self):
        self._slide_started = False
        self._pending_clear_keep = None
        self.camera.background_color = ManimColor(BG)
        self.provenance = Text(
            "Source: planck_to_ktb.py",
            font_size=15,
            color=MUTED,
        ).to_corner(DR, buff=0.18)
        if SHOW_PROVENANCE:
            self.add(self.provenance)

    def start_slide(self, name: str):
        if self._slide_started:
            self.next_slide(name)
            self._flush_pending_clear()
        else:
            self.next_section(name)
            self._slide_started = True

    def title(self, text: str) -> Text:
        title = Text(text, font_size=44, weight=SEMIBOLD, color=FG)
        if title.width > 13.1:
            title.scale_to_fit_width(13.1)
        return title.to_edge(UP, buff=0.32)

    def footer_note(self, text: str) -> Text:
        note = Text(text, font_size=22, color=MUTED)
        note.to_edge(DOWN, buff=0.32)
        if SHOW_PROVENANCE:
            note.shift(LEFT * 0.75)
        return note

    def clear_slide(self, *keep: Mobject):
        self._pending_clear_keep = keep

    def _flush_pending_clear(self):
        if self._pending_clear_keep is None:
            return
        keep = self._pending_clear_keep
        self._pending_clear_keep = None
        protected = set(keep)
        if SHOW_PROVENANCE:
            protected.add(self.provenance)
        removable = [mob for mob in self.mobjects if mob not in protected]
        if removable:
            self.play(*[FadeOut(mob, shift=0.08 * DOWN) for mob in removable], run_time=0.70)

    def construct(self):
        self.opening()
        self.planck_spectrum()
        self.planck_and_rj_plot()
        self.rayleigh_jeans_limit()
        self.single_mode_bridge()
        self.bandwidth_integration()
        self.validity_and_close()

    def opening(self):
        self.start_slide("Haslam radio sky")

        title = self.title("The radio sky at 408 MHz")
        sky_map = ImageMobject(str(HASLAM_MAP))
        sky_map.scale_to_fit_width(12.55).shift(DOWN * 0.18)
        question = Text(
            "Why do radio engineers use temperature to describe power?",
            font_size=35,
            weight=SEMIBOLD,
            color=FG,
            t2c={"temperature": ACCENT, "power": RADIO},
        ).to_edge(DOWN, buff=0.24)
        question_background = BackgroundRectangle(
            question,
            color=BG,
            fill_opacity=0.92,
            buff=0.18,
        )

        self.play(FadeIn(title))
        self.play(FadeIn(sky_map), run_time=1.6)
        self.play(FadeIn(question_background), FadeIn(question, shift=0.12 * UP))
        self.wait(2.5)
        self.clear_slide()

    def planck_spectrum(self):
        self.start_slide("Planck spectrum")

        title = self.title("Planck spectral radiance")
        formula = MathTex(
            r"B_\nu(T)=",
            r"\frac{2h\nu^3}{c^2}",
            r"\frac{1}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=44,
        ).next_to(title, DOWN, buff=0.34)
        formula[1].set_color(PLANCK)
        formula[2].set_color(PLANCK)

        quantity = MathTex(
            r"B_\nu=\frac{dP}{dA_\perp\,d\Omega\,d\nu}",
            font_size=34,
            color=FG,
        ).next_to(formula, DOWN, buff=0.34)
        units = MathTex(
            r"[B_\nu]=\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}",
            font_size=30,
            color=ACCENT,
        ).next_to(quantity, DOWN, buff=0.18)

        left_definitions = MathTex(
            r"\begin{aligned}"
            r"\nu&:\ \text{frequency}\\"
            r"T&:\ \text{thermodynamic temperature}\\"
            r"h&:\ \text{Planck constant}"
            r"\end{aligned}",
            font_size=27,
            color=FG,
        )
        right_definitions = MathTex(
            r"\begin{aligned}"
            r"k_{\mathrm B}&:\ \text{Boltzmann constant}\\"
            r"c&:\ \text{speed of light}\\"
            r"B_\nu&:\ \text{both polarizations}"
            r"\end{aligned}",
            font_size=27,
            color=FG,
        )
        notes = VGroup(left_definitions, right_definitions).arrange(
            RIGHT, aligned_edge=UP, buff=0.95
        ).next_to(units, DOWN, buff=0.28)

        content = VGroup(formula, quantity, units, notes)
        if content.width > 12.4:
            content.scale_to_fit_width(12.4)
        if content.height > 6.25:
            content.scale_to_fit_height(6.25)
        content.next_to(title, DOWN, buff=0.30)

        self.play(FadeIn(title), Write(formula))
        self.play(Write(quantity), Write(units))
        self.play(LaggedStart(*[FadeIn(note, shift=0.12 * RIGHT) for note in notes], lag_ratio=0.16))
        self.wait(2.0)
        self.clear_slide()

    def planck_and_rj_plot(self):
        self.start_slide("Planck and Rayleigh-Jeans plot")

        h = 6.62607015e-34
        k_b = 1.380649e-23
        c = 299792458.0
        temperature = 300.0
        radiance_scale = 1e-12
        mode_scale = 1e-21
        rj_level = k_b * temperature / mode_scale

        title = self.title("Planck and Rayleigh-Jeans spectral radiance at 300 K")
        relation = MathTex(
            r"B_\nu^{\rm P}=\frac{2h\nu^3/c^2}{e^{h\nu/(k_{\mathrm B}T)}-1},"
            r"\qquad B_\nu^{\rm RJ}=\frac{2k_{\mathrm B}T\nu^2}{c^2}",
            font_size=34,
            color=FG,
        ).next_to(title, DOWN, buff=0.22)

        def planck_radiance_thz(f_thz):
            if f_thz < 1e-9:
                return 0.0
            frequency = f_thz * 1e12
            x = h * frequency / (k_b * temperature)
            value = 2 * h * frequency**3 / c**2 / np.expm1(x)
            return value / radiance_scale

        def rj_radiance_thz(f_thz):
            frequency = f_thz * 1e12
            return 2 * k_b * temperature * frequency**2 / c**2 / radiance_scale

        axes = Axes(
            x_range=[0, 150, 30],
            y_range=[0, 6, 1],
            x_length=10.3,
            y_length=4.15,
            axis_config={
                "color": MUTED,
                "stroke_width": 2,
                "include_numbers": True,
                "font_size": 22,
            },
            tips=False,
        ).shift(DOWN * 0.72)
        x_label = Text("frequency [THz]", font_size=25, color=FG).next_to(
            axes.x_axis, DOWN, buff=0.36
        )
        y_label = MathTex(
            r"B_\nu\ [10^{-12}\,\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}]",
            font_size=25,
            color=FG,
        ).rotate(PI / 2).next_to(axes.y_axis, LEFT, buff=0.26)
        planck_curve = axes.plot(
            planck_radiance_thz,
            x_range=[0, 150],
            color=PLANCK,
            stroke_width=5,
        )
        rj_curve = axes.plot(
            rj_radiance_thz,
            x_range=[0, 8.05],
            color=RJ,
            stroke_width=4,
        )
        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=PLANCK, stroke_width=5), Text("Planck", font_size=23, color=PLANCK)),
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=RJ, stroke_width=4), Text("Rayleigh-Jeans", font_size=23, color=RJ)),
        )
        for entry in legend:
            entry.arrange(RIGHT, buff=0.16)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(axes.c2p(112, 4.6))

        low_region = Rectangle(
            width=axes.c2p(12, 0)[0] - axes.c2p(0, 0)[0],
            height=axes.y_length,
            color=RADIO,
            fill_color=RADIO,
            fill_opacity=0.10,
            stroke_width=2,
        ).move_to((axes.c2p(0, 0) + axes.c2p(12, 6)) / 2)
        low_text = Text("low-frequency region", font_size=24, color=RADIO).next_to(
            low_region, RIGHT, buff=0.18
        ).shift(DOWN * 1.3)
        tail_marker = DashedLine(
            axes.c2p(142.84, 0),
            axes.c2p(142.84, 0.85),
            color=ACCENT,
            stroke_width=2,
        )
        tail_label = MathTex(
            r"\frac{B_\nu}{B_{\nu,\max}}<10^{-6}"
            r"\quad\text{at}\quad\nu>142.8\,\mathrm{THz}",
            font_size=27,
            color=ACCENT,
        ).move_to(axes.c2p(105, 0.72))

        self.play(FadeIn(title), Write(relation))
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(Create(planck_curve), Create(rj_curve), FadeIn(legend), run_time=1.7)
        self.play(
            FadeIn(low_region),
            FadeIn(low_text),
            Create(tail_marker),
            FadeIn(tail_label),
        )
        self.wait(1.2)

        # Hold the complete radiance plot and its yellow annotation until the
        # presenter advances. The transformation belongs to the next segment.
        self.start_slide("Spectral radiance to single-mode power")
        mode_title = self.title("Power spectral density of one received mode")
        mode_relation = MathTex(
            r"S_\nu\equiv\frac{\lambda^2}{2}B_\nu"
            r"=\frac{h\nu}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=39,
            color=FG,
        ).next_to(mode_title, DOWN, buff=0.22)

        def planck_mode_log_hz(log_frequency):
            frequency = 10**log_frequency
            x = h * frequency / (k_b * temperature)
            return h * frequency / np.expm1(x) / mode_scale

        mode_axes = Axes(
            x_range=[8, 14, 1],
            y_range=[0, 5, 1],
            x_length=10.3,
            y_length=4.15,
            axis_config={
                "color": MUTED,
                "stroke_width": 2,
                "include_numbers": True,
                "font_size": 22,
            },
            tips=False,
        ).move_to(axes)
        mode_x_label = MathTex(
            r"\log_{10}(\nu/\mathrm{Hz})", font_size=29, color=FG
        ).next_to(
            mode_axes.x_axis, DOWN, buff=0.36
        )
        mode_y_label = MathTex(
            r"S_\nu\ [10^{-21}\,\mathrm{W\,Hz^{-1}}]",
            font_size=28,
            color=FG,
        ).rotate(PI / 2).next_to(mode_axes.y_axis, LEFT, buff=0.32)
        mode_planck = mode_axes.plot(
            planck_mode_log_hz,
            x_range=[8, 14],
            color=PLANCK,
            stroke_width=5,
        )
        mode_rj = mode_axes.plot(
            lambda _: rj_level,
            x_range=[8, 14],
            color=RJ,
            stroke_width=4,
            use_smoothing=False,
        )
        mode_legend = legend.copy().move_to(mode_axes.c2p(12.7, 3.25))

        self.play(
            FadeOut(low_region),
            FadeOut(low_text),
            FadeOut(tail_marker),
            FadeOut(tail_label),
            Transform(title, mode_title),
            Transform(relation, mode_relation),
            Transform(axes, mode_axes),
            Transform(x_label, mode_x_label),
            Transform(y_label, mode_y_label),
            Transform(planck_curve, mode_planck),
            Transform(rj_curve, mode_rj),
            Transform(legend, mode_legend),
            run_time=1.8,
        )

        radio_region = Rectangle(
            width=mode_axes.c2p(10.5, 0)[0] - mode_axes.c2p(8, 0)[0],
            height=mode_axes.y_length,
            color=RADIO,
            fill_color=RADIO,
            fill_opacity=0.10,
            stroke_width=2,
        ).move_to((mode_axes.c2p(8, 0) + mode_axes.c2p(10.5, 5)) / 2)
        zoom_text = Text("zoom to radio frequencies", font_size=24, color=RADIO).next_to(
            radio_region, RIGHT, buff=0.18
        ).shift(DOWN * 1.3)
        self.play(FadeIn(radio_region), FadeIn(zoom_text))
        self.wait(1.2)

        zoom_axes = Axes(
            x_range=[6, 11, 1],
            y_range=[0, 4.5, 1],
            x_length=10.3,
            y_length=4.15,
            axis_config={
                "color": MUTED,
                "stroke_width": 2,
                "include_numbers": True,
                "font_size": 22,
            },
            tips=False,
        ).move_to(mode_axes)
        zoom_x_label = MathTex(
            r"\log_{10}(\nu/\mathrm{Hz})", font_size=29, color=FG
        ).next_to(
            zoom_axes.x_axis, DOWN, buff=0.36
        )
        zoom_y_label = mode_y_label.copy().next_to(zoom_axes.y_axis, LEFT, buff=0.32)
        zoom_planck = zoom_axes.plot(
            planck_mode_log_hz,
            x_range=[6, 11],
            color=PLANCK,
            stroke_width=5,
        )
        zoom_rj_solid = zoom_axes.plot(
            lambda _: rj_level,
            x_range=[6, 11],
            color=RJ,
            stroke_width=4,
            use_smoothing=False,
        )
        zoom_rj = DashedVMobject(
            zoom_rj_solid,
            num_dashes=34,
            dashed_ratio=0.55,
        )
        zoom_legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.6, color=PLANCK, stroke_width=5), Text("Planck", font_size=23, color=PLANCK)),
            VGroup(
                DashedVMobject(Line(ORIGIN, RIGHT * 0.6, color=RJ, stroke_width=4), num_dashes=5),
                Text("Rayleigh-Jeans", font_size=23, color=RJ),
            ),
        )
        for entry in zoom_legend:
            entry.arrange(RIGHT, buff=0.16)
        zoom_legend.arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to(zoom_axes.c2p(9.6, 2.9))
        radio_title = self.title("Radio limit on a logarithmic frequency axis")
        flat_label = MathTex(
            r"S_\nu^{\rm P}\approx S_\nu^{\rm RJ}\approx k_{\mathrm B}\,T"
            r"=4.14\times10^{-21}\,\mathrm{W\,Hz^{-1}}",
            font_size=32,
            color=ACCENT,
        ).move_to(zoom_axes.c2p(8.7, 1.35))

        self.play(
            FadeOut(radio_region),
            FadeOut(zoom_text),
            Transform(title, radio_title),
            Transform(legend, zoom_legend),
            Transform(axes, zoom_axes),
            Transform(x_label, zoom_x_label),
            Transform(y_label, zoom_y_label),
            Transform(planck_curve, zoom_planck),
            Transform(rj_curve, zoom_rj),
            run_time=1.8,
        )
        self.play(FadeIn(flat_label, shift=0.15 * UP), run_time=1.0)
        self.wait(2.0)
        self.clear_slide()

    def rayleigh_jeans_limit(self):
        self.start_slide("Rayleigh-Jeans limit")

        title = self.title("The low-frequency limit")
        condition = MathTex(r"x\equiv\frac{h\nu}{k_{\mathrm B}T}\ll 1", font_size=48, color=RJ)
        expansion = MathTex(r"e^x-1=x+\mathcal O(x^2)\approx x", font_size=45, color=FG)
        condition.next_to(title, DOWN, buff=0.48)
        expansion.next_to(condition, DOWN, buff=0.38)

        planck_eq = MathTex(
            r"B_\nu(T)=\frac{2h\nu^3}{c^2}\frac{1}{e^x-1}",
            font_size=48,
            color=PLANCK,
        ).shift(DOWN * 0.65)
        approx_eq = MathTex(
            r"B_\nu(T)\approx\frac{2h\nu^3}{c^2}\frac{1}{x}",
            font_size=48,
            color=FG,
        ).move_to(planck_eq)
        substituted = MathTex(
            r"B_\nu(T)\approx\frac{2h\nu^3}{c^2}\frac{k_{\mathrm B}T}{h\nu}",
            font_size=48,
            color=FG,
        ).move_to(planck_eq)
        rj_box = SurroundingRectangle(
            MathTex(r"B_\nu(T)=\frac{2k_{\mathrm B}T\nu^2}{c^2}", font_size=58, color=RJ),
            buff=0.28,
            color=RJ,
            corner_radius=0.12,
        )
        rj_eq = rj_box.get_center()
        rj_formula = MathTex(
            r"B_\nu(T)=\frac{2k_{\mathrm B}T\nu^2}{c^2}",
            font_size=58,
            color=RJ,
        ).move_to(rj_eq)
        result = VGroup(rj_box, rj_formula).shift(DOWN * 2.25)

        interpretation = VGroup(
            Text("Each thermally occupied mode carries mean energy", font_size=22, color=MUTED),
            MathTex(r"k_{\mathrm B}\,T", font_size=30, color=RJ),
        ).arrange(RIGHT, buff=0.16).to_edge(DOWN, buff=0.30)

        self.play(FadeIn(title), Write(condition))
        self.play(Write(expansion))
        self.play(Write(planck_eq))
        self.play(TransformMatchingTex(planck_eq, approx_eq))
        self.play(TransformMatchingTex(approx_eq, substituted))
        self.play(TransformFromCopy(substituted, rj_formula), Create(rj_box))
        self.play(FadeIn(interpretation))
        self.wait(2.0)
        self.clear_slide()

    def single_mode_bridge(self):
        """Radiance to one matched, lossless, reciprocal receiver mode.

        B_nu includes both polarizations; A_e is the peak co-polar effective
        aperture. The beam integral is over the full sphere, not just its FWHM.
        The exact antenna theorem applies to the ideal lossless case used here.
        """
        def equation(tex, y, color=FG, size=40):
            mob = MathTex(tex, font_size=size, color=color)
            if mob.width > 12.3:
                mob.scale_to_fit_width(12.3)
            return mob.move_to(UP * y)

        def caption(text, y, color=MUTED, size=26):
            mob = Text(text, font_size=size, color=color)
            if mob.width > 12.3:
                mob.scale_to_fit_width(12.3)
            return mob.move_to(UP * y)

        def finish():
            self.wait(2.5)
            self.clear_slide()

        self.start_slide("Radiance is not yet received power")
        self.play(FadeIn(self.title("Radiance is not yet received power")))
        radiance = equation(
            r"B_\nu(T)\quad[\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}]", 2.35, RJ)
        self.play(Write(radiance))
        sky = Ellipse(width=1.0, height=2.0, color=PLANCK).move_to(LEFT * 4.4 + UP * .55)
        aperture = Ellipse(width=.65, height=2.2, color=RADIO,
                           fill_color=RADIO, fill_opacity=.3).move_to(RIGHT * 3.4 + UP * .55)
        rays = VGroup(*[
            Arrow(LEFT * 3.8 + UP * (.55 + dy),
                  RIGHT * 3.0 + UP * (.55 + dy * .35),
                  color=PLANCK, stroke_width=3, buff=.1)
            for dy in (-.65, 0, .65)
        ])
        labels = VGroup(
            MathTex(r"d\Omega\ [\mathrm{sr}]", font_size=30, color=PLANCK).next_to(sky, DOWN),
            MathTex(r"A_{\mathrm e}(\theta,\phi)\ [\mathrm{m^2}]",
                    font_size=30, color=RADIO).next_to(aperture, DOWN),
        )
        self.play(Create(sky), Create(aperture), LaggedStart(*[GrowArrow(r) for r in rays]), Write(labels))
        self.play(FadeIn(caption("Collect from an angular patch, through an effective area,", -1.35)))
        self.play(FadeIn(caption("within a small frequency interval.", -1.85)))
        self.play(Write(equation(
            r"d\nu:\ \text{frequency interval}\ [\mathrm{Hz}],\qquad"
            r"\theta,\phi:\ \text{sky angles}\ [\mathrm{rad}]", -2.6, size=29)))
        finish()

        self.start_slide("One polarization and the receiving beam")
        self.play(FadeIn(self.title("One polarization; a weighted view of the sky")))
        self.play(FadeIn(caption("Unpolarized thermal radiance contains two equal polarizations.", 2.4)))
        self.play(Write(equation(
            r"B_{\nu,\mathrm{one\ pol}}=\frac{B_\nu}{2}", 1.55, RED, 46)))
        self.play(FadeIn(caption("A single-polarization receiver collects only one of them.", .75)))
        self.play(Write(equation(
            r"dP=\frac12\left[\int_{4\pi}B_\nu(\theta,\phi)\,"
            r"A_{\mathrm e}(\theta,\phi)\,d\Omega\right]d\nu", -.25, size=39)))
        self.play(Write(equation(
            r"A_{\mathrm e}(\theta,\phi)=A_{\mathrm e}\,p(\theta,\phi),"
            r"\qquad \max p=1", -1.5, RADIO, 36)))
        self.play(FadeIn(caption("Effective area includes directional response; it is not just dish area.", -2.35, size=24)))
        self.play(Write(equation(
            r"dP:\ \text{available received power}\ [\mathrm W],\quad "
            r"p:\ \text{normalized power pattern}\ [1]", -3.05, size=27)))
        finish()

        self.start_slide("Area times beam solid angle")
        self.play(FadeIn(self.title("Uniform sky: area × beam solid angle")))
        self.play(FadeIn(caption("If the temperature is uniform over the receiving pattern,", 2.35)))
        self.play(FadeIn(caption("the radiance comes outside the angular integral.", 1.9)))
        self.play(Write(equation(
            r"\Omega_A\equiv\int_{4\pi}p(\theta,\phi)\,d\Omega"
            r"\quad[\mathrm{sr}]", .95, ACCENT, 44)))
        self.play(Write(equation(
            r"dP=\frac12 B_\nu(T)\,"
            r"\underbrace{A_{\mathrm e}\Omega_A}_{\text{area times angular acceptance}}"
            r"\,d\nu", -.5, size=44)))
        self.play(Write(equation(
            r"\frac{\mathrm W}{\mathrm{m^2\,sr\,Hz}}"
            r"\ \times\ \mathrm{m^2\,sr}\ \times\ \mathrm{Hz}"
            r"\ =\ \mathrm W", -2.05, RADIO, 34)))
        self.play(FadeIn(caption("The beam solid angle integrates the whole pattern, including sidelobes.", -2.9, size=24)))
        finish()

        self.start_slide("Why one spatial mode has lambda squared throughput")
        self.play(FadeIn(self.title("Bigger aperture, narrower view of the sky")))
        # A side view of the angular acceptance, not a literal dish shape.
        diagrams = VGroup()
        for x, height, spread, label in [
            (-3.2, .8, 1.1, "small aperture · wide beam"),
            (3.2, 1.6, .42, "large aperture · narrow beam"),
        ]:
            origin = np.array([x + 1.35, 1.0, 0])
            collector = Line(origin + UP * height / 2, origin - UP * height / 2,
                             color=RADIO, stroke_width=8)
            cone = Polygon(origin, origin + LEFT * 2.7 + UP * spread,
                           origin + LEFT * 2.7 - UP * spread,
                           color=PLANCK, fill_color=PLANCK, fill_opacity=.15)
            text = Text(label, font_size=24, color=FG).move_to([x, -.5, 0])
            diagrams.add(VGroup(cone, collector, text))
        self.play(FadeIn(diagrams))
        self.play(Write(equation(
            r"A_{\mathrm e}\propto D^2,\qquad"
            r"\Omega_A\propto\left(\frac{\lambda}{D}\right)^2",
            -1.4, ACCENT, 43)))
        self.play(FadeIn(caption("One receiver port combines the aperture field into one spatial mode.", -2.35, size=25)))
        self.play(Write(equation(
            r"D:\ \text{aperture size}\ [\mathrm m],\qquad"
            r"\lambda=\frac c\nu:\ \text{wavelength}\ [\mathrm m]", -3.0, size=28)))
        finish()

        self.start_slide("Exact single mode antenna theorem")
        self.play(FadeIn(self.title("The exact area–solid-angle relation")))
        self.play(FadeIn(caption("For a lossless, reciprocal antenna with a matched receiver:", 2.4, size=27)))
        self.play(Write(equation(
            r"G_{\max}=\frac{4\pi}{\Omega_A},\qquad "
            r"A_{\mathrm e}=\frac{\lambda^2}{4\pi}G_{\max}", 1.3, size=46)))
        self.play(FadeIn(caption("Gain concentrates power; reciprocity gives the same collecting response.", .3, size=24)))
        theorem = equation(
            r"A_{\mathrm e}\Omega_A"
            r"=\frac{\lambda^2G_{\max}}{4\pi}\,\frac{4\pi}{G_{\max}}"
            r"=\lambda^2", -.7, ACCENT, 46)
        self.play(Write(theorem))
        self.play(FadeIn(caption("Area and angular acceptance are not independent for one spatial mode.", -1.8, size=25)))
        self.play(Write(equation(
            r"G_{\max}:\ \text{peak gain}\ [1]\quad"
            r"(\text{equals directivity for a lossless antenna})", -2.55, size=27)))
        self.play(FadeIn(caption("This is a product, not Ω alone; steradians are dimensionless in SI.", -3.15, size=23)))
        finish()

        self.start_slide("Radiance becomes kBT per hertz")
        self.play(FadeIn(self.title("Now the factors cancel")))
        self.play(Write(equation(
            r"dP=\frac12\,B_\nu(T)\,(A_{\mathrm e}\Omega_A)\,d\nu",
            2.15, size=46)))
        self.play(Write(equation(
            r"B_\nu(T)\simeq\frac{2k_{\mathrm B}T}{\lambda^2}"
            r"\quad(h\nu\ll k_{\mathrm B}T),\qquad "
            r"A_{\mathrm e}\Omega_A=\lambda^2", .95, RJ, 39)))
        self.play(Write(equation(
            r"dP=\underbrace{\frac12}_{\text{one polarization}}"
            r"\underbrace{\frac{2k_{\mathrm B}T}{\lambda^2}}_{\text{radiance}}"
            r"\underbrace{\lambda^2}_{\text{one spatial mode}}\,d\nu",
            -.45, size=42)))
        result = equation(r"dP=k_{\mathrm B}T\,d\nu", -1.95, RADIO, 56)
        self.play(Write(result), Create(SurroundingRectangle(result, color=RADIO, buff=.18)))
        self.play(Write(equation(
            r"k_{\mathrm B}T\ [\mathrm J]=[\mathrm{W/Hz}],"
            r"\qquad d\nu\ [\mathrm{Hz}]\quad\Longrightarrow\quad dP\ [\mathrm W]",
            -3.0, size=29)))
        finish()

    def bandwidth_integration(self):
        self.start_slide("Bandwidth integration")

        title = self.title("Flat radio noise across the receiver bandwidth")

        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 1.4, 0.5],
            x_length=9.5,
            y_length=3.6,
            axis_config={"color": MUTED, "include_ticks": False},
            tips=False,
        ).shift(DOWN * 0.72)
        baseline = axes.plot(lambda x: 0.82, x_range=[0.5, 9.5], color=RADIO, stroke_width=5)
        bandwidth_area = axes.get_area(
            baseline,
            x_range=[3.0, 7.2],
            color=RADIO,
            opacity=0.26,
        )
        left = DashedLine(axes.c2p(3.0, 0), axes.c2p(3.0, 0.82), color=MUTED)
        right = DashedLine(axes.c2p(7.2, 0), axes.c2p(7.2, 0.82), color=MUTED)

        psd = MathTex(r"\frac{dP}{d\nu}=k_{\mathrm B}T", font_size=42, color=RADIO).next_to(
            axes.c2p(7.6, 0.82), UP, buff=0.12
        )
        b_label = MathTex(r"B=\nu_2-\nu_1", font_size=34, color=ACCENT).next_to(
            axes.c2p(5.1, 0), DOWN, buff=0.28
        )
        x_label = Text("frequency", font_size=23, color=MUTED).next_to(
            axes.x_axis, RIGHT, buff=0.18
        ).shift(DOWN * 0.08)

        integral = MathTex(
            r"P=\int_{\nu_1}^{\nu_2}k_{\mathrm B}T\,d\nu",
            font_size=43,
            color=FG,
        )
        answer = MathTex(r"P=k_{\mathrm B}\,T\,B", font_size=55, color=ACCENT)
        answer_box = SurroundingRectangle(answer, buff=0.25, color=ACCENT, corner_radius=0.12)
        equation_row = VGroup(integral, VGroup(answer_box, answer)).arrange(RIGHT, buff=0.75)
        equation_row.next_to(title, DOWN, buff=0.32)

        self.play(FadeIn(title), Write(integral))
        self.play(TransformFromCopy(integral, answer), Create(answer_box))
        self.play(Create(axes), FadeIn(x_label))
        self.play(Create(baseline), FadeIn(psd))
        self.play(FadeIn(bandwidth_area), Create(left), Create(right), FadeIn(b_label))
        self.wait(2.0)
        self.clear_slide()

    def validity_and_close(self):
        self.start_slide("Validity and example")

        title = self.title("What the radio formula assumes")

        exact = MathTex(
            r"\frac{dP}{d\nu}=\frac{h\nu}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=48,
            color=PLANCK,
        ).next_to(title, DOWN, buff=0.45)
        limit_arrow = MathTex(
            r"\xrightarrow{\ h\nu\ll k_{\mathrm B}T\ } k_{\mathrm B}T",
            font_size=45,
            color=RJ,
        ).next_to(exact, RIGHT, buff=0.42)

        assumptions = VGroup(
            VGroup(MathTex(r"1", font_size=31, color=ACCENT), Text("one matched spatial mode", font_size=28, color=FG)),
            VGroup(MathTex(r"2", font_size=31, color=ACCENT), Text("one polarization", font_size=28, color=FG)),
            VGroup(MathTex(r"3", font_size=31, color=ACCENT), Text("classical limit across bandwidth B", font_size=28, color=FG)),
        )
        for row in assumptions:
            row.arrange(RIGHT, buff=0.28)
        assumptions.arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(LEFT * 3.4 + DOWN * 0.65)

        example_title = Text("Room-temperature example", font_size=30, weight=SEMIBOLD, color=RADIO)
        example = MathTex(
            r"T=290\,\mathrm{K},\quad B=1\,\mathrm{MHz}",
            r"\\[5pt] P=4.00\times10^{-15}\,\mathrm{W}",
            r"\\[-1pt] =-114.0\,\mathrm{dBm}",
            font_size=38,
            color=FG,
        )
        example_group = VGroup(example_title, example).arrange(DOWN, buff=0.22).shift(RIGHT * 3.55 + DOWN * 0.78)

        takeaway = VGroup(
            Text("Planck gives the energy in each mode", font_size=30, color=PLANCK),
            Text("A single radio mode turns that energy into power per hertz", font_size=30, color=RADIO),
        ).arrange(DOWN, buff=0.18).to_edge(DOWN, buff=0.42)

        self.play(FadeIn(title), Write(exact), FadeIn(limit_arrow))
        self.play(LaggedStart(*[FadeIn(row, shift=0.15 * RIGHT) for row in assumptions], lag_ratio=0.18))
        self.play(FadeIn(example_group, shift=0.2 * UP))
        self.play(FadeIn(takeaway))
        self.wait(2.5)
