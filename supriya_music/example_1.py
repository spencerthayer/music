#!/usr/bin/env python3
"""
Supriya Real-time Control Example 1
PyQt6 interface for controlling SuperCollider synths via Supriya
Based on techniques from SCTutorial_2.ipynb
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


class SupriyaController(QMainWindow):
    """Main window for controlling Supriya synths"""

    def __init__(self):
        super().__init__()
        self.server = None
        self.synth = None
        self.sine_synthdef = None

        # Current synth parameters
        self.current_frequency = 440
        self.current_amplitude = 0.1

        self.setup_ui()
        self.setup_supriya()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Supriya Real-time Control - Example 1")
        self.setGeometry(100, 100, 400, 300)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🎵 Supriya Synth Controller")
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
        self.start_button = QPushButton("🔊 Start Synth (440 Hz)")
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

        # Frequency slider
        freq_label = QLabel("🎵 Frequency (Hz)")
        freq_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        freq_label.setStyleSheet("QLabel { color: #2E86AB; margin: 5px; }")
        sliders_layout.addWidget(freq_label, 0, 0)

        self.freq_value_label = QLabel("440 Hz")
        self.freq_value_label.setStyleSheet("QLabel { color: #333; margin: 5px; }")
        sliders_layout.addWidget(self.freq_value_label, 0, 1)

        self.freq_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_slider.setMinimum(110)  # A2
        self.freq_slider.setMaximum(1760)  # A6
        self.freq_slider.setValue(440)  # A4
        self.freq_slider.setStyleSheet(
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
        self.freq_slider.valueChanged.connect(self.on_frequency_changed)
        sliders_layout.addWidget(self.freq_slider, 1, 0, 1, 2)

        # Amplitude slider
        amp_label = QLabel("🔊 Amplitude")
        amp_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        amp_label.setStyleSheet("QLabel { color: #A23B72; margin: 5px; }")
        sliders_layout.addWidget(amp_label, 2, 0)

        self.amp_value_label = QLabel("0.10")
        self.amp_value_label.setStyleSheet("QLabel { color: #333; margin: 5px; }")
        sliders_layout.addWidget(self.amp_value_label, 2, 1)

        self.amp_slider = QSlider(Qt.Orientation.Horizontal)
        self.amp_slider.setMinimum(1)  # 0.01
        self.amp_slider.setMaximum(50)  # 0.50
        self.amp_slider.setValue(10)  # 0.10
        self.amp_slider.setStyleSheet(
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
        self.amp_slider.valueChanged.connect(self.on_amplitude_changed)
        sliders_layout.addWidget(self.amp_slider, 3, 0, 1, 2)

        main_layout.addLayout(sliders_layout)

        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "1. Click 'Start Synth' to create a sine wave\n"
            "2. Use sliders to control frequency and amplitude in real-time\n"
            "3. Click 'Free Synth' to stop and remove the synth\n"
            "4. Check the terminal for detailed Supriya output"
        )
        instructions.setStyleSheet(
            "QLabel { color: #555; margin: 20px; line-height: 1.4; }"
        )
        main_layout.addWidget(instructions)

        # Spacer
        main_layout.addStretch()

    def setup_supriya(self):
        """Initialize Supriya server and SynthDef"""
        try:
            rprint("[bold blue]🎵 Initializing Supriya server...[/bold blue]")

            # Create and boot server
            self.server = supriya.Server()
            self.server.boot()

            # Define the sine wave SynthDef (using new decorator syntax from tutorial)
            @supriya.synthdef()
            def sine_synth(amplitude=0.1, frequency=440):
                sine = supriya.ugens.SinOsc.ar(frequency=frequency)
                scaled_sine = sine * amplitude
                supriya.ugens.Out.ar(bus=0, source=scaled_sine)

            # Add SynthDef to server
            self.sine_synthdef = sine_synth
            self.server.add_synthdefs(self.sine_synthdef)

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
                "Make sure SuperCollider is installed and try again.",
            )

    def on_frequency_changed(self, value):
        """Handle frequency slider changes"""
        self.current_frequency = value
        self.freq_value_label.setText(f"{value} Hz")

        # Update synth in real-time if it's running
        if self.synth is not None:
            try:
                self.synth.set(frequency=value)
                self.update_synth_info()
                rprint(f"[cyan]🎵 Frequency updated to {value} Hz[/cyan]")
            except Exception as e:
                rprint(f"[red]❌ Error updating frequency: {e}[/red]")

    def on_amplitude_changed(self, value):
        """Handle amplitude slider changes"""
        # Convert slider value (1-50) to amplitude (0.01-0.50)
        amplitude = value / 100.0
        self.current_amplitude = amplitude
        self.amp_value_label.setText(f"{amplitude:.2f}")

        # Update synth in real-time if it's running
        if self.synth is not None:
            try:
                self.synth.set(amplitude=amplitude)
                self.update_synth_info()
                rprint(f"[magenta]🔊 Amplitude updated to {amplitude:.2f}[/magenta]")
            except Exception as e:
                rprint(f"[red]❌ Error updating amplitude: {e}[/red]")

    def update_synth_info(self):
        """Update the synth info display"""
        if self.synth is not None:
            self.synth_info_label.setText(
                f"Synth: {self.current_frequency} Hz sine wave (amplitude: {self.current_amplitude:.2f})"
            )
            self.update_status(
                f"🎵 Synth playing at {self.current_frequency} Hz, amp: {self.current_amplitude:.2f}"
            )

    def start_synth(self):
        """Start a sine wave synth with current slider values"""
        try:
            if self.synth is not None:
                rprint(
                    "[yellow]⚠️  Synth already running, freeing existing synth first[/yellow]"
                )
                self.synth.free()

            rprint(
                f"[bold cyan]🎵 Starting synth at {self.current_frequency} Hz, amplitude {self.current_amplitude:.2f}...[/bold cyan]"
            )

            # Create synth with current slider parameters
            self.synth = self.server.add_synth(
                self.sine_synthdef,
                amplitude=self.current_amplitude,
                frequency=self.current_frequency,
            )

            # Update UI
            self.update_synth_info()
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

            # Enable sliders for real-time control
            self.freq_slider.setEnabled(True)
            self.amp_slider.setEnabled(True)

            rprint("[bold green]✅ Synth started successfully![/bold green]")
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

            rprint("[bold yellow]🔇 Freeing synth...[/bold yellow]")

            # Free the synth
            self.synth.free()
            self.synth = None

            # Update UI
            self.update_status("🔇 Synth freed - ready to start new synth")
            self.synth_info_label.setText("Synth: None active")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

            # Keep sliders enabled for setting next synth parameters
            # (they still update the current_* values)

            rprint("[bold green]✅ Synth freed successfully![/bold green]")
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
                rprint("[green]✅ Synth freed on shutdown[/green]")
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
    rprint("[bold blue]🎵 Starting Supriya Real-time Control Example 1[/bold blue]")

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Supriya Controller")
    app.setApplicationVersion("1.0")
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
