# Alpha AI - Condition Reflex Agent for ARC-AGI

---

## I. Capabilities of the Current Minimum Version

This system aims to **verify the agent's ability to summarize experiences from environmental feedback, form memories, and modify exploration behavior**, rather than pursuing benchmark scores. The system utilizes the **DreamCoder's Default Wake Generative** algorithm to perform autonomous interactive exploration under known clickable object categories, achieving the following core capabilities:

1. **Experience Summarization**: Summarize interaction experiences and form experience programs based on environmental feedback after clicks
2. **Memory Formation**: Store formed experience programs into memory library, establishing long-term memory in the format: `if click ID, program`
3. **Behavior Adjustment**: Retrieve memory library when exploring win conditions, adjusting exploration behavior based on existing experience
4. **Condition Reflex**: Avoid ineffective clicks (clicks with no effect, i.e., IDs recorded as `lambda$0`), no longer clicking blindly and randomly, but rather tending to click areas that cause environmental changes

This system uses **ft09** as a sample for verification, demonstrating the transformation from "blind random clicking" to "memory-based intelligent exploration".

**Core Workflow**:

```
Manually specify clickable objects (divided into four categories, each listing grid coordinates)
 ↓ 
 Select one representative from each category according to predetermined exploration order until all four categories are explored
 ↓ 
 Click
 ↓ 
 Environmental feedback
 ↓ 
 Default Wake Generative
 ↓ 
 Experience program
 ↓ 
 Memory (fill all objects representing this category with the same experience program)
 ↓ 
 Attempt to win
 ↓ 
 Check if objects in memory are recorded as lambda$0
   ↓ Yes → Prune, no longer click
   ↓ No → Can attempt clicking
```

**Demo Videos**:
- `blind_clicking_*.mp4` - Blind random clicking video (no experience): System clicks between non-responsive and responsive areas without reflecting on which areas are ineffective
- `curiosity_exploration_*.mp4` - Curiosity exploration video (with condition reflex): System summarizes `lambda$0` program after initial clicks in ineffective areas, then only clicks within effective areas to attempt winning

**Core Files**:
- `curiosity_exploration.py` - Main program containing manually preset exploration logic, program synthesis, memory formation, and win attempts
- `customPrimitives.py` - DreamCoder custom primitives, defining core primitives like `if_click_{object_id}` and `no_effect`

---

## II. Capabilities Verified in Current Version

Through click interactions, recording click effects based on environmental feedback to form experience programs and save as memories:

1. **From Blind Exploration to Intelligent Exploration**: The system can transform from initial random clicking to targeted intelligent exploration by recording click effects and forming memories
2. **Ineffective Click Pruning**: By identifying `lambda$0` programs (no-effect clicks), the system can automatically block repeated clicks in ineffective areas
3. **Memory-Based Decision Making**: When attempting to win, the system can retrieve memory library and select effective click strategies based on existing experience

## III. Controlled Aspects in Current Version

This version artificially constrains the following aspects to control variables and highlight the verification focus of "experience summarization and memory":

1. **Exploration Strategy is Manually Specified**: Manually specify the range of clickable objects and pre-divide them into four categories; the system selects only one object from each category for one click trial, generates a program, writes it to memory, and defaults other objects in the same category to have the same reaction, filling them with the same memory. This design lacks intrinsic motivation and rigorous exploration strategies.

2. **Filtering Strategy is Manually Specified**: Retrieve records for each object in memory, if memory is `if click ID, lambda$0` then immediately exclude, classify into non-attemptable range, never click.

## IV. Potential Defect Analysis

Based on theoretical derivation, this system has the following defects:

1. **Exploration strategy relies on manual specification, lacking intrinsic motivation**: Cannot independently establish effective exploration methods in unfamiliar environments

2. **Pruning strategy is too rigid**: Permanently excludes objects upon retrieving `lambda$0` records, never clicking them again, which potentially eliminates many possibilities and is not conducive to discovering complex patterns

3. Only records local experience memories of individual objects, cannot abstract deep patterns from a small number of interaction phenomena, and cannot discover global complex patterns where multiple objects interact with each other. For example, after clicking object 12, DreamCoder can abstract `color_block lambda 9 8 $0`, and after the second click gets `color_block 89 $0`, but cannot determine this is a color cycle and predict that the third click will turn blue to red

As seen in the `curiosity_exploration` video, although the system eventually determines to explore win conditions within the object 11-18 area, it ultimately fails to pass the level. The reason is that the system can only record experience programs, has not thoroughly understood the deep patterns of individual objects, and has not grasped global visual patterns, naturally unable to pass the level.

## V. Open Research Questions

These limitations raise the following research questions:

1. **How to establish effective autonomous exploration strategies in unfamiliar environments?**

2. **How to establish scientific win condition hypotheses in unfamiliar environments?**

3. **How to quickly abstract patterns of individual objects from a small number of recorded interaction phenomena, discover interaction patterns among multiple objects in the game world, and construct effective world models?**

4. **How to dynamically evolve win goal hypotheses, exploration strategies, and world models based on interaction feedback in dynamic interaction environments?**

## VI. Future Expansion Directions

Based on current results, the expansion plan for this project is as follows: Use GPT large model as the engine for generating win goal hypotheses, exploration strategies, and world models (i.e., patterns of object interactions in games). Generate initial win goal hypotheses and exploration strategies based on the initial game screen, and during interaction, form world models based on statistical results of interaction phenomena, continuously updating win goal hypotheses, exploration strategies, and world models. Then, record the process of forming initial win goal hypotheses, exploration strategies, world models, continuously updating them based on environmental feedback, and deriving final results.

After that, we can consider no longer using GPT and instead train a neural network to directly mimic human intuition and curiosity, focusing on training the ability to form win condition hypotheses and establish exploration intuition in unfamiliar environments. Intuition is responsible for determining the most likely way to explore and what the win conditions are likely to be. Curiosity is responsible for trying innovative approaches based on intuition, which can discover more novel phenomena. Generating win condition hypotheses, exploration strategies, and constructing world models based on statistics of a small number of interaction phenomena in unfamiliar environments all rely on intuition and curiosity. At this point, the saved processes can serve as training data.

---

## Quick Start

### 1. Modify Configuration

Edit `config.py` to adjust parameters:

```python
GAME_NAME = "ft09"                    # Game name
ENABLE_EXPLORATION = True             # Enable exploration
ENABLE_WIN_ATTEMPT = True             # Attempt to win
ENABLE_VIDEO_RECORDING = True         # Record video
```

### 2. Customize Core Logic (Optional)

Edit `core_strategies.py` to customize algorithms. The following extension interfaces are currently supported:

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
    # Return the most worthy object_id to explore
    ...

# Bayesian belief update pruning strategy
def belief_decay_pruning(object_id, memory):
    # Return belief degree value (0.0 - 1.0)
    ...

# Intuition neural network - mimic human intuition for exploration
def intuition_network(exploration_history, pruning_history, new_environment):
    # Return recommended next exploration target object_id
    ...
```

**Strategy Registration**: Register strategies you want to use in the `ACTIVE_STRATEGIES` dictionary. Changes take effect after restarting the program.

### 3. Run

```bash
python curiosity_exploration.py
```

## Configuration Options

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
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
| `SCALE_FACTOR` | Screen scaling factor | `16` |
| `USE_LONG_TERM_MEMORY` | Use long-term memory | `True` |
| `CLEAR_MEMORY_AFTER_RUN` | Clear memory after run | `False` |

## Core Strategies

### Customizable Strategy Interfaces

| Function | Description | Return Value |
|----------|-------------|--------------|
| `select_exploration_target()` | Select target to explore | `(category, object)` |
| `select_grid_coordinate()` | Select grid coordinate to click | `(x, y)` |
| `should_click_object()` | Determine whether to click | `bool` |
| `classify_effect()` | Classify click effect | `'no_effect'` or `'has_effect'` |
| `decide_win_strategy()` | Decide win strategy | `[object_ids]` |
| `custom_reward_function()` | Custom reward function | `float` |
| `curiosity_driven_exploration()` | Curiosity-driven exploration | `object_id` |

### Example: Custom Strategy

```python
# Prioritize exploring unexplored objects
def explore_unexplored_first(all_categories, memory):
    unexplored = []
    for category in all_categories:
        for obj in category:
            if not memory.get_programs_for_object(obj["id"]):
                unexplored.append((category, obj))
    
    if unexplored:
        return random.choice(unexplored)
    
    # Default random selection
    selected_category = random.choice(all_categories)
    selected_object = random.choice(selected_category)
    return selected_category, selected_object

# Register in ACTIVE_STRATEGIES
ACTIVE_STRATEGIES['exploration'] = explore_unexplored_first
```

## Project Structure

```
Alpha AI/
├── config.py              # Configuration file (parameter adjustment)
├── core_strategies.py     # Core strategy entry (algorithm modification)
├── curiosity_exploration.py  # Main program
├── categories.py          # Object category definitions
├── grid_coordinates.py    # Coordinate calculation
├── frame_saver.py         # Frame saving
├── long_term_memory.py    # Long-term memory system
├── customPrimitives.py    # DreamCoder primitives
└── memory/
    └── program_library.json  # Program memory library
```