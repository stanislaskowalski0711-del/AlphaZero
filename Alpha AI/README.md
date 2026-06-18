# Alpha AI - ARC-AGI-3 Conditioned Reflex Agent

---

## I. Capabilities of the Current Minimum Version

Existing ARC-AGI-3 methods primarily rely on massive computational power for brute-force training, yet still exhibit numerous ineffective clicks in real ARC-AGI-3 environments. This project investigates: **Can an agent form experiences and memories based on real-time environmental feedback and adjust exploration strategies, rather than pursuing benchmark scores?** The system utilizes the **DreamCoder's Default Wake Generative** algorithm to perform autonomous interactive exploration under known clickable object categories. This system uses **ft09** as a sample for validation, demonstrating the transition from "blind random clicking" to "memory-based intelligent exploration".

**Core Workflow**:

1. Manually specify clickable object ranges, divide them into four categories, and list grid coordinates for each category
2. Select a representative object from each category according to a predetermined exploration order for click testing, until all four categories have been explored
3. Click the selected object
4. Receive environmental feedback
5. Invoke DreamCoder's Default Wake Generative algorithm for program synthesis

   Example of program synthesis process (terminal output screenshot):
   
   ```bash
   # Category 1/4 Exploration
   Selected Category ID: 1
   Selected Object ID: 3
   Object ID: 3
   Object grid coordinates: [(20, 10), (21, 10), ...]
   Selected grid coordinate (x, y): (22, 13)
   
   === Save before-click image: cat1_obj3_before.png ===
   === Execute click: (22, 13) ===
   === Save after-click image: cat1_obj3_after.png ===
   
   === Start program synthesis: cat1_obj3 ===
   Starting program synthesis...
   Object ID: 3
   Input matrix shape: (6, 6)
   Output matrix shape: (6, 6)
   
   Generative model enumeration results:
   HIT click_object_3 w/ (lambda $0); log prior = -1.386...
   Hits 1/1 tasks
   
   Found explanation program:
     Inner program: (lambda $0)
     Complete program: (if_click_3 (lambda $0))
   
   Verification results:
     Expected output: [[9, 9, 9, ...], ...]
     Actual output: [[9, 9, 9, ...], ...]
     Correct: YES
   Program stored to program memory
   Program synthesis completed
   
   Storing same program memory for other objects in the same category...
   Object ID 1: (if_click_1 (lambda $0))
   Object ID 2: (if_click_2 (lambda $0))
   Object ID 4: (if_click_4 (lambda $0))
   Memory saved to memory\memory.json
   ```

   Another example of effective clicking:
   
   ```bash
   # Category 4/4 Exploration
   Object ID: 18
   Selected grid coordinate (x, y): (55, 54)
   
   Generative model enumeration results:
   HIT click_object_18 w/ (lambda (color_block 9 8 $0))
   
   Found explanation program:
     Inner program: (lambda (color_block 9 8 $0))
     Complete program: (if_click_18 (lambda (color_block 9 8 $0)))
   
   Verification results:
     Correct: YES
   Program synthesis completed
   
   Storing same program memory for other objects in the same category...
   Object ID 11: (if_click_11 (lambda (color_block 9 8 $0)))
   Object ID 12: (if_click_12 (lambda (color_block 9 8 $0)))
   ...
   All categories explored!
   Final program memory: Program library: 18 programs, 18 object_ids
   ```

6. Generate experience programs

   Experience program storage format (`program_library.json` file screenshot):
   
   ```json
   {
     "3": [
       {
         "program": "(if_click_3 (lambda $0))",
         "input": [
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9]
         ],
         "output": [
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9]
         ],
         "mdl": 1.3862943611198906,
         "learned_at": "2026-06-18T08:25:00.816395",
         "use_count": 0
       }
     ],
     "12": [
       {
         "program": "(if_click_12 (lambda (color_block 9 8 $0)))",
         "input": [
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9],
           [9, 9, 9, 9, 9, 9]
         ],
         "output": [
           [8, 8, 8, 8, 8, 8],
           [8, 8, 8, 8, 8, 8],
           [8, 8, 8, 8, 8, 8],
           [8, 8, 8, 8, 8, 8],
           [8, 8, 8, 8, 8, 8],
           [8, 8, 8, 8, 8, 8]
         ],
         "mdl": 0.0,
         "learned_at": "2026-06-18T08:25:17.169841",
         "use_count": 0
       }
     ]
   }
   ```

   Notes:
   - `"3"` and `"12"` are Object IDs
   - The `"program"` field stores the synthesized experience program
   - `"input"` and `"output"` store the image matrices (color values) before and after clicking
   - `"mdl"` is the Minimum Description Length score
   - `"learned_at"` records the program learning time
   - `"use_count"` records how many times the program has been used

7. Store experience programs in memory and populate all objects in the category with the same experience program
8. Attempt to win: Check object records in memory, if recorded as `lambda$0` (no effect) then prune and no longer click, otherwise attempt clicking

   Example of win attempt process (terminal output screenshot):
   
   ```bash
   All categories explored!
   Final program memory: Program library: 18 programs, 18 object_ids
   
   Non-clickable objects: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
   Clickable objects: [11, 12, 13, 14, 15, 16, 17, 18]
   
   Starting to explore win conditions...
   === Reset game screen to initial state ===
   
   Attempt 1/20: Click Category 4 Object 15 grid (47, 52)
   Attempt 2/20: Click Category 4 Object 13 grid (38, 52)
   Attempt 3/20: Click Category 4 Object 11 grid (40, 46)
   Attempt 4/20: Click Category 4 Object 16 grid (56, 48)
   Attempt 5/20: Click Category 4 Object 17 grid (53, 41)
   Attempt 6/20: Click Category 4 Object 16 grid (52, 44)
   Attempt 7/20: Click Category 4 Object 12 grid (36, 37)
   Attempt 8/20: Click Category 4 Object 15 grid (46, 52)
   ...
   Attempt 27/20: Click Category 4 Object 18 grid (55, 57)
   Attempt 28/20: Click Category 4 Object 16 grid (57, 45)
   ...
   Attempt 50/20: Click Category 4 Object 13 grid (37, 52)
   ```

   Notes:
   - The system automatically filters out non-clickable objects (objects recorded as `lambda$0`)
   - Only attempts to win among clickable objects
   - The number of attempts exceeds the preset limit of 20, indicating the current strategy failed to find the win condition

**Demo Videos**:
- `blind_clicking_*.mp4` - Blind random clicking video (no experience): The system clicks between non-responsive and responsive areas without reflecting on which areas are invalid
- `curiosity_exploration_*.mp4` - Curiosity exploration video (with conditioned reflex): After initially clicking in invalid areas and summarizing the `lambda$0` program, the system only clicks in valid areas to attempt winning

**Core Files**:
- `curiosity_exploration.py` - Main program containing manually preset exploration logic, program synthesis, memory formation, and win attempts
- `customPrimitives.py` - DreamCoder custom primitives defining core primitives like `if_click_{object_id}` and `no_effect`

---

## II. Verified Capabilities of Current Version

Through click interactions, recording click effects based on environmental feedback to form experience programs and save as memory:

1. **From blind exploration to intelligent exploration**: The system can transition from initial random clicking to targeted intelligent exploration by recording click effects and forming memories
2. **Ineffective click pruning**: By identifying the `lambda$0` program (no-effect clicks), the system can automatically block repeated clicks in invalid areas
3. **Memory-based decision making**: When attempting to win, the system can retrieve the memory library and select effective click strategies based on existing experience

## III. Controlled Aspects in Current Version

This version controls variables to highlight the verification focus of "experience summarization and memory", with the following manual constraints:

1. **Exploration strategy is manually specified**: Manually specify the range of clickable objects and pre-divide them into four categories; the system selects only one object from each category for one click test, generates a program and writes it to memory, and defaults that other objects in the category have the same reaction, filling them with the same memory. This design lacks intrinsic motivation and rigorous exploration strategies.

2. **Filter strategy is manually specified**: Check each object's record in memory; if the memory is `if click ID, lambda$0`, immediately exclude it, classify it as untouchable, and never click it.

## IV. Potential Defect Analysis

Based on theoretical derivation, this system has the following defects:

1. **Exploration strategy relies on manual specification, lacking intrinsic motivation**: Cannot independently establish effective exploration methods in unfamiliar environments

2. **Pruning strategy is too rigid**: Once a `lambda$0` record is retrieved, it is permanently excluded and never clicked again, which potentially eliminates many possibilities and is not conducive to discovering complex patterns

3. Only records local experience memories of individual objects, cannot abstract deep patterns from a small number of interaction phenomena, and cannot discover global, complex patterns where multiple objects interact with each other. For example, after clicking object 12, DreamCoder can abstract `color_block lambda 9 8 $0`, and after the second click gets `color_block 89 $0`, but cannot determine this is a color cycle and predict that the third click will change blue to red

As seen in the `curiosity_exploration` video, although the system eventually focused on exploring win conditions within objects 11-18, it ultimately failed to win. The reason is that the system can only record experience programs, has not yet fully understood the deep patterns of individual objects, and has not grasped global visual patterns, naturally making it unable to win.

## V. Open Research Questions

These limitations lead to the following research questions:

1. **How to establish effective autonomous exploration strategies in unfamiliar environments?** Instead of relying on manual presets?

2. **How to establish scientific win condition hypotheses in unfamiliar environments?** Instead of random attempts based on exploration behavior pruning?

3. **How to quickly abstract individual object patterns from a small number of recorded interaction phenomena, discover interaction patterns among multiple objects in the game world, and construct effective world models?** Instead of only recording local experience programs?

4. **How to dynamically evolve the formed win goal hypotheses, exploration strategies, and world models based on interaction feedback in a dynamic interaction environment?**

## VI. Future Expansion Directions

Based on current results, the expansion plan for this project is as follows: Use GPT large model as the engine for generating win goal hypotheses, exploration strategies, and world models (i.e., patterns of object interactions in the game). Generate initial win goal hypotheses and exploration strategies based on the initial game screen, and during interaction, form world models based on statistical results of a small number of interaction phenomena, continuously updating win goal hypotheses, exploration strategies, and world models. After that, record the process of forming initial win goal hypotheses, exploration strategies, world models, and continuously updating them based on environmental feedback to arrive at final results. Whether it can win is not important; achieving this is the priority.

After this, we can consider no longer using GPT, and instead train a neural network that directly mimics human intuition and curiosity, focusing on training the ability to form win condition hypotheses and establish exploration intuition in unfamiliar environments, which involves meta-learning. Intuition is responsible for how to explore with high probability and what the win condition is likely to be. Curiosity is responsible for trying innovative approaches based on intuition to discover more novel phenomena. Generating win condition hypotheses, exploration strategies, and constructing world models based on statistical results of a small number of interaction phenomena in unfamiliar environments cannot be achieved without intuition and curiosity. At this point, the saved processes can be used as training data.

---

## Quick Start

### 1. Modify Configuration

Edit the `config.py` file to adjust parameters:

```python
GAME_NAME = "ft09"                    # Game name
ENABLE_EXPLORATION = True             # Enable exploration phase
ENABLE_WIN_ATTEMPT = True             # Enable win attempts
ENABLE_VIDEO_RECORDING = True         # Enable video recording
```

### 2. Customize Core Logic (Optional)

Edit the `core_strategies.py` file to customize algorithms. The following extension interfaces are currently supported:

```python
# Select grid coordinate to click
def select_grid_coordinate(object_grid_coordinates):
    # Return selected grid coordinate (x, y)
    ...

# Classify click effect
def classify_effect(program_str):
    # Return 'no_effect' or 'has_effect'
    ...

# Curiosity mechanism - select exploration target based on intrinsic motivation
def curiosity_mechanism(objects, memory):
    # Return the most worth-exploring object_id
    ...

# GPT hypothesis generator
def gpt_hypothesis_generator(initial_screen, game_state):
    # Return multiple candidate win goal hypotheses
    ...

# GPT strategy generator
def gpt_strategy_generator(environment_state, memory):
    # Return multiple candidate exploration strategies
    ...

# GPT world model generator
def gpt_world_model_generator(interaction_history, objects):
    # Return world model with object interaction patterns
    ...

# Intuition network - mimic human intuition for exploration
def intuition_network(exploration_history, pruning_history, new_environment):
    # Return recommended next exploration target object_id
    ...
```

**Strategy Registration**: Register your desired strategies in the `ACTIVE_STRATEGIES` dictionary. Changes take effect after restarting the program.

### 3. Run

```bash
python curiosity_exploration.py
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `GAME_NAME` | Game name | `"ft09"` |
| `ARC_API_KEY` | ARC-AGI API Key | - |
| `ENABLE_EXPLORATION` | Enable exploration phase | `True` |
| `OBJECTS_PER_CATEGORY` | Number of objects to explore per category | `1` |
| `EXPLORATION_DELAY` | Exploration delay in seconds | `2` |
| `ENABLE_WIN_ATTEMPT` | Enable win attempts | `True` |
| `MAX_WIN_ATTEMPTS` | Maximum win attempts | `50` |
| `CLICK_DELAY` | Click delay in seconds | `2` |
| `ENABLE_VIDEO_RECORDING` | Enable video recording | `True` |
| `VIDEO_FPS` | Video frames per second | `1` |
| `SCALE_FACTOR` | Screen magnification factor | `16` |
| `USE_LONG_TERM_MEMORY` | Use long-term memory | `True` |
| `CLEAR_MEMORY_AFTER_RUN` | Clear memory after run | `False` |

## Core Strategies

The core strategies are defined in `core_strategies.py`:

### Interface List

| Interface | Function | Description |
|-----------|----------|-------------|
| `select_grid_coordinate` | Grid Selection | Select which grid coordinate to click within an object |
| `classify_effect` | Effect Classification | Classify whether a click has effect or not |
| `curiosity_mechanism` | Curiosity Mechanism | Select exploration targets based on intrinsic motivation |
| `gpt_hypothesis_generator` | GPT Integration | Generate win goal hypotheses using GPT |
| `gpt_strategy_generator` | GPT Integration | Generate exploration strategies using GPT |
| `gpt_world_model_generator` | GPT Integration | Construct world models using GPT |
| `intuition_network` | Intuition Network | Recommend exploration targets based on historical experience |
| `interaction_history_recorder` | History Recording | Record interaction history for later analysis |

### Strategy Registration Example

```python
ACTIVE_STRATEGIES = {
    'grid_selection': select_grid_coordinate,
    'effect_classification': classify_effect,
}
```

## Project Structure

```
Alpha AI/
├── curiosity_exploration.py    # Main program
├── customPrimitives.py         # DreamCoder custom primitives
├── core_strategies.py          # Core strategy interfaces
├── config.py                   # Configuration file
├── memory/                     # Memory storage directory
│   ├── program_library.json    # Program memory
│   └── memory.json             # Object memory
├── screenshots/                # Screenshots directory
├── videos/                     # Video recordings directory
└── README.md                   # Documentation
```

---

*This project is part of ARC-AGI-3 research, focusing on developing intelligent agents that can learn from interaction experience.*