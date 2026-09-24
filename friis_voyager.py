"""Manim presentation: diffraction, antenna gain, Friis, and Voyager SNR.

Preview:
    conda run -n base manim -pql friis_voyager.py FriisVoyager

Final render:
    conda run -n base manim -r 1920,1080 --fps 30 friis_voyager.py FriisVoyager
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from scipy.special import j1
from manim import *
from manim_slides import Slide


BG = "#07111F"
FG = "#F3F7FA"
MUTED = "#9DB0C3"
GOLD = "#F3D35A"
SIGNAL = "#74A9FF"
APERTURE = "#45C2B1"
POWER = "#F5A65B"
RED = "#FF6B6B"
GREEN = "#7BD88F"

SHOW_PROVENANCE = os.getenv("SHOW_PROVENANCE", "0") == "1"
ASSET_DIR = Path(__file__).resolve().parent / "assets"
VOYAGER_IMAGE = ASSET_DIR / "voyager_spacecraft.png"
GOLDSTONE_IMAGE = ASSET_DIR / "dss14_goldstone.png"


class FriisVoyager(Slide):
    """Derive the Friis equation and apply it to a Voyager 1 link."""

    def setup(self):
        self._slide_started = False
        self._clear_pending = False
        self.camera.background_color = ManimColor(BG)
        self.provenance = Text(
            "Source: friis_voyager.py", font_size=15, color=MUTED
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
        heading = Text(text, font_size=44, weight=SEMIBOLD, color=FG)
        if heading.width > 13.1:
            heading.scale_to_fit_width(13.1)
        return heading.to_edge(UP, buff=0.30)

    def clear_slide(self):
        self._clear_pending = True

    def _flush_pending_clear(self):
        if not self._clear_pending:
            return
        self._clear_pending = False
        keep = {self.provenance} if SHOW_PROVENANCE else set()
        removable = [mob for mob in self.mobjects if mob not in keep]
        if removable:
            self.play(
                *[FadeOut(mob, shift=0.08 * DOWN) for mob in removable],
                run_time=0.70,
            )

    def construct(self):
        self.opening_question()
        self.inverse_square_spreading()
        self.antenna_gain()
        self.receiver_collection()
        self.lambda_over_d()
        self.area_wavelength_gain()
        self.friis_derivation()
        self.voyager_link_budget()
        self.noise_and_snr()
        self.shannon_capacity()
        self.voyager_capacity()
        self.close()

    def voyager_icon(self) -> VGroup:
        dish = Arc(
            radius=0.66,
            start_angle=-0.74 * PI,
            angle=1.48 * PI,
            color=GOLD,
            stroke_width=6,
        ).rotate(PI)
        feed = Dot(dish.get_center() + RIGHT * 0.22, radius=0.06, color=GOLD)
        boom = Line(dish.get_center() + RIGHT * 0.15, RIGHT * 0.82, color=GOLD, stroke_width=4)
        bus = Rectangle(width=0.58, height=0.38, color=POWER, fill_opacity=0.24).next_to(
            boom, RIGHT, buff=0
        )
        return VGroup(dish, feed, boom, bus)

    def earth_icon(self) -> VGroup:
        globe = Circle(radius=0.78, color=SIGNAL, fill_color=SIGNAL, fill_opacity=0.15)
        equator = Ellipse(width=1.48, height=0.43, color=SIGNAL, stroke_opacity=0.65)
        meridian = Ellipse(width=0.55, height=1.48, color=SIGNAL, stroke_opacity=0.65)
        return VGroup(globe, equator, meridian)

    def antenna_icon(self, color=APERTURE) -> VGroup:
        top_left = np.array([-0.62, 0.54, 0.0])
        top_right = np.array([0.62, 0.54, 0.0])
        top_mid = np.array([0.0, 0.54, 0.0])
        vertex = np.array([0.0, -0.34, 0.0])
        mast_bottom = np.array([0.0, -0.98, 0.0])
        return VGroup(
            Line(top_left, top_right, color=color, stroke_width=6),
            Line(top_left, vertex, color=color, stroke_width=6),
            Line(top_right, vertex, color=color, stroke_width=6),
            Line(top_mid, vertex, color=color, stroke_width=6),
            Line(vertex, mast_bottom, color=color, stroke_width=6),
        )

    def opening_question(self):
        self.start_slide("Voyager question")

        voyager = ImageMobject(str(VOYAGER_IMAGE)).set(width=3.25).move_to(LEFT * 4.85 + UP * 0.72)
        earth = ImageMobject(str(GOLDSTONE_IMAGE)).set(height=2.65).move_to(RIGHT * 4.85 + UP * 0.72)
        voyager_frame = SurroundingRectangle(voyager, buff=0.05, color=GOLD, stroke_width=2)
        earth_frame = SurroundingRectangle(earth, buff=0.05, color=SIGNAL, stroke_width=2)
        path_start = voyager.get_right() + RIGHT * 0.25
        path_end = earth.get_left() + LEFT * 0.25
        path = DashedLine(
            path_start,
            path_end,
            color=SIGNAL,
            stroke_width=3,
            dash_length=0.16,
        )
        pulses = VGroup(
            *[
                Dot(path_start + p * (path_end - path_start), radius=0.055, color=SIGNAL)
                for p in (0.12, 0.31, 0.50, 0.69, 0.88)
            ]
        )
        voyager_label = Text("Voyager 1 high-gain antenna", font_size=25, color=GOLD).next_to(voyager, DOWN, buff=0.18)
        earth_label = Text("DSS-14, Goldstone (70 m)", font_size=25, color=SIGNAL).next_to(earth, DOWN, buff=0.18)
        distance = MathTex(
            r"R\approx171.8\,\mathrm{AU}\approx25.7\times10^{12}\,\mathrm m",
            r"\\[5pt]t_{\rm one\ way}\approx23.8\,\mathrm h",
            font_size=31,
            color=MUTED,
        ).next_to(path, UP, buff=0.34)
        question = Text(
            "What is the SNR of the Voyager 1 to Earth radio link?",
            font_size=42,
            weight=SEMIBOLD,
            color=FG,
            t2c={"SNR": POWER, "Voyager 1": GOLD, "Earth": SIGNAL},
        ).shift(DOWN * 1.90)
        data_question = Text(
            "How much data can be sent between the spacecraft and Earth?",
            font_size=36,
            weight=SEMIBOLD,
            color=FG,
            t2c={"data": GOLD, "Earth": SIGNAL},
        ).next_to(question, DOWN, buff=0.40)
        self.play(FadeIn(voyager), Create(voyager_frame), FadeIn(earth), Create(earth_frame))
        self.play(Create(path), LaggedStart(*[FadeIn(p) for p in pulses], lag_ratio=0.12))
        self.play(FadeIn(voyager_label), FadeIn(earth_label), Write(distance))
        self.play(FadeIn(question, shift=0.18 * UP))
        self.play(FadeIn(data_question, shift=0.18 * UP))
        self.wait(2.5)
        self.clear_slide()

    def inverse_square_spreading(self):
        self.start_slide("Inverse-square spreading")

        title = self.title("Power spreads over a sphere")
        source = Dot(LEFT * 3.9 + DOWN * 0.15, radius=0.14, color=POWER)
        source_label = MathTex(r"P_{\rm t}", font_size=35, color=POWER).next_to(
            source, DOWN, buff=0.26
        )
        wavefronts = VGroup(
            *[
                Arc(
                    radius=r,
                    start_angle=-0.42 * PI,
                    angle=0.84 * PI,
                    arc_center=source.get_center(),
                    color=SIGNAL,
                    stroke_opacity=0.28 + 0.12 * i,
                    stroke_width=3,
                )
                for i, r in enumerate((0.8, 1.55, 2.3, 3.05))
            ]
        )
        receiver = self.antenna_icon().scale(0.70).move_to(RIGHT * 3.95 + DOWN * 0.15)
        radius_line = DoubleArrow(
            source.get_center() + DOWN * 1.7,
            receiver.get_center() + DOWN * 1.7,
            buff=0,
            color=MUTED,
            stroke_width=2.5,
            tip_length=0.18,
        )
        radius_label = MathTex(r"R", font_size=36, color=MUTED).next_to(radius_line, DOWN, buff=0.10)

        statement = MathTex(
            r"S_{\rm iso}(R)=\frac{P_{\rm t}}{4\pi R^2}",
            r"\quad[\mathrm{W\,m^{-2}}]",
            font_size=50,
        ).shift(UP * 1.90)
        statement[0].set_color(POWER)
        statement[1].set_color(MUTED)
        note = Text(
            "The same transmitted power crosses every sphere; its area is 4πR²",
            font_size=26,
            color=MUTED,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title), FadeIn(source), FadeIn(source_label), FadeIn(receiver))
        self.play(LaggedStart(*[Create(w) for w in wavefronts], lag_ratio=0.18), run_time=1.6)
        self.play(Create(radius_line), FadeIn(radius_label))
        self.play(Write(statement))
        self.play(FadeIn(note))
        self.wait(2.0)
        self.clear_slide()

    def antenna_gain(self):
        self.start_slide("Antenna gain")

        title = self.title("An antenna focuses power into a direction")

        isotropic_source = Dot(LEFT * 3.75 + UP * 0.75, radius=0.12, color=POWER)
        isotropic_waves = VGroup(
            *[
                Circle(
                    radius=r,
                    color=SIGNAL,
                    stroke_opacity=0.55 - 0.09 * i,
                    stroke_width=3,
                ).move_to(isotropic_source)
                for i, r in enumerate((0.45, 0.85, 1.25))
            ]
        )
        isotropic_label = Text("isotropic radiator", font_size=27, color=MUTED).next_to(
            isotropic_waves, DOWN, buff=0.20
        )

        # Side view of a paraboloid opening toward the transmitted beam (+x).
        vertex = RIGHT * 2.70 + UP * 0.75
        focal_length = 0.50
        dish = ParametricFunction(
            lambda y: vertex + np.array([y * y / (4 * focal_length), y, 0]),
            t_range=[-0.85, 0.85],
            color=POWER,
            stroke_width=7,
        )
        focus = vertex + RIGHT * focal_length
        feed = Dot(focus, radius=0.07, color=GOLD)
        supports = VGroup(
            Line(dish.get_start(), focus, color=MUTED, stroke_width=2),
            Line(dish.get_end(), focus, color=MUTED, stroke_width=2),
        )
        pedestal = VGroup(
            Line(vertex + LEFT * 0.10, vertex + LEFT * 0.10 + DOWN * 1.02,
                 color=POWER, stroke_width=5),
            Line(vertex + LEFT * 0.38 + DOWN * 1.02,
                 vertex + RIGHT * 0.18 + DOWN * 1.02,
                 color=POWER, stroke_width=5),
        )
        antenna = VGroup(pedestal, dish, supports, feed)
        beam = Polygon(
            focus + RIGHT * 0.10,
            RIGHT * 6.15 + UP * 1.70,
            RIGHT * 6.15 + DOWN * 0.20,
            color=SIGNAL,
            fill_color=SIGNAL,
            fill_opacity=0.15,
            stroke_opacity=0.65,
        )
        beam.set_z_index(-1)
        antenna_label = Text("parabolic dish", font_size=27, color=POWER).next_to(
            antenna, DOWN, buff=0.28
        )

        definition = MathTex(
            r"\underbrace{G(\theta,\phi)}_{\text{antenna gain}}\equiv"
            r"\frac{S(\theta,\phi)}{P_{\rm t}/(4\pi R^2)}",
            font_size=43,
            color=GOLD,
        ).shift(DOWN * 1.05)
        flux = MathTex(
            r"S(\theta,\phi)=\frac{P_{\rm t}G(\theta,\phi)}{4\pi R^2}",
            font_size=42,
            color=FG,
        ).next_to(definition, DOWN, buff=0.22)
        units = VGroup(
            MathTex(
                r"G\ \text{is dimensionless},\qquad G_{\mathrm{dBi}}=10\log_{10}G",
                font_size=29, color=MUTED,
            ),
            Text(
                'dBi = decibels relative to isotropic; "i" means isotropic',
                font_size=25, color=FG,
            ),
            MathTex(
                r"G=1\ \Longleftrightarrow\ 0\,\mathrm{dBi}"
                r"\qquad G=10\ \Longleftrightarrow\ 10\,\mathrm{dBi}",
                font_size=27, color=GOLD,
            ),
        ).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.22)

        # Leave a clear band between the antenna captions and the gain equation.
        for visual in (isotropic_source, isotropic_waves, isotropic_label,
                       antenna, antenna_label, beam):
            visual.shift(UP * 0.50)
        definition.move_to(DOWN * 1.15)

        self.play(FadeIn(title))
        self.play(FadeIn(isotropic_source), LaggedStart(*[Create(w) for w in isotropic_waves], lag_ratio=0.15))
        self.play(FadeIn(isotropic_label))
        self.play(FadeIn(antenna), FadeIn(antenna_label), FadeIn(beam))
        self.play(Write(definition))
        self.play(FadeIn(units))
        self.wait(2.2)
        self.clear_slide()

    def receiver_collection(self):
        self.start_slide("Receiver collection")

        title = self.title("One antenna transmits and another collects")
        tx = self.antenna_icon(POWER).scale(0.78).move_to(LEFT * 5.0 + UP * 0.65)
        # Projected collecting aperture, normal to the incident power flow.
        # This represents effective area, not necessarily the physical dish area.
        aperture_center = RIGHT * 2.80 + UP * 0.65
        rx = Polygon(
            aperture_center + np.array([-0.40, -1.00, 0]),
            aperture_center + np.array([0.40, -0.65, 0]),
            aperture_center + np.array([0.40, 1.00, 0]),
            aperture_center + np.array([-0.40, 0.65, 0]),
            color=APERTURE, stroke_width=4,
            fill_color=APERTURE, fill_opacity=0.28,
        )
        link = DoubleArrow(
            [-4.75, 2.20, 0], [2.80, 2.20, 0],
            buff=0, color=MUTED, stroke_width=2,
        )
        incoming = VGroup(*[
            Arrow([-1.80, 0.65 + y, 0], [2.80, 0.65 + y, 0],
                  buff=0, color=SIGNAL, stroke_width=3,
                  max_tip_length_to_length_ratio=0.045)
            for y in (-0.60, -0.20, 0.20, 0.60)
        ])
        poynting_label = VGroup(
            Text("incident Poynting flux", font_size=25, color=SIGNAL),
            MathTex(r"\langle\mathbf S\rangle\ [\mathrm{W\,m^{-2}}]",
                    font_size=29, color=SIGNAL),
        ).arrange(DOWN, buff=0.10).move_to(LEFT * 0.20 + UP * 1.63)
        receiver_box = RoundedRectangle(
            width=1.65, height=0.85, corner_radius=0.10,
            color=APERTURE, stroke_width=2,
        ).move_to(RIGHT * 5.30 + UP * 0.65)
        receiver_text = Text("receiver", font_size=25, color=APERTURE).move_to(receiver_box)
        power_arrow = Arrow(rx.get_right(), receiver_box.get_left(),
                            buff=0.12, color=GOLD, stroke_width=5)
        received_label = MathTex(r"P_{\rm r}\ [\mathrm W]", font_size=30,
                                 color=GOLD).next_to(power_arrow, UP, buff=0.15)
        r_label = MathTex(r"R", font_size=36, color=MUTED).next_to(link, UP, buff=0.16)
        tx_label = MathTex(r"P_{\rm t},\ G_{\rm t}", font_size=34, color=POWER).next_to(
            tx, DOWN, buff=0.24
        )
        rx_label = MathTex(r"A_{\mathrm{e,r}}", font_size=34, color=APERTURE).next_to(
            rx, DOWN, buff=0.24
        )

        flux = MathTex(
            r"S(R)=\frac{P_{\rm t}G_{\rm t}}{4\pi R^2}",
            r"\quad[\mathrm{W\,m^{-2}}]",
            font_size=44,
        ).shift(DOWN * 1.25)
        flux[0].set_color(POWER)
        flux[1].set_color(MUTED)
        collected = MathTex(
            r"P_{\rm r}=S(R)A_{\mathrm{e,r}}"
            r"=\frac{P_{\rm t}G_{\rm t}A_{\mathrm{e,r}}}{4\pi R^2}",
            font_size=49,
            color=GOLD,
        ).next_to(flux, DOWN, buff=0.40)
        area_definition = MathTex(
            r"A_{\mathrm{e,r}}\,[\mathrm{m^2}]:\ "
            r"\text{effective collecting area of the receiving antenna}",
            font_size=30,
            color=MUTED,
        ).to_edge(DOWN, buff=0.30)

        self.play(FadeIn(title), FadeIn(tx), FadeIn(rx), GrowArrow(link))
        self.play(FadeIn(r_label), FadeIn(tx_label), FadeIn(rx_label))
        self.play(FadeIn(poynting_label),
                  LaggedStart(*[GrowArrow(a) for a in incoming], lag_ratio=0.15))
        self.play(Indicate(rx, color=GOLD), FadeIn(receiver_box), FadeIn(receiver_text))
        self.play(GrowArrow(power_arrow), FadeIn(received_label))
        self.play(Write(flux))
        self.play(Write(collected))
        self.play(FadeIn(area_definition))
        self.wait(2.3)
        self.clear_slide()

    def aperture_equations(self, rows, center=ORIGIN, font_size=36):
        """Reveal a short derivation one line at a time, with bounded width."""
        group = VGroup(*[
            MathTex(row, font_size=font_size, color=FG) for row in rows
        ]).arrange(DOWN, buff=0.30).move_to(center)
        if group.width > 12.4:
            group.scale_to_fit_width(12.4)
        for row in group:
            self.play(Write(row))
            self.wait(0.65)
        return group

    def lambda_over_d(self):
        self.start_slide("Plane wave across a linear aperture")
        title = self.title("An oblique plane wave arrives with a phase gradient")
        center = LEFT * 3.3 + UP * 0.35
        aperture = Line(center + DOWN * 1.35, center + UP * 1.35,
                        color=APERTURE, stroke_width=8)
        brace = Brace(aperture, LEFT, color=APERTURE)
        length = MathTex(r"L\ [\mathrm m]", font_size=32, color=APERTURE).next_to(brace, LEFT)
        normal = DashedLine(center + LEFT * 2.5, center + RIGHT * 1.4, color=MUTED)
        theta = 25 * DEGREES
        direction = np.array([np.cos(theta), np.sin(theta), 0])
        tangent = np.array([-np.sin(theta), np.cos(theta), 0])
        fronts = VGroup(*[
            Line(center - direction * d - tangent * 1.30,
                 center - direction * d + tangent * 1.30,
                 color=SIGNAL, stroke_width=2)
            for d in (0.5, 1.15, 1.8)
        ])
        arrival = Arrow(center - 2.4 * direction, center, buff=0,
                        color=GOLD, stroke_width=4)
        angle = Arc(radius=0.80, start_angle=PI, angle=theta,
                    arc_center=center, color=GOLD)
        theta_label = MathTex(r"\theta", font_size=30, color=GOLD).move_to(
            center + np.array([-1.02, -0.20, 0]))
        x_label = MathTex(r"x", font_size=32, color=APERTURE).next_to(aperture, UP)
        caption = Text("Receive with equal weights and equal cable delays",
                       font_size=25, color=MUTED).to_edge(DOWN, buff=0.48)
        self.play(FadeIn(title), Create(aperture), GrowFromCenter(brace),
                  FadeIn(length), Create(normal), FadeIn(x_label))
        self.play(LaggedStart(*[Create(f) for f in fronts], lag_ratio=0.20),
                  GrowArrow(arrival), Create(angle), FadeIn(theta_label))
        self.play(fronts.animate.shift(0.35 * direction), run_time=1.2)
        self.aperture_equations([
            r"k=\frac{2\pi}{\lambda}\quad[\mathrm{rad\,m^{-1}}]",
            r"\widetilde E(x,\theta)=E_0e^{ikx\sin\theta}",
            r"\Delta\varphi=kL\sin\theta",
            r"\theta=0:\quad\text{all contributions in phase}",
        ], center=RIGHT * 3.15 + UP * 0.10, font_size=32)
        self.play(FadeIn(caption))
        self.wait(2.5)
        self.clear_slide()

        self.start_slide("Integrate the received electric field")
        self.play(FadeIn(self.title("Sum the electric-field phasors across the aperture")))
        self.aperture_equations([
            r"V(\theta)\propto\int_{-L/2}^{L/2}\widetilde E(x,\theta)\,dx"
            r"\qquad \widetilde E\ [\mathrm{V\,m^{-1}}],\quad dx\ [\mathrm m]",
            r"F(\theta)\equiv\frac{V(\theta)}{V(0)}"
            r"=\frac{1}{L}\int_{-L/2}^{L/2}e^{ikx\sin\theta}\,dx",
            r"F(\theta)=\frac{e^{ikL\sin\theta/2}-e^{-ikL\sin\theta/2}}{ikL\sin\theta}",
            r"F(\theta)=\frac{\sin u}{u}=\operatorname{sinc}u"
            r"\qquad u=\frac{\pi L}{\lambda}\sin\theta",
            r"\theta\ll1:\quad \sin\theta\simeq\theta,\quad "
            r"F(\theta)\simeq\operatorname{sinc}\!\left(\frac{\pi L\theta}{\lambda}\right)",
        ], center=DOWN * 0.15, font_size=35)
        note = Text("sinc(u) = sin(u)/u; sinc(0) = 1. Angles in radians.",
                    font_size=25, color=GOLD).to_edge(DOWN, buff=0.34)
        self.play(FadeIn(note))
        self.wait(3)
        self.clear_slide()

        self.start_slide("Square the field to obtain the power pattern")
        self.play(FadeIn(self.title("Coherent field addition gives a sinc-squared power pattern")))
        axes = Axes(x_range=[-3, 3, 1], y_range=[-0.3, 1.1, 0.5],
                    x_length=7.2, y_length=3.2,
                    axis_config={"color": MUTED, "include_numbers": True,
                                 "font_size": 20}, tips=False).shift(LEFT * 2.7 + UP * 0.30)
        field = axes.plot(lambda q: np.sinc(q), x_range=[-3, 3, 0.015],
                          color=SIGNAL, stroke_width=3)
        power = axes.plot(lambda q: np.sinc(q) ** 2, x_range=[-3, 3, 0.015],
                          color=POWER, stroke_width=4)
        x_label = MathTex(r"q=L\theta/\lambda\quad[1]", font_size=27).next_to(axes, DOWN)
        legend = VGroup(Text("field F", font_size=24, color=SIGNAL),
                        Text("power |F|²", font_size=24, color=POWER)).arrange(
                            RIGHT, buff=0.55).next_to(axes, UP, buff=0.20)
        self.play(Create(axes), FadeIn(x_label), FadeIn(legend))
        self.play(Create(field))
        self.play(TransformFromCopy(field, power))
        self.aperture_equations([
            r"p(\theta)=|F(\theta)|^2",
            r"G(\theta)=G(0)\,p(\theta)",
            r"p(0)=1,\quad p(\theta)\geq0",
        ], center=RIGHT * 4.35 + UP * 0.35, font_size=31)
        self.aperture_equations([
            r"\sin\theta_{\rm null}=\frac{\lambda}{L}"
            r"\quad\Longrightarrow\quad\theta_{\rm null}\simeq\frac{\lambda}{L}",
            r"\text{full half-power beamwidth}\simeq0.886\,\frac{\lambda}{L}\quad[\mathrm{rad}]",
        ], center=DOWN * 2.60, font_size=32)
        self.wait(3)
        self.clear_slide()

        self.start_slide("Two-dimensional rectangular aperture")
        self.play(FadeIn(self.title("An asymmetric aperture needs two angular coordinates")))
        angle_definitions = MathTex(
            r"\theta:\ \text{angle from aperture normal},\quad "
            r"\phi:\ \text{azimuth about the normal}\quad[\mathrm{rad}]",
            font_size=25, color=MUTED,
        ).move_to(UP * 2.65)
        self.play(FadeIn(angle_definitions))
        rectangle = Rectangle(width=3.0, height=1.4, color=APERTURE,
                              fill_color=APERTURE, fill_opacity=0.15).move_to(LEFT * 4.65 + UP * 0.7)
        lx = MathTex(r"L_x\ [\mathrm m]", font_size=28).next_to(rectangle, DOWN)
        ly = MathTex(r"L_y", font_size=28).next_to(rectangle, LEFT)
        self.play(Create(rectangle), FadeIn(lx), FadeIn(ly))
        self.aperture_equations([
            r"\alpha=\sin\theta\cos\phi,\quad\beta=\sin\theta\sin\phi",
            r"F(\alpha,\beta)=\frac{1}{L_xL_y}\iint_A"
            r"e^{ik(\alpha x+\beta y)}\,dx\,dy",
            r"F=\operatorname{sinc}\!\left(\frac{\pi L_x\alpha}{\lambda}\right)"
            r"\operatorname{sinc}\!\left(\frac{\pi L_y\beta}{\lambda}\right)",
            r"p(\theta,\phi)=|F(\alpha,\beta)|^2",
        ], center=RIGHT * 1.55 + UP * 0.40, font_size=30)
        # Display unequal principal cuts: double the aperture dimension halves the width.
        axes = Axes(x_range=[-2, 2, 1], y_range=[0, 1, 0.5],
                    x_length=5.3, y_length=1.45,
                    axis_config={"color": MUTED, "include_numbers": True,
                                 "font_size": 18}, tips=False).move_to(LEFT * 3.6 + DOWN * 2.15)
        cuts = VGroup(
            axes.plot(lambda q: np.sinc(2*q)**2, x_range=[-2, 2, 0.01], color=APERTURE),
            axes.plot(lambda q: np.sinc(q)**2, x_range=[-2, 2, 0.01], color=SIGNAL),
        )
        cut_label = MathTex(r"L_y\theta/\lambda\quad[1]", font_size=22).next_to(axes, DOWN, buff=0.10)
        labels = VGroup(
            Text("Example: Lx = 2 Ly", font_size=25, color=FG),
            Text("x cut: narrower beam", font_size=24, color=APERTURE),
            Text("y cut: wider beam", font_size=24, color=SIGNAL),
            MathTex(r"\theta_{x,\rm null}\simeq\lambda/L_x,\quad "
                    r"\theta_{y,\rm null}\simeq\lambda/L_y", font_size=27),
        ).arrange(DOWN, buff=0.15).move_to(RIGHT * 3.1 + DOWN * 2.15)
        self.play(Create(axes), FadeIn(cut_label), Create(cuts), FadeIn(labels))
        self.wait(3)
        self.clear_slide()

        self.start_slide("Circular aperture and the Airy pattern")
        self.play(FadeIn(self.title("A circular aperture gives the Airy diffraction pattern")))
        disk = Circle(radius=0.8, color=APERTURE, fill_color=APERTURE,
                      fill_opacity=0.20).move_to(LEFT * 5.1 + UP * 1.2)
        diameter = DoubleArrow(disk.get_left(), disk.get_right(), buff=0,
                               color=GOLD, stroke_width=2)
        d_label = MathTex(r"D=2a", font_size=27).next_to(disk, DOWN)
        self.play(Create(disk), GrowArrow(diameter), FadeIn(d_label))
        self.aperture_equations([
            r"F(\theta)=\frac{1}{\pi a^2}\int_0^a\!\!\int_0^{2\pi}"
            r"e^{ikr\sin\theta\cos\psi}\,r\,d\psi\,dr",
            r"F(\theta)=\frac{2}{a^2}\int_0^a rJ_0(kr\sin\theta)\,dr"
            r"=\frac{2J_1(u)}{u}",
            r"u=\frac{\pi D}{\lambda}\sin\theta,\qquad "
            r"p(\theta)=\left[\frac{2J_1(u)}{u}\right]^2",
        ], center=RIGHT * 1.2 + UP * 1.05, font_size=30)
        axes = Axes(x_range=[-3, 3, 1], y_range=[0, 1, 0.5],
                    x_length=6.2, y_length=1.7,
                    axis_config={"color": MUTED, "include_numbers": True,
                                 "font_size": 18}, tips=False).move_to(LEFT * 3.25 + DOWN * 1.75)
        def airy(q):
            u = PI * q
            return 1.0 if abs(u) < 1e-8 else (2 * j1(u) / u) ** 2
        curves = VGroup(
            axes.plot(lambda q: np.sinc(q)**2, x_range=[-3, 3, 0.015], color=SIGNAL),
            axes.plot(airy, x_range=[-3, 3, 0.015], color=GOLD),
        )
        labels = VGroup(
            Text("linear aperture: sinc²", font_size=24, color=SIGNAL),
            Text("circular aperture: Airy", font_size=24, color=GOLD),
            MathTex(r"\theta_{\rm null}\simeq1.22\,\lambda/D", font_size=30),
            MathTex(r"\text{full HPBW}\simeq1.03\,\lambda/D", font_size=28),
        ).arrange(DOWN, buff=0.18).move_to(RIGHT * 3.8 + DOWN * 1.75)
        x_label = MathTex(r"D\theta/\lambda\quad[1]", font_size=23).next_to(axes, DOWN, buff=0.08)
        self.play(Create(axes), Create(curves), FadeIn(labels), FadeIn(x_label))
        note = MathTex(
            r"J_0,J_1:\ \text{Bessel functions};\quad "
            r"\text{HPBW: half-power beamwidth (radians)}",
            font_size=24, color=MUTED,
        ).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(note))
        self.wait(3)
        self.clear_slide()

    def area_wavelength_gain(self):
        self.start_slide("Beam solid angle and antenna gain")
        self.play(FadeIn(self.title("Integrate the whole two-angle power pattern")))
        self.aperture_equations([
            r"p(\theta,\phi)=G(\theta,\phi)/G_{\max},\qquad p_{\max}=1",
            r"\Omega_A=\int_{4\pi}p(\theta,\phi)\,d\Omega"
            r"=\int_0^{2\pi}\!\!\int_0^\pi p(\theta,\phi)\sin\theta\,d\theta\,d\phi",
            r"\mathcal D_{\max}=\frac{4\pi}{\Omega_A},\qquad "
            r"G_{\max}=\eta_{\rm rad}\mathcal D_{\max}",
            r"\text{narrow rectangular beam:}\quad "
            r"\Omega_A\simeq\iint\operatorname{sinc}^2\!\left(\frac{\pi L_x\alpha}{\lambda}\right)"
            r"\operatorname{sinc}^2\!\left(\frac{\pi L_y\beta}{\lambda}\right)d\alpha\,d\beta",
            r"\int_{-\infty}^{\infty}\operatorname{sinc}^2(\pi L_x\alpha/\lambda)\,d\alpha"
            r"=\lambda/L_x\quad\Longrightarrow\quad\Omega_A\simeq\lambda^2/(L_xL_y)",
        ], center=UP * 0.05, font_size=32)
        note = VGroup(
            MathTex(r"\Omega_A\ [\mathrm{sr}],\quad\mathcal D:\ \text{directivity},\quad "
                    r"\eta_{\rm rad}=P_{\rm radiated}/P_{\rm accepted}\ [1]", font_size=27),
            Text("Exact integral: all lobes. Narrow-beam estimate: large, uniformly illuminated, forward aperture.",
                 font_size=22, color=MUTED),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.32)
        self.play(FadeIn(note))
        self.wait(3)
        self.clear_slide()

        self.start_slide("Effective aperture and wavelength")
        self.play(FadeIn(self.title("Effective aperture connects receiving area to gain")))
        self.aperture_equations([
            r"\text{reciprocal, polarization-matched antenna:}\qquad "
            r"\boxed{A_{\rm e}(\theta,\phi)=\frac{\lambda^2}{4\pi}G(\theta,\phi)}",
            r"P_{\rm r}=S\,A_{\rm e}(\theta,\phi),\qquad "
            r"G(\theta,\phi)=G_{\max}p(\theta,\phi)",
            r"A_{\mathrm{e},\max}=\eta_{\rm ap}A_{\rm physical}"
            r"\quad\Longrightarrow\quad G_{\max}=\frac{4\pi\eta_{\rm ap}A_{\rm physical}}{\lambda^2}",
            r"\text{circular dish:}\quad A_{\rm physical}=\pi D^2/4,\qquad "
            r"G_{\max}=\eta_{\rm ap}(\pi D/\lambda)^2",
            r"A_{\mathrm{e},\max}\Omega_A=\eta_{\rm rad}\lambda^2"
            r"\quad\xrightarrow{\ \eta_{\rm rad}=1\ }\quad\lambda^2",
        ], center=UP * 0.05, font_size=32)
        definitions = VGroup(
            MathTex(r"A_{\rm e},A_{\rm physical}\ [\mathrm{m^2}],\quad "
                    r"\lambda,D\ [\mathrm m],\quad G,\eta_{\rm ap}\ [1]", font_size=27),
            Text("Aperture efficiency includes illumination and losses; received power assumes a matched load.",
                 font_size=23, color=MUTED),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.32)
        self.play(FadeIn(definitions))
        self.wait(3)
        self.clear_slide()

    def friis_derivation(self):
        self.start_slide("Friis derivation")

        title = self.title("Friis transmission equation")
        tx = self.antenna_icon(POWER).scale(0.68).move_to(LEFT * 5.0 + UP * 1.15)
        rx = self.antenna_icon(APERTURE).scale(0.68).move_to(RIGHT * 5.0 + UP * 1.15)
        link = Arrow(tx.get_right() + RIGHT * 0.2, rx.get_left() + LEFT * 0.2, color=SIGNAL, stroke_width=4, buff=0)
        r_label = MathTex(r"R", font_size=34, color=MUTED).next_to(link, UP, buff=0.16)
        tx_label = MathTex(r"P_{\rm t},\ G_{\rm t}", font_size=30, color=POWER).next_to(tx, DOWN, buff=0.18)
        rx_label = MathTex(r"A_{\mathrm{e,r}},\ G_{\rm r}", font_size=30, color=APERTURE).next_to(rx, DOWN, buff=0.18)

        flux = MathTex(
            r"S=\frac{P_{\rm t}G_{\rm t}}{4\pi R^2}",
            font_size=42,
            color=POWER,
        ).shift(LEFT * 3.7 + DOWN * 0.55)
        collected = MathTex(
            r"P_{\rm r}=S A_{\mathrm{e,r}}",
            font_size=42,
            color=APERTURE,
        ).shift(DOWN * 0.55)
        aperture_gain = MathTex(
            r"A_{\mathrm{e,r}}=\frac{G_{\rm r}\lambda^2}{4\pi}",
            font_size=42,
            color=SIGNAL,
        ).shift(RIGHT * 3.85 + DOWN * 0.55)
        answer = MathTex(
            r"P_{\rm r}=P_{\rm t}G_{\rm t}G_{\rm r}"
            r"\left(\frac{\lambda}{4\pi R}\right)^2",
            font_size=55,
            color=GOLD,
        ).shift(DOWN * 2.0)
        box = SurroundingRectangle(answer, buff=0.26, color=GOLD, corner_radius=0.11)
        left_definitions = MathTex(
            r"\begin{aligned}"
            r"P_{\rm t}&:\ \text{transmitted power}\quad[\mathrm W]\\"
            r"P_{\rm r}&:\ \text{received power}\quad[\mathrm W]\\"
            r"G_{\rm t}&:\ \text{transmit gain}\quad[1]"
            r"\end{aligned}",
            font_size=31,
            color=FG,
        )
        right_definitions = MathTex(
            r"\begin{aligned}"
            r"G_{\rm r}&:\ \text{receive gain}\quad[1]\\"
            r"R&:\ \text{antenna separation}\quad[\mathrm m]\\"
            r"\lambda&:\ \text{wavelength}\quad[\mathrm m]"
            r"\end{aligned}",
            font_size=31,
            color=FG,
        )
        definitions = VGroup(left_definitions, right_definitions).arrange(
            RIGHT, aligned_edge=UP, buff=1.15
        ).shift(DOWN * 0.70)
        assumptions = Text(
            "Free space, far field, aligned polarization, and matched impedances",
            font_size=24,
            color=MUTED,
        ).to_edge(DOWN, buff=0.32)

        self.play(FadeIn(title), FadeIn(tx), FadeIn(rx), GrowArrow(link))
        self.play(FadeIn(r_label), FadeIn(tx_label), FadeIn(rx_label))
        self.play(Write(flux), Write(collected), Write(aperture_gain))
        self.play(TransformFromCopy(VGroup(flux, collected, aperture_gain), answer), Create(box))
        self.wait(1.4)
        self.play(
            FadeOut(tx),
            FadeOut(rx),
            FadeOut(link),
            FadeOut(r_label),
            FadeOut(tx_label),
            FadeOut(rx_label),
            FadeOut(flux),
            FadeOut(collected),
            FadeOut(aperture_gain),
            VGroup(answer, box).animate.move_to(UP * 1.55),
            run_time=1.0,
        )
        self.play(FadeIn(definitions), FadeIn(assumptions))
        self.wait(2.5)
        self.clear_slide()

    def voyager_link_budget(self):
        self.start_slide("Voyager link budget")

        title = self.title("Representative Voyager 1 X-band link")
        voyager = ImageMobject(str(VOYAGER_IMAGE)).set(height=1.18).move_to(LEFT * 5.45 + UP * 2.18)
        goldstone = ImageMobject(str(GOLDSTONE_IMAGE)).set(height=1.18).move_to(RIGHT * 5.45 + UP * 2.18)
        voyager_frame = SurroundingRectangle(voyager, buff=0.04, color=GOLD, stroke_width=1.5)
        goldstone_frame = SurroundingRectangle(goldstone, buff=0.04, color=SIGNAL, stroke_width=1.5)
        link = Arrow(LEFT * 4.20 + UP * 2.18, RIGHT * 4.20 + UP * 2.18, buff=0, color=SIGNAL, stroke_width=3)
        range_label = MathTex(r"R=25.7\times10^{12}\,\mathrm m", font_size=28, color=MUTED).next_to(
            link, UP, buff=0.10
        )
        voyager_caption = Text("Voyager 1", font_size=18, color=GOLD).next_to(voyager, DOWN, buff=0.08)
        goldstone_caption = Text("DSS-14, Goldstone", font_size=18, color=SIGNAL).next_to(goldstone, DOWN, buff=0.08)
        values_left = MathTex(
            r"\begin{aligned}"
            r"f&=8.4\,\mathrm{GHz} & \lambda&=35.7\,\mathrm{mm}\\"
            r"R&=25.7\times10^{12}\,\mathrm m & P_{\rm t}&\approx20\,\mathrm W\\"
            r"D_{\rm t}&=3.7\,\mathrm m & \eta_{\rm t}&=0.55"
            r"\end{aligned}",
            font_size=34,
            color=FG,
        ).shift(LEFT * 3.30 + UP * 0.12)
        values_right = MathTex(
            r"\begin{aligned}"
            r"D_{\rm r}&=70\,\mathrm m & \eta_{\rm r}&=0.65\\"
            r"G_{\rm t}&=47.7\,\mathrm{dBi} & G_{\rm r}&=73.9\,\mathrm{dBi}\\"
            r"L_{\rm fs}&=20\log_{10}\!\frac{4\pi R}{\lambda}=319.1\,\mathrm{dB}"
            r"\end{aligned}",
            font_size=34,
            color=FG,
        ).shift(RIGHT * 3.25 + UP * 0.12)
        separator = Line(UP * 0.90, DOWN * 0.92, color=MUTED, stroke_opacity=0.45)

        db_budget = MathTex(
            r"P_{\rm r}\,[\mathrm{dBW}]"
            r"=13.0+47.7+73.9-319.1"
            r"=-184.5\,\mathrm{dBW}",
            font_size=43,
            color=GOLD,
        ).shift(DOWN * 1.25)
        watts = MathTex(
            r"P_{\rm r}=3.52\times10^{-19}\,\mathrm W"
            r"=-154.5\,\mathrm{dBm}",
            font_size=43,
            color=POWER,
        ).next_to(db_budget, DOWN, buff=0.38)
        note = Text(
            "Ideal free-space result before pointing, polarization, atmosphere, and hardware losses",
            font_size=24,
            color=MUTED,
        ).to_edge(DOWN, buff=0.30)

        self.play(FadeIn(title), FadeIn(voyager), Create(voyager_frame), FadeIn(goldstone), Create(goldstone_frame))
        self.play(GrowArrow(link), FadeIn(range_label), FadeIn(voyager_caption), FadeIn(goldstone_caption))
        self.play(FadeIn(values_left, shift=0.15 * RIGHT), Create(separator), FadeIn(values_right, shift=0.15 * LEFT))
        self.play(Write(db_budget))
        self.play(Write(watts))
        self.play(FadeIn(note))
        self.wait(2.5)
        self.clear_slide()

    def noise_and_snr(self):
        self.start_slide("Noise and SNR")

        title = self.title("SNR depends on receiver bandwidth")
        received = MathTex(
            r"P_{\rm r}=3.52\times10^{-19}\,\mathrm W",
            font_size=43,
            color=POWER,
        ).next_to(title, DOWN, buff=0.43)
        assumptions = MathTex(
            r"T_{\rm sys}=20\,\mathrm K,\qquad B=160\,\mathrm{Hz}",
            font_size=38,
            color=MUTED,
        ).next_to(received, DOWN, buff=0.32)
        noise = MathTex(
            r"N=k_{\mathrm B}T_{\rm sys}B"
            r"=(1.380649\times10^{-23})(20)(160)\,\mathrm W"
            r"=4.42\times10^{-20}\,\mathrm W",
            font_size=35,
            color=SIGNAL,
        ).next_to(assumptions, DOWN, buff=0.38)
        snr = MathTex(
            r"\mathrm{SNR}=\frac{P_{\rm r}}{N}"
            r"=\frac{3.52\times10^{-19}}{4.42\times10^{-20}}\approx7.97"
            r"\qquad 10\log_{10}(7.97)\approx9.0\,\mathrm{dB}",
            font_size=36,
            color=GOLD,
        ).next_to(noise, DOWN, buff=0.48)
        box = SurroundingRectangle(snr, buff=0.26, color=GOLD, corner_radius=0.11)

        bandwidth_examples = VGroup(
            MathTex(r"B=1\,\mathrm{Hz}:\quad\mathrm{SNR}=31.1\,\mathrm{dB}", font_size=28, color=APERTURE),
            MathTex(r"B=160\,\mathrm{Hz}:\quad\mathrm{SNR}=9.0\,\mathrm{dB}", font_size=28, color=GOLD),
            MathTex(r"B=1\,\mathrm{kHz}:\quad\mathrm{SNR}=1.1\,\mathrm{dB}", font_size=28, color=POWER),
        ).arrange(RIGHT, buff=0.50).to_edge(DOWN, buff=0.38)

        self.play(FadeIn(title), Write(received))
        self.play(FadeIn(assumptions))
        self.play(Write(noise))
        self.play(Write(snr), Create(box))
        self.play(LaggedStart(*[FadeIn(item, shift=0.12 * UP) for item in bandwidth_examples], lag_ratio=0.15))
        self.wait(2.6)
        self.clear_slide()

    def shannon_capacity(self):
        self.start_slide("Shannon channel capacity")
        self.play(FadeIn(self.title("How much information can this noisy link carry?")))
        model = Text(
            "Ideal band-limited channel with additive white Gaussian noise",
            font_size=27, color=MUTED,
        ).move_to(UP * 2.55)
        self.play(FadeIn(model))
        # Real orthogonal channel coordinates have 2B degrees of freedom per
        # second. Gaussian inputs maximize output differential entropy for a
        # given average power. This is a derivation sketch, not the coding proof.
        self.aperture_equations([
            r"Y=X+Z,\quad Z\ \text{independent Gaussian noise};\quad "
            r"\sigma_X^2/\sigma_Z^2=P_{\rm r}/N",
            r"I(X;Y)=h(Y)-h(Z)"
            r"\quad\text{(output entropy minus noise entropy)}",
            r"I_{\max}=\frac12\log_2\!\left[2\pi e(\sigma_X^2+\sigma_Z^2)\right]"
            r"-\frac12\log_2(2\pi e\sigma_Z^2)",
            r"I_{\max}=\frac12\log_2\!\left(1+\frac{P_{\rm r}}{N}\right)"
            r"\quad[\mathrm{bit/real\ coordinate}]",
            r"\underbrace{2B}_{\text{real coordinates per second}}\,I_{\max}"
            r"=\boxed{C=B\log_2(1+\mathrm{SNR})}\quad[\mathrm{bit\,s^{-1}}]",
        ], center=DOWN * 0.05, font_size=30)
        notes = VGroup(
            Text("Gaussian signals maximize entropy at fixed average power; h is differential entropy (bits).",
                 font_size=22, color=MUTED),
            MathTex(r"B\ [\mathrm{Hz}],\quad \mathrm{SNR}=P_{\rm r}/N\ [1]"
                    r"\quad\text{(use the linear ratio, not dB)}", font_size=27, color=GOLD),
            Text("Rates below C can approach arbitrarily small error with sufficiently long, suitable codes.",
                 font_size=22, color=FG),
        ).arrange(DOWN, buff=0.13).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(notes))
        self.wait(3)
        self.clear_slide()

    def voyager_capacity(self):
        self.start_slide("Voyager theoretical information rate")
        self.play(FadeIn(self.title("Voyager to Earth: the theoretical information limit")))
        self.aperture_equations([
            r"P_{\rm r}=3.52\times10^{-19}\,\mathrm W,\quad "
            r"T_{\rm sys}=20\,\mathrm K,\quad B=160\,\mathrm{Hz}",
            r"N=k_{\mathrm B}T_{\rm sys}B=4.42\times10^{-20}\,\mathrm W"
            r"\quad\Longrightarrow\quad P_{\rm r}/N\simeq7.97",
            r"C=B\log_2\!\left(1+\frac{P_{\rm r}}{k_{\mathrm B}T_{\rm sys}B}\right)",
            r"C=160\log_2(1+7.97)\simeq\boxed{506\,\mathrm{bit\,s^{-1}}}",
            r"\text{continuous 24-hour reception:}\quad "
            r"C\Delta t\simeq43.7\,\mathrm{Mbit}\simeq5.47\,\mathrm{MB}",
        ], center=UP * 0.12, font_size=34)
        notes = VGroup(
            Text("This bound uses the example's power, bandwidth and temperature; it is not Voyager's actual data rate.",
                 font_size=22, color=MUTED),
            Text("Practical rates are lower: coding, modulation, overhead, losses and ground-station availability matter.",
                 font_size=22, color=MUTED),
            Text("Data totals assume a continuous link; MB means 10⁶ bytes. Changing bandwidth also changes noise.",
                 font_size=22, color=MUTED),
        ).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.30)
        self.play(FadeIn(notes))
        self.wait(3)
        self.clear_slide()

    def close(self):
        self.start_slide("Summary")

        title = self.title("From diffraction to information rate")
        steps = VGroup(
            MathTex(r"\theta\sim\frac{\lambda}{D}", font_size=42, color=SIGNAL),
            MathTex(r"A_{\mathrm{e},\max}\Omega_A=\eta_{\rm rad}\lambda^2", font_size=42, color=APERTURE),
            MathTex(r"G=\frac{4\pi A_{\rm e}}{\lambda^2}", font_size=42, color=POWER),
            MathTex(
                r"P_{\rm r}=P_{\rm t}G_{\rm t}G_{\rm r}"
                r"\left(\frac{\lambda}{4\pi R}\right)^2",
                font_size=42,
                color=GOLD,
            ),
        ).arrange(DOWN, buff=0.36).shift(UP * 0.05)
        arrows = VGroup(
            *[
                MathTex(r"\Downarrow", font_size=30, color=MUTED).move_to(
                    (steps[i].get_bottom() + steps[i + 1].get_top()) / 2
                )
                for i in range(len(steps) - 1)
            ]
        )
        result = MathTex(
            r"C=B\log_2\!\left(1+\frac{P_{\rm r}}{k_{\mathrm B}T_{\rm sys}B}\right)"
            r"\simeq506\,\mathrm{bit\,s^{-1}}\quad(B=160\,\mathrm{Hz})",
            font_size=36,
            color=FG,
        ).to_edge(DOWN, buff=0.45)

        self.play(FadeIn(title))
        for index, step in enumerate(steps):
            self.play(Write(step), run_time=0.65)
            if index < len(arrows):
                self.play(FadeIn(arrows[index]), run_time=0.25)
        self.play(FadeIn(result, shift=0.14 * UP))
        self.wait(3.0)
