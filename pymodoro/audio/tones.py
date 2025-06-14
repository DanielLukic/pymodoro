import math
import wave
import struct
import tempfile
import os
from typing import List, Tuple

class ToneGenerator:
    """Generate pleasant chime tones for timer events"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.temp_files = []
    
    def generate_sine_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> List[float]:
        """Generate a sine wave at given frequency and duration"""
        samples = []
        for i in range(int(self.sample_rate * duration)):
            t = i / self.sample_rate
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
            samples.append(sample)
        return samples
    
    def apply_envelope(self, samples: List[float], attack: float = 0.1, decay: float = 0.2, 
                      sustain: float = 0.7, release: float = 0.3) -> List[float]:
        """Apply ADSR envelope to samples for natural sound"""
        total_samples = len(samples)
        attack_samples = int(attack * total_samples)
        decay_samples = int(decay * total_samples)
        release_samples = int(release * total_samples)
        sustain_samples = total_samples - attack_samples - decay_samples - release_samples
        
        enveloped = []
        
        for i, sample in enumerate(samples):
            if i < attack_samples:
                # Attack phase
                envelope = i / attack_samples
            elif i < attack_samples + decay_samples:
                # Decay phase
                envelope = 1.0 - (1.0 - sustain) * (i - attack_samples) / decay_samples
            elif i < attack_samples + decay_samples + sustain_samples:
                # Sustain phase
                envelope = sustain
            else:
                # Release phase
                envelope = sustain * (1.0 - (i - attack_samples - decay_samples - sustain_samples) / release_samples)
            
            enveloped.append(sample * envelope)
        
        return enveloped
    
    def create_chord(self, frequencies: List[float], duration: float) -> List[float]:
        """Create a chord by mixing multiple frequencies"""
        chord_samples = []
        for freq in frequencies:
            samples = self.generate_sine_wave(freq, duration, amplitude=0.3)
            if not chord_samples:
                chord_samples = samples
            else:
                for i in range(len(samples)):
                    chord_samples[i] += samples[i]
        
        # Normalize to prevent clipping
        max_amplitude = max(abs(s) for s in chord_samples)
        if max_amplitude > 1.0:
            chord_samples = [s / max_amplitude for s in chord_samples]
        
        return self.apply_envelope(chord_samples)
    
    def save_wav_file(self, samples: List[float], filename: str) -> str:
        """Save samples as WAV file"""
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            
            # Convert float samples to 16-bit integers
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', int(sample * 32767)))
        
        return filename
    
    def create_chime_sounds(self) -> dict:
        """Create pleasant chime sounds for different timer events"""
        temp_dir = tempfile.gettempdir()
        sounds = {}
        
        # Work start - Uplifting major chord (C major)
        work_chord = [261.63, 329.63, 392.00]  # C4, E4, G4
        work_samples = self.create_chord(work_chord, 1.0)
        work_file = os.path.join(temp_dir, 'pymodoro_work_start.wav')
        sounds['work_start'] = self.save_wav_file(work_samples, work_file)
        self.temp_files.append(work_file)
        
        # Break start - Relaxing minor chord (A minor)
        break_chord = [220.00, 261.63, 329.63]  # A3, C4, E4
        break_samples = self.create_chord(break_chord, 1.2)
        break_file = os.path.join(temp_dir, 'pymodoro_break_start.wav')
        sounds['break_start'] = self.save_wav_file(break_samples, break_file)
        self.temp_files.append(break_file)
        
        # Session complete - Achievement sound (Perfect fifth + octave)
        complete_chord = [261.63, 392.00, 523.25]  # C4, G4, C5
        complete_samples = self.create_chord(complete_chord, 1.5)
        complete_file = os.path.join(temp_dir, 'pymodoro_session_complete.wav')
        sounds['session_complete'] = self.save_wav_file(complete_samples, complete_file)
        self.temp_files.append(complete_file)
        
        # Timer finish - Gentle notification (Single tone with harmonics)
        finish_chord = [440.00, 880.00]  # A4, A5
        finish_samples = self.create_chord(finish_chord, 0.8)
        finish_file = os.path.join(temp_dir, 'pymodoro_timer_finish.wav')
        sounds['timer_finish'] = self.save_wav_file(finish_samples, finish_file)
        self.temp_files.append(finish_file)
        
        return sounds
    
    def cleanup(self):
        """Clean up temporary sound files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass
        self.temp_files.clear() 