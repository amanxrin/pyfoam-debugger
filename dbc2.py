import tkinter as tk
from tkinter import ttk, messagebox

def load_openfoam_file():
    try:
        with open('fvSolution', 'r') as file:  
            content = file.readlines()
            global openfoam_dict
            openfoam_dict = parse_openfoam_file(content)
            tree.delete(*tree.get_children())  
            populate_treeview("", openfoam_dict)
    except FileNotFoundError:
        messagebox.showerror("Error", "OpenFOAM file not found. Please check the file path.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load OpenFOAM file: {str(e)}")

# Function to parse OpenFOAM file into a nested dictionary
def parse_openfoam_file(lines):
    parsed_dict = {}
    stack = [parsed_dict]
    current_key = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("//"):  # Skip empty lines and comments
            continue
        if line.endswith("{"):  # Start of a nested block
            new_dict = {}
            if current_key:
                stack[-1][current_key] = new_dict
            else:
                stack[-1][len(stack[-1])] = new_dict  # For unnamed blocks
            stack.append(new_dict)
            current_key = None
        elif line == "}":  # End of a nested block
            stack.pop()
        elif line.endswith(";"):  # Key-value pair
            key_value = line[:-1].split(maxsplit=1)
            if len(key_value) == 2:
                key, value = key_value
                try:
                    value = float(value)  # Convert numeric values
                except ValueError:
                    value = value.strip('"')  # Remove quotes if present
                stack[-1][key] = value
        else:  # Key without a value
            current_key = line
    return parsed_dict

# Function to generate OpenFOAM file content from a nested dictionary
def generate_openfoam_file_content(data, indent=0):
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):  # Handle nested blocks
            lines.append(f"{' ' * indent}{key} {{\n")
            lines.extend(generate_openfoam_file_content(value, indent + 4))
            lines.append(f"{' ' * indent}}}\n")
        else:
            if isinstance(value, float):
                value_str = f"{value:.6g}"
            else:
                value_str = f'"{value}"'
            lines.append(f"{' ' * indent}{key} {value_str};\n")
    return lines

# Populate the Treeview with nested dictionary data
def populate_treeview(parent, data):
    for key, value in data.items():
        if isinstance(value, dict):
            node_id = tree.insert(parent, 'end', text=key, open=True)
            populate_treeview(node_id, value)
        else:
            tree.insert(parent, 'end', text=key, values=(value,))

# Update a value in the nested dictionary


# Compare parsed values with user-defined values
def compare_values():
    user_input = compare_entry.get()
    if not user_input:
        messagebox.showerror("Error", "Please enter values to compare.")
        return

    comparisons = user_input.split(',')
    mismatches = []
    for item in comparisons:
        if '=' not in item:
            continue
        key_path, user_value = item.split('=', 1)
        user_value = user_value.strip()
        key_parts = key_path.strip().split('.')

        def find_key_in_dict(d, key_parts):
            """Recursively find a nested key in a dictionary."""
            if not key_parts:
                return d
            key = key_parts[0]
            if key in d:
                return find_key_in_dict(d[key], key_parts[1:])
            return None

        parsed_value = find_key_in_dict(openfoam_dict, key_parts)
        if parsed_value is None:
            mismatches.append(f"{key_path}: not found in parsed data.")
        elif str(parsed_value) != user_value:
            mismatches.append(f"{key_path}: expected {user_value}, found {parsed_value}")

    if mismatches:
        messagebox.showinfo("Comparison Results", "\n".join(mismatches))
    else:
        messagebox.showinfo("Comparison Results", "All values match!")

# Create the Tkinter window
window = tk.Tk()
window.title("OpenFOAM Editor")

# Load button
load_button = tk.Button(window, text="Load OpenFOAM File", command=load_openfoam_file)
load_button.pack()

# Treeview for nested data
tree = ttk.Treeview(window, columns=("Value",), show='tree headings')
tree.heading("#0", text="Property")
tree.heading("Value", text="Value")
tree.pack(fill=tk.BOTH, expand=True)



# Compare field and button
compare_label = tk.Label(window, text="Enter values to compare (key.subkey=value or block.key.subkey=value):")
compare_label.pack()

compare_entry = tk.Entry(window, width=50)
compare_entry.pack()

compare_button = tk.Button(window, text="Compare Values", command=compare_values)
compare_button.pack()

# Run the Tkinter loop
window.mainloop()
