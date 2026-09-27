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
from rayleigh_jeans_accuracy import frequency_for_error


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


class Text(Tex):
    """Typeset prose with LaTeX; bypass Pango/SVG glyph-position corruption.

    Keep the deck's serif appearance and TeX's word spacing/kerning. Escape
    ordinary prose before typesetting; mathematical content uses MathTex.
    """

    def __init__(self, text, font_size=48, color=WHITE, weight=None, t2c=None, **kwargs):
        escapes = {
            "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
            "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
            "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
            "–": "--", "—": "---", "\n": r"\\",
        }
        def escape(value):
            return "".join(escapes.get(char, char) for char in value)
        prose = escape(text)
        for phrase, shade in (t2c or {}).items():
            rgb = ManimColor(shade).to_hex().lstrip("#")
            prose = prose.replace(escape(phrase), r"\textcolor[HTML]{" + rgb + "}{" + escape(phrase) + "}")
        if weight in (BOLD, SEMIBOLD):
            prose = r"\textbf{" + prose + "}"
        template = TexTemplate()
        template.add_to_preamble(r"\usepackage{xcolor}")
        kwargs.setdefault("tex_template", template)
        super().__init__(prose, font_size=font_size, color=color, **kwargs)


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
        self.what_is_spectral_radiance()
        self.planck_and_rj_plot()
        self.rayleigh_jeans_limit()
        self.planck_and_rj_plot(compare=True)
        self.single_mode_bridge()
        self.received_mode_plot()
        self.bandwidth_integration()
        self.validity_and_close()
        self.clear_slide()
        self.credits()

    def credits(self):
        self.start_slide("Credits and references")
        self.play(FadeIn(self.title("Credits and references")))
        entries = [
            ("Radio sky software: PyGDSM", "Python interface to Global Diffuse Sky Models",
             "github.com/telegraphic/pygdsm"),
            ("408 MHz survey: Haslam et al. (1982)",
             "A 408 MHz all-sky continuum survey. II. The atlas of contour maps",
             "Astronomy and Astrophysics Supplement Series, 47, 1-143"),
            ("Reprocessed map: Remazeilles et al. (2015)",
             "An improved source-subtracted and destriped 408-MHz all-sky map",
             "MNRAS 451, 4311-4327 | doi:10.1093/mnras/stv1274"),
        ]
        rows = VGroup()
        for heading, detail, reference in entries:
            row = VGroup(Text(heading, font_size=29, color=RADIO),
                         Text(detail, font_size=23, color=FG),
                         Text(reference, font_size=21, color=MUTED)).arrange(
                             DOWN, aligned_edge=LEFT, buff=0.12)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(UP * 0.05)
        if rows.width > 12.5:
            rows.scale_to_fit_width(12.5)
        self.play(LaggedStart(*[FadeIn(row) for row in rows], lag_ratio=0.25))
        note = Text("Opening map: Galactic coordinates, kelvins; CMB monopole excluded.",
                    font_size=22, color=MUTED).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note))
        self.wait(3)

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
            DOWN, aligned_edge=LEFT, buff=0.30
        )
        definitions = VGroup(quantity, units, notes).arrange(
            DOWN, aligned_edge=LEFT, buff=0.25
        )
        if definitions.width > 6.0:
            definitions.scale_to_fit_width(6.0)
        definitions.move_to(LEFT * 3.45 + DOWN * 0.75)

        # Oblique projection: z runs horizontally; x and y are transverse.
        # Separate lanes depict independent modes, not a coherent superposition.
        phase = ValueTracker(0)
        wave_origin = RIGHT * 0.65
        length, amplitude = 5.25, 0.57
        transverse = (UP, np.array([0.42, 0.72, 0.0]))
        colors = (RADIO, RJ)
        wave_axes = VGroup()
        wave_labels = VGroup()
        for index, (direction, color) in enumerate(zip(transverse, colors)):
            origin = wave_origin + DOWN * (0.20 + 1.75 * index)
            wave_axes.add(Arrow(origin, origin + RIGHT * (length + 0.25),
                                buff=0, color=MUTED, stroke_width=2))
            wave_axes.add(DoubleArrow(origin - direction * 0.8,
                                      origin + direction * 0.8,
                                      buff=0, color=color, stroke_width=2))
            wave_labels.add(MathTex(r"E_x" if index == 0 else r"E_y",
                                    font_size=30, color=color)
                            .move_to(origin + direction * 1.08))
            wave_labels.add(MathTex(r"z", font_size=25, color=MUTED)
                            .next_to(wave_axes[-2], RIGHT, buff=0.1))

        def electric_fields():
            fields = VGroup()
            for index, (direction, color) in enumerate(zip(transverse, colors)):
                origin = wave_origin + DOWN * (0.20 + 1.75 * index)
                offset = 0.8 * index
                def point(z):
                    return (origin + RIGHT * z + direction * amplitude
                            * np.sin(TAU * 2 * z / length - phase.get_value() + offset))
                fields.add(ParametricFunction(point, t_range=[0, length, 0.025],
                                              color=color, stroke_width=4))
                for z in np.linspace(0.15, length - 0.15, 19):
                    fields.add(Line(origin + RIGHT * z, point(z),
                                    color=color, stroke_width=1.5, stroke_opacity=0.55))
            return fields

        fields = always_redraw(electric_fields)
        wave_heading = Text("Two transverse electric-field modes", font_size=23,
                            color=FG).move_to(RIGHT * 3.45 + UP * 1.05)
        wave_note = VGroup(
            MathTex(r"\mathbf{E}\perp\hat{\mathbf{z}},\quad [E_x]=[E_y]=\mathrm{V\,m^{-1}}",
                    font_size=25, color=FG),
            Text("Independent thermal modes (schematic)", font_size=19, color=MUTED),
        ).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.45 + DOWN * 3.0)

        self.play(FadeIn(title), Write(formula))
        self.play(Write(quantity), Write(units))
        self.play(LaggedStart(*[FadeIn(note, shift=0.12 * RIGHT) for note in notes], lag_ratio=0.16))
        self.play(FadeIn(wave_heading), FadeIn(wave_axes), FadeIn(wave_labels),
                  FadeIn(fields), FadeIn(wave_note))
        self.play(phase.animate.set_value(2 * TAU), run_time=5, rate_func=linear)
        fields.clear_updaters()
        self.wait(2.0)
        self.clear_slide()

    def what_is_spectral_radiance(self):
        self.start_slide("What spectral radiance measures")
        self.play(FadeIn(self.title("What is spectral radiance?")))
        definition = MathTex(
            r"B_\nu=\frac{dP}{dA_{\perp,\mathrm s}\,d\Omega_{\mathrm r}\,d\nu}"
            r"\quad[\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}]",
            font_size=34, color=FG).move_to(UP * 2.25)
        source = Ellipse(width=.55, height=1.5, color=PLANCK,
                         fill_color=PLANCK, fill_opacity=.4).move_to([-4.8,.45,0])
        cone = Polygon([-4.8,.45,0], [.3,1.55,0], [.3,-.65,0],
                       color=PLANCK, fill_color=PLANCK, fill_opacity=.12)
        rays = VGroup(*[Arrow([-4.5,.45,0],[.2,y,0], color=PLANCK,
                              buff=.1, stroke_width=3) for y in (-.5,.45,1.4)])
        area = MathTex(r"dA_{\perp,\mathrm s}\ [\mathrm{m^2}]",
                       font_size=28, color=PLANCK).move_to([-4.8,-.65,0])
        area_note = Text("projected emitting area",font_size=19,color=PLANCK).move_to([-4.8,-1.12,0])
        angle = MathTex(r"d\Omega_{\mathrm r}\ [\mathrm{sr}]",font_size=30,color=PLANCK).move_to([-1.5,1.55,0])
        angle_note = Text("cone of outgoing directions",font_size=19,color=PLANCK).move_to([-1.4,-1.35,0])
        axis = Arrow([1.8,.05,0],[6,.05,0],buff=0,color=MUTED)
        bars = VGroup(*[Line([x,.05,0],[x,1.05,0],color=FG,stroke_opacity=.3,stroke_width=1)
                        for x in np.linspace(1.95,5.75,35)])
        band = Rectangle(width=.5,height=1,color=PLANCK,fill_opacity=.35).move_to([3.8,.55,0])
        band_label = MathTex(r"d\nu\ [\mathrm{Hz}]",font_size=30,color=PLANCK).next_to(band,UP,buff=.2)
        axis_label = MathTex(r"\nu\ [\mathrm{Hz}]",font_size=27,color=FG).next_to(axis,DOWN,buff=.2)
        power = MathTex(r"dP=B_\nu\,dA_{\perp,\mathrm s}\,d\Omega_{\mathrm r}\,d\nu",
                        font_size=42,color=FG).move_to(DOWN*2.15)
        note = VGroup(
            MathTex(r"d\Omega_{\mathrm r}:\ \text{solid angle of this cone, viewed from the emitting patch}",
                    font_size=26,color=PLANCK),
            Tex(r"The subscript $\mathrm r$ denotes the receiving side of the cone.",
                font_size=28,color=MUTED),
        ).arrange(DOWN,buff=.23).move_to(DOWN*3.13)
        assert note.width < 13, "Radiance caption must fit without shrinking"
        self.play(Write(definition),FadeIn(source),Write(area),FadeIn(area_note))
        self.play(FadeIn(cone),Create(rays),Write(angle),FadeIn(angle_note))
        self.play(Create(axis),FadeIn(bars),FadeIn(band),Write(band_label),Write(axis_label))
        self.play(Write(power),FadeIn(note))
        self.wait(2.5)
        self.clear_slide()

    def source_receiver_geometry(self):
        self.start_slide("The two solid angles connect emission and reception")
        self.play(FadeIn(self.title("The same bundle of rays, viewed from each end")))
        patches = VGroup(
            Ellipse(width=.4,height=.85,color=PLANCK,fill_opacity=.25).move_to([-4.3,1.4,0]),
            Ellipse(width=.4,height=.85,color=RADIO,fill_opacity=.25).move_to([4.3,1.4,0]))
        labels = VGroup(
            MathTex(r"dA_{\perp,\mathrm s}:\ \text{source}",font_size=28,color=PLANCK).next_to(patches[0],UP,buff=.15),
            MathTex(r"dA_{\perp,\mathrm r}:\ \text{receiver}",font_size=28,color=RADIO).next_to(patches[1],UP,buff=.15))
        distance = DoubleArrow([-4,1.4,0],[4,1.4,0],buff=0,color=MUTED)
        r_label = MathTex(r"R\ [\mathrm m]",font_size=28,color=FG).next_to(distance,UP,buff=.12)
        angles = VGroup(
            MathTex(r"d\Omega_{\mathrm r}=\frac{dA_{\perp,\mathrm r}}{R^2}",font_size=38,color=RADIO),
            MathTex(r"d\Omega_{\mathrm s}=\frac{dA_{\perp,\mathrm s}}{R^2}",font_size=38,color=PLANCK),
        ).arrange(RIGHT,buff=1.1).move_to(UP*.05)
        angle_notes = VGroup(
            Text("receiver seen from source",font_size=20,color=RADIO).move_to([-2.3,-.65,0]),
            Text("source seen from receiver",font_size=20,color=PLANCK).move_to([2.4,-.65,0]))
        emitted = MathTex(
            r"dP=B_\nu\,dA_{\perp,\mathrm s}\,"
            r"\frac{dA_{\perp,\mathrm r}}{R^2}\,d\nu",
            font_size=39,color=FG).move_to(DOWN*1.5)
        received = MathTex(
            r"dP=B_\nu\,dA_{\perp,\mathrm r}\,"
            r"\underbrace{\frac{dA_{\perp,\mathrm s}}{R^2}}_{d\Omega_{\mathrm s}}\,d\nu",
            font_size=39,color=FG).move_to(DOWN*2.65)
        assumption = Text("Small angular patches; unobstructed propagation without absorption.",
                          font_size=20,color=MUTED).to_edge(DOWN,buff=.2)
        self.play(FadeIn(patches),Write(labels),Create(distance),Write(r_label))
        self.play(Write(angles),FadeIn(angle_notes))
        self.play(Write(emitted))
        self.play(TransformFromCopy(emitted,received),FadeIn(assumption))
        self.wait(2.5)
        self.clear_slide()

        self.start_slide("From geometric receiver area to antenna effective area")
        self.play(FadeIn(self.title("Now replace the collecting surface with an antenna")))
        geometric = MathTex(
            r"dP=B_\nu\,dA_{\perp,\mathrm r}\,d\Omega_{\mathrm s}\,d\nu",
            font_size=43,color=FG).move_to(UP*2.0)
        collecting = Text("Use the antenna's effective collecting area for this direction:",
                          font_size=26,color=FG).move_to(UP*.9)
        effective = MathTex(r"dA_{\perp,\mathrm r}\ \longrightarrow\
A_{\mathrm e}(\theta,\phi)\quad[\mathrm{m^2}]",font_size=40,color=RADIO).move_to(UP*.1)
        power = MathTex(
            r"dP=\frac12 B_\nu(\theta,\phi)\,A_{\mathrm e}(\theta,\phi)\,d\Omega_{\mathrm s}\,d\nu",
            font_size=40,color=FG).move_to(DOWN*1.2)
        notes = VGroup(
            Text("The source area is already accounted for in its apparent solid angle.",
                 font_size=24,color=PLANCK),
            Text("The factor 1/2 selects one polarization; Planck radiance includes both.",
                 font_size=23,color=MUTED),
            MathTex(r"d\Omega_{\mathrm s}\equiv d\Omega:\ \text{small patch of sky seen by the antenna}",
                    font_size=27,color=FG),
        ).arrange(DOWN,buff=.25).move_to(DOWN*2.75)
        self.play(Write(geometric))
        self.play(FadeIn(collecting),Write(effective))
        self.play(Write(power),FadeIn(notes))
        self.wait(2.5)
        self.clear_slide()

    def planck_and_rj_plot(self, compare=False):
        """Radiance only: changing the frequency scale cannot flatten B_nu."""
        self.start_slide("Planck spectral radiance at 300 K")
        title = self.title("Planck spectral radiance at 300 K")
        relation = MathTex(
            r"B_\nu(T)=\frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=38, color=PLANCK,
        ).next_to(title, DOWN, buff=0.25)
        axes = Axes(
            x_range=[0, 150, 30], y_range=[0, 6, 1],
            x_length=10.3, y_length=3.6,
            axis_config={"color": MUTED, "include_numbers": True, "font_size": 22},
            tips=False,
        ).shift(DOWN * 0.35)
        x_label = Text("frequency [THz]", font_size=25, color=FG).next_to(
            axes.x_axis, DOWN, buff=0.25)
        y_label = MathTex(
            r"B_\nu\ [10^{-12}\,\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}]",
            font_size=25, color=FG,
        ).rotate(PI / 2).next_to(axes.y_axis, LEFT, buff=0.25)

        def radiance(f):
            if f == 0:
                return 0.0
            nu = f * 1e12
            return 2 * 6.62607015e-34 * nu**3 / 299792458.0**2 / np.expm1(
                6.62607015e-34 * nu / (1.380649e-23 * 300)) / 1e-12

        curve = axes.plot(radiance, x_range=[0, 150, 0.15],
                          color=PLANCK, stroke_width=5)
        note = Text("Spectral radiance: power per area, solid angle and frequency.",
                    font_size=23, color=MUTED).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(title), Write(relation))
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))
        self.play(Create(curve), run_time=2)
        self.play(FadeIn(note))
        self.wait(2)
        if not compare:
            self.clear_slide()
            return

        # This comparison is introduced only after deriving the approximation.
        rj_relation = MathTex(
            r"B_\nu^{\rm P}=\frac{2h\nu^3/c^2}{e^{h\nu/(k_{\mathrm B}T)}-1},"
            r"\qquad B_\nu^{\rm RJ}=\frac{2k_{\mathrm B}T\nu^2}{c^2}",
            font_size=32, color=FG,
        ).move_to(relation)

        def rj_radiance(f):
            return 2 * 1.380649e-23 * 300 * (f * 1e12)**2 / 299792458.0**2 / 1e-12

        # Stop at the top of the plotting window; the approximation keeps rising.
        top_frequency = np.sqrt(6 / rj_radiance(1))
        rj_curve = axes.plot(rj_radiance, x_range=[0, top_frequency, 0.025],
                            color=RJ, stroke_width=4)
        legend = VGroup(Text("Planck", font_size=25, color=PLANCK),
                        Text("Rayleigh-Jeans", font_size=25, color=RJ)).arrange(
                            DOWN, aligned_edge=LEFT, buff=0.18).move_to(axes.c2p(112, 4.5))
        divergence = Text("RJ continues upward", font_size=21, color=RJ).move_to(
            axes.c2p(35, 5.5))
        comparison_note = Text("Rayleigh-Jeans fails at high frequency: it has no peak or falling tail.",
                               font_size=23, color=MUTED).move_to(note)
        self.play(Transform(relation, rj_relation), Create(rj_curve), FadeIn(legend),
                  FadeIn(divergence), Transform(note, comparison_note))
        self.wait(2)

        self.start_slide("Zoom into low-frequency spectral radiance")
        zoom_title = self.title("Zoom into the radio-frequency part of the same spectrum")
        # End where RJ is 5% above exact Planck radiance, rather than at
        # an arbitrary radio-band boundary. This threshold depends on T.
        zoom_end = np.log10(frequency_for_error(0.05, 300.0))
        zoom_axes = Axes(
            x_range=[6, zoom_end, 1], y_range=[0, 4, 1],
            x_length=10.3, y_length=3.6,
            axis_config={"color": MUTED, "include_numbers": True, "font_size": 22},
            tips=False,
        ).shift(DOWN * 0.35)
        zoom_x = MathTex(r"\log_{10}(\nu/\mathrm{Hz})", font_size=27,
                         color=FG).next_to(zoom_axes.x_axis, DOWN, buff=0.25)
        zoom_y = MathTex(
            r"B_\nu\ [10^{-14}\,\mathrm{W\,m^{-2}\,sr^{-1}\,Hz^{-1}}]",
            font_size=25, color=FG,
        ).rotate(PI / 2).next_to(zoom_axes.y_axis, LEFT, buff=0.25)
        zoom_curve = zoom_axes.plot(
            lambda log_nu: radiance(10**log_nu / 1e12) * 1e2,
            x_range=[6, zoom_end, 0.01], color=PLANCK, stroke_width=5,
        )
        zoom_rj = DashedVMobject(zoom_axes.plot(
            lambda log_nu: rj_radiance(10**log_nu / 1e12) * 1e2,
            x_range=[6, zoom_end, 0.01], color=RJ, stroke_width=4,
        ), num_dashes=55)
        zoom_note = Text("300 K: RJ is 1% high at 124 GHz and 5% high at 605 GHz (relative to Planck).",
                         font_size=22, color=MUTED).to_edge(DOWN, buff=0.25)
        endpoint = Text("605 GHz", font_size=22, color=FG).move_to(zoom_axes.c2p(10.9, 3.75))
        self.play(Transform(title, zoom_title), Transform(axes, zoom_axes),
                  Transform(x_label, zoom_x), Transform(y_label, zoom_y),
                  Transform(curve, zoom_curve), Transform(rj_curve, zoom_rj),
                  legend.animate.move_to(zoom_axes.c2p(7.5, 2.8)), FadeOut(divergence),
                  Transform(note, zoom_note), run_time=3)
        self.play(FadeIn(endpoint))
        self.wait(2)
        self.clear_slide()

    def received_mode_plot(self):
        """Only show a flat spectrum after deriving the receiving-mode conversion."""
        self.start_slide("Power spectral density")
        title = self.title("Power spectral density: received power per hertz")
        definition = MathTex(r"S_\nu\equiv\frac{dP}{d\nu}\quad[\mathrm{W\,Hz^{-1}}]",
                             font_size=53,color=FG).move_to(UP*1.45)
        result = MathTex(r"S_\nu\simeq k_{\mathrm B}T\qquad(h\nu\ll k_{\mathrm B}T)",
                         font_size=47,color=RADIO).move_to(DOWN*.2)
        self.play(FadeIn(title),Write(definition))
        self.play(Write(result))
        self.wait(2.5)
        self.clear_slide()

        self.start_slide("Received thermal power per hertz")
        title = self.title("Received power per hertz: 300 K, one polarization")
        relation = MathTex(
            r"S_\nu=\frac{h\nu}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=38, color=PLANCK,
        ).next_to(title, DOWN, buff=0.25)

        def spectrum(log_nu):
            nu = 10**log_nu
            return 6.62607015e-34 * nu / np.expm1(
                6.62607015e-34 * nu / (1.380649e-23 * 300)) / 1e-21

        def plot_objects(lo, hi):
            axes = Axes(
                x_range=[lo, hi, 1], y_range=[0, 5, 1],
                x_length=10.3, y_length=3.2,
                axis_config={"color": MUTED, "include_numbers": True, "font_size": 22},
                tips=False,
            )
            x_label = MathTex(r"\log_{10}(\nu/\mathrm{Hz})", font_size=28,
                             color=FG).move_to([0, -2.55, 0])
            y_label = MathTex(r"S_\nu\ [10^{-21}\,\mathrm{W\,Hz^{-1}}]",
                             font_size=26, color=FG).rotate(PI/2).next_to(
                                 axes.y_axis, LEFT, buff=0.3)
            curve = axes.plot(spectrum, x_range=[lo, hi, 0.02],
                              color=PLANCK, stroke_width=5)
            return VGroup(axes, x_label, y_label, curve)

        plot = plot_objects(6, 15)
        note = Text("Received power per hertz is nearly constant at low frequencies and falls at high frequencies.",
                    font_size=22, color=MUTED).move_to([0, -3.5, 0])
        if note.width > 13:
            note.scale_to_fit_width(13)
        assert plot[1].get_bottom()[1] - note.get_top()[1] > .35
        self.play(FadeIn(title), Write(relation))
        self.play(Create(plot), run_time=2)
        self.play(FadeIn(note))
        self.wait(2)

        # A genuine zoom now keeps the same vertical physical quantity.
        self.start_slide("Radio-frequency received power")
        limit_frequency = frequency_for_error(.05, 300)
        upper_log_frequency = np.log10(limit_frequency)
        zoom = plot_objects(6, upper_log_frequency)
        self.play(Transform(plot, zoom), FadeOut(note), run_time=2)
        axes = zoom[0]
        rj_line = DashedVMobject(axes.plot(
            lambda _: 1.380649e-23 * 300 / 1e-21,
            x_range=[6, upper_log_frequency], color=RJ, stroke_width=4,
        ), num_dashes=40)
        limit = MathTex(
            r"S_\nu\simeq k_{\mathrm B}T=4.14\times10^{-21}\,\mathrm{W\,Hz^{-1}}",
            font_size=34, color=RJ,
        ).move_to(axes.c2p((6+upper_log_frequency)/2, 2.2))
        endpoint = Dot(axes.c2p(upper_log_frequency,spectrum(upper_log_frequency)),
                       color=PLANCK,radius=.055)
        endpoint_label = Text(f"{limit_frequency/1e9:.0f} GHz: 5% high",font_size=22,
                              color=RJ).next_to(endpoint,DOWN,buff=.22).shift(LEFT*.8)
        caption = Text("At 300 K, the kBT approximation is within 5% of the exact power up to about 605 GHz.",
                       font_size=23, color=FG).move_to([0, -3.5, 0])
        if caption.width > 13:
            caption.scale_to_fit_width(13)
        assert zoom[1].get_bottom()[1] - caption.get_top()[1] > .35
        self.play(Create(rj_line), Write(limit), FadeIn(caption))
        self.play(FadeIn(endpoint),FadeIn(endpoint_label))
        self.wait(2)
        self.clear_slide()

    def rayleigh_jeans_limit(self):
        self.start_slide("Rayleigh-Jeans limit")

        title = self.title("The low-frequency limit")
        condition = MathTex(r"x\equiv\frac{h\nu}{k_{\mathrm B}T}\ll1",
                            font_size=35,color=RJ).move_to(UP*2.55)
        planck_eq = MathTex(
            r"B_\nu(T)=\frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/(k_{\mathrm B}T)}-1}",
            font_size=43,color=PLANCK).move_to(UP*1.2)
        expansion = MathTex(r"e^x=1+x+\frac{x^2}{2!}+\cdots",
                            font_size=35,color=FG).move_to(DOWN*.15)
        denominator = MathTex(
            r"e^x-1=x+\frac{x^2}{2!}+\cdots\simeq x=\frac{h\nu}{k_{\mathrm B}T}",
            font_size=35,color=FG).move_to(expansion)
        substituted = MathTex(
            r"B_\nu(T)\simeq\frac{2h\nu^3}{c^2}\frac{k_{\mathrm B}T}{h\nu}",
            font_size=39,color=FG).move_to(DOWN*1.55)
        result = MathTex(
            r"B_\nu(T)\simeq\frac{2h\nu^3}{c^2}\frac{k_{\mathrm B}T}{h\nu}",
            r"=\frac{2k_{\mathrm B}T\nu^2}{c^2}",
            font_size=39,color=FG).move_to(substituted)
        result[1].set_color(RJ)
        interpretation = Text("Rayleigh–Jeans approximation: spectral radiance still rises as frequency squared.",
                              font_size=21,color=MUTED).move_to(DOWN*3.5)
        if interpretation.width>13:
            interpretation.scale_to_fit_width(13)
        self.play(FadeIn(title),Write(planck_eq),run_time=1.5)
        self.play(Write(condition),run_time=1.2)
        self.play(Write(expansion),run_time=1.5)
        self.wait(.6)
        self.play(TransformMatchingTex(expansion,denominator),run_time=1.8)
        self.wait(.6)
        self.play(Write(substituted),run_time=2)
        self.wait(2)
        self.start_slide("Cancel h and reduce the frequency power")
        self.play(TransformMatchingTex(substituted,result),run_time=2)
        self.play(Create(SurroundingRectangle(result[1],buff=.15,color=RJ)),
                  FadeIn(interpretation))
        self.wait(2.5)
        self.clear_slide()

    def receiver_view(self):
        """Track projected source area into receiver solid angle, then sum patches."""
        angle_template = TexTemplate()
        angle_template.add_to_preamble(r"\usepackage{xcolor}")
        self.start_slide("Radiance is not yet received power")
        title = self.title("From the emitting surface to the receiving antenna")
        self.play(FadeIn(title))
        source = Ellipse(width=.7, height=2.25, color=PLANCK).move_to([-4.5, 1.05, 0])
        receiver = Ellipse(width=.5, height=1.25, color=RADIO,
                           fill_opacity=.25).move_to([4.4, 1.05, 0])
        patches = VGroup(*[
            Ellipse(width=.52, height=.65, color=PLANCK, fill_opacity=.45)
            .move_to([-4.5, 1.05 + dy, 0]) for dy in (-.72, 0, .72)
        ])
        labels = VGroup(
            Text("Emitting surface", font_size=25, color=PLANCK).next_to(source, UP, buff=.2),
            MathTex(r"A_{\mathrm e}(\theta,\phi)\ [\mathrm{m^2}]", font_size=29,
                    color=RADIO).next_to(receiver, UP, buff=.4),
            Text("Receiver", font_size=24, color=RADIO).next_to(receiver, DOWN, buff=.2),
        )
        cones = VGroup(*[
            Polygon([-4.25, 1.05+dy, 0], [4.15, .45, 0], [4.15, 1.65, 0],
                    color=PLANCK, stroke_width=2, fill_opacity=.09)
            for dy in (-.72, 0, .72)
        ])
        source_cone = Polygon([4.15,1.05,0],[-4.25,.75,0],[-4.25,1.35,0],
                              color=RADIO,stroke_width=3,fill_opacity=.1)
        receiver_cone_label = MathTex(r"d\Omega_{\mathrm{r,eff}}",font_size=25,
                                     color=PLANCK).move_to([-2.85,1.64,0])
        source_cone_label = MathTex(r"d\Omega_{\mathrm s}",font_size=25,
                                   color=RADIO).move_to([2.7,.72,0])
        distance = DoubleArrow([-4.3, -.5, 0], [4.15, -.5, 0], buff=0, color=MUTED)
        distance_label = MathTex(r"R\ [\mathrm m]", font_size=27).next_to(distance, DOWN, buff=.1)
        patch_label = MathTex(r"dA_{\perp,\mathrm s}\ [\mathrm{m^2}]", font_size=28,
                              color=PLANCK).move_to([-4.5, -.95, 0])
        omega = MathTex(r"d\Omega_{\mathrm{r,eff}}=\frac{\textcolor[HTML]{74A9FF}{A_{\mathrm e}(\theta,\phi)}}{R^2}\ [\mathrm{sr}]",
                        font_size=25, color=PLANCK,tex_template=angle_template).move_to([0, 2.65, 0])
        source_angle = MathTex(r"d\Omega_{\mathrm s}=\frac{\textcolor[HTML]{F5A65B}{dA_{\perp,\mathrm s}}}{R^2}\ [\mathrm{sr}]",
                              font_size=25,color=RADIO,tex_template=angle_template).move_to([0,1.98,0])
        power = MathTex(
            r"dP=\frac12 B_\nu\,dA_{\perp,\mathrm s}",
            r"\underbrace{\frac{\textcolor[HTML]{74A9FF}{A_{\mathrm e}(\theta,\phi)}}{R^2}}_{\textcolor[HTML]{F5A65B}{d\Omega_{\mathrm{r,eff}}}}", r"\,d\nu",
            font_size=38,tex_template=angle_template).move_to(DOWN*2.05)
        note = VGroup(
            MathTex(r"\theta:\ \text{angle from the receiver's pointing axis}\quad[\mathrm{rad}]",
                    font_size=25,color=RADIO),
            MathTex(r"\phi:\ \text{azimuth around that axis}\quad[\mathrm{rad}]",
                    font_size=25,color=RADIO),
            Text("Together they specify the direction of the source as seen by the antenna.",
                 font_size=20,color=MUTED),
        ).arrange(DOWN,buff=.12).to_edge(DOWN,buff=.2)
        if note.width > 13:
            note.scale_to_fit_width(13)
        self.play(Create(source), Create(receiver), FadeIn(labels))
        self.play(FadeIn(note))
        self.play(FadeIn(patches[1]), Write(patch_label), Create(distance), Write(distance_label))
        self.play(FadeIn(cones[1]),Write(receiver_cone_label))
        self.play(TransformFromCopy(labels[1], omega))
        self.play(FadeIn(source_cone),Write(source_cone_label),
                  TransformFromCopy(patch_label,source_angle),run_time=2)
        self.play(Write(power))
        self.wait(2.5)
        self.start_slide("Integrating the source includes its projected area")
        surface = MathTex(
            r"P_\nu=\frac{dP}{d\nu}=\frac12\int_{\mathrm{surface}} B_\nu\,",
            r"\frac{A_{\mathrm e}(\theta,\phi)}{R^2}",r"\,dA_{\perp,\mathrm s}",
            font_size=34).move_to(DOWN*1.7)
        surface[1].set_color(RADIO)
        surface[2].set_color(PLANCK)
        regrouped = MathTex(
            r"=\frac12\int_{\mathrm{surface}}B_\nu\,",
            r"A_{\mathrm e}(\theta,\phi)",
            r"\underbrace{\frac{\textcolor[HTML]{F5A65B}{dA_{\perp,\mathrm s}}}{R^2}}_{\textcolor[HTML]{74A9FF}{d\Omega_{\mathrm s}}}",
            font_size=34,tex_template=angle_template).move_to(DOWN*2.75)
        regrouped[1].set_color(RADIO)
        sky = MathTex(
            r"=\frac12\int_{\mathrm{sky}}B_\nu\,",
            r"A_{\mathrm e}(\theta,\phi)",r"\,d\Omega_{\mathrm s}",
            font_size=34).move_to(regrouped)
        sky[1].set_color(RADIO)
        sky[2].set_color(RADIO)
        summed_note = Text("Change viewpoint: each emitting patch occupies a solid angle on the antenna's sky.",
                           font_size=20,color=MUTED).to_edge(DOWN,buff=.22)
        if summed_note.width>13:
            summed_note.scale_to_fit_width(13)
        self.play(FadeOut(cones[1]),FadeOut(receiver_cone_label),
                  FadeIn(patches[0]),FadeIn(patches[2]))
        self.play(TransformMatchingTex(power,surface),FadeOut(note),FadeIn(summed_note),run_time=2)
        self.wait(.8)
        self.play(TransformFromCopy(surface,regrouped),run_time=2.5)
        self.play(Indicate(regrouped[2],color=RADIO),Indicate(source_angle,color=RADIO))
        self.wait(.8)
        antenna_note = Text("Integrate looking outward from the antenna: its collecting area times each source patch's solid angle.",
                            font_size=20,color=RADIO).move_to(summed_note)
        if antenna_note.width>13:
            antenna_note.scale_to_fit_width(13)
        self.play(TransformMatchingTex(regrouped,sky),
                  Transform(title,self.title("Integrate over the sky seen by the antenna")),
                  FadeOut(summed_note),FadeIn(antenna_note),run_time=2.5)
        # Sweep the integration element across the source, not the receiver.
        # Its vertex remains at the antenna throughout the animation.
        selected_patch = Ellipse(width=.52,height=.65,color=RADIO,
                                 stroke_width=4,fill_opacity=.16).move_to(patches[1])
        self.play(FadeIn(selected_patch),Indicate(receiver,color=RADIO))
        for offset in (.72,-.72,0):
            scanned_cone = Polygon([4.15,1.05,0],
                                   [-4.25,.75+offset,0],[-4.25,1.35+offset,0],
                                   color=RADIO,stroke_width=3,fill_opacity=.1)
            self.play(Transform(source_cone,scanned_cone),
                      selected_patch.animate.move_to([-4.5,1.05+offset,0]),
                      source_cone_label.animate.move_to([2.7,.72+.17*offset,0]),
                      run_time=2,rate_func=smooth)
        self.wait(2.5)
        self.clear_slide()

    def beam_solid_angle_explanation(self):
        self.start_slide("What beam solid angle means")
        self.play(FadeIn(self.title("Beam solid angle: an equivalent ideal field of view")))
        definition = MathTex(
            r"p(\theta,\phi)=\frac{A_{\mathrm e}(\theta,\phi)}{A_{\mathrm e,max}}"
            r"\quad\text{relative collecting response; peak }p=1",
            font_size=31,color=RADIO).move_to(UP*2.5)
        self.play(Write(definition))
        axes = VGroup(*[Axes(x_range=[0,4*PI,2*PI],y_range=[0,1.15,1],
                            x_length=4.6,y_length=1.9,tips=False,
                            axis_config={"color":MUTED,"include_ticks":False})
                       .move_to([x,.5,0]) for x in (-3.2,3.2)])
        headings = VGroup(Text("Real antenna response",font_size=25,color=PLANCK).move_to([-3.2,1.9,0]),
                         Text("Equivalent ideal beam",font_size=25,color=RJ).move_to([3.2,1.9,0]))
        ticks = VGroup()
        for ax in axes:
            ticks.add(MathTex("0",font_size=23).next_to(ax.c2p(0,0),DOWN,buff=.12),
                      MathTex(r"4\pi",font_size=23).next_to(ax.c2p(4*PI,0),DOWN,buff=.12),
                      MathTex("1",font_size=23).next_to(ax.c2p(0,1),LEFT,buff=.12))
        # Axisymmetric example: cumulative sky angle u=2*pi*(1-cos(theta));
        # hence du=dOmega after integrating azimuth. Shaded areas are in sr,
        # not the misleading area under a one-dimensional angular cut.
        width = 3.0*(1-np.exp(-4*PI/3.0))
        curve = axes[0].plot(lambda u:np.exp(-u/3.0),x_range=[0,4*PI,.03],color=PLANCK)
        fill = axes[0].get_area(curve,x_range=[0,4*PI],color=PLANCK,opacity=.3)
        ideal = Polygon(axes[1].c2p(0,0),axes[1].c2p(0,1),
                        axes[1].c2p(width,1),axes[1].c2p(width,0),
                        color=RJ,fill_opacity=.3)
        tail = Line(axes[1].c2p(width,0),axes[1].c2p(4*PI,0),color=RJ)
        omega_label = MathTex(r"\Omega_A",font_size=29,color=RJ).next_to(
            axes[1].c2p(width/2,0),DOWN,buff=.14)
        axis_note = Text("Enclosed solid angle from beam axis [sr] -- circularly symmetric example",
                         font_size=20,color=MUTED).move_to(DOWN*1.05)
        self.play(Create(axes),FadeIn(ticks),FadeIn(headings),FadeIn(axis_note))
        self.play(Create(curve),FadeIn(fill),run_time=2)
        self.play(TransformFromCopy(fill,ideal),Create(tail),run_time=3)
        self.play(Write(omega_label))
        meaning = Text("Full sensitivity inside the ideal beam, zero outside; same power from a uniform sky.",
                       font_size=23,color=FG).move_to(DOWN*1.8)
        if meaning.width>13:
            meaning.scale_to_fit_width(13)
        formula = MathTex(r"\underbrace{\int_{4\pi}p(\theta,\phi)\,d\Omega}_{\text{real beam}}"
                          r"=\underbrace{1\times\Omega_A}_{\text{ideal beam}}"
                          r"\quad\Longrightarrow\quad\Omega_A\equiv\int_{4\pi}p\,d\Omega\ [\mathrm{sr}]",
                          font_size=32,color=ACCENT).move_to(DOWN*2.8)
        if formula.width>13:
            formula.scale_to_fit_width(13)
        self.play(FadeIn(meaning))
        self.play(Write(formula),run_time=2)
        self.wait(2.5)
        self.clear_slide()

    def spatial_mode_explanation(self):
        self.start_slide("What one spatial mode means")
        self.play(FadeIn(self.title("One spatial mode: one field pattern, one receiver signal")))
        intro = Text("At each frequency, the antenna combines the field across its aperture.",
                     font_size=25,color=FG).move_to(UP*2.5)
        self.play(FadeIn(intro))
        positions = [np.array([-4.7,y,0]) for y in (1.7,1.15,.6,.05,-.5)]
        aperture = Line([-4.7,-.8,0],[-4.7,2,0],color=RADIO,stroke_width=6)
        samples = VGroup(*[Dot(pos,color=PLANCK,radius=.07) for pos in positions])
        summer = Circle(radius=.45,color=RADIO).move_to([.2,.6,0])
        sigma = MathTex(r"\Sigma",font_size=38,color=FG).move_to(summer)
        paths = VGroup(*[Arrow(pos+RIGHT*.13,[-.3,.6,0],buff=.08,
                              color=MUTED,stroke_width=2) for pos in positions])
        output = Arrow([.7,.6,0],[3.8,.6,0],buff=.05,color=RADIO)
        voltage = MathTex(r"v_\nu",font_size=45,color=RADIO).move_to([4.5,.6,0])
        labels = VGroup(
            Text("Field across aperture",font_size=23,color=PLANCK).move_to([-4.6,-1.2,0]),
            Text("Amplitude + phase weights",font_size=22,color=FG).move_to([-1.6,1.85,0]),
            Text("One receiver signal",font_size=23,color=RADIO).move_to([3.4,-.4,0]),
        )
        self.play(Create(aperture),FadeIn(samples),Create(paths),Create(summer),Write(sigma),FadeIn(labels))
        markers = VGroup(*[Dot(pos,color=PLANCK,radius=.07) for pos in positions])
        self.add(markers)
        self.play(*[m.animate.move_to(summer.get_center()) for m in markers],run_time=2)
        self.play(FadeOut(markers),GrowArrow(output),Write(voltage))
        formula = Text("One feed combines many aperture points into one voltage signal.",
                       font_size=26,color=FG).move_to(DOWN*1.95)
        explanation = Text("This particular spatial combination is one receiving mode; its weights determine the beam.",
                           font_size=22,color=FG).move_to(DOWN*2.7)
        distinction = Text("Not one ray or direction. Polarization is separate: here we select one field component.",
                           font_size=21,color=MUTED).move_to(DOWN*3.4)
        for text in (intro,formula,explanation,distinction):
            if text.width>13:
                text.scale_to_fit_width(13)
        self.play(Write(formula),FadeIn(explanation))
        self.play(FadeIn(distinction))
        self.wait(2.5)
        self.clear_slide()

    def area_beam_intuition(self):
        self.start_slide("Why area times solid angle is fixed")
        self.play(FadeIn(self.title("A larger antenna has a narrower beam")))
        introduction = MathTex(r"\Omega_A\ [\mathrm{sr}]:\ \text{the antenna's effective solid opening angle}",
                               font_size=30,color=PLANCK).move_to(UP*2.75)
        self.play(Write(introduction))
        terms = MathTex(
            r"D:\ \text{antenna diameter [m]}\qquad"
            r"\theta:\ \text{full beam opening in one plane [rad]}\qquad"
            r"\lambda:\ \text{wavelength [m]}",font_size=23,color=FG).move_to(UP*2.25)
        self.play(FadeIn(terms))
        scaling = MathTex(
            r"A_{\mathrm e}\propto D^2,\qquad"
            r"\theta\sim\frac{\lambda}{D},\qquad\Omega_A\sim\theta^2"
            r"\quad\text{(circular aperture)}",
            font_size=30, color=FG).move_to(UP*1.65)
        self.play(Write(scaling))
        origin = np.array([3.4, .3, 0])
        aperture = Ellipse(width=.45, height=1.0, color=RADIO, fill_opacity=.3).move_to(origin)
        beam = Polygon(origin, [-3.4, 1.0, 0], [-3.4, -.4, 0],
                       color=PLANCK, fill_opacity=.15)
        narrow = Polygon(origin, [-3.4, .65, 0], [-3.4, -.05, 0],
                         color=PLANCK, fill_opacity=.15)
        diameter = DoubleArrow([4.2,-.2,0],[4.2,.8,0],buff=0,color=RADIO)
        diameter_label = MathTex("D",font_size=30,color=RADIO).move_to([4.75,.3,0])
        half_angle = np.arctan(.7/6.8)
        opening = Arc(radius=2.7,start_angle=PI-half_angle,angle=2*half_angle,
                      arc_center=origin,color=PLANCK,stroke_width=3)
        theta_label = MathTex(r"\theta",font_size=30,color=PLANCK).move_to([.15,.3,0])
        area_label = MathTex(r"A_{\mathrm e}", font_size=35, color=RADIO).move_to([3.4,-.9,0])
        beam_label = MathTex(r"\Omega_A", font_size=35, color=PLANCK).move_to([-3.4,-.85,0])
        self.play(FadeIn(beam), Create(aperture), Write(area_label), Write(beam_label))
        self.play(Create(diameter),Write(diameter_label),Create(opening),Write(theta_label))
        self.wait(1)
        self.play(aperture.animate.scale(2), Transform(beam,narrow),
                  Transform(diameter,DoubleArrow([4.2,-.7,0],[4.2,1.3,0],buff=0,color=RADIO)),
                  Transform(diameter_label,MathTex("2D",font_size=30,color=RADIO).move_to(diameter_label)),
                  Transform(opening,Arc(radius=2.7,start_angle=PI-np.arctan(.35/6.8),
                                        angle=2*np.arctan(.35/6.8),arc_center=origin,color=PLANCK,stroke_width=3)),
                  Transform(theta_label,MathTex(r"\theta/2",font_size=30,color=PLANCK).move_to(theta_label)),
                  Transform(area_label,MathTex(r"4A_{\mathrm e}",font_size=35,color=RADIO).move_to(area_label)),
                  Transform(beam_label,MathTex(r"\Omega_A/4",font_size=35,color=PLANCK).move_to(beam_label)),
                  run_time=3)
        explanation = Text("Double the diameter: four times the area, half the beam opening in each plane, one quarter the solid angle.",
                           font_size=23,color=FG).move_to(DOWN*1.35)
        if explanation.width > 13:
            explanation.scale_to_fit_width(13)
        self.play(FadeIn(explanation))
        exact_label = Text("Diffraction sets this area--angle relation; we omit the detailed proof.",font_size=24,color=FG).move_to(DOWN*1.95)
        exact = MathTex(r"A_{\mathrm e}\Omega_A=\lambda^2",font_size=44,color=RJ).move_to(DOWN*2.7)
        self.play(FadeIn(exact_label),Write(exact))
        self.wait(2.5)
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

        self.receiver_view()
        self.area_beam_intuition()
        self.start_slide("Radiance becomes kBT per hertz")
        self.play(FadeIn(self.title("Now the factors cancel")))
        self.play(Write(equation(
            r"dP=\frac12\,B_\nu(T)\,A_{\mathrm e}\Omega_A\,d\nu",
            2.15, size=46)))
        self.play(Write(equation(
            r"B_\nu(T)\simeq\frac{2k_{\mathrm B}T}{\lambda^2}"
            r"\quad(h\nu\ll k_{\mathrm B}T),\qquad "
            r"A_{\mathrm e}\Omega_A=\lambda^2", .95, RJ, 39)))
        self.play(Write(equation(
            r"dP=\underbrace{\frac12}_{\text{one polarization}}"
            r"\underbrace{\frac{2k_{\mathrm B}T}{\lambda^2}}_{\text{radiance}}"
            r"\underbrace{\lambda^2}_{A_{\mathrm e}\Omega_A}\,d\nu",
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
            VGroup(MathTex(r"1", font_size=31, color=ACCENT), Text("ideal antenna, matched receiver", font_size=28, color=FG)),
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
            Text("Planck gives the thermal radiation spectrum", font_size=30, color=PLANCK),
            Text("The antenna receives nearly constant power per hertz in the radio limit", font_size=30, color=RADIO),
        ).arrange(DOWN, buff=0.18).to_edge(DOWN, buff=0.42)

        self.play(FadeIn(title), Write(exact), FadeIn(limit_arrow))
        self.play(LaggedStart(*[FadeIn(row, shift=0.15 * RIGHT) for row in assumptions], lag_ratio=0.18))
        self.play(FadeIn(example_group, shift=0.2 * UP))
        self.play(FadeIn(takeaway))
        self.wait(2.5)
