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

SHOW_PROVENANCE = os.getenv("SHOW_PROVENANCE", "0") == "1"


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
        self.wait(1.2)
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
        self.antenna_radiation()
        self.signal_model()
        self.bpsk_mapping()
        self.psk()
        self.rate_definitions()
        self.bits_to_symbols()
        self.qpsk_waveform()
        self.ask()
        self.fsk()
        self.qam()

    def opening(self):
        self.next_section("Opening")
        question = Text(
            "How do we transmit information\nwith electromagnetic waves?",
            font_size=50,
            weight=SEMIBOLD,
            color=FG,
            line_spacing=0.92,
        ).to_edge(UP, buff=0.52)

        antenna_center = DOWN * 0.55
        dipole = VGroup(
            Line([0, 0.12, 0], [0, 1.55, 0], color=FG, stroke_width=7),
            Line([0, -0.12, 0], [0, -1.55, 0], color=FG, stroke_width=7),
            Dot(ORIGIN, radius=0.10, color=ORANGE),
        ).move_to(antenna_center)
        current = DoubleArrow(
            dipole.get_bottom() + UP * 0.35,
            dipole.get_top() + DOWN * 0.35,
            color=ORANGE,
            stroke_width=4,
        )
        current_label = MathTex(r"I(t)", font_size=34, color=ORANGE).next_to(dipole, LEFT, buff=0.28)
        waves = VGroup()
        for radius in [0.85, 1.55, 2.25, 2.95, 3.65]:
            waves.add(
                Arc(radius=radius, start_angle=-0.72, angle=1.44, color=BLUE, stroke_width=3).move_arc_center_to(antenna_center),
                Arc(radius=radius, start_angle=PI - 0.72, angle=1.44, color=BLUE, stroke_width=3).move_arc_center_to(antenna_center),
            )
        field_label = Text(
            "electromagnetic\nradiation",
            font_size=25,
            color=BLUE,
            line_spacing=0.90,
        ).move_to(RIGHT * 4.85 + DOWN * 0.45)
        follow_up = Text(
            "How can this waveform carry bits?",
            font_size=30,
            color=YELLOW,
        ).to_edge(DOWN, buff=0.48)

        self.play(FadeIn(question, shift=UP * 0.15))
        self.play(FadeIn(dipole), GrowArrow(current), FadeIn(current_label))
        self.play(LaggedStart(*[Create(arc) for arc in waves], lag_ratio=0.08), run_time=1.7)
        self.play(FadeIn(field_label), FadeIn(follow_up))
        self.wait(1.2)
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

    def bpsk_mapping(self):
        self.next_section("BPSK mapping")
        title = self.title("Binary phase shift keying")
        subtitle = Text(
            "One bit selects one of two carrier phases",
            font_size=27,
            color=PURPLE,
        ).next_to(title, DOWN, buff=0.18)

        rows = VGroup()
        for bit, phase, sign, y in [
            (0, r"0^\circ", 1, 0.75),
            (1, r"180^\circ", -1, -0.75),
        ]:
            cell = RoundedRectangle(
                width=0.82,
                height=0.72,
                corner_radius=0.10,
                stroke_color=YELLOW if bit else FG,
                stroke_width=2.5,
            )
            digit = Text(str(bit), font_size=32, color=YELLOW if bit else FG).move_to(cell)
            phase_text = MathTex(r"\phi=" + phase, font_size=31, color=PURPLE)
            wave = FunctionGraph(
                lambda x, sign=sign: sign * 0.35 * np.cos(8 * x),
                x_range=[-1.15, 1.15],
                color=PURPLE,
                stroke_width=3.5,
            )
            row = VGroup(VGroup(cell, digit), Arrow(LEFT * 0.45, RIGHT * 0.45, color=MUTED), phase_text, wave)
            row.arrange(RIGHT, buff=0.34).move_to(LEFT * 3.05 + UP * y)
            rows.add(row)

        axes = Axes(
            x_range=[-1.5, 1.5, 1],
            y_range=[-1.0, 1.0, 1],
            x_length=3.5,
            y_length=2.5,
            axis_config={"color": MUTED, "include_ticks": False, "include_numbers": False, "stroke_width": 2},
            tips=True,
        ).shift(RIGHT * 3.65 + DOWN * 0.05)
        i_label = MathTex("I", font_size=29, color=FG).next_to(axes.x_axis, RIGHT, buff=0.10)
        q_label = MathTex("Q", font_size=29, color=FG).next_to(axes.y_axis, UP, buff=0.10)
        points = VGroup(
            Dot(axes.c2p(1, 0), radius=0.12, color=YELLOW),
            Dot(axes.c2p(-1, 0), radius=0.12, color=YELLOW),
        )
        point_labels = VGroup(
            Text("0", font_size=28, color=FG).next_to(points[0], UP, buff=0.15),
            Text("1", font_size=28, color=YELLOW).next_to(points[1], UP, buff=0.15),
        )
        constellation_label = Text("two possible symbols", font_size=24, color=MUTED).next_to(axes, DOWN, buff=0.18)
        timing = VGroup(
            MathTex(r"T_s=T_b", font_size=37, color=CYAN),
            Text("one symbol interval carries one bit", font_size=25, color=FG),
        ).arrange(RIGHT, buff=0.40).to_edge(DOWN, buff=0.50)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.12) for row in rows], lag_ratio=0.20))
        self.play(Create(axes), FadeIn(i_label), FadeIn(q_label), FadeIn(points), FadeIn(point_labels))
        self.play(FadeIn(constellation_label), FadeIn(timing))
        self.wait(1.0)
        self.clear_slide()

    def rate_definitions(self):
        self.next_section("Bit rate and symbol rate")
        title = self.title("Bit rate and symbol rate")

        bit_column = VGroup(
            VGroup(
                MathTex(r"R_b", font_size=46, color=YELLOW),
                Text("bit rate", font_size=28, color=FG),
                MathTex(r"[\mathrm{bit\,s^{-1}}]", font_size=30, color=MUTED),
            ).arrange(RIGHT, buff=0.28),
            VGroup(
                MathTex(r"T_b=\frac{1}{R_b}", font_size=40, color=YELLOW),
                Text("bit duration", font_size=27, color=FG),
                MathTex(r"[\mathrm{s}]", font_size=30, color=MUTED),
            ).arrange(RIGHT, buff=0.28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(LEFT * 3.25 + UP * 1.05)

        symbol_column = VGroup(
            VGroup(
                MathTex(r"R_s", font_size=46, color=CYAN),
                Text("symbol rate", font_size=28, color=FG),
                MathTex(r"[\mathrm{symbol\,s^{-1}}]", font_size=27, color=MUTED),
            ).arrange(RIGHT, buff=0.24),
            VGroup(
                MathTex(r"T_s=\frac{1}{R_s}", font_size=40, color=CYAN),
                Text("symbol duration", font_size=27, color=FG),
                MathTex(r"[\mathrm{s}]", font_size=30, color=MUTED),
            ).arrange(RIGHT, buff=0.24),
            Text("1 baud = 1 symbol per second", font_size=23, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 3.25 + UP * 1.0)

        relation = VGroup(
            VGroup(
                MathTex(r"M", font_size=38, color=PURPLE),
                Text("number of possible symbols", font_size=25, color=FG),
            ).arrange(RIGHT, buff=0.30),
            VGroup(
                MathTex(r"k=\log_2 M", font_size=38, color=PURPLE),
                Text("bits per symbol", font_size=25, color=FG),
            ).arrange(RIGHT, buff=0.30),
            VGroup(
                MathTex(r"R_b=kR_s", font_size=38, color=CYAN),
                MathTex(r"T_s=kT_b", font_size=38, color=YELLOW),
            ).arrange(RIGHT, buff=0.85),
        ).arrange(DOWN, buff=0.28).shift(DOWN * 1.10)
        examples = MathTex(
            r"\mathrm{BPSK:}\ M=2,\ k=1"
            r"\qquad"
            r"\mathrm{QPSK:}\ M=4,\ k=2",
            font_size=31,
            color=FG,
        ).to_edge(DOWN, buff=0.42)

        self.play(FadeIn(title))
        self.play(FadeIn(bit_column, shift=RIGHT * 0.10), FadeIn(symbol_column, shift=LEFT * 0.10))
        self.play(Write(relation), FadeIn(examples))
        self.wait(1.2)
        self.clear_slide()

    def bits_to_symbols(self):
        self.next_section("Bits to symbols")
        title = self.title("More bits per symbol")
        subtitle = Text(
            "QPSK groups the bit stream into pairs",
            font_size=27,
            color=PURPLE,
        ).next_to(title, DOWN, buff=0.18)
        bits = [0, 1, 1, 0, 1, 1, 0, 0]
        bit_text = VGroup(*[Text(str(b), font_size=37, color=YELLOW if b else FG) for b in bits]).arrange(RIGHT, buff=0.48)
        bit_text.shift(UP * 1.15)
        braces = VGroup()
        symbol_labels = VGroup()
        pairs = ["01", "10", "11", "00"]
        phases = [r"90^\circ", r"270^\circ", r"180^\circ", r"0^\circ"]
        for i, (pair, phase) in enumerate(zip(pairs, phases)):
            pair_group = VGroup(bit_text[2 * i], bit_text[2 * i + 1])
            brace = Brace(pair_group, DOWN, buff=0.13, color=MUTED)
            label = MathTex(phase, font_size=29, color=PURPLE).next_to(brace, DOWN, buff=0.14)
            braces.add(brace)
            symbol_labels.add(label)
        rate = MathTex(r"R_s=\frac{R_b}{\log_2 M}", font_size=48, color=CYAN).shift(DOWN * 0.60)
        note = Text("QPSK: 2 bits per symbol", font_size=29, color=FG).next_to(rate, DOWN, buff=0.35)
        caveat = Text("Coding and pulse shaping are omitted here", font_size=23, color=MUTED).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(title), FadeIn(subtitle))
        self.play(LaggedStart(*[FadeIn(b) for b in bit_text], lag_ratio=0.08))
        self.play(Create(braces), FadeIn(symbol_labels))
        self.play(Write(rate), FadeIn(note), FadeIn(caveat))
        self.wait(1.0)
        self.clear_slide()

    def qpsk_waveform(self):
        self.next_section("QPSK waveform")
        title = self.title("QPSK waveform")
        subtitle = Text(
            "Each dibit selects one of four carrier phases",
            font_size=27,
            color=PURPLE,
        ).next_to(title, DOWN, buff=0.18)

        dibits = ["00", "01", "11", "10"]
        phases = [0, PI / 2, PI, 3 * PI / 2]
        phase_labels = [r"0^\circ", r"90^\circ", r"180^\circ", r"270^\circ"]
        width = 10.4
        left = -width / 2
        cell_width = width / len(dibits)

        cells = VGroup()
        phase_texts = VGroup()
        for i, (dibit, phase_label) in enumerate(zip(dibits, phase_labels)):
            center_x = left + (i + 0.5) * cell_width
            cell = Rectangle(
                width=cell_width,
                height=0.68,
                stroke_color=MUTED,
                stroke_width=2,
            ).move_to([center_x, 1.85, 0])
            label = Text(dibit, font_size=30, color=YELLOW).move_to(cell)
            phase_text = MathTex(phase_label, font_size=27, color=PURPLE).next_to(cell, DOWN, buff=0.13)
            cells.add(VGroup(cell, label))
            phase_texts.add(phase_text)

        samples_per_symbol = 120
        points = []
        cycles_per_symbol = 3
        wave_y = -0.80
        for i, phase in enumerate(phases):
            for j in range(samples_per_symbol + 1):
                u = j / samples_per_symbol
                x = left + width * (i + u) / len(dibits)
                carrier_phase = TAU * cycles_per_symbol * (i + u)
                value = np.cos(carrier_phase + phase)
                points.append([x, wave_y + 0.72 * value, 0])
        wave = VMobject(color=PURPLE, stroke_width=3.5).set_points_as_corners(points)
        boundaries = self.symbol_boundaries(len(dibits), width=width, y=wave_y, height=1.75)
        equation = MathTex(
            r"s_k(t)=A\cos(2\pi f_ct+\phi_k)",
            font_size=37,
            color=FG,
        ).shift(DOWN * 2.08)
        timing = MathTex(
            r"M=4,\quad k=2,\quad T_s=2T_b,\quad R_s=R_b/2",
            font_size=32,
            color=CYAN,
        ).to_edge(DOWN, buff=0.42)

        self.play(FadeIn(title), FadeIn(subtitle))
        self.play(LaggedStart(*[FadeIn(cell) for cell in cells], lag_ratio=0.10), FadeIn(phase_texts))
        self.play(Create(boundaries), Create(wave), run_time=1.9)
        self.play(Write(equation), FadeIn(timing))
        self.wait(1.1)
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
        self.next_section("BPSK waveform")
        self.modulation_slide(
            "BPSK waveform",
            "Each bit selects phase 0° or 180°",
            "psk",
            PURPLE,
            "The carrier reverses sign when the selected phase changes by 180°.",
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

    def antenna_radiation(self):
        self.next_section("Antenna radiation")
        title = self.title("An antenna launches an electromagnetic wave")
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
