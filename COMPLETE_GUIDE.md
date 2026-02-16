# CAN Frame Generator - Complete User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Configuration Tab](#configuration-tab)
4. [Variables Tab](#variables-tab)
5. [State Machine Tab](#state-machine-tab)
6. [Output Generation](#output-generation)
7. [Generated Code Examples](#generated-code-examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The **CAN Frame Generator** is a graphical tool that automates the generation of C++ and C# code for CAN (Controller Area Network) message handling and state machine management. It simplifies the process of:

- Defining CAN frame structures with type mapping
- Generating serialization code for C# and C++
- Creating event-driven state machines
- Mapping state transitions with conditions
- Generating output actions for events

### Key Features
- **Type Mapping**: Automatic conversion between C++ and C# types (int8_t ↔ sbyte, float ↔ float, etc.)
- **State Machine Generator**: Visual builder for state transitions with conditions
- **Output Actions**: Define code to execute for each event
- **Time-based Conditions**: Trigger transitions after specified durations
- **Edge Detection**: React to button press events
- **Code Preview**: Real-time preview of generated C++ code
- **Configuration Persistence**: Automatically saves file paths and settings

---

## Installation & Setup

### Requirements
- Python 3.7+
- tkinter (usually included with Python)
- Windows, macOS, or Linux

### Running the Application
```bash
python generator.py
```

The application will:
1. Load saved configuration from `generator_config.json`
2. Display the user interface with three tabs
3. Auto-load variables from existing C++ and C# files

### Configuration File
The `generator_config.json` stores:
```json
{
    "path_cs": "path/to/Program.cs",
    "path_cpp": "path/to/UserMain.cpp",
    "com_port": "COM3",
    "baud_rate": "1500000"
}
```

---

## Configuration Tab

### Purpose
Configure file paths and communication settings for your C# project.

### File Paths

#### C# File Path
- Click **"Durchsuchen"** to select your C# project file (Program.cs)
- Expected markers in file:
  - `// [GENERATED_STRUCT_START]` and `// [GENERATED_STRUCT_END]`
  - `// [GENERATED_SERIALIZE_START]` and `// [GENERATED_SERIALIZE_END]`

#### C++ File Path
- Click **"Durchsuchen"** to select your C++ source file (UserMain.cpp)
- Expected markers in file:
  - `// [GENERATED_STRUCT_START]` and `// [GENERATED_STRUCT_END]`

### C# Project Settings

#### COM Port
- Enter the serial port name (e.g., COM3, COM4)
- Click **"Speichern"** to update the C# code
- This updates the value between `// [PORTNAME_START]` and `// [PORTNAME_END]` markers

#### Baud Rate
- Enter the communication speed (e.g., 1500000, 115200)
- Click **"Speichern"** to update the C# code
- This updates the value between `// [BAUDRATE_START]` and `// [BAUDRATE_END]` markers

---

## Variables Tab

### Purpose
Define all variables/signals that will be transmitted via CAN.

### Adding Variables

1. **Click "+ Variable hinzufügen"** to add a new row

2. **Select Data Type**
   - Opens dropdown with available types:
     - `int8_t / sbyte`
     - `uint8_t / byte`
     - `int16_t / short`
     - `uint16_t / ushort`
     - `int32_t / int`
     - `uint32_t / uint`
     - `int64_t / long`
     - `uint64_t / ulong`
     - `float`
     - `double`
     - `bool`
   - Selecting a type auto-fills the C++ and C# type columns

3. **C++ Type**
   - Auto-filled based on selected data type
   - Shows C++ native types (e.g., `float`, `int32_t`)

4. **C# Type**
   - Auto-filled based on selected data type
   - Shows C# equivalent types (e.g., `float`, `int`)

5. **Variable Name**
   - Enter the variable name (e.g., `wechselSignal`, `startFloatSignal`)
   - Used in both C++ and C# code

### Organizing Variables

- **▲ / ▼ Buttons**: Move variables up or down in the list
- **X Button**: Delete a variable row

### Generating Code

Click **"CODE GENERIEREN"** to:
1. Generate C++ struct with all variables
2. Generate C# struct with all variables
3. Generate C# serialization code
4. Update the C++ and C# files with markers

---

## State Machine Tab

### Purpose
Create event-driven state machines with transitions, conditions, and output actions.

### Configuration Section

#### Class Name
- Enter the name for your state machine class (e.g., `CanFrameSender`)
- Used for C++ code generation

#### States Definition
Enter all states, one per line:
```
Ready
pauseFirstFrame
pauseSecondFrame
pauseThirdFrame
```

#### Events Definition
Enter all events, one per line:
```
Init
sendFirstFrame
sendSecondFrame
sendThirdFrame
sendFourthFrame
```

### Transition Builder

#### Creating a New Transition

1. **Von State (From State)**
   - Select the starting state
   - Special option: **(alle)** - Expands to all states

2. **Event**
   - Select the event that triggers this transition

3. **Zu State (To State)**
   - Select the destination state

4. **Bedingungen (Conditions)** - Optional

   **Zeit (Time)**
   - Enable with checkbox
   - Operator: `>`, `<`, `==`, `>=`, `<=`, `!=`
   - Value: Time in seconds (e.g., 0.3, 1.0)
   - Example: Time > 1.5 seconds

   **Click Edge**
   - Enable with checkbox
   - Triggers when button is pressed (positive edge detected)

5. **Output Action** - Optional
   - Enter C++ code to execute when event occurs
   - Examples:
     - `wechselSignal.toggle();`
     - `startFloatSignal = startFloatSignal + 0.5f;`
     - `startIntSignal1 = startIntSignal1 + 1;`
     - `startIntSignal5 = startIntSignal5 + 5;`

6. **✓ Übergang hinzufügen**
   - Click to add the transition to the list

### Transition Management

#### Viewing Transitions
The "Definierte Übergänge" (Defined Transitions) list shows all transitions with:
- Source state → [Event] → Destination state
- Conditions (if any)
- Output action (if any)

#### Editing Transitions
1. Select a transition from the list
2. Click **"✎ Bearbeiten"** (Edit)
3. Modify the fields
4. Click **"✓ Übergang hinzufügen"** to save changes

#### Deleting Transitions
1. Select a transition from the list
2. Click **"✗ Markierten Übergang löschen"**

#### Reordering Transitions
1. Select a transition from the list
2. Click **"↑ Nach oben"** (Move up) or **"↓ Nach unten"** (Move down)

### Example Configuration

Click **"Beispiel laden"** to load a pre-configured example:

**States:**
```
Ready
pauseFirstFrame
pauseSecondFrame
pauseThirdFrame
```

**Events:**
```
Init
sendFirstFrame
sendSecondFrame
sendThirdFrame
sendFourthFrame
```

**Example Transitions:**
1. Ready → [sendFirstFrame] → pauseFirstFrame
   - Condition: click_Edge
   - Output: `wechselSignal.toggle();`

2. pauseFirstFrame → [sendSecondFrame] → pauseSecondFrame
   - Condition: t > 0.3
   - Output: `startFloatSignal = startFloatSignal + 0.5f;`

3. pauseSecondFrame → [sendThirdFrame] → pauseThirdFrame
   - Condition: t > 1.0
   - Output: `startIntSignal1 = startIntSignal1 + 1;`

4. pauseThirdFrame → [sendFourthFrame] → Ready
   - Condition: t > 1.9
   - Output: `startIntSignal5 = startIntSignal5 + 5;`

---

## Output Generation

### Overview
Output generation creates C++ code that executes actions when specific events occur. This is part of the state machine computation.

### How It Works

1. **For Each Event**, you can define an output action
2. The generator creates an if-else chain that executes the appropriate action
3. Actions execute in the `compute()` method after state transitions

### Output Format

Generated outputs follow this pattern:

```cpp
//Outputs
if			(E==Event::sendFirstFrame		) wechselSignal.toggle();
else if	(E==Event::sendSecondFrame	) startFloatSignal = startFloatSignal + 0.5f;
else if	(E==Event::sendThirdFrame		) startIntSignal1 = startIntSignal1 + 1;
else if	(E==Event::sendFourthFrame	) startIntSignal5 = startIntSignal5 + 5;
else;
```

### Writing Output Actions

**Rules:**
- Valid C++ code only
- Must be a single statement or enclosed in braces
- Include semicolon at the end
- Variables must be accessible in scope

**Examples:**
```cpp
// Simple toggle
wechselSignal.toggle();

// Increment
counter++;

// Arithmetic operation
startFloatSignal = startFloatSignal + 0.5f;

// Function call
startIntSignal1 = startIntSignal1 + 1;

// Compound operation
startIntSignal5 = startIntSignal5 + 5;

// Multiple statements (use braces)
{ startFloatSignal += 0.5f; wechselSignal.toggle(); }
```

### Optional Outputs
- Output actions are **optional**
- If an event has no output action, it won't appear in the if-else chain
- The generator always adds a final `else;` clause

---

## Generated Code Examples

### Example 1: Basic State Machine with Outputs

**Input Configuration:**
- States: Ready, pauseFirstFrame
- Events: Init, sendFirstFrame
- Transition: Ready → [sendFirstFrame] → pauseFirstFrame (Output: `counter++;`)

**Generated C++ Code:**
```cpp
class CanFrameSender {
	public:
		enum class State { Ready, pauseFirstFrame } S;
		enum class Event { None, Init, sendFirstFrame } E;
		
		bool		iniOK = false;
		uint64_t	t_cyc = 0;
		float		t = 0;

		bool		click_Edge = false;

		void compute(float T)
		{
			
			if(!iniOK) t_cyc = 0;
			else if(E == Event::None) t_cyc++;
			else t_cyc = 0;
			t = (t_cyc + 0.5f) * T;
			
			if     (!iniOK) { E = Event::Init; S = State::Ready; }
			else if(S==State::Ready && click_Edge) { E = Event::sendFirstFrame; S = State::pauseFirstFrame; }
			else{ E = Event::None; }
			
			//Outputs
			if			(E==Event::sendFirstFrame		) counter++;
			else;
			
			iniOK = true;
		}
};
```

### Example 2: Variables Generation

**Input:**
- Variable: `wechselSignal` (bool)
- Variable: `startFloatSignal` (float)

**Generated C++ Struct:**
```cpp
struct __attribute__((packed)) CanFrame {
    bool wechselSignal;
    float startFloatSignal;
};
```

**Generated C# Struct:**
```cpp
public struct CanFrame {
    public bool wechselSignal;
    public float startFloatSignal;
}
```

**Generated C# Serialization:**
```cpp
private static byte[] SerializeFrame(CanFrame frame) {
    List<byte> bytes = new List<byte>();
    bytes.AddRange(BitConverter.GetBytes(frame.wechselSignal));
    bytes.AddRange(BitConverter.GetBytes(frame.startFloatSignal));
    return bytes.ToArray();
}
```

---

## Troubleshooting

### Common Issues

#### "Tag fehlt in {file}: {tag}"
**Problem:** Required markers not found in the target file
**Solution:** 
1. Add the required markers to your C++ or C# file:
   - For structs: `// [GENERATED_STRUCT_START]` and `// [GENERATED_STRUCT_END]`
   - For serialization: `// [GENERATED_SERIALIZE_START]` and `// [GENERATED_SERIALIZE_END]`
2. Place them in the correct location with proper indentation

#### "Lesezugriff verweigert: {file}"
**Problem:** Cannot read the file
**Solution:**
1. Ensure the file path is correct
2. Check that you have read permissions
3. Close the file if it's open in another application

#### Variables not loading from files
**Problem:** Existing variables don't appear in the Variables tab
**Solution:**
1. Verify the file paths are correct in Configuration tab
2. Check that the C++ and C# files have the markers: `// [GENERATED_STRUCT_START]` and `// [GENERATED_STRUCT_END]`
3. Ensure variable declarations are in the correct format:
   - C++: `type variableName;`
   - C#: `public type variableName;`

#### Output code not generated
**Problem:** Output action section is empty or shows "TODO"
**Solution:**
1. Add transitions with output actions
2. Make sure each transition specifies an output action in the "Output Action" field
3. Only events that have output actions defined will appear in the output chain

#### State machine code looks wrong
**Problem:** Generated code has formatting issues
**Solution:**
1. Check that state and event names don't have special characters
2. Verify condition syntax (operators: `>`, `<`, `==`, `>=`, `<=`, `!=`)
3. Ensure output action code is valid C++

### Getting Help

1. **Check this guide** - Most issues are covered here
2. **Review the example** - Click "Beispiel laden" to see a working configuration
3. **Verify file markers** - Ensure all required markers are in target files
4. **Test incrementally** - Add variables/transitions one at a time

---

## File Structure

The generator maintains the following workflow:

```
generator.py (Main Application)
    ↓
generator_config.json (Configuration Storage)
    ↓
    ├→ C# File (Program.cs)
    │   ├ // [PORTNAME_START] ... // [PORTNAME_END]
    │   ├ // [BAUDRATE_START] ... // [BAUDRATE_END]
    │   ├ // [GENERATED_STRUCT_START] ... // [GENERATED_STRUCT_END]
    │   └ // [GENERATED_SERIALIZE_START] ... // [GENERATED_SERIALIZE_END]
    │
    └→ C++ File (UserMain.cpp)
        └ // [GENERATED_STRUCT_START] ... // [GENERATED_STRUCT_END]
```

---

## Advanced Tips

### Using Wildcards
When adding transitions, use **(alle)** (all) as the "Von State" to:
- Create the same transition from every state
- Each state gets its own transition entry
- Useful for "reset" or "emergency stop" events

### Condition Combinations
You can combine multiple conditions:
- Time AND Click Edge: Add both conditions to trigger on both
- Either uses AND logic: all conditions must be true

### Organizing Large State Machines
1. Group related states together
2. Use descriptive state names (pauseFirstFrame, pauseSecondFrame)
3. Use the up/down arrows to order transitions logically
4. Test with the example first, then customize

### Performance Considerations
- Keep state machines simple for embedded systems
- Minimize output action complexity
- Avoid expensive operations in compute()
- Consider timing for time-based transitions

---

## Summary of Key Workflows

### Workflow 1: Generate Basic CAN Frame
1. Go to **Variables** tab
2. Click "+ Variable hinzufügen"
3. Select data types from dropdown
4. Enter variable names
5. Click "CODE GENERIEREN"
6. Code is inserted into C++ and C# files

### Workflow 2: Create a State Machine
1. Go to **State Machine** tab
2. Enter states (one per line)
3. Enter events (one per line)
4. Build transitions using the builder
5. Add output actions for each event
6. Click "CODE GENERIEREN"
7. Code appears in the output window

### Workflow 3: Update Communication Settings
1. Go to **Configuration** tab
2. Update COM Port
3. Click "Speichern"
4. Update Baud Rate
5. Click "Speichern"
6. C# file is automatically updated

---

## Version History & Updates

**Current Version:** 1.0 with Output Actions Support

**Recent Features:**
- Output action generation for state machine events
- Transition editing and reordering
- Wildcard state transitions
- Time-based and edge-triggered conditions
- Real-time code preview
- Configuration persistence

---

**For additional support or feature requests, refer to the project documentation or contact the development team.**
