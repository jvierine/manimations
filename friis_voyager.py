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
        return Text(text, font_size=44, weight=SEMIBOLD, color=FG).to_edge(UP, buff=0.30)

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
            r"R\approx25.7\times10^{12}\,\mathrm m",
            r"\qquad t_{\rm one\ way}\approx23.8\,\mathrm h",
            font_size=31,
            color=MUTED,
        ).next_to(path, UP, buff=0.34)
        question = Text(
            "What is the SNR of the Voyager 1 to Earth radio link?",
            font_size=42,
            weight=SEMIBOLD,
            color=FG,
            t2c={"SNR": POWER, "Voyager 1": GOLD, "Earth": SIGNAL},
        ).shift(DOWN * 2.05)
        self.play(FadeIn(voyager), Create(voyager_frame), FadeIn(earth), Create(earth_frame))
        self.play(Create(path), LaggedStart(*[FadeIn(p) for p in pulses], lag_ratio=0.12))
        self.play(FadeIn(voyager_label), FadeIn(earth_label), Write(distance))
        self.play(FadeIn(question, shift=0.18 * UP))
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

        antenna = self.antenna_icon(POWER).scale(0.90).move_to(RIGHT * 3.10 + UP * 0.75)
        beam = Polygon(
            antenna.get_center() + RIGHT * 0.20,
            RIGHT * 6.15 + UP * 1.70,
            RIGHT * 6.15 + DOWN * 0.20,
            color=SIGNAL,
            fill_color=SIGNAL,
            fill_opacity=0.15,
            stroke_opacity=0.65,
        )
        antenna_label = Text("directional antenna", font_size=27, color=POWER).next_to(
            antenna, DOWN, buff=0.28
        )

        definition = MathTex(
            r"G(\theta,\phi)\equiv"
            r"\frac{S(\theta,\phi)}{P_{\rm t}/(4\pi R^2)}",
            font_size=47,
            color=GOLD,
        ).shift(DOWN * 1.25)
        flux = MathTex(
            r"S(\theta,\phi)=\frac{P_{\rm t}G(\theta,\phi)}{4\pi R^2}",
            font_size=48,
            color=FG,
        ).next_to(definition, DOWN, buff=0.38)
        units = MathTex(
            r"G\ \text{is dimensionless},\qquad G_{\mathrm{dBi}}=10\log_{10}G",
            font_size=30,
            color=MUTED,
        ).to_edge(DOWN, buff=0.28)

        self.play(FadeIn(title))
        self.play(FadeIn(isotropic_source), LaggedStart(*[Create(w) for w in isotropic_waves], lag_ratio=0.15))
        self.play(FadeIn(isotropic_label))
        self.play(FadeIn(antenna), FadeIn(antenna_label), FadeIn(beam))
        self.play(Write(definition))
        self.play(Write(flux), FadeIn(units))
        self.wait(2.2)
        self.clear_slide()

    def receiver_collection(self):
        self.start_slide("Receiver collection")

        title = self.title("One antenna transmits and another collects")
        tx = self.antenna_icon(POWER).scale(0.78).move_to(LEFT * 5.0 + UP * 0.65)
        rx = self.antenna_icon(APERTURE).scale(0.78).move_to(RIGHT * 5.0 + UP * 0.65)
        link = Arrow(
            tx.get_right() + RIGHT * 0.18,
            rx.get_left() + LEFT * 0.18,
            buff=0,
            color=SIGNAL,
            stroke_width=4,
        )
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
        self.play(Write(flux))
        self.play(Write(collected))
        self.play(FadeIn(area_definition))
        self.wait(2.3)
        self.clear_slide()

    def lambda_over_d(self):
        self.start_slide("Lambda over D")

        title = self.title("Why a larger aperture makes a narrower beam")

        center = LEFT * 3.75 + UP * 0.30
        aperture = Line(center + DOWN * 1.45, center + UP * 1.45, color=APERTURE, stroke_width=10)
        aperture_label = Text("uniform aperture", font_size=24, color=APERTURE).next_to(
            aperture, DOWN, buff=0.28
        )
        d_brace = Brace(aperture, LEFT, color=APERTURE)
        d_label = MathTex(r"D", font_size=42, color=APERTURE).next_to(d_brace, LEFT, buff=0.12)

        axis = DashedLine(center, center + RIGHT * 4.20, color=MUTED, stroke_opacity=0.65)
        theta = 18 * DEGREES
        direction_end = center + 4.20 * np.array([np.cos(theta), np.sin(theta), 0.0])
        direction = Arrow(center, direction_end, buff=0, color=SIGNAL, stroke_width=5)
        direction_label = Text("far-field direction", font_size=24, color=SIGNAL).next_to(
            direction, UP, buff=0.12
        )
        angle_arc = Arc(radius=0.95, start_angle=0, angle=theta, arc_center=center, color=GOLD, stroke_width=4)
        theta_label = MathTex(r"\theta", font_size=38, color=GOLD).next_to(angle_arc, RIGHT, buff=0.08)

        top_ray = Line(
            aperture.get_top(),
            aperture.get_top() + 3.35 * np.array([np.cos(theta), np.sin(theta), 0.0]),
            color=SIGNAL,
            stroke_width=2.5,
            stroke_opacity=0.45,
        )
        bottom_ray = Line(
            aperture.get_bottom(),
            aperture.get_bottom() + 3.35 * np.array([np.cos(theta), np.sin(theta), 0.0]),
            color=SIGNAL,
            stroke_width=2.5,
            stroke_opacity=0.45,
        )

        equation_panel = RoundedRectangle(
            width=5.65,
            height=4.70,
            corner_radius=0.16,
            color=MUTED,
            stroke_opacity=0.35,
            fill_color="#0B1A2B",
            fill_opacity=0.92,
        ).move_to(RIGHT * 3.25 + DOWN * 0.05)
        path_difference = MathTex(
            r"\Delta \ell=D\sin\theta",
            font_size=45,
            color=FG,
        )
        first_null = MathTex(
            r"\text{first null:}\quad \Delta \ell=\lambda",
            font_size=39,
            color=SIGNAL,
        )
        combine = MathTex(
            r"D\sin\theta_{\rm null}=\lambda",
            font_size=45,
            color=FG,
        )
        small_angle = MathTex(
            r"\sin\theta\simeq\theta\quad(\theta\ll1)",
            font_size=37,
            color=MUTED,
        )
        result = MathTex(
            r"\boxed{\theta_{\rm null}\simeq\frac{\lambda}{D}}",
            font_size=53,
            color=GOLD,
        )
        derivation = VGroup(path_difference, first_null, combine, small_angle, result).arrange(
            DOWN, buff=0.32
        ).move_to(equation_panel)
        exact = MathTex(
            r"\text{circular dish:}\quad\theta_{\rm null}=1.22\frac{\lambda}{D}",
            font_size=29,
            color=MUTED,
        ).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(title), Create(aperture), GrowFromCenter(d_brace), FadeIn(d_label), FadeIn(aperture_label))
        self.play(Create(axis), GrowArrow(direction), Create(angle_arc), FadeIn(theta_label), FadeIn(direction_label))
        self.play(Create(top_ray), Create(bottom_ray))
        self.play(FadeIn(equation_panel), Write(path_difference))
        self.play(Write(first_null), Write(combine))
        self.play(Write(small_angle), Write(result))
        self.play(FadeIn(exact))
        self.wait(2.8)
        self.clear_slide()

    def area_wavelength_gain(self):
        self.start_slide("Area wavelength and gain")

        title = self.title("Effective area and gain describe the same antenna")
        beam_scale = MathTex(
            r"\theta\sim\frac{\lambda}{D}",
            r"\quad\Longrightarrow\quad",
            r"\Omega_A\sim\theta^2\sim\frac{\lambda^2}{D^2}",
            font_size=44,
        ).next_to(title, DOWN, buff=0.45)
        beam_scale[0].set_color(GOLD)
        beam_scale[2].set_color(SIGNAL)

        area = MathTex(
            r"A_{\rm e}=\eta_{\rm a}\frac{\pi D^2}{4}",
            font_size=48,
            color=APERTURE,
        ).shift(LEFT * 3.5 + UP * 0.50)
        theorem = MathTex(
            r"A_{\rm e}\Omega_A=\lambda^2",
            font_size=58,
            color=GOLD,
        ).shift(RIGHT * 3.25 + UP * 0.50)
        directivity = MathTex(
            r"G=\frac{4\pi}{\Omega_A}",
            font_size=49,
            color=SIGNAL,
        ).shift(LEFT * 3.5 + DOWN * 1.05)
        gain = MathTex(
            r"G=\frac{4\pi A_{\rm e}}{\lambda^2}"
            r"=\eta_{\rm a}\left(\frac{\pi D}{\lambda}\right)^2",
            font_size=49,
            color=POWER,
        ).shift(RIGHT * 2.65 + DOWN * 1.05)
        box = SurroundingRectangle(gain, buff=0.25, color=POWER, corner_radius=0.10)

        definitions = MathTex(
            r"A_{\rm e}\,[\mathrm{m^2}]:\ \text{effective aperture}"
            r"\qquad \Omega_A\,[\mathrm{sr}]:\ \text{beam solid angle}"
            r"\qquad G\ \text{is dimensionless}",
            font_size=28,
            color=MUTED,
        ).to_edge(DOWN, buff=0.34)

        self.play(FadeIn(title), Write(beam_scale))
        self.play(Write(area), Write(directivity))
        self.play(Write(theorem))
        self.play(TransformFromCopy(VGroup(area, directivity, theorem), gain), Create(box))
        self.play(FadeIn(definitions))
        self.wait(2.3)
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
        noise = MathTex(
            r"N=k_{\mathrm B}T_{\rm sys}B",
            font_size=53,
            color=SIGNAL,
        ).next_to(title, DOWN, buff=0.43)
        cn0 = MathTex(
            r"\frac{C}{N_0}=\frac{P_{\rm r}}{k_{\mathrm B}T_{\rm sys}}"
            r"=31.1\,\mathrm{dB\,Hz}",
            font_size=43,
            color=FG,
        ).next_to(noise, DOWN, buff=0.34)
        assumptions = MathTex(
            r"T_{\rm sys}=20\,\mathrm K,\qquad B=160\,\mathrm{Hz}",
            font_size=38,
            color=MUTED,
        ).next_to(cn0, DOWN, buff=0.38)
        snr = MathTex(
            r"\mathrm{SNR}_{\rm dB}="
            r"\left(\frac{C}{N_0}\right)_{\rm dB\,Hz}"
            r"-10\log_{10}\!B"
            r"=9.0\,\mathrm{dB}",
            font_size=47,
            color=GOLD,
        ).next_to(assumptions, DOWN, buff=0.43)
        box = SurroundingRectangle(snr, buff=0.26, color=GOLD, corner_radius=0.11)

        bandwidth_examples = VGroup(
            MathTex(r"B=1\,\mathrm{Hz}:\quad\mathrm{SNR}=31.1\,\mathrm{dB}", font_size=28, color=APERTURE),
            MathTex(r"B=160\,\mathrm{Hz}:\quad\mathrm{SNR}=9.0\,\mathrm{dB}", font_size=28, color=GOLD),
            MathTex(r"B=1\,\mathrm{kHz}:\quad\mathrm{SNR}=1.1\,\mathrm{dB}", font_size=28, color=POWER),
        ).arrange(RIGHT, buff=0.50).to_edge(DOWN, buff=0.38)

        self.play(FadeIn(title), Write(noise))
        self.play(Write(cn0))
        self.play(FadeIn(assumptions))
        self.play(Write(snr), Create(box))
        self.play(LaggedStart(*[FadeIn(item, shift=0.12 * UP) for item in bandwidth_examples], lag_ratio=0.15))
        self.wait(2.6)
        self.clear_slide()

    def close(self):
        self.start_slide("Summary")

        title = self.title("From diffraction to link SNR")
        steps = VGroup(
            MathTex(r"\theta\sim\frac{\lambda}{D}", font_size=42, color=SIGNAL),
            MathTex(r"A_{\rm e}\Omega_A=\lambda^2", font_size=42, color=APERTURE),
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
            r"\mathrm{SNR}=\frac{P_{\rm r}}{k_{\mathrm B}T_{\rm sys}B}"
            r"\approx9\,\mathrm{dB}\quad(B=160\,\mathrm{Hz})",
            font_size=49,
            color=FG,
        ).to_edge(DOWN, buff=0.45)

        self.play(FadeIn(title))
        for index, step in enumerate(steps):
            self.play(Write(step), run_time=0.65)
            if index < len(arrows):
                self.play(FadeIn(arrows[index]), run_time=0.25)
        self.play(FadeIn(result, shift=0.14 * UP))
        self.wait(3.0)
