import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import hsv_to_rgb

# Set up the dark theme for maximum contrast
plt.style.use('dark_background')

class ColorfulIllusion:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='black')
        self.ax.set_facecolor('black')
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
    def create_rainbow_spiral(self, t):
        """Create a colorful hypnotic spiral pattern"""
        # Clear previous frame
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')
        
        # Parameters for the illusion
        n_rings = 16
        points_per_ring = 200
        max_radius = 0.95
        
        # Create concentric rings with rainbow colors
        for ring in range(n_rings):
            radius = max_radius * (ring + 1) / n_rings
            theta = np.linspace(0, 2*np.pi, points_per_ring)
            
            # Create waving effect
            wave_radius = radius * (1 + 0.1 * np.sin(8 * theta + t))
            
            x = wave_radius * np.cos(theta + t * (1 if ring % 2 == 0 else -1))
            y = wave_radius * np.sin(theta + t * (1 if ring % 2 == 0 else -1))
            
            # Rainbow colors based on angle and time
            hues = (theta / (2*np.pi) + t * 0.1 + ring * 0.05) % 1
            colors = hsv_to_rgb(np.column_stack([hues, np.ones_like(hues), np.ones_like(hues)]))
            
            size = 40 + 30 * np.sin(t * 2 + ring)
            
            self.ax.scatter(x, y, s=size, c=colors, alpha=0.9, edgecolors='none')
        
        # Add radiating lines for the spinning effect
        n_lines = 48
        for i in range(n_lines):
            angle = 2 * np.pi * i / n_lines + t
            x_line = [0, 0.9 * np.cos(angle)]
            y_line = [0, 0.9 * np.sin(angle)]
            line_hue = (t * 0.2 + i / n_lines) % 1
            line_color = hsv_to_rgb([line_hue, 0.8, 1])
            self.ax.plot(x_line, y_line, color=line_color, alpha=0.4, linewidth=1.5)
            
        # Add central pulsating sphere
        central_size = 70 + 40 * np.sin(t * 8)
        central_hue = (t * 0.3) % 1
        central_color = hsv_to_rgb([central_hue, 0.9, 1])
        self.ax.scatter(0, 0, s=central_size, color=central_color, alpha=0.9, edgecolors='none')
        
        # Add rotating dots for motion effect
        n_dots = 36
        for i in range(n_dots):
            dot_angle = 2 * np.pi * i / n_dots - t * 2
            dot_radius = 0.75 + 0.1 * np.sin(t * 3)
            x_dot = dot_radius * np.cos(dot_angle)
            y_dot = dot_radius * np.sin(dot_angle)
            dot_hue = (t * 0.15 + i / n_dots) % 1
            dot_color = hsv_to_rgb([dot_hue, 0.9, 1])
            self.ax.scatter(x_dot, y_dot, s=50, color=dot_color, alpha=0.9, edgecolors='none')

    def create_color_zoom(self, t):
        """Create a colorful zooming illusion effect"""
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')
        
        # Create concentric circles with rainbow colors
        n_circles = 24
        for i in range(n_circles):
            radius = 0.05 + 0.85 * ((i + t*2) % n_circles) / n_circles
            circle_hue = (t * 0.1 + i / n_circles) % 1
            circle_color = hsv_to_rgb([circle_hue, 0.8, 1])
            circle = plt.Circle((0, 0), radius, fill=False, 
                               color=circle_color, alpha=0.7, linewidth=2.5)
            self.ax.add_patch(circle)
            
        # Add radiating lines with gradient colors
        n_lines = 60
        for i in range(n_lines):
            angle = 2 * np.pi * i / n_lines
            x_line = [0, 1.5 * np.cos(angle)]
            y_line = [0, 1.5 * np.sin(angle)]
            line_hue = (t * 0.2 + i / n_lines) % 1
            line_color = hsv_to_rgb([line_hue, 0.8, 1])
            self.ax.plot(x_line, y_line, color=line_color, alpha=0.5, linewidth=2)

        # Add central pulsating element
        central_size = 100 + 50 * np.sin(t * 5)
        central_hue = (t * 0.3) % 1
        central_color = hsv_to_rgb([central_hue, 0.9, 1])
        self.ax.scatter(0, 0, s=central_size, color=central_color, alpha=0.8, edgecolors='white', linewidth=1)

    def create_rainbow_waves(self, t):
        """Create colorful wave patterns"""
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')
        
        # Create grid of points
        n_points = 40
        x = np.linspace(-1, 1, n_points)
        y = np.linspace(-1, 1, n_points)
        X, Y = np.meshgrid(x, y)
        
        # Create wave pattern with color
        Z = np.sin(8 * (X + 0.5 * np.sin(t))) * np.sin(8 * (Y + 0.5 * np.cos(t)))
        
        # Convert wave pattern to colors
        hues = (0.7 + 0.3 * Z + t * 0.1) % 1
        saturations = 0.8 + 0.2 * np.sin(X * Y * 10 + t)
        values = 0.9 + 0.1 * Z
        
        # Convert HSV to RGB
        hsv_colors = np.dstack((hues, saturations, values))
        rgb_colors = hsv_to_rgb(hsv_colors)
        
        # Plot points with color based on wave pattern
        sizes = 60 + 50 * Z
        self.ax.scatter(X, Y, s=sizes, c=rgb_colors.reshape(-1, 3), alpha=0.9, edgecolors='none')
        
        # Add rotating overlay pattern with colors
        n_lines = 30
        for i in range(n_lines):
            angle = 2 * np.pi * i / n_lines + t
            x_line = [-np.cos(angle), np.cos(angle)]
            y_line = [-np.sin(angle), np.sin(angle)]
            line_hue = (t * 0.25 + i / n_lines) % 1
            line_color = hsv_to_rgb([line_hue, 0.7, 1])
            self.ax.plot(x_line, y_line, color=line_color, alpha=0.4, linewidth=1.5)

    def create_morphing_grid(self, t):
        """Create a morphing and rotating grid illusion"""
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')

        grid_size = 25
        x = np.linspace(-1.2, 1.2, grid_size)
        y = np.linspace(-1.2, 1.2, grid_size)
        xx, yy = np.meshgrid(x, y)

        # Morphing effect based on distance from center and time
        dist = np.sqrt(xx**2 + yy**2)
        angle = np.arctan2(yy, xx)
        
        scale = 0.6 + 0.4 * np.sin(dist * 6 - t * 3)
        
        xx_morphed = xx * scale
        yy_morphed = yy * scale
        
        # Rotation effect
        angle_rot = t * 0.4
        xx_rot = xx_morphed * np.cos(angle_rot) - yy_morphed * np.sin(angle_rot)
        yy_rot = xx_morphed * np.sin(angle_rot) + yy_morphed * np.cos(angle_rot)

        # Coloring based on distance and time
        hues = (dist * 0.4 + t * 0.1) % 1
        saturations = 0.7 + 0.3 * np.sin(angle * 5 + t * 2)
        colors = hsv_to_rgb(np.dstack([hues, saturations, np.ones_like(hues)]))

        # Varying sizes for a more dynamic effect
        sizes = 20 + 15 * np.sin(dist * 8 - t * 4)

        self.ax.scatter(xx_rot, yy_rot, s=sizes, c=colors.reshape(-1, 3), marker='o', alpha=0.9)

    def create_in_out_illusion(self, t):
        """Create an in-out zooming illusion effect"""
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')

        # Create concentric circles with dynamic zooming effect
        n_circles = 24
        for i in range(n_circles):
            # Radius oscillates to create in-out effect
            radius = 0.05 + 0.85 * (np.sin(t * 2 + i * 0.3) + 1) / 2
            circle_hue = (t * 0.1 + i / n_circles) % 1
            circle_color = hsv_to_rgb([circle_hue, 0.8, 1])
            circle = plt.Circle((0, 0), radius, fill=False, 
                               color=circle_color, alpha=0.7, linewidth=2.5)
            self.ax.add_patch(circle)

        # Add radiating lines with gradient colors
        n_lines = 60
        for i in range(n_lines):
            angle = 2 * np.pi * i / n_lines
            x_line = [0, 1.5 * np.cos(angle)]
            y_line = [0, 1.5 * np.sin(angle)]
            line_hue = (t * 0.2 + i / n_lines) % 1
            line_color = hsv_to_rgb([line_hue, 0.8, 1])
            self.ax.plot(x_line, y_line, color=line_color, alpha=0.5, linewidth=2)

        # Add central pulsating element
        central_size = 100 + 50 * np.sin(t * 5)
        central_hue = (t * 0.3) % 1
        central_color = hsv_to_rgb([central_hue, 0.9, 1])
        self.ax.scatter(0, 0, s=central_size, color=central_color, alpha=0.8, edgecolors='white', linewidth=1)

    def create_pure_in_out_wave(self, t):
        """Create a pure in-out wave illusion without rotation"""
        self.ax.clear()
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor('black')

        # Concentric circles with pure in-out motion
        n_circles = 20
        for i in range(n_circles):
            # Radius oscillates to create in-out effect
            radius = 0.05 + 0.85 * (np.sin(t * 2 + i * 0.3) + 1) / 2
            circle_hue = (t * 0.1 + i / n_circles) % 1
            circle_color = hsv_to_rgb([circle_hue, 0.8, 1])
            circle = plt.Circle((0, 0), radius, fill=False, 
                               color=circle_color, alpha=0.7, linewidth=2)
            self.ax.add_patch(circle)

        # Central pulsating element for focus
        central_size = 100 + 50 * np.sin(t * 4)
        central_hue = (t * 0.3) % 1
        central_color = hsv_to_rgb([central_hue, 0.9, 1])
        self.ax.scatter(0, 0, s=central_size, color=central_color, alpha=0.8, edgecolors='white', linewidth=1)

    def animate(self, frame):
        """Animation function"""
        t = frame * 0.05
        
        # Cycle through different illusions
        illusion_type = int(t) % 4
        if illusion_type == 0:
            self.create_rainbow_spiral(t)
            plt.title("RAINBOW HYPNOTIC SPIRAL", color='white', fontsize=16, pad=20)
        elif illusion_type == 1:
            self.create_color_zoom(t)
            plt.title("COLOR ZOOM TUNNEL", color='white', fontsize=16, pad=20)
        elif illusion_type == 2:
            self.create_rainbow_waves(t)
            plt.title("RAINBOW WAVE PATTERN", color='white', fontsize=16, pad=20)
        else:
            self.create_pure_in_out_wave(t)
            plt.title("IN-OUT WAVE ILLUSION", color='white', fontsize=16, pad=20)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Generate mesmerizing illusions.")
    parser.add_argument('--illusion', type=str, default='spiral', 
                        choices=['spiral', 'zoom', 'grid', 'waves', 'all'],
                        help='The type of illusion to display (spiral, zoom, grid, waves, or all).')
    args = parser.parse_args()

    illusion_generator = ColorfulIllusion()

    if args.illusion == 'all':
        illusions = [
            illusion_generator.create_rainbow_spiral,
            illusion_generator.create_color_zoom,
            illusion_generator.create_morphing_grid,
            illusion_generator.create_rainbow_waves,
            illusion_generator.create_pure_in_out_wave
        ]
        
        def update_all(t):
            illusion_index = int(t / (4 * np.pi)) % len(illusions)
            illusions[illusion_index](t)
            
        update_function = update_all
        frames = np.linspace(0, 4 * np.pi * len(illusions), 240 * len(illusions))
    else:
        update_function = {
            'spiral': illusion_generator.create_rainbow_spiral,
            'zoom': illusion_generator.create_color_zoom,
            'grid': illusion_generator.create_morphing_grid,
            'waves': illusion_generator.create_rainbow_waves
        }.get(args.illusion)
        frames = np.linspace(0, 4*np.pi, 240)
    anim = animation.FuncAnimation(illusion_generator.fig, update_function, 
                                   frames=frames, 
                                   interval=40, blit=False)

    plt.show()
