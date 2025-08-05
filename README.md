# AIDA64 BAR GUAGES IMAGE GENERATOR


![AIDA64-sensorpanel](https://github.com/user-attachments/assets/048ed4fa-0330-4820-a60d-d0dcd977384f)

## Usage

Clone the Project

```bash
git clone https://github.com/s-raza/aida64-bar-gauge-generator.git
```

Switch to the project directory

```bash
cd aida64-bar-gauge-generator/
```

Install virtual environment if needed

```bash
python -m venv .venv
```

Active virtual environment

```bash
source .venv/bin/activate
```

Install requirements

```bash
pip install -r requirements.txt
```

Switch to the directory above the project directory

```bash
cd ..
```

Run the script and view help message


```bash
$python -m aida64-bar-gauge-generator --help
usage: __main__.py [-h] [--base_screen_width BASE_SCREEN_WIDTH] [--base_screen_height BASE_SCREEN_HEIGHT]
                   [--target_screen_width TARGET_SCREEN_WIDTH] [--target_screen_height TARGET_SCREEN_HEIGHT]
                   [--base_total_gauge_width BASE_TOTAL_GAUGE_WIDTH] [--base_bar_height BASE_BAR_HEIGHT] [--base_bar_spacing BASE_BAR_SPACING]
                   [--bar_count BAR_COUNT] [--outline_width OUTLINE_WIDTH] [--vertical] [--base_line_color BASE_LINE_COLOR]
                   [--base_line_thickness BASE_LINE_THICKNESS] [--background BACKGROUND] [--outline_color OUTLINE_COLOR]
                   [--file_prefix FILE_PREFIX] [--output_dir OUTPUT_DIR] [--file_ext FILE_EXT]

options:
  -h, --help            show this help message and exit
  --base_screen_width BASE_SCREEN_WIDTH
  --base_screen_height BASE_SCREEN_HEIGHT
  --target_screen_width TARGET_SCREEN_WIDTH
  --target_screen_height TARGET_SCREEN_HEIGHT
  --base_total_gauge_width BASE_TOTAL_GAUGE_WIDTH
  --base_bar_height BASE_BAR_HEIGHT
  --base_bar_spacing BASE_BAR_SPACING
  --bar_count BAR_COUNT
  --outline_width OUTLINE_WIDTH
  --vertical
  --base_line_color BASE_LINE_COLOR
  --base_line_thickness BASE_LINE_THICKNESS
  --background BACKGROUND
  --outline_color OUTLINE_COLOR
  --file_prefix FILE_PREFIX
  --output_dir OUTPUT_DIR
  --file_ext FILE_EXT
```

Generate bar images with the required arguments

```bash
python -m aida64-bar-gauge-generator --vertical --file_prefix "processor_utilization" --target_screen_width 1024 --target_screen_height 768 --base_bar_height 20 --base_total_gauge_width 250
✅ Done! 16 bar images saved to: 'output/vertical_processor_utilization_20x250'
```

Bar images generated

<img width="1236" height="412" alt="image" src="https://github.com/user-attachments/assets/670bb0ee-abdf-4108-b645-e5da93126025" />

Use in AIDA 64

<img width="1838" height="793" alt="image" src="https://github.com/user-attachments/assets/ada4a09b-0047-4ff3-bf81-dab5b411da5d" />


