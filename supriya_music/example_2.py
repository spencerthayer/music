#!/usr/bin/env python3
"""
Supriya Real-time Control Example 2
PyQt6 interface for controlling SuperCollider synths via Supriya
Based on techniques from SCTutorial_3.ipynb - Noise-modulated synthesis
"""

import sys
import supriya
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QSlider,
    QGridLayout,
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


class SupriyaController(QMainWindow):
    """Main window for controlling Supriya synths with noise modulation"""

    def __init__(self):
        super().__init__()
        self.server = None
        self.synth = None
        self.sine_test_synthdef = None
        self.console = Console()

        # Current synth parameters
        self.current_noise_hz = 8.0
        self.current_amp_noise = 12.0
        self.current_note_offset = 50.0

        self.setup_ui()
        self.setup_supriya()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Supriya Real-time Control - Example 2 (Noise Modulated)")
        self.setGeometry(100, 100, 450, 400)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🎛️ Supriya Noise-Modulated Synth Controller")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("QLabel { color: #2E86AB; margin: 10px; }")
        main_layout.addWidget(title)

        # Status display
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("QLabel { color: #666; margin: 5px; }")
        main_layout.addWidget(self.status_label)

        # Synth info
        self.synth_info_label = QLabel("Synth: None active")
        self.synth_info_label.setStyleSheet("QLabel { color: #333; margin: 5px; }")
        main_layout.addWidget(self.synth_info_label)

        # Button layout
        button_layout = QHBoxLayout()

        # Start synth button
        self.start_button = QPushButton("🎵 Start Noise Synth")
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #A23B72;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B84C7A;
            }
            QPushButton:disabled {
                background-color: #CCC;
                color: #666;
            }
        """
        )
        self.start_button.clicked.connect(self.start_synth)
        button_layout.addWidget(self.start_button)

        # Stop synth button
        self.stop_button = QPushButton("🔇 Free Synth")
        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #F18F01;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF9F11;
            }
            QPushButton:disabled {
                background-color: #CCC;
                color: #666;
            }
        """
        )
        self.stop_button.clicked.connect(self.free_synth)
        self.stop_button.setEnabled(False)  # Disabled initially
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        # Slider controls
        sliders_layout = QGridLayout()

        # Noise frequency slider for pitch modulation
        noise_freq_label = QLabel("🎲 Noise Frequency (Hz)")
        noise_freq_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        noise_freq_label.setStyleSheet("QLabel { color: #2E86AB; margin: 5px; }")
        sliders_layout.addWidget(noise_freq_label, 0, 0)

        self.noise_freq_value_label = QLabel("8.0 Hz")
        self.noise_freq_value_label.setStyleSheet(
            "QLabel { color: #333; margin: 5px; }"
        )
        sliders_layout.addWidget(self.noise_freq_value_label, 0, 1)

        self.noise_freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_freq_slider.setMinimum(1)  # 0.1 Hz
        self.noise_freq_slider.setMaximum(500)  # 50.0 Hz
        self.noise_freq_slider.setValue(80)  # 8.0 Hz
        self.noise_freq_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2E86AB, stop:1 #1A5F7A);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """
        )
        self.noise_freq_slider.valueChanged.connect(self.on_noise_freq_changed)
        sliders_layout.addWidget(self.noise_freq_slider, 1, 0, 1, 2)

        # Amplitude noise frequency slider
        amp_noise_label = QLabel("🔊 Amp Noise Frequency")
        amp_noise_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        amp_noise_label.setStyleSheet("QLabel { color: #A23B72; margin: 5px; }")
        sliders_layout.addWidget(amp_noise_label, 2, 0)

        self.amp_noise_value_label = QLabel("12.0 Hz")
        self.amp_noise_value_label.setStyleSheet("QLabel { color: #333; margin: 5px; }")
        sliders_layout.addWidget(self.amp_noise_value_label, 2, 1)

        self.amp_noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.amp_noise_slider.setMinimum(1)  # 0.1 Hz
        self.amp_noise_slider.setMaximum(500)  # 50.0 Hz
        self.amp_noise_slider.setValue(120)  # 12.0 Hz
        self.amp_noise_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A23B72, stop:1 #7A2B54);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """
        )
        self.amp_noise_slider.valueChanged.connect(self.on_amp_noise_changed)
        sliders_layout.addWidget(self.amp_noise_slider, 3, 0, 1, 2)

        # Note offset slider
        note_offset_label = QLabel("🎼 Note Offset (MIDI)")
        note_offset_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        note_offset_label.setStyleSheet("QLabel { color: #F18F01; margin: 5px; }")
        sliders_layout.addWidget(note_offset_label, 4, 0)

        self.note_offset_value_label = QLabel("50.0")
        self.note_offset_value_label.setStyleSheet(
            "QLabel { color: #333; margin: 5px; }"
        )
        sliders_layout.addWidget(self.note_offset_value_label, 4, 1)

        self.note_offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.note_offset_slider.setMinimum(200)  # 20.0 MIDI
        self.note_offset_slider.setMaximum(900)  # 90.0 MIDI
        self.note_offset_slider.setValue(500)  # 50.0 MIDI
        self.note_offset_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F18F01, stop:1 #D17A01);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """
        )
        self.note_offset_slider.valueChanged.connect(self.on_note_offset_changed)
        sliders_layout.addWidget(self.note_offset_slider, 5, 0, 1, 2)

        main_layout.addLayout(sliders_layout)

        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Click 'Start Noise Synth' to create a noise-modulated synthesizer\n"
            "2. Use 'Noise Frequency' to control pitch randomness speed\n"
            "3. Use 'Amp Noise Frequency' to control volume tremolo speed\n"
            "4. Use 'Note Offset' to control the base MIDI note range\n"
            "5. Click 'Free Synth' to stop and remove the synth\n"
            "6. Check the terminal for detailed Supriya code examples"
        )
        instructions.setStyleSheet(
            "QLabel { color: #555; margin: 20px; line-height: 1.4; }"
        )
        main_layout.addWidget(instructions)

        # Spacer
        main_layout.addStretch()

    def show_code_panel(self, title, code, description=None):
        """Display a panel with relevant Supriya code"""
        # Display description if provided
        if description:
            self.console.print(f"[dim]{description}[/dim]")

        # Display syntax-highlighted code in a panel
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        self.console.print(
            Panel(
                syntax, title=f"📝 {title}", border_style="bright_cyan", padding=(1, 2)
            )
        )
        self.console.print()  # Add spacing

    def setup_supriya(self):
        """Initialize Supriya server and SynthDef"""
        try:
            rprint("[bold blue]🎵 Initializing Supriya server...[/bold blue]")

            # Show server setup code
            server_code = """# Create and boot SuperCollider server
server = supriya.Server()
server.boot()"""
            self.show_code_panel(
                "Server Setup",
                server_code,
                "Creating and booting the SuperCollider audio server:",
            )

            # Create and boot server
            self.server = supriya.Server()
            self.server.boot()

            # Show advanced SynthDef creation code
            synthdef_code = """# Define noise-modulated SynthDef with controllable parameters
@supriya.synthdef()
def sine_test(noise_hz=8, amp_noise_hz=12, note_offset=50):
    # Generate random MIDI note numbers (note_offset to note_offset+16 range)
    note = ((supriya.ugens.LFNoise0.kr(frequency=noise_hz) + 1) * 8) + note_offset
    
    # Convert MIDI note to frequency in Hz
    freq = note.midi_to_hz()
    
    # Create controllable amplitude modulation
    amp = (supriya.ugens.LFNoise1.kr(frequency=amp_noise_hz) * 0.01 + 0.02)
    
    # Generate stereo sine wave with frequency doubling
    sig = supriya.ugens.SinOsc.ar(frequency=[freq, freq * 2]) * amp
    
    # Output to stereo speakers
    supriya.ugens.Out.ar(bus=0, source=sig)

# Add SynthDef to server
server.add_synthdefs(sine_test)"""
            self.show_code_panel(
                "Advanced SynthDef Creation",
                synthdef_code,
                "Creating a noise-modulated synthesizer with pitch and amplitude variation:",
            )

            # Define the noise-modulated SynthDef with controllable parameters
            @supriya.synthdef()
            def sine_test(noise_hz=8, amp_noise_hz=12, note_offset=50):
                note = (
                    (supriya.ugens.LFNoise0.kr(frequency=noise_hz) + 1) * 8
                ) + note_offset
                freq = note.midi_to_hz()
                amp = supriya.ugens.LFNoise1.kr(frequency=amp_noise_hz) * 0.01 + 0.02
                sig = supriya.ugens.SinOsc.ar(frequency=[freq, freq * 2]) * amp
                supriya.ugens.Out.ar(bus=0, source=sig)

            # Add SynthDef to server
            self.sine_test_synthdef = sine_test
            self.server.add_synthdefs(self.sine_test_synthdef)

            self.update_status("✅ Server ready - SuperCollider connected")
            rprint(
                "[bold green]✅ Supriya server initialized successfully![/bold green]"
            )

        except Exception as e:
            error_msg = f"❌ Failed to initialize Supriya: {str(e)}"
            self.update_status(error_msg)
            rprint(f"[bold red]{error_msg}[/bold red]")

            # Show error dialog
            QMessageBox.critical(
                self,
                "Supriya Error",
                f"Failed to connect to SuperCollider server:\n\n{str(e)}\n\n"
                "Make sure SuperCollider is installed and try again.\n\n"
                "Application will now exit.",
            )

            # Exit the application since server boot failed
            QApplication.quit()
            sys.exit(1)

    def on_noise_freq_changed(self, value):
        """Handle noise frequency slider changes"""
        # Convert slider value (1-500) to frequency (0.1-50.0 Hz)
        freq = value / 10.0
        self.current_noise_hz = freq
        self.noise_freq_value_label.setText(f"{freq:.1f} Hz")

        # Update synth in real-time if it's running
        if self.synth is not None:
            try:
                # Show real-time parameter update code (only on significant changes)
                if value % 50 == 0:  # Show occasionally
                    update_code = f"""# Real-time noise frequency control
synth.set(noise_hz={freq:.1f})  # Update pitch randomness speed

# Higher values = faster pitch changes
# Lower values = slower, more gradual pitch evolution"""
                    self.show_code_panel(
                        "Pitch Modulation Control",
                        update_code,
                        "Controlling the speed of pitch randomness:",
                    )

                self.synth.set(noise_hz=freq)
                self.update_synth_info()
                rprint(f"[cyan]🎲 Noise frequency updated to {freq:.1f} Hz[/cyan]")
            except Exception as e:
                rprint(f"[red]❌ Error updating noise frequency: {e}[/red]")

    def on_amp_noise_changed(self, value):
        """Handle amplitude noise frequency slider changes"""
        # Convert slider value (1-500) to frequency (0.1-50.0 Hz)
        freq = value / 10.0
        self.current_amp_noise = freq
        self.amp_noise_value_label.setText(f"{freq:.1f} Hz")

        # Update synth in real-time if it's running
        if self.synth is not None:
            try:
                # Show real-time parameter update code (only on significant changes)
                if value % 50 == 0:  # Show occasionally
                    update_code = f"""# Real-time amplitude modulation control
synth.set(amp_noise_hz={freq:.1f})  # Update volume tremolo speed

# Higher values = faster amplitude changes
# Lower values = slower, more subtle amplitude modulation"""
                    self.show_code_panel(
                        "Amplitude Modulation Control",
                        update_code,
                        "Controlling the speed of amplitude tremolo:",
                    )

                self.synth.set(amp_noise_hz=freq)
                self.update_synth_info()
                rprint(
                    f"[magenta]🔊 Amp noise frequency updated to {freq:.1f} Hz[/magenta]"
                )
            except Exception as e:
                rprint(f"[red]❌ Error updating amp noise frequency: {e}[/red]")

    def on_note_offset_changed(self, value):
        """Handle note offset slider changes"""
        # Convert slider value (200-900) to MIDI note (20.0-90.0)
        note = value / 10.0
        self.current_note_offset = note
        self.note_offset_value_label.setText(f"{note:.1f}")

        # Update synth in real-time if it's running
        if self.synth is not None:
            try:
                # Show real-time parameter update code (only on significant changes)
                if value % 50 == 0:  # Show occasionally
                    update_code = f"""# Real-time note offset control
synth.set(note_offset={note:.1f})  # Update base MIDI note range

# This shifts the entire pitch range:
# note_offset=50 → MIDI notes 50-66 (D3 to F#4)
# note_offset=60 → MIDI notes 60-76 (C4 to E5)
# note_offset=40 → MIDI notes 40-56 (E2 to G#3)"""
                    self.show_code_panel(
                        "Note Range Control",
                        update_code,
                        "Controlling the base MIDI note range:",
                    )

                self.synth.set(note_offset=note)
                self.update_synth_info()
                rprint(
                    f"[yellow]🎼 Note offset updated to {note:.1f} (range: {note:.1f}-{note+16:.1f})[/yellow]"
                )
            except Exception as e:
                rprint(f"[red]❌ Error updating note offset: {e}[/red]")

    def update_synth_info(self):
        """Update the synth info display"""
        if self.synth is not None:
            self.synth_info_label.setText(
                f"Synth: Noise-modulated (pitch: {self.current_noise_hz:.1f}Hz, amp: {self.current_amp_noise:.1f}Hz, notes: {self.current_note_offset:.1f}-{self.current_note_offset+16:.1f})"
            )
            self.update_status(
                f"🎵 Noise synth playing - pitch mod: {self.current_noise_hz:.1f}Hz, note range: {self.current_note_offset:.1f}-{self.current_note_offset+16:.1f}"
            )

    def start_synth(self):
        """Start a noise-modulated synth with current slider values"""
        try:
            if self.synth is not None:
                rprint(
                    "[yellow]⚠️  Synth already running, freeing existing synth first[/yellow]"
                )
                self.synth.free()

            rprint(
                f"[bold cyan]🎵 Starting noise-modulated synth (pitch noise: {self.current_noise_hz:.1f}Hz)...[/bold cyan]"
            )

            # Show synth creation code
            create_code = f"""# Create noise-modulated synth instance with all parameters
synth = server.add_synth(
    sine_test,  # Our noise-modulated SynthDef
    noise_hz={self.current_noise_hz:.1f},        # Control pitch randomness speed
    amp_noise_hz={self.current_amp_noise:.1f},   # Control amplitude tremolo speed
    note_offset={self.current_note_offset:.1f}   # Control base MIDI note range
)

# This synth will:
# - Generate random pitches between MIDI notes {self.current_note_offset:.1f}-{self.current_note_offset+16:.1f}
# - Use LFNoise0 for stepped pitch changes at {self.current_noise_hz:.1f} Hz
# - Use LFNoise1 for smooth amplitude modulation at {self.current_amp_noise:.1f} Hz
# - Output stereo with frequency doubling (fundamental + octave)"""
            self.show_code_panel(
                "Advanced Noise Synth Creation",
                create_code,
                "Creating a fully controllable noise-modulated synthesizer:",
            )

            # Create synth with current slider parameters
            self.synth = self.server.add_synth(
                self.sine_test_synthdef,
                noise_hz=self.current_noise_hz,
                amp_noise_hz=self.current_amp_noise,
                note_offset=self.current_note_offset,
            )

            # Update UI
            self.update_synth_info()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            # Enable sliders for real-time control
            self.noise_freq_slider.setEnabled(True)
            self.amp_noise_slider.setEnabled(True)
            self.note_offset_slider.setEnabled(True)

            rprint(
                "[bold green]✅ Noise-modulated synth started successfully![/bold green]"
            )
            rprint(f"[dim]Server tree: {self.server.query_tree()}[/dim]")

        except Exception as e:
            error_msg = f"❌ Failed to start synth: {str(e)}"
            self.update_status(error_msg)
            rprint(f"[bold red]{error_msg}[/bold red]")

    def free_synth(self):
        """Free (stop) the current synth"""
        try:
            if self.synth is None:
                rprint("[yellow]⚠️  No synth to free[/yellow]")
                return

            rprint("[bold yellow]🔇 Freeing noise-modulated synth...[/bold yellow]")

            # Show synth cleanup code
            cleanup_code = """# Stop and remove noise synth from server
synth.free()  # Immediately stops all oscillators and noise generators

# The complex synth with multiple UGens is now cleaned up
# All LFNoise0, LFNoise1, SinOsc, and Out UGens are freed
synth = None

# Server resources are available for new synths"""
            self.show_code_panel(
                "Complex Synth Cleanup",
                cleanup_code,
                "Properly stopping and cleaning up noise-modulated synth:",
            )

            # Free the synth
            self.synth.free()
            self.synth = None

            # Update UI
            self.update_status("🔇 Noise synth freed - ready to start new synth")
            self.synth_info_label.setText("Synth: None active")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            # Keep sliders enabled for setting next synth parameters

            rprint(
                "[bold green]✅ Noise-modulated synth freed successfully![/bold green]"
            )
            rprint(f"[dim]Server tree: {self.server.query_tree()}[/dim]")

        except Exception as e:
            error_msg = f"❌ Failed to free synth: {str(e)}"
            self.update_status(error_msg)
            rprint(f"[bold red]{error_msg}[/bold red]")

    def update_status(self, message):
        """Update the status label"""
        self.status_label.setText(f"Status: {message}")
        rprint(f"[dim]Status: {message}[/dim]")

    def closeEvent(self, event):
        """Handle application closure"""
        rprint("[bold blue]🔄 Shutting down Supriya controller...[/bold blue]")

        # Free any active synth
        if self.synth is not None:
            try:
                self.synth.free()
                rprint("[green]✅ Noise synth freed on shutdown[/green]")
            except Exception as e:
                rprint(f"[red]❌ Error freeing synth on shutdown: {e}[/red]")

        # Quit server
        if self.server is not None:
            try:
                self.server.quit()
                rprint("[green]✅ Supriya server shutdown[/green]")
            except Exception as e:
                rprint(f"[red]❌ Error shutting down server: {e}[/red]")

        rprint("[bold blue]👋 Goodbye![/bold blue]")
        event.accept()


def main():
    """Main application entry point"""
    rprint("[bold blue]🎛️ Starting Supriya Real-time Control Example 2[/bold blue]")

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Supriya Noise Controller")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Strudel Music")

    # Create and show main window
    controller = SupriyaController()
    controller.show()

    # Run the application
    try:
        exit_code = app.exec()
        rprint(f"[dim]Application exited with code: {exit_code}[/dim]")
        return exit_code
    except KeyboardInterrupt:
        rprint("[yellow]⚠️  Interrupted by user[/yellow]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
