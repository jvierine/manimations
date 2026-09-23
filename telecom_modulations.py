"""Manim lecture: how digital bits become a radiated electromagnetic wave.

Render a quick preview:
    conda run -n base manim -pql telecom_modulations.py TelecomModulations

Render the final 1080p presentation:
    conda run -n base manim -pqh telecom_modulations.py TelecomModulations

Script provenance is shown by default. Set SHOW_PROVENANCE=0 to hide it.
"""

from __future__ import annotations

import os

import numpy as np
from manim import *


BG = "#07111F"
FG = "#F3F7FA"
MUTED = "#9DB0C3"
BLUE = "#74A9FF"
CYAN = "#45C2B1"
YELLOW = "#F3D35A"
ORANGE = "#F5A65B"
RED = "#FF6B6B"
PURPLE = "#C792EA"
GREEN = "#8BD17C"

SHOW_PROVENANCE = os.getenv("SHOW_PROVENANCE", "1") != "0"


class TelecomModulations(Scene):
    """Ten-section animated lecture for a 16:9 screen."""

    bits = [0, 1, 0, 1, 0]

    def setup(self):
        self.camera.background_color = BG
        self.provenance = Text(
            "Source: telecom_modulations.py",
            font_size=15,
            color=MUTED,
        ).to_corner(DR, buff=0.18)
        if SHOW_PROVENANCE:
            self.add(self.provenance)

    def title(self, text: str) -> Text:
        return Text(text, font_size=43, weight=SEMIBOLD, color=FG).to_edge(UP, buff=0.28)

    def subtitle(self, text: str) -> Text:
        return Text(text, font_size=25, color=MUTED)

    def clear_slide(self):
        protected = {self.provenance} if SHOW_PROVENANCE else set()
        removable = [m for m in self.mobjects if m not in protected]
        if removable:
            self.play(*[FadeOut(m, shift=0.08 * DOWN) for m in removable], run_time=0.45)

    def bit_cells(self, bits, width=8.8, y=2.15, labels=True):
        n = len(bits)
        cell_w = width / n
        group = VGroup()
        left = -width / 2
        for i, bit in enumerate(bits):
            rect = Rectangle(
                width=cell_w,
                height=0.72,
                stroke_color=MUTED,
                stroke_width=2,
                fill_color=BLUE if bit else BG,
                fill_opacity=0.18 if bit else 0.0,
            ).move_to([left + (i + 0.5) * cell_w, y, 0])
            group.add(rect)
            if labels:
                group.add(Text(str(bit), font_size=31, color=YELLOW if bit else FG).move_to(rect))
        return group

    def digital_trace(self, bits, width=8.8, y=0.95, high=0.42, low=-0.42, color=YELLOW):
        left = -width / 2
        cell_w = width / len(bits)
        points = []
        for i, bit in enumerate(bits):
            level = y + (high if bit else low)
            x0 = left + i * cell_w
            x1 = x0 + cell_w
            if i == 0:
                points.append([x0, level, 0])
            else:
                points.append([x0, y + (high if bits[i - 1] else low), 0])
                points.append([x0, level, 0])
            points.append([x1, level, 0])
        return VMobject(color=color, stroke_width=4).set_points_as_corners(points)

    def modulated_wave(self, bits, mode, width=10.3, y=-1.35, amp=0.63, color=BLUE):
        left = -width / 2
        samples_per_bit = 100
        points = []
        phase_acc = 0.0
        for i, bit in enumerate(bits):
            for j in range(samples_per_bit + 1):
                u = j / samples_per_bit
                x = left + width * (i + u) / len(bits)
                if mode == "ask":
                    a = 0.30 if bit == 0 else 0.95
                    cycles = 4.0
                    value = a * np.sin(TAU * cycles * u)
                elif mode == "fsk":
                    cycles = 2.0 if bit == 0 else 5.0
                    value = np.sin(phase_acc + TAU * cycles * u)
                elif mode == "psk":
                    cycles = 3.0
                    phase = 0 if bit == 0 else PI
                    value = np.sin(TAU * cycles * u + phase)
                else:
                    raise ValueError(mode)
                points.append([x, y + amp * value, 0])
            if mode == "fsk":
                phase_acc += TAU * cycles
        return VMobject(color=color, stroke_width=3.5).set_points_as_corners(points)

    def symbol_boundaries(self, n, width=10.3, y=-1.35, height=1.65):
        left = -width / 2
        return VGroup(*[
            DashedLine(
                [left + i * width / n, y - height / 2, 0],
                [left + i * width / n, y + height / 2, 0],
                dash_length=0.08,
                stroke_width=1.4,
                color=MUTED,
            )
            for i in range(n + 1)
        ])

    def construct(self):
        self.opening()
        self.signal_model()
        self.bits_to_symbols()
        self.ask()
        self.fsk()
        self.psk()
        self.qam()
        self.iq_transmitter()
        self.antenna_radiation()
        self.receiver_and_summary()

    def opening(self):
        self.next_section("Opening")
        headline = Text(
            "How bits become radio waves",
            font_size=56,
            weight=SEMIBOLD,
            color=FG,
        ).to_edge(UP, buff=0.80)
        bits = Text("0  1  0  1  0", font_size=42, color=YELLOW)
        arrow = Arrow(LEFT * 1.5, RIGHT * 1.5, color=MUTED, stroke_width=4)
        wave = FunctionGraph(lambda x: 0.48 * np.sin(7 * x), x_range=[-2.1, 2.1], color=BLUE, stroke_width=4)
        antenna = VGroup(
            Line(DOWN * 0.75, UP * 0.75, color=FG, stroke_width=5),
            Line(ORIGIN, UL * 0.68, color=FG, stroke_width=5),
            Line(ORIGIN, UR * 0.68, color=FG, stroke_width=5),
        )
        row = VGroup(bits, arrow, antenna, wave).arrange(RIGHT, buff=0.55).shift(DOWN * 0.35)
        stages = Text(
            "bits      symbols      RF voltage and current      electromagnetic field",
            font_size=23,
            color=MUTED,
        ).next_to(row, DOWN, buff=0.58)
        self.play(FadeIn(headline, shift=UP * 0.15))
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.10) for m in row], lag_ratio=0.17))
        self.play(FadeIn(stages))
        self.wait(1.0)
        self.clear_slide()

    def signal_model(self):
        self.next_section("Signal model")
        title = self.title("Three controls on a carrier")
        eq = MathTex(
            r"E(t)=", r"A(t)", r"\cos\!\left(2\pi", r"f(t)", r"t+", r"\phi(t)", r"\right)",
            font_size=55,
        ).shift(UP * 0.78)
        eq[1].set_color(ORANGE)
        eq[3].set_color(CYAN)
        eq[5].set_color(PURPLE)
        labels = VGroup(
            VGroup(Text("amplitude", font_size=27, color=ORANGE), Text("ASK", font_size=23, color=MUTED)),
            VGroup(Text("frequency", font_size=27, color=CYAN), Text("FSK", font_size=23, color=MUTED)),
            VGroup(Text("phase", font_size=27, color=PURPLE), Text("PSK", font_size=23, color=MUTED)),
        )
        for g in labels:
            g.arrange(DOWN, buff=0.14)
        labels.arrange(RIGHT, buff=1.25).shift(DOWN * 1.0)
        combined = VGroup(
            Text("Amplitude + phase", font_size=30, color=YELLOW),
            Text("QAM", font_size=29, color=FG),
        ).arrange(DOWN, buff=0.12).shift(DOWN * 2.35)
        arrows = VGroup(
            Arrow(labels[0].get_top(), eq[1].get_bottom(), buff=0.18, color=ORANGE),
            Arrow(labels[1].get_top(), eq[3].get_bottom(), buff=0.18, color=CYAN),
            Arrow(labels[2].get_top(), eq[5].get_bottom(), buff=0.18, color=PURPLE),
        )
        self.play(FadeIn(title), Write(eq))
        self.play(LaggedStart(*[FadeIn(g) for g in labels], lag_ratio=0.16), Create(arrows))
        self.play(FadeIn(combined, shift=UP * 0.12))
        self.wait(1.1)
        self.clear_slide()

    def bits_to_symbols(self):
        self.next_section("Bits to symbols")
        title = self.title("The modulator sends symbols")
        bits = [0, 1, 1, 0, 1, 1, 0, 0]
        bit_text = VGroup(*[Text(str(b), font_size=37, color=YELLOW if b else FG) for b in bits]).arrange(RIGHT, buff=0.48)
        bit_text.shift(UP * 1.35)
        braces = VGroup()
        symbol_labels = VGroup()
        pairs = ["01", "10", "11", "00"]
        phases = [r"90^\circ", r"180^\circ", r"270^\circ", r"0^\circ"]
        for i, (pair, phase) in enumerate(zip(pairs, phases)):
            pair_group = VGroup(bit_text[2 * i], bit_text[2 * i + 1])
            brace = Brace(pair_group, DOWN, buff=0.13, color=MUTED)
            label = MathTex(phase, font_size=29, color=PURPLE).next_to(brace, DOWN, buff=0.14)
            braces.add(brace)
            symbol_labels.add(label)
        rate = MathTex(r"R_s=\frac{R_b}{\log_2 M}", font_size=48, color=CYAN).shift(DOWN * 0.45)
        note = Text("QPSK: 2 bits per symbol", font_size=29, color=FG).next_to(rate, DOWN, buff=0.35)
        caveat = Text("Coding and pulse shaping are omitted here", font_size=23, color=MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(title), LaggedStart(*[FadeIn(b) for b in bit_text], lag_ratio=0.08))
        self.play(Create(braces), FadeIn(symbol_labels))
        self.play(Write(rate), FadeIn(note), FadeIn(caveat))
        self.wait(1.0)
        self.clear_slide()

    def modulation_slide(self, name, expansion, mode, color, mapping):
        title = self.title(name)
        expansion_text = Text(expansion, font_size=25, color=color).next_to(title, DOWN, buff=0.18)
        cells = self.bit_cells(self.bits)
        wave = self.modulated_wave(self.bits, mode=mode, color=color)
        bounds = self.symbol_boundaries(len(self.bits))
        label = Text(mapping, font_size=24, color=MUTED).to_edge(DOWN, buff=0.52)
        self.play(FadeIn(title), FadeIn(expansion_text))
        self.play(LaggedStart(*[FadeIn(m) for m in cells], lag_ratio=0.04))
        self.play(Create(bounds), Create(wave), run_time=1.8)
        self.play(FadeIn(label))
        self.wait(0.9)
        self.clear_slide()

    def ask(self):
        self.next_section("ASK")
        self.modulation_slide(
            "Amplitude shift keying",
            "The symbol selects the carrier amplitude",
            "ask",
            ORANGE,
            "Example: 0 = weak carrier, 1 = strong carrier. On-off keying uses zero amplitude for 0.",
        )

    def fsk(self):
        self.next_section("FSK")
        self.modulation_slide(
            "Frequency shift keying",
            "The symbol selects the instantaneous frequency",
            "fsk",
            CYAN,
            "Example: 0 = lower frequency, 1 = higher frequency",
        )

    def psk(self):
        self.next_section("PSK")
        self.modulation_slide(
            "Phase shift keying",
            "The symbol selects the carrier phase",
            "psk",
            PURPLE,
            "BPSK example: 0 = 0°, 1 = 180°. The phase changes at symbol boundaries.",
        )

    def qam(self):
        self.next_section("QAM")
        title = self.title("Quadrature amplitude modulation")
        subtitle = self.subtitle("Each symbol selects both amplitude and phase").next_to(title, DOWN, buff=0.18)
        axes = Axes(
            x_range=[-4, 4, 1], y_range=[-4, 4, 1], x_length=5.0, y_length=5.0,
            axis_config={"color": MUTED, "include_ticks": False, "include_numbers": False, "stroke_width": 2},
            tips=True,
        ).shift(LEFT * 2.5 + DOWN * 0.45)
        i_label = MathTex("I", font_size=32, color=FG).next_to(axes.x_axis, RIGHT, buff=0.12)
        q_label = MathTex("Q", font_size=32, color=FG).next_to(axes.y_axis, UP, buff=0.12)
        dots = VGroup(*[
            Dot(axes.c2p(i, q), radius=0.085, color=YELLOW)
            for i in (-3, -1, 1, 3) for q in (-3, -1, 1, 3)
        ])
        selected = [(-3, -1), (-1, 3), (3, 1), (1, -3)]
        path = VMobject(color=BLUE, stroke_width=3).set_points_as_corners([axes.c2p(i, q) for i, q in selected])
        rings = VGroup(*[Circle(radius=0.19, color=BLUE, stroke_width=3).move_to(axes.c2p(i, q)) for i, q in selected])
        equation = MathTex(
            r"s(t)=I_k\cos(2\pi f_ct)-Q_k\sin(2\pi f_ct)",
            font_size=39,
        ).shift(RIGHT * 3.0 + UP * 0.65)
        equation[0][5:7].set_color(ORANGE)
        explanation = VGroup(
            Text("16-QAM", font_size=34, color=YELLOW),
            Text("16 symbols", font_size=27, color=FG),
            Text("4 bits per symbol", font_size=27, color=FG),
            Text("larger M needs higher SNR", font_size=23, color=MUTED),
        ).arrange(DOWN, buff=0.22).shift(RIGHT * 3.1 + DOWN * 1.05)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.play(Create(axes), FadeIn(i_label), FadeIn(q_label), FadeIn(dots))
        self.play(Create(path), FadeIn(rings), Write(equation))
        self.play(LaggedStart(*[FadeIn(m) for m in explanation], lag_ratio=0.12))
        self.wait(1.0)
        self.clear_slide()

    def iq_transmitter(self):
        self.next_section("Transmitter")
        title = self.title("From symbols to radio-frequency current")
        labels = ["bits", "symbol\nmapper", "pulse-shaping\nfilter", "I/Q\nmodulator", "power\namplifier", "antenna"]
        colors = [YELLOW, PURPLE, CYAN, BLUE, ORANGE, FG]
        boxes = VGroup()
        for label, color in zip(labels, colors):
            box = RoundedRectangle(width=1.72, height=1.05, corner_radius=0.12, stroke_color=color, stroke_width=2.5)
            text = Text(label, font_size=22, color=color, line_spacing=0.85).move_to(box)
            boxes.add(VGroup(box, text))
        boxes.arrange(RIGHT, buff=0.35).shift(DOWN * 0.15)
        arrows = VGroup(*[
            Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=2.5, max_tip_length_to_length_ratio=0.16)
            for i in range(len(boxes) - 1)
        ])
        baseband = Text("complex baseband", font_size=23, color=CYAN).next_to(VGroup(boxes[1], boxes[2]), DOWN, buff=0.45)
        rf = Text("radio frequency", font_size=23, color=BLUE).next_to(VGroup(boxes[3], boxes[4]), DOWN, buff=0.45)
        eq = MathTex(
            r"x(t)=I(t)\cos(2\pi f_ct)-Q(t)\sin(2\pi f_ct)",
            font_size=39,
            color=FG,
        ).shift(DOWN * 2.15)
        pulse = Dot(color=YELLOW, radius=0.11).move_to(boxes[0].get_center())
        self.play(FadeIn(title))
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.12) for b in boxes], lag_ratio=0.10), Create(arrows))
        self.play(FadeIn(baseband), FadeIn(rf), Write(eq))
        self.add(pulse)
        for i in range(1, len(boxes)):
            self.play(pulse.animate.move_to(boxes[i].get_center()).set_color(colors[i]), run_time=0.38)
        self.play(FadeOut(pulse))
        self.wait(0.8)
        self.clear_slide()

    def antenna_radiation(self):
        self.next_section("Antenna radiation")
        title = self.title("The antenna converts guided current into radiation")
        dipole = VGroup(
            Line([0, 0.10, 0], [0, 2.0, 0], color=FG, stroke_width=8),
            Line([0, -0.10, 0], [0, -2.0, 0], color=FG, stroke_width=8),
            Dot([0, 0, 0], radius=0.10, color=ORANGE),
        ).shift(LEFT * 3.8 + DOWN * 0.20)
        feed = FunctionGraph(lambda x: 0.23 * np.sin(10 * x), x_range=[-1.5, 0], color=ORANGE, stroke_width=4)
        feed.rotate(PI / 2).next_to(dipole, DOWN, buff=0.15)
        current_arrow = DoubleArrow(dipole.get_bottom() + UP * 0.45, dipole.get_top() + DOWN * 0.45, color=ORANGE, stroke_width=4)
        current_label = MathTex(r"I(t)", font_size=35, color=ORANGE).next_to(dipole, LEFT, buff=0.35)
        waves = VGroup()
        for radius in [0.8, 1.55, 2.3, 3.05]:
            arc_top = Arc(radius=radius, start_angle=-0.75, angle=1.5, color=BLUE, stroke_width=3).shift(LEFT * 3.8 + DOWN * 0.20)
            arc_bottom = Arc(radius=radius, start_angle=PI - 0.75, angle=1.5, color=BLUE, stroke_width=3).shift(LEFT * 3.8 + DOWN * 0.20)
            waves.add(arc_top, arc_bottom)
        physics = VGroup(
            Text("Oscillating voltage drives charge", font_size=28, color=FG),
            Text("Accelerating charge creates changing E and B fields", font_size=27, color=FG),
            Text("The far field carries energy away", font_size=28, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.40).shift(RIGHT * 3.0 + UP * 0.35)
        equations = VGroup(
            MathTex(r"\mathbf{S}=\mathbf{E}\times\mathbf{H}", font_size=38, color=CYAN),
            MathTex(r"c=\frac{1}{\sqrt{\mu_0\varepsilon_0}}", font_size=36, color=BLUE),
        ).arrange(DOWN, buff=0.34).next_to(physics, DOWN, buff=0.48)
        note = Text("The antenna does not radiate isolated bits. It radiates the modulated RF waveform.", font_size=23, color=MUTED).to_edge(DOWN, buff=0.48)
        self.play(FadeIn(title), FadeIn(dipole), FadeIn(feed), GrowArrow(current_arrow), FadeIn(current_label))
        self.play(LaggedStart(*[Create(a) for a in waves], lag_ratio=0.10), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.12) for line in physics], lag_ratio=0.16))
        self.play(Write(equations), FadeIn(note))
        self.wait(1.1)
        self.clear_slide()

    def receiver_and_summary(self):
        self.next_section("Summary")
        title = self.title("The receiver estimates the transmitted symbols")
        chain_labels = ["radiated\nfield", "antenna", "downconvert", "sample", "decide", "bits"]
        colors = [BLUE, FG, ORANGE, CYAN, PURPLE, YELLOW]
        chain = VGroup()
        for label, color in zip(chain_labels, colors):
            circ = Circle(radius=0.55, stroke_color=color, stroke_width=2.5)
            text = Text(label, font_size=19, color=color, line_spacing=0.85).move_to(circ)
            chain.add(VGroup(circ, text))
        chain.arrange(RIGHT, buff=0.58).shift(UP * 1.15)
        arrows = VGroup(*[
            Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=2.3)
            for i in range(len(chain) - 1)
        ])
        rows = [
            ("ASK", "amplitude", ORANGE),
            ("FSK", "frequency", CYAN),
            ("PSK", "phase", PURPLE),
            ("QAM", "amplitude + phase", YELLOW),
        ]
        summary = VGroup()
        for acronym, control, color in rows:
            summary.add(VGroup(
                Text(acronym, font_size=30, weight=SEMIBOLD, color=color),
                Text(control, font_size=27, color=FG),
            ).arrange(RIGHT, buff=0.42))
        summary.arrange(DOWN, aligned_edge=LEFT, buff=0.25).shift(DOWN * 1.35)
        key = Text("Modulation maps information onto a carrier that an antenna can radiate", font_size=29, color=BLUE).to_edge(DOWN, buff=0.42)
        self.play(FadeIn(title))
        self.play(LaggedStart(*[FadeIn(c) for c in chain], lag_ratio=0.10), Create(arrows))
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in summary], lag_ratio=0.13))
        self.play(FadeIn(key))
        self.wait(1.6)
