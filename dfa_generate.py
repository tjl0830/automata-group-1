import os
from automata.fa.nfa import NFA
from automata.fa.dfa import DFA
import graphviz
from PIL import Image
import glob

def regex_to_dfa(regex):
    # Replace '+' with '|' for alternation
    regex = regex.replace('+', '|')
    nfa = NFA.from_regex(regex)
    dfa = DFA.from_nfa(nfa)
    return dfa

def simulate_dfa_path(dfa, input_str):
    """Simulate DFA on input_str and return the path as a list of (src, symbol, dst) tuples."""
    current_state = dfa.initial_state
    path = []
    for symbol in input_str:
        print(f"Current state: {current_state}, symbol: {symbol}")
        print(f"Available transitions: {dfa.transitions[current_state]}")
        if symbol not in dfa.input_symbols:
            raise ValueError(f"Symbol '{symbol}' not in DFA alphabet.")
        if symbol not in dfa.transitions[current_state]:
            # No transition for this symbol, not accepted
            return path, False
        next_state = dfa.transitions[current_state][symbol]
        path.append((current_state, symbol, next_state))
        current_state = next_state
    return path, current_state in dfa.final_states

def normalize_state(state):
    # If state is a tuple, join its elements; else, just str
    if isinstance(state, tuple):
        return ','.join(map(str, state))
    return str(state)

def draw_dfa(dfa, filename='dfa', path=None, input_str=None, current_index=None, highlight_states=None):
    dot = graphviz.Digraph(engine='dot')
    dot.attr(rankdir='LR')
    dot.attr('graph', splines='true', concentrate='true', seed='42')

    highlight_states = set(highlight_states) if highlight_states else set()

    # Add states in sorted order with normalized names
    for state in sorted(dfa.states, key=normalize_state):
        state_str = normalize_state(state)
        if state_str in highlight_states:
            dot.node(
                state_str,
                shape='doublecircle' if state in dfa.final_states or state == dfa.initial_state else 'circle',
                color='red',
                fontcolor='red'  # Black text, red border, no fill
            )
        elif state == dfa.initial_state:
            dot.node(state_str, shape='doublecircle', color='green')
        elif state in dfa.final_states:
            dot.node(state_str, shape='doublecircle')
        else:
            dot.node(state_str, shape='circle')

    # Prepare set of traversed transitions for highlighting
    traversed = set()
    if path:
        for src, symbol, dst in path:
            traversed.add((normalize_state(src), normalize_state(dst), symbol))

    # Add transitions in sorted order with normalized names
    for src in sorted(dfa.transitions, key=normalize_state):
        transitions = dfa.transitions[src]
        for symbol in sorted(transitions):
            dst = transitions[symbol]
            if (normalize_state(src), normalize_state(dst), symbol) in traversed:
                dot.edge(normalize_state(src), normalize_state(dst), label=symbol, color='red', penwidth='2')
            else:
                dot.edge(normalize_state(src), normalize_state(dst), label=symbol)

    # Add the input string at the bottom, highlighting the current character in red and making the font bold
    if input_str is not None and current_index is not None:
        label = ""
        for i, c in enumerate(input_str):
            if i == current_index:
                label += f'<B><FONT COLOR="red">{c}</FONT></B>'
            else:
                label += f'<B>{c}</B>'
        dot.attr(label=f'<{label}>', labelloc="b", fontsize="32")

    dot.render(filename, format='png', cleanup=True)
    print(f"DFA diagram saved as {filename}.png")

def create_gif_from_frames(frames_dir, output_file='dfa_animation.gif', duration=100):
    """
    Creates an animated GIF from PNG frames in the specified directory.
    :param frames_dir: Directory containing frame_0.png, frame_1.png, ...
    :param output_file: Output GIF file name.
    :param duration: Duration of each frame in milliseconds.
    """
    frames = []
    files = sorted(glob.glob(os.path.join(frames_dir, 'frame_*.png')), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[1]))
    for file in files:
        frames.append(Image.open(file))
    if frames:
        frames[0].save(
            output_file,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0
        )
        print(f"GIF created: {output_file}")
    else:
        print("No frames found to create GIF.")

# if __name__ == "__main__":
#     # Create the frames directory if it doesn't exist
#     frames_dir = "dfa_frames"
#     os.makedirs(frames_dir, exist_ok=True)

#     regex = input("Enter a regular expression: ")
#     dfa = regex_to_dfa(regex)
#     # draw the DFA
#     draw_dfa(dfa, os.path.join(frames_dir, 'dfa_diagram'))
#     # simulate the DFA with user input
#     test_str = input("Enter a string to validate: ")
#     try:
#         path, accepted = simulate_dfa_path(dfa, test_str)
#         # Generate a frame for each step in the path, highlighting only the current edge
#         for i in range(len(path)):
#             current_edge = [path[i]]
#             draw_dfa(
#                 dfa,
#                 os.path.join(frames_dir, f'frame_{i}'),
#                 path=current_edge,
#                 input_str=test_str,
#                 current_index=i
#             )
#         # Create a GIF from the generated frames
#         create_gif_from_frames(frames_dir, output_file='dfa_frames/dfa_animation.gif', duration=250)
#         print("GIF animation created successfully.")
#         # Clean up frames after GIF creation
#         for file in glob.glob(os.path.join(frames_dir, 'frame_*.png')):
#             os.remove(file)
#         print("Temporary frames cleaned up.")
#         # Generate a final frame with the entire path highlighted
#         draw_dfa(
#             dfa,
#             os.path.join(frames_dir, 'dfa_diagram_path'),
#             path=path,
#             input_str=test_str,
#             current_index=None
#         )
#         if accepted:
#             print("The string is accepted by the DFA.")
#         else:
#             print("The string is NOT accepted by the DFA.")
#     except Exception as e:
#         print(f"Error: {e}")